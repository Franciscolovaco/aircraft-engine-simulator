"""
Thermodynamics Calculator Module

Calculates thermodynamic properties for gas turbine engine stations.
Uses European notation: p_t/T_t (total), p/T (static).

See: docs/physics/THERMODYNAMICS_REFERENCE.md
"""

import math
from typing import Tuple


class AirProperties:
    """Standard air properties (constant across engine types)."""
    GAMMA = 1.4
    R_SPECIFIC = 287.05
    C_P = 1005.0
    C_V = C_P - R_SPECIFIC
    T0_KELVIN = 288.15
    P0_PASCAL = 101325
    FUEL_HEATING_VALUE = 43.0e6  # Jet fuel


class ThermodynamicsCalculator:
    """
    Calculates thermodynamic properties for engine cycle stations.
    
    Handles isentropic/polytropic processes, nozzle expansion, combustor energy balance.
    See: docs/physics/ for detailed physics and examples.
    """
    
    def __init__(self):
        self.gamma = AirProperties.GAMMA
        self.R = AirProperties.R_SPECIFIC
        self.cp = AirProperties.C_P
        self.cv = AirProperties.C_V
    
    # ISENTROPIC RELATIONS
    
    def isentropic_temperature_ratio(self, pressure_ratio: float) -> float:
        """T2/T1 = (P2/P1)^((γ-1)/γ). See ISENTROPIC_POLYTROPIC.md."""
        if pressure_ratio <= 0:
            raise ValueError("Pressure ratio must be positive")
        return pressure_ratio ** ((self.gamma - 1) / self.gamma)
    
    def total_temperature_ratio_from_mach(self, mach: float) -> float:
        """T_t/T = 1 + ((γ-1)/2) × M². See STATION_PROPERTIES.md."""
        if mach < 0:
            raise ValueError("Mach cannot be negative")
        return 1 + ((self.gamma - 1) / 2) * (mach ** 2)
    
    def total_pressure_ratio_from_mach(self, mach: float) -> float:
        """P_t/P = (T_t/T)^(γ/(γ-1)). See STATION_PROPERTIES.md."""
        if mach < 0:
            raise ValueError("Mach cannot be negative")
        temp_ratio = self.total_temperature_ratio_from_mach(mach)
        return temp_ratio ** (self.gamma / (self.gamma - 1))
    
    # POLYTROPIC PROCESSES (TURBINE/COMPRESSOR)
    
    def polytropic_compression(
        self,
        T_inlet: float,
        pressure_ratio: float,
        polytropic_efficiency: float
    ) -> float:
        """
        T_outlet = T_inlet × (PR)^((γ-1)/(γ×η_poly))
        See: ISENTROPIC_POLYTROPIC.md for detailed derivation.
        """
        if T_inlet <= 0:
            raise ValueError("Inlet temperature must be positive")
        if pressure_ratio <= 1:
            raise ValueError("Compression PR must be > 1")
        if not (0 < polytropic_efficiency <= 1):
            raise ValueError("Polytropic efficiency must be (0, 1]")
        
        exponent = (self.gamma - 1) / (self.gamma * polytropic_efficiency)
        return T_inlet * (pressure_ratio ** exponent)
    
    def polytropic_expansion(
        self,
        T_inlet: float,
        pressure_ratio: float,
        polytropic_efficiency: float
    ) -> float:
        """
        T_outlet = T_inlet × (PR)^((γ-1)×η_poly/γ)
        See: ISENTROPIC_POLYTROPIC.md for detailed derivation.
        """
        if T_inlet <= 0:
            raise ValueError("Inlet temperature must be positive")
        if not (0 < pressure_ratio < 1):
            raise ValueError("Expansion PR must be (0, 1)")
        if not (0 < polytropic_efficiency <= 1):
            raise ValueError("Polytropic efficiency must be (0, 1]")
        
        exponent = (self.gamma - 1) * polytropic_efficiency / self.gamma
        return T_inlet * (pressure_ratio ** exponent)
    
    # NOZZLE CALCULATIONS
    
    def nozzle_exit_velocity(self, T_total: float, T_static: float) -> float:
        """V = √(2 × cp × (T_t - T)). See THERMODYNAMICS_REFERENCE.md."""
        if T_total <= 0 or T_static <= 0:
            raise ValueError("Temperatures must be positive")
        if T_static > T_total:
            raise ValueError("T_static cannot exceed T_total")
        return math.sqrt(2 * self.cp * (T_total - T_static))
    
    def isentropic_nozzle_expansion(
        self,
        T_total: float,
        p_total: float,
        p_static: float,
        nozzle_efficiency: float = 1.0
    ) -> Tuple[float, float, float]:
        """
        Returns: (T_exit, V_exit, M_exit)
        See: THERMODYNAMICS_REFERENCE.md for isentropic expansion theory.
        """
        if not (0 < nozzle_efficiency <= 1):
            raise ValueError("Nozzle efficiency must be (0, 1]")
        
        pressure_ratio = p_static / p_total
        exponent = (self.gamma - 1) / self.gamma
        T_isentropic = T_total * (pressure_ratio ** exponent)
        T_exit = T_total - nozzle_efficiency * (T_total - T_isentropic)
        
        V_exit = self.nozzle_exit_velocity(T_total, T_exit)
        a_exit = math.sqrt(self.gamma * self.R * T_exit)
        M_exit = V_exit / a_exit
        
        return T_exit, V_exit, M_exit
    
    # COMBUSTOR
    
    def fuel_air_ratio_from_temperature_rise(
        self,
        T_inlet: float,
        T_outlet: float,
        combustor_efficiency: float = 0.98
    ) -> float:
        """
        f = cp·ΔT / (η·q_r - cp·T_outlet)
        See: THERMODYNAMICS_REFERENCE.md for combustor energy balance.
        """
        if T_inlet <= 0 or T_outlet <= 0:
            raise ValueError("Temperatures must be positive")
        if T_outlet <= T_inlet:
            raise ValueError("Outlet temp must exceed inlet")
        if not (0 < combustor_efficiency <= 1):
            raise ValueError("Combustor efficiency must be (0, 1]")
        
        delta_T = T_outlet - T_inlet
        numerator = self.cp * delta_T
        denominator = combustor_efficiency * AirProperties.FUEL_HEATING_VALUE - self.cp * T_outlet
        f = numerator / denominator
        
        if f < 0 or f > 0.1:
            raise ValueError(f"FAR {f} unrealistic (typically < 0.05)")
        
        return f
    
    # AMBIENT CONDITIONS (RAM EFFECT)
    
    def ram_effect_conditions(
        self,
        T_static: float,
        p_static: float,
        mach: float
    ) -> Tuple[float, float]:
        """
        (T_t, P_t) from static conditions and Mach.
        See: FREESTREAM_STATION0.md for ram effect physics.
        """
        if T_static <= 0 or p_static <= 0 or mach < 0:
            raise ValueError("T, P must be positive; Mach >= 0")
        
        T_total = T_static * self.total_temperature_ratio_from_mach(mach)
        P_total = p_static * self.total_pressure_ratio_from_mach(mach)
        
        return T_total, P_total
    
    # UTILITY FUNCTIONS
    
    def speed_of_sound(self, T: float) -> float:
        """a = √(γ × R × T)."""
        if T <= 0:
            raise ValueError("Temperature must be positive")
        return math.sqrt(self.gamma * self.R * T)
    
    def density_from_pressure_temperature(self, p: float, T: float) -> float:
        """ρ = p / (R × T)."""
        if p <= 0 or T <= 0:
            raise ValueError("Pressure and temperature must be positive")
        return p / (self.R * T)

    def velocity_from_mach(self, mach: float, speed_of_sound: float) -> float:
        """V = M × a."""
        if mach < 0:
            raise ValueError("Mach cannot be negative")
        if speed_of_sound <= 0:
            raise ValueError("Speed of sound must be positive")
        return mach * speed_of_sound

    def mass_flow_from_continuity(
        self,
        density: float,
        velocity: float,
        area: float
    ) -> float:
        """ṁ = ρ × V × A."""
        if density <= 0:
            raise ValueError("Density must be positive")
        if velocity < 0:
            raise ValueError("Velocity cannot be negative")
        if area <= 0:
            raise ValueError("Area must be positive")
        return density * velocity * area