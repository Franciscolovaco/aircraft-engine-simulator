"""
Freestream Module

Manages Station 0 (freestream) creation and ambient conditions.
Central hub for design inputs: altitude, Mach, mass flow.
See: docs/physics/FREESTREAM_STATION0.md
"""

import math
from typing import Tuple, Optional

from src.physics.atmosphere import ISAAtmosphere
from src.physics.thermodynamics import ThermodynamicsCalculator, AirProperties
from src.physics.stations import ThermodynamicStation


class FreestreamConditions:
    """
    Manages Station 0 creation and freestream/ambient condition conversions.
    
    Integrates ISAAtmosphere, ThermodynamicsCalculator, and ThermodynamicStation.
    Supports ISA or manual ambient specification.
    """
    
    def __init__(self):
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
        Get static ambient conditions from ISA or manual input.
        
        Args:
            altitude_mode: "ISA" or "manual"
            altitude: Altitude (m) if ISA mode
            T0_static: Temperature (K) if manual mode
            P0_static: Pressure (Pa) if manual mode
        
        Returns:
            (T_static, P_static) in Kelvin and Pascals
        """
        if altitude_mode == "ISA":
            return self.isa.conditions_at_altitude(altitude)
        elif altitude_mode == "manual":
            return T0_static, P0_static
        else:
            raise ValueError(f"altitude_mode must be 'ISA' or 'manual', got '{altitude_mode}'")
    
    def calculate_m_dot_from_diameter(
        self,
        diameter_fan: float,
        hub_to_tip_ratio: float,
        M0: float,
        T0_static: float,
        P0_static: float
    ) -> float:
        """
        Forward: diameter → mass flow.
        
        TURBOFAN-SPECIFIC: Annular inlet area (hub-to-tip ratio).
        For other engines, override to use solid circle or other geometry.
        
        ṁ = ρ × V × A_annular = ρ × (M × a) × π/4 × D² × (1 - η²)
        
        See: FREESTREAM_STATION0.md
        """
        # Annular area: A = (π/4) × D² × (1 - η²)
        area_fan = (math.pi / 4) * (diameter_fan ** 2) * (1 - hub_to_tip_ratio ** 2)
        
        # Air properties at freestream
        rho0 = self.calc.density_from_pressure_temperature(P0_static, T0_static)
        a0 = self.calc.speed_of_sound(T0_static)
        V0 = self.calc.velocity_from_mach(M0, a0)
        
        # Continuity
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
        Inverse: mass flow → diameter.
        
        TURBOFAN-SPECIFIC: Annular inlet geometry.
        
        D = √[ṁ / (ρ × V × (π/4) × (1 - η²))]
        
        See: FREESTREAM_STATION0.md
        """
        rho0 = self.calc.density_from_pressure_temperature(P0_static, T0_static)
        a0 = self.calc.speed_of_sound(T0_static)
        V0 = self.calc.velocity_from_mach(M0, a0)
        
        denominator = rho0 * V0 * (math.pi / 4) * (1 - hub_to_tip_ratio ** 2)
        
        if denominator <= 0:
            raise ValueError("Invalid geometry or flow properties")
        
        diameter_fan = math.sqrt(m_dot_total / denominator)
        
        if diameter_fan < 0.5 or diameter_fan > 5.0:
            raise ValueError(f"Diameter {diameter_fan:.2f} m unrealistic for turbofan (0.5-5.0 m)")
        
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
        Create Station 0 (freestream) with ram effect applied.
        
        Design input: (altitude_mode, M0, m_dot_total) fully define Station 0.
        
        Station 0 contains:
        - Static: ambient T, P at freestream
        - Total: T_t, P_t with ram effect applied (crucial for cruise)
        - Flow: Mach, velocity, speed of sound
        - Mass flow: ṁ (constant through engine)
        
        See: FREESTREAM_STATION0.md for ram effect physics
        """
        # Get ambient static conditions
        T0_static, P0_static = self.get_ambient_conditions(
            altitude_mode, altitude, T0_static, P0_static
        )
        
        # Freestream properties
        rho0 = self.calc.density_from_pressure_temperature(P0_static, T0_static)
        a0 = self.calc.speed_of_sound(T0_static)
        V0 = self.calc.velocity_from_mach(M0, a0)
        
        # Ram effect: static → total
        T0_total, P0_total = self.calc.ram_effect_conditions(T0_static, P0_static, M0)
        
        # Create Station 0
        station_0 = ThermodynamicStation(
            station_id="0",
            name="Freestream",
            p_t=P0_total,
            T_t=T0_total,
            p=P0_static,
            T=T0_static,
            M=M0,
            V=V0,
            a=a0,
            m_dot=m_dot_total,
            rho=rho0
        )
        
        return station_0