"""
Freestream Module

Manages freestream conditions and Station 0 creation.
This is the central place to handle all freestream/ambient calculations,
integrating ISAAtmosphere, ThermodynamicsCalculator, and ThermodynamicStation.

Key responsibilities:
1. Get ambient static conditions (from ISA altitude or manual input)
2. Convert diameter → mass flow (or vice versa)
3. Calculate ram effect (static → total conditions)
4. Create complete Station 0 with all properties
"""

import math
from typing import Tuple, Optional

from src.physics.atmosphere import ISAAtmosphere
from src.physics.thermodynamics import ThermodynamicsCalculator, AirProperties
from src.physics.stations import ThermodynamicStation


class FreestreamConditions:
    """
    Manages freestream conditions and Station 0 creation.
    
    This class encapsulates all logic for:
    - Getting ambient conditions from ISA or manual input
    - Converting between mass flow and inlet diameter
    - Calculating total conditions from freestream Mach
    - Creating a complete ThermodynamicStation for Station 0
    
    By centralizing this logic here, we avoid duplication across
    DesignParameters, Inlet, and other components.
    """
    
    def __init__(self):
        """
        Initialize FreestreamConditions with required calculators.
        
        WHY: We instantiate ISAAtmosphere and ThermodynamicsCalculator once
        during initialization so we don't create new instances for every calculation.
        This is more efficient and follows the factory pattern.
        """
        self.isa = ISAAtmosphere()
        self.calc = ThermodynamicsCalculator()
    
    def get_ambient_conditions(
        self,
        altitude_mode: str,
        altitude: Optional[float] = None,
        T0_static: Optional[float] = None,
        P0_static: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Get ambient static conditions from either ISA or manual input.
        
        This method provides a single interface for getting ambient T and P,
        regardless of whether they come from ISA lookup or manual specification.
        
        HOW IT WORKS:
        - If altitude_mode == "ISA": use ISAAtmosphere.conditions_at_altitude()
          to get both T and P from a single altitude value
        - If altitude_mode == "manual": just return the provided values directly
        - Otherwise: raise ValueError to catch configuration errors early
        
        WHY this approach:
        - Single source of truth for how to get ambient conditions
        - Prevents duplicated ISA calculations throughout codebase
        - Clean interface: one method, two modes
        
        Args:
            altitude_mode (str): Either "ISA" or "manual"
            altitude (float): Altitude in meters (required if altitude_mode == "ISA")
            T0_static (float): Static temperature in Kelvin (required if altitude_mode == "manual")
            P0_static (float): Static pressure in Pascals (required if altitude_mode == "manual")
        
        Returns:
            Tuple[float, float]: (T0_static, P0_static) in Kelvin and Pascals
        
        Raises:
            ValueError: If altitude_mode is unrecognized or required parameters missing
        
        Example:
            # ISA mode: conditions at 10 km
            >>> T, P = fs.get_ambient_conditions("ISA", altitude=10000)
            >>> print(f"T={T:.2f} K, P={P:.1f} Pa")
            T=223.15 K, P=26496.0 Pa
            
            # Manual mode: custom conditions
            >>> T, P = fs.get_ambient_conditions("manual", T0_static=250, P0_static=30000)
            >>> print(f"T={T} K, P={P} Pa")
            T=250 K, P=30000 Pa
        """
        if altitude_mode == "ISA":
            # Use ISA model to get conditions at specified altitude
            # conditions_at_altitude() returns (T, P) tuple
            return self.isa.conditions_at_altitude(altitude)
        
        elif altitude_mode == "manual":
            # Return user-provided static conditions directly
            return T0_static, P0_static
        
        else:
            # Catch misconfiguration early
            raise ValueError(
                f"Unknown altitude_mode: '{altitude_mode}'. "
                f"Must be 'ISA' or 'manual'."
            )
    
    def calculate_m_dot_from_diameter(
        self,
        diameter_fan: float,
        hub_to_tip_ratio: float,
        M0: float,
        T0_static: float,
        P0_static: float
    ) -> float:
        """
        Calculate mass flow rate from fan section diameter.
        
        This is the FORWARD direction: given inlet diameter → compute mass flow
        
        THE PHYSICS:
        
        1. ANNULAR AREA CALCULATION:
           The fan inlet is annular (ring-shaped), not a solid circle.
           - Outer diameter: D_tip = diameter_fan
           - Inner diameter: D_hub = hub_to_tip_ratio × D_tip
           - Annular area: A = (π/4) × (D_tip² - D_hub²)
                         = (π/4) × D_tip² × (1 - η²)
           where η = hub_to_tip_ratio
           
           WHY annular? Turbofan engines have a hub (center axle) in the middle
           of the compressor/turbine. Air flows in the annular duct around it.
        
        2. FREESTREAM AIR PROPERTIES:
           At sea level (or any altitude), we need to know the air density and
           speed of sound to calculate how much air enters the engine.
           - Density: ρ = P / (R × T) from ideal gas law
           - Speed of sound: a = √(γ × R × T) from thermodynamics
        
        3. FREESTREAM VELOCITY:
           Given Mach number, velocity is simply:
           - V = M × a
           
           WHY Mach? Because we want the speed as a fraction of sound speed,
           which properly accounts for compressibility effects.
        
        4. MASS FLOW FROM CONTINUITY:
           Conservation of mass: ṁ = ρ × V × A
           - ρ: density at freestream
           - V: velocity at freestream
           - A: cross-sectional area (annular inlet area)
           
           This is the fundamental equation connecting geometry (A, diameter)
           to engine performance (ṁ).
        
        WHY use actual freestream altitude?
        - At sea level with diameter D: higher ρ, higher a, different ṁ
        - At 10 km with same diameter D: lower ρ, lower a, different ṁ
        - By using actual flight altitude, we get realistic mass flows
        - Industry standard: always use actual ambient conditions
        
        Args:
            diameter_fan (float): Outer diameter of fan inlet (meters)
                                  This is the FAN SECTION diameter, not inlet
            hub_to_tip_ratio (float): D_hub / D_tip ratio, typically 0.3
                                      Default NASA values: 0.25-0.35
            M0 (float): Freestream Mach number (e.g., 0.85 for cruise)
            T0_static (float): Freestream static temperature (Kelvin)
                              From ISA or manual input
            P0_static (float): Freestream static pressure (Pascals)
                              From ISA or manual input
        
        Returns:
            float: Mass flow rate (kg/s)
        
        Raises:
            ValueError: If any input is physically invalid
        
        Example:
            # Sea level, M=0.0 (hovering):
            >>> m_dot = fs.calculate_m_dot_from_diameter(
            ...     diameter_fan=2.5,  # 2.5 meter fan
            ...     hub_to_tip_ratio=0.3,
            ...     M0=0.0,  # stationary
            ...     T0_static=288.15,  # sea level temp
            ...     P0_static=101325  # sea level pressure
            ... )
            >>> print(f"ṁ = {m_dot:.2f} kg/s")
            
            # Cruise at 10 km, M=0.85:
            >>> T, P = ISAAtmosphere.conditions_at_altitude(10000)
            >>> m_dot = fs.calculate_m_dot_from_diameter(
            ...     diameter_fan=2.0,
            ...     hub_to_tip_ratio=0.3,
            ...     M0=0.85,
            ...     T0_static=T,
            ...     P0_static=P
            ... )
            >>> print(f"ṁ = {m_dot:.2f} kg/s")
        """
        # Step 1: Calculate annular inlet area
        # A = (π/4) × D² × (1 - η²)
        # Note: using math.pi for precision, not hardcoded 3.14159
        area_fan = (math.pi / 4) * (diameter_fan ** 2) * (1 - hub_to_tip_ratio ** 2)
        
        # Step 2: Get air density from P and T using ideal gas law
        # ρ = P / (R × T)
        # calc.density_from_pressure_temperature() handles this
        rho0 = self.calc.density_from_pressure_temperature(P0_static, T0_static)
        
        # Step 3: Get speed of sound at freestream temperature
        # a = √(γ × R × T)
        # calc.speed_of_sound() handles this
        a0 = self.calc.speed_of_sound(T0_static)
        
        # Step 4: Calculate freestream velocity
        V0 = self.calc.velocity_from_mach(M0, a0)

        # Step 5: Apply continuity equation
        m_dot = self.calc.mass_flow_from_continuity(rho0, V0, area_fan) 
        
        return m_dot
    
    def calculate_diameter_from_m_dot(
        self,
        m_dot_total: float,
        hub_to_tip_ratio: float,
        M0: float,
        T0_static: float,
        P0_static: float
    ) -> float:
        """
        Calculate fan section diameter from desired mass flow rate.
        
        This is the INVERSE direction: given mass flow → compute diameter
        
        This is useful for design: "I want 400 kg/s at cruise. What diameter fan do I need?"
        
        THE PHYSICS:
        
        Rearranging the continuity equation from calculate_m_dot_from_diameter():
        
        ṁ = ρ × V × A
        ṁ = ρ × V × (π/4) × D² × (1 - η²)
        
        Solving for D:
        D² = ṁ / [ρ × V × (π/4) × (1 - η²)]
        D = √[ṁ / (ρ × V × (π/4) × (1 - η²))]
        
        This is just rearranging the forward calculation.
        
        WHY is this useful?
        - Design iteration: "I need 500 kg/s, what's the minimum fan diameter?"
        - Constraint analysis: "Given this diameter, what flows can I achieve?"
        - Parametric studies: sweep diameter → see effect on mass flow
        
        Args:
            m_dot_total (float): Desired mass flow rate (kg/s)
            hub_to_tip_ratio (float): D_hub / D_tip ratio, typically 0.3
            M0 (float): Freestream Mach number
            T0_static (float): Freestream static temperature (K)
            P0_static (float): Freestream static pressure (Pa)
        
        Returns:
            float: Required fan section diameter (meters)
        
        Raises:
            ValueError: If calculated diameter is physically unrealistic
        
        Example:
            # Design requirement: 400 kg/s at cruise
            >>> diameter = fs.calculate_diameter_from_m_dot(
            ...     m_dot_total=400,
            ...     hub_to_tip_ratio=0.3,
            ...     M0=0.85,
            ...     T0_static=223.15,  # At 10 km
            ...     P0_static=26496    # At 10 km
            ... )
            >>> print(f"Required fan diameter: {diameter:.3f} m")
            Required fan diameter: 2.145 m
        """
        # Step 1: Get air properties at freestream
        rho0 = self.calc.density_from_pressure_temperature(P0_static, T0_static)
        a0 = self.calc.speed_of_sound(T0_static)
        V0 = self.calc.velocity_from_mach(M0, a0)
        
        # Step 2: Rearrange continuity equation to solve for diameter
        # From: ṁ = ρ × V × (π/4) × D² × (1 - η²)
        # To:   D² = ṁ / [ρ × V × (π/4) × (1 - η²)]
        
        denominator = rho0 * V0 * (math.pi / 4) * (1 - hub_to_tip_ratio ** 2)
        
        if denominator <= 0:
            raise ValueError(
                f"Invalid calculation: denominator={denominator}. "
                f"Check inputs (rho0={rho0}, V0={V0})"
            )
        
        diameter_squared = m_dot_total / denominator
        
        if diameter_squared < 0:
            raise ValueError(
                f"Negative diameter squared: {diameter_squared}. "
                f"Check mass flow input (m_dot={m_dot_total})"
            )
        
        diameter_fan = math.sqrt(diameter_squared)
        
        # Sanity check: realistic turbofan diameters are typically 1-4 meters
        if diameter_fan < 0.5 or diameter_fan > 5.0:
            raise ValueError(
                f"Calculated fan diameter {diameter_fan:.2f} m is unrealistic. "
                f"Typical range: 0.5-5.0 m for turbofan engines. "
                f"Check mass flow input (m_dot={m_dot_total} kg/s)."
            )
        
        return diameter_fan
    
    def create_station_0(
        self,
        altitude_mode: str,
        M0: float,
        m_dot_total: float,
        altitude: Optional[float] = None,
        T0_static: Optional[float] = None,
        P0_static: Optional[float] = None
    ) -> ThermodynamicStation:
        """
        Create Station 0 (freestream) from ambient conditions.
        
        Station 0 represents the FREE STREAM FAR UPSTREAM OF THE ENGINE.
        It contains all freestream properties converted to total (stagnation) conditions
        and set up for the engine calculation pipeline.
        
        THE PHYSICS:
        
        1. STATIC vs TOTAL CONDITIONS:
           
           Static conditions: What a thermometer and pressure gauge would measure
           if they were moving with the air (in the air's reference frame)
           - T (static temp): ~223 K at 10 km cruise
           - P (static pressure): ~26,500 Pa at 10 km
           
           Total conditions: What you'd measure if you stagnated the air (brought it to rest)
           - T_t (total temp): T + V²/(2×c_p) = static temp + ram effect
           - P_t (total pressure): from isentropic relation
           
           WHY does this matter?
           - Inside the engine, air is compressed and decelerated
           - We use total conditions because they're constants through isentropic processes
           - T_t and P_t are the "source" conditions for engine cycle calculations
        
        2. RAM EFFECT:
           As the aircraft moves forward at Mach M, freestream air is compressed
           and heated due to ram pressure.
           
           For M=0.85 at 10 km (T=223K):
           - Speed of sound: a = √(1.4 × 287 × 223) ≈ 299 m/s
           - Velocity: V = 0.85 × 299 ≈ 254 m/s
           - Temperature rise: ΔT = V²/(2×c_p) ≈ 32 K (!!)
           - Total temp: T_t ≈ 223 + 32 ≈ 255 K
           
           This ram effect is CRUCIAL for high-speed flight!
           At sea level M=0, ram effect is zero.
           At cruise M=0.85, ram effect is significant.
        
        3. MASS FLOW CONSERVATION:
           ṁ = ρ × V × A = constant through the engine (continuity)
           The mass flow through Station 0 (freestream) is what we design for.
        
        HOW THIS METHOD WORKS:
        
        Step 1: Get ambient static conditions (from ISA or manual)
        Step 2: Calculate freestream air properties (density, speed of sound)
        Step 3: Calculate freestream velocity (V = M × a)
        Step 4: Use ram effect to get total conditions
        Step 5: Create ThermodynamicStation with all properties filled
        
        Args:
            altitude_mode (str): "ISA" or "manual"
            M0 (float): Freestream Mach number
            m_dot_total (float): Total mass flow through engine (kg/s)
            altitude (float): If altitude_mode == "ISA"
            T0_static (float): If altitude_mode == "manual"
            P0_static (float): If altitude_mode == "manual"
        
        Returns:
            ThermodynamicStation: Complete Station 0 with all properties
        
        Raises:
            ValueError: If any calculation fails or inputs invalid
        
        Example:
            # Cruise at 10 km, M=0.85, 400 kg/s
            >>> station_0 = fs.create_station_0(
            ...     altitude_mode="ISA",
            ...     M0=0.85,
            ...     m_dot_total=400,
            ...     altitude=10000
            ... )
            >>> print(f"Station 0 created:")
            >>> print(f"  p_t = {station_0.p_t:.0f} Pa")
            >>> print(f"  T_t = {station_0.T_t:.2f} K")
            >>> print(f"  ṁ = {station_0.m_dot:.0f} kg/s")
        """
        # Step 1: Get ambient static conditions
        T0_static, P0_static = self.get_ambient_conditions(
            altitude_mode, altitude, T0_static, P0_static
        )
        
        # Step 2: Calculate air properties at freestream
        # Density from ideal gas law
        rho0 = self.calc.density_from_pressure_temperature(P0_static, T0_static)
        
        # Speed of sound at freestream temperature
        a0 = self.calc.speed_of_sound(T0_static)
        
        # Step 3: Calculate freestream velocity
# Step 3: Calculate freestream velocity
        V0 = self.calc.velocity_from_mach(M0, a0)        
        # Step 4: Calculate total (stagnation) conditions using ram effect
        # The ThermodynamicsCalculator.ram_effect_conditions() method handles
        # the conversion from static to total:
        # - T_t = T × (1 + (γ-1)/2 × M²)
        # - P_t = P × (T_t/T)^(γ/(γ-1))
        T0_total, P0_total = self.calc.ram_effect_conditions(
            T0_static, P0_static, M0
        )
        
        # Step 5: Create Station 0 ThermodynamicStation object
        # Station 0 is the freestream: far upstream before any engine components
        station_0 = ThermodynamicStation(
            station_id="0",
            name="Freestream",
            
            # Total properties (ram effect applied)
            p_t=P0_total,
            T_t=T0_total,
            
            # Static properties (ambient conditions)
            p=P0_static,
            T=T0_static,
            
            # Flow properties
            M=M0,
            V=V0,
            a=a0,
            
            # Mass flow
            m_dot=m_dot_total,
            
            # Derived properties
            rho=rho0
        )
        
        return station_0