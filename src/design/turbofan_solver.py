"""
Generic Turbofan Design Solver

Solves complete two-spool turbofan cycle using scipy matrix solver.

TURBOFAN-SPECIFIC ASSUMPTIONS:
- Two spools: HPC+HPT (high-pressure), Fan+LPT (low-pressure)
- Bypass splits after fan (Station 2.5)
- Convergent nozzles (subsonic, M < 1.0)
- Simple pressure loss in bypass duct (no cooling)
- Fan diameter ↔ mass flow sizing with hub/tip ratio

EXTENSIBLE TO:
- Turboprop: subclass, remove bypass, change power coupling (LPT drives propeller)
- Turbojet: subclass, remove fan, direct turbine to compressor
- Three-spool: subclass, add intermediate pressure spool

Physics Reference:
- Station numbering: 0 (freestream) → 1 (inlet) → 2.5 (fan) → 4 (HPC) → 5 (combustor)
  → 6 (HPT) → 7 (LPT) → 8 (core nozzle), 19 (bypass nozzle)
- Power balance: Work_turbine = Work_compressor (solved via scipy.fsolve)
- Fan sizing: ṁ = ρ × V × A_annulus, where A_annulus = π × r_tip² × (1 - λ²)

See: docs/design/SOLVER.md
"""

import math
from scipy.optimize import fsolve
from src.physics.stations import ThermodynamicStation
from src.physics.freestream import FreestreamCalculator
from src.physics.thermodynamics import ThermodynamicsCalculator
from src.design.parameters import DesignCase
from src.design.defaults import AllDefaults
from src.components.inlet import Inlet
from src.components.compressor import Compressor
from src.components.combustor import Combustor
from src.components.turbine import Turbine
from src.components.nozzle import Nozzle


class TurbofanDesignSolver:
    """
    Generic turbofan design-point cycle solver.
    
    Solves power balance equations using scipy.optimize.fsolve() to find
    turbine pressure ratios (PR_HPT, PR_LPT) such that:
    - HPT work = HPC work
    - LPT work = Fan work
    
    Handles fan sizing: given diameter, calculates mass flow; given mass flow,
    calculates required diameter.
    """
    
    def __init__(self, design_case: DesignCase):
        """
        Initialize solver with design case.
        
        Args:
            design_case (DesignCase): Design parameters (altitude, M0, PRs, efficiencies, etc.)
        """
        self.case = design_case
        self.calc = ThermodynamicsCalculator()
        self.freestream_calc = FreestreamCalculator()
        
        # Thermodynamic stations (populated during solve)
        self.stations = {}
        
        # Performance metrics (calculated at end)
        self.performance = {}
        
        # Fan sizing (resolved during initialization)
        self._resolve_fan_sizing()
    
    def _resolve_fan_sizing(self):
        """
        Resolve fan diameter ↔ mass flow relationship.
        
        If both specified: use fan_diameter, recalculate m_dot (diameter takes precedence)
        If only fan_diameter: m_dot calculated during solve (using Station 2)
        If only m_dot: fan_diameter calculated during solve (using Station 2)
        If neither: use default m_dot from AllDefaults
        
        Note: Actual calculation deferred to solve() when Station 2 is available.
        """
        self.fan_diameter = self.case.get_fan_diameter()
        self.m_dot_total = self.case.get_m_dot_total() if self.case.m_dot_total is not None else AllDefaults.MASS_FLOW_TOTAL
        self.hub_tip_ratio = self.case.get_hub_tip_ratio()
    
    def solve(self):
        """
        Solve complete turbofan cycle.
        
        Sequence:
        1. Freestream (Station 0)
        2. Inlet (Station 1)
        3. Fan (Station 2.5)
        4. Split: bypass and core
        5. HPC (Station 4)
        6. Combustor (Station 5)
        7. [Power Balance] Solve for PR_HPT using scipy.fsolve
        8. HPT (Station 6)
        9. [Power Balance] Solve for PR_LPT using scipy.fsolve
        10. LPT (Station 7)
        11. Fan nozzle (Station 2.7 → 19)
        12. Core nozzle (Station 8)
        13. Resolve fan sizing (diameter ↔ mass flow at Station 2)
        14. Calculate performance (thrust, SFC, efficiency)
        15. Return EngineState
        
        Returns:
            EngineState: Complete cycle solution with all stations and performance.
        """
        # ===== Step 1: Freestream (Station 0) =====
        altitude = self.case.get_altitude()
        M0 = self.case.get_M0()
        
        p0, T0, rho0, a0 = self.freestream_calc.atmospheric_conditions(altitude)
        V0 = self.freestream_calc.velocity_from_mach(M0, T0)
        p_t0 = self.freestream_calc.total_pressure_from_mach(M0, p0)
        T_t0 = self.freestream_calc.total_temperature_from_mach(M0, T0)
        
        station_0 = ThermodynamicStation(
            station_id="0",
            name="Freestream",
            p=p0,
            T=T0,
            p_t=p_t0,
            T_t=T_t0,
            V=V0,
            a=a0,
            M=M0,
            m_dot=self.m_dot_total
        )
        self.stations[0] = station_0
        
        # ===== Step 2: Inlet (Station 1) =====
        inlet = Inlet(recovery_factor=self.case.get_inlet_recovery())
        station_1 = inlet.process(station_0, station_id="1")
        station_1.m_dot = self.m_dot_total
        self.stations[1] = station_1
        
        # ===== Step 3: Fan (Station 2.5) =====
        fan = Compressor(
            name="Fan",
            pressure_ratio=self.case.get_PR_fan(),
            polytropic_efficiency=self.case.get_compressor_efficiency()
        )
        station_2_5 = fan.compress(station_1, station_id="2.5")
        station_2_5.m_dot = self.m_dot_total
        self.stations["2.5"] = station_2_5
        
        # ===== Step 4: Split flow into bypass and core =====
        bypass_ratio = self.case.get_bypass_ratio()
        m_dot_bypass = self.m_dot_total * bypass_ratio / (1 + bypass_ratio)
        m_dot_core = self.m_dot_total / (1 + bypass_ratio)
        
        # ===== Step 5: HPC (Station 4) =====
        hpc = Compressor(
            name="HPC",
            pressure_ratio=self.case.get_PR_HPC(),
            polytropic_efficiency=self.case.get_compressor_efficiency()
        )
        station_4 = hpc.compress(station_2_5, station_id="4")
        station_4.m_dot = m_dot_core
        self.stations[4] = station_4
        
        # ===== Step 6: Combustor (Station 5) =====
        combustor = Combustor(
            target_T_t=self.case.get_combustor_target_T_t(),
            efficiency=self.case.get_combustor_efficiency(),
            pressure_loss=self.case.get_combustor_pressure_loss()
        )
        station_5, far = combustor.combust(station_4, station_id="5")
        station_5.m_dot = m_dot_core
        self.stations[5] = station_5
        self.far = far
        
        # ===== Step 7: Power Balance - Solve for PR_HPT =====
        # Define power balance equation: Work_HPT - Work_HPC = 0
        def power_balance_HPT(PR_HPT):
            """Power balance: HPT work equals HPC work."""
            # Calculate HPT outlet
            hpt = Turbine(name="HPT", polytropic_efficiency=self.case.get_turbine_efficiency())
            station_6_test = hpt.expand(station_5, pressure_ratio=PR_HPT, station_id="6_test")
            
            # Work comparison (temperature-based proxy for enthalpy)
            # HPT work ∝ m_dot × cp × (T_in - T_out)
            # HPC work ∝ m_dot × cp × (T_out - T_in)
            # With different mass flows: m_dot_core × ΔT_HPT ≈ m_dot_total × ΔT_HPC
            work_HPT = m_dot_core * (station_5.T_t - station_6_test.T_t)
            work_HPC = m_dot_total * (station_4.T_t - station_2_5.T_t)
            
            return work_HPT - work_HPC
        
        # Solve for PR_HPT (initial guess: 0.3)
        PR_HPT_solution = fsolve(power_balance_HPT, 0.3)[0]
        
        # ===== Step 8: HPT (Station 6) =====
        hpt = Turbine(name="HPT", polytropic_efficiency=self.case.get_turbine_efficiency())
        station_6 = hpt.expand(station_5, pressure_ratio=PR_HPT_solution, station_id="6")
        station_6.m_dot = m_dot_core
        self.stations[6] = station_6
        
        # ===== Step 9: Power Balance - Solve for PR_LPT =====
        def power_balance_LPT(PR_LPT):
            """Power balance: LPT work equals fan work."""
            # LPT expands core flow, drives fan (which compresses all flow)
            lpt = Turbine(name="LPT", polytropic_efficiency=self.case.get_turbine_efficiency())
            station_7_test = lpt.expand(station_6, pressure_ratio=PR_LPT, station_id="7_test")
            
            work_LPT = m_dot_core * (station_6.T_t - station_7_test.T_t)
            work_fan = m_dot_total * (station_2_5.T_t - station_1.T_t)
            
            return work_LPT - work_fan
        
        # Solve for PR_LPT (initial guess: 0.4)
        PR_LPT_solution = fsolve(power_balance_LPT, 0.4)[0]
        
        # ===== Step 10: LPT (Station 7) =====
        lpt = Turbine(name="LPT", polytropic_efficiency=self.case.get_turbine_efficiency())
        station_7 = lpt.expand(station_6, pressure_ratio=PR_LPT_solution, station_id="7")
        station_7.m_dot = m_dot_core
        self.stations[7] = station_7
        
        # ===== Step 11: Bypass duct (Station 2.7) =====
        # Simple pressure loss in bypass duct
        bypass_loss = self.case.get_bypass_duct_loss()
        p_t_2_7 = station_2_5.p_t * (1 - bypass_loss)
        
        station_2_7 = ThermodynamicStation(
            station_id="2.7",
            name="Bypass Nozzle Inlet",
            p_t=p_t_2_7,
            T_t=station_2_5.T_t,  # Adiabatic
            m_dot=m_dot_bypass
        )
        self.stations["2.7"] = station_2_7
        
        # ===== Step 12: Bypass Nozzle (Station 19) =====
        bypass_nozzle = Nozzle(name="Bypass", efficiency=self.case.get_nozzle_efficiency())
        # Exit to ambient pressure
        p_ambient = p0
        station_19, V_19, M_19 = bypass_nozzle.expand(
            station_2_7,
            exit_pressure=p_ambient,
            station_id="19"
        )
        station_19.m_dot = m_dot_bypass
        self.stations[19] = station_19
        
        # ===== Step 13: Core Nozzle (Station 8) =====
        core_nozzle = Nozzle(name="Core", efficiency=self.case.get_nozzle_efficiency())
        station_8, V_8, M_8 = core_nozzle.expand(
            station_7,
            exit_pressure=p_ambient,
            station_id="8"
        )
        station_8.m_dot = m_dot_core
        self.stations[8] = station_8
        
        # ===== Step 14: Resolve Fan Sizing (Diameter ↔ Mass Flow) =====
        self._calculate_fan_sizing(station_2_5, p0, T0)
        
        # ===== Step 15: Calculate Performance Metrics =====
        self._calculate_performance(
            V_0=V0,
            V_8=V_8,
            V_19=V_19,
            m_dot_core=m_dot_core,
            m_dot_bypass=m_dot_bypass
        )
        
        # ===== Step 16: Return EngineState =====
        from src.physics.engine_state import EngineState
        
        engine_state = EngineState(
            design_case=self.case,
            stations=self.stations,
            performance=self.performance,
            fan_diameter=self.fan_diameter,
            hub_tip_ratio=self.hub_tip_ratio,
            PR_HPT=PR_HPT_solution,
            PR_LPT=PR_LPT_solution,
            fuel_air_ratio=self.far
        )
        
        return engine_state
    
    def _calculate_fan_sizing(self, station_2, p0, T0):
        """
        Calculate fan diameter ↔ mass flow relationship.
        
        At fan inlet (Station 2):
        - ṁ = ρ₂ × V₂ × A_annulus
        - A_annulus = π × r_tip² × (1 - λ²)
        
        If fan_diameter specified: calculate m_dot
        If fan_diameter not specified: calculate D from m_dot
        """
        # Calculate velocity at Station 2 (fan inlet)
        V_2 = math.sqrt(2 * self.calc.cp * (station_2.T_t - station_2.T)) if station_2.T is None else 0
        
        # If T at Station 2 not available, estimate from total temperature
        # Using isentropic relation: T = T_t / (1 + (γ-1)/2 × M²)
        # At inlet, assume low Mach (~0.1), so T ≈ T_t × 0.995
        if station_2.T is None:
            station_2.T = station_2.T_t * 0.995
        
        # Density at Station 2
        rho_2 = station_2.p_t / (self.calc.R * station_2.T)  # Approximation using total pressure
        
        # Annulus area coefficient: π × (1 - λ²)
        lambda_sq = self.hub_tip_ratio ** 2
        area_coeff = math.pi * (1 - lambda_sq)
        
        if self.fan_diameter is not None:
            # Given diameter: calculate mass flow
            r_tip = self.fan_diameter / 2
            A_annulus = area_coeff * r_tip ** 2
            self.m_dot_total = rho_2 * V_2 * A_annulus
        else:
            # Given mass flow: calculate diameter
            A_annulus = self.m_dot_total / (rho_2 * V_2 + 1e-10)  # Add epsilon to avoid division by zero
            r_tip = math.sqrt(A_annulus / area_coeff)
            self.fan_diameter = 2 * r_tip
    
    def _calculate_performance(self, V_0, V_8, V_19, m_dot_core, m_dot_bypass):
        """
        Calculate performance metrics:
        - Thrust (core + bypass)
        - Specific Fuel Consumption (SFC)
        - Thermal efficiency
        - Propulsive efficiency
        - Overall efficiency
        
        Args:
            V_0 (float): Freestream velocity (m/s)
            V_8 (float): Core nozzle exit velocity (m/s)
            V_19 (float): Bypass nozzle exit velocity (m/s)
            m_dot_core (float): Core mass flow (kg/s)
            m_dot_bypass (float): Bypass mass flow (kg/s)
        """
        # ===== Thrust Calculation =====
        # F = ṁ × (V_exit - V_0) [momentum thrust]
        thrust_core = m_dot_core * (V_8 - V_0)
        thrust_bypass = m_dot_bypass * (V_19 - V_0)
        total_thrust = thrust_core + thrust_bypass
        
        # ===== Fuel Flow =====
        fuel_flow = self.m_dot_total * self.far  # kg/s
        
        # ===== SFC (Specific Fuel Consumption) =====
        # SFC = fuel_flow / thrust [kg/(N·s) or lb/(lb·h)]
        SFC = fuel_flow / (total_thrust + 1e-10)
        
        # ===== Fuel Energy Input =====
        fuel_heating_value = 43.15e6  # J/kg (Jet A-1)
        Q_fuel = fuel_flow * fuel_heating_value  # W (Joules/s)
        
        # ===== Turbine vs Compressor Work =====
        station_5 = self.stations[5]
        station_7 = self.stations[7]
        station_4 = self.stations[4]
        station_2_5 = self.stations["2.5"]
        
        # Work (Joules/s = Watts)
        W_HPT = m_dot_core * self.calc.cp * (station_5.T_t - station_7.T_t)
        W_HPC = self.m_dot_total * self.calc.cp * (station_4.T_t - station_2_5.T_t)
        W_fan = self.m_dot_total * self.calc.cp * (station_2_5.T_t - self.stations[1].T_t)
        
        W_total_turbine = W_HPT + W_fan  # Approximation (LPT work ≈ fan work)
        W_total_compressor = W_HPC + W_fan
        
        # ===== Thermal Efficiency =====
        # η_th = (W_turbine - W_compressor) / Q_fuel
        eta_thermal = (W_total_turbine - W_total_compressor) / (Q_fuel + 1e-10)
        
        # ===== Propulsive Efficiency =====
        # η_prop = (useful power out) / (kinetic energy flux out)
        # η_prop = 2 / (1 + V_exit/V_0)  [for ideal case]
        # More general: η_prop = thrust × V_0 / (kinetic energy flux)
        KE_core = 0.5 * m_dot_core * V_8 ** 2
        KE_bypass = 0.5 * m_dot_bypass * V_19 ** 2
        KE_total = KE_core + KE_bypass
        
        eta_propulsive = (total_thrust * V_0) / (KE_total + 1e-10)
        
        # ===== Overall Efficiency =====
        # η_overall = η_thermal × η_propulsive
        eta_overall = eta_thermal * eta_propulsive
        
        # Store all metrics
        self.performance = {
            "thrust_core": thrust_core,
            "thrust_bypass": thrust_bypass,
            "total_thrust": total_thrust,
            "fuel_flow": fuel_flow,
            "SFC": SFC,
            "thermal_efficiency": eta_thermal,
            "propulsive_efficiency": eta_propulsive,
            "overall_efficiency": eta_overall,
            "work_HPC": W_HPC,
            "work_turbine": W_total_turbine,
            "fuel_energy_input": Q_fuel,
        }