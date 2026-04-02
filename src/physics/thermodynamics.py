"""
Thermodynamics Calculator Module

Provides thermodynamic calculations for turbofan engine analysis.
All calculations use SI units and standard air properties.
"""

import math
from typing import Tuple


class AirProperties:
    """Standard air properties and gas constants."""
    
    # Air properties at sea level (standard conditions)
    GAMMA = 1.4  # Specific heat ratio (Cp/Cv)
    R_SPECIFIC = 287.05  # Specific gas constant (J/kg·K)
    C_P = 1005.0  # Specific heat at constant pressure (J/kg·K)
    C_V = 718.0  # Specific heat at constant volume (J/kg·K)
    
    # Standard atmosphere
    T0_KELVIN = 288.15  # Sea level standard temperature (K)
    P0_PASCAL = 101325  # Sea level standard pressure (Pa)
    
    # Fuel properties
    FUEL_HEATING_VALUE = 43.0e6  # Jet fuel (kerosene) heating value (J/kg)


class ThermodynamicsCalculator:
    """
    Calculates thermodynamic properties for turbofan engine stations.
    
    This calculator handles:
    - Isentropic relations for compression and expansion
    - Polytropic processes for real components
    - Total/static property conversions
    - Nozzle calculations
    - Combustor energy balance
    """
    
    def __init__(self):
        """Initialize the calculator with air properties."""
        self.gamma = AirProperties.GAMMA
        self.R = AirProperties.R_SPECIFIC
        self.cp = AirProperties.C_P
        self.cv = AirProperties.C_V
    
    # ========== ISENTROPIC RELATIONS ==========
    
    def isentropic_temperature_ratio(self, pressure_ratio: float) -> float:
        """
        Calculate ideal temperature ratio across an isentropic process.
        
        Formula: T2/T1 = (P2/P1)^((γ-1)/γ)
        
        Args:
            pressure_ratio (float): P2/P1
            
        Returns:
            float: Temperature ratio T2/T1
            
        Raises:
            ValueError: If pressure_ratio is negative
        """
        if pressure_ratio < 0:
            raise ValueError("Pressure ratio cannot be negative")
        
        exponent = (self.gamma - 1) / self.gamma
        return pressure_ratio ** exponent
    
    def total_temperature_ratio_from_mach(self, mach: float) -> float:
        """
        Calculate total to static temperature ratio from Mach number.
        
        Formula: T_t / T = 1 + ((γ-1)/2) × M²
        
        Args:
            mach (float): Mach number
            
        Returns:
            float: Temperature ratio T_t / T
            
        Raises:
            ValueError: If Mach number is negative
        """
        if mach < 0:
            raise ValueError("Mach number cannot be negative")
        
        return 1 + ((self.gamma - 1) / 2) * (mach ** 2)
    
    def total_pressure_ratio_from_mach(self, mach: float) -> float:
        """
        Calculate total to static pressure ratio from Mach number.
        
        Formula: P_t / P = (1 + ((γ-1)/2) × M²)^(γ/(γ-1))
        
        Args:
            mach (float): Mach number
            
        Returns:
            float: Pressure ratio P_t / P
            
        Raises:
            ValueError: If Mach number is negative
        """
        if mach < 0:
            raise ValueError("Mach number cannot be negative")
        
        temp_ratio = self.total_temperature_ratio_from_mach(mach)
        exponent = self.gamma / (self.gamma - 1)
        return temp_ratio ** exponent
    
    # ========== COMPRESSION & EXPANSION ==========
    
    def polytropic_compression(
        self,
        T_inlet: float,
        pressure_ratio: float,
        polytropic_efficiency: float
    ) -> float:
        """
        Calculate outlet temperature for polytropic compression.
        
        Formula: T_outlet = T_inlet × (PR)^((γ-1)/(γ×η_poly))
        
        Args:
            T_inlet (float): Inlet total temperature (K)
            pressure_ratio (float): Pressure ratio (P_out / P_in)
            polytropic_efficiency (float): Polytropic efficiency (0-1)
            
        Returns:
            float: Outlet total temperature (K)
            
        Raises:
            ValueError: If inputs are invalid
        """
        if T_inlet <= 0:
            raise ValueError("Inlet temperature must be positive")
        if pressure_ratio <= 1:
            raise ValueError("Pressure ratio must be greater than 1 for compression")
        if not (0 < polytropic_efficiency <= 1):
            raise ValueError("Polytropic efficiency must be between 0 and 1")
        
        exponent = (self.gamma - 1) / (self.gamma * polytropic_efficiency)
        T_outlet = T_inlet * (pressure_ratio ** exponent)
        return T_outlet
    
    def polytropic_expansion(
        self,
        T_inlet: float,
        pressure_ratio: float,
        polytropic_efficiency: float
    ) -> float:
        """
        Calculate outlet temperature for polytropic expansion.
        
        Formula: T_outlet = T_inlet - (T_inlet - T_isentropic) / η_poly
        
        Args:
            T_inlet (float): Inlet total temperature (K)
            pressure_ratio (float): Expansion ratio (P_out / P_in) < 1
            polytropic_efficiency (float): Polytropic efficiency (0-1)
            
        Returns:
            float: Outlet total temperature (K)
            
        Raises:
            ValueError: If inputs are invalid
        """
        if T_inlet <= 0:
            raise ValueError("Inlet temperature must be positive")
        if not (0 < pressure_ratio < 1):
            raise ValueError("Pressure ratio must be between 0 and 1 for expansion")
        if not (0 < polytropic_efficiency <= 1):
            raise ValueError("Polytropic efficiency must be between 0 and 1")
        
        # Isentropic outlet temperature
        exponent = (self.gamma - 1) / self.gamma
        T_isentropic = T_inlet * (pressure_ratio ** exponent)
        
        # Actual outlet with efficiency loss
        T_outlet = T_inlet - (T_inlet - T_isentropic) / polytropic_efficiency
        return T_outlet
    
    # ========== NOZZLE CALCULATIONS ==========
    
    def nozzle_exit_velocity(
        self,
        T_total: float,
        T_static: float
    ) -> float:
        """
        Calculate exit velocity using energy equation for ideal nozzle.
        
        Formula: V = √(2 × c_p × (T_t - T))
        
        Args:
            T_total (float): Total temperature (K)
            T_static (float): Static temperature at exit (K)
            
        Returns:
            float: Exit velocity (m/s)
            
        Raises:
            ValueError: If temperatures are invalid
        """
        if T_total <= 0 or T_static <= 0:
            raise ValueError("Temperatures must be positive")
        if T_static > T_total:
            raise ValueError("Static temperature cannot exceed total temperature")
        
        velocity = math.sqrt(2 * self.cp * (T_total - T_static))
        return velocity
    
    def isentropic_nozzle_expansion(
        self,
        T_total: float,
        p_total: float,
        p_static: float,
        nozzle_efficiency: float = 1.0
    ) -> Tuple[float, float, float]:
        """
        Calculate nozzle exit properties with isentropic expansion.
        
        Args:
            T_total (float): Total temperature at nozzle inlet (K)
            p_total (float): Total pressure at nozzle inlet (Pa)
            p_static (float): Static pressure at exit (usually ambient) (Pa)
            nozzle_efficiency (float): Nozzle efficiency (0-1), default 1.0 (ideal)
            
        Returns:
            Tuple[T_exit, V_exit, M_exit]:
                - T_exit (float): Static temperature at exit (K)
                - V_exit (float): Exit velocity (m/s)
                - M_exit (float): Exit Mach number
                
        Raises:
            ValueError: If inputs are invalid
        """
        if not (0 < nozzle_efficiency <= 1):
            raise ValueError("Nozzle efficiency must be between 0 and 1")
        
        # Isentropic expansion
        pressure_ratio = p_static / p_total
        exponent = (self.gamma - 1) / self.gamma
        T_isentropic = T_total * (pressure_ratio ** exponent)
        
        # Apply nozzle efficiency
        T_exit = T_total - nozzle_efficiency * (T_total - T_isentropic)
        
        # Calculate exit velocity and Mach
        V_exit = self.nozzle_exit_velocity(T_total, T_exit)
        a_exit = math.sqrt(self.gamma * self.R * T_exit)
        M_exit = V_exit / a_exit
        
        return T_exit, V_exit, M_exit
    
    # ========== COMBUSTOR CALCULATIONS ==========
    
    def fuel_air_ratio_from_temperature_rise(
        self,
        T_inlet: float,
        T_outlet: float,
        combustor_efficiency: float = 0.98
    ) -> float:
        """
        Calculate fuel-to-air ratio needed to achieve desired temperature rise.
        
        Formula: f = (c_p × ΔT) / (η_comb × q_r - c_p × T_inlet)
        
        Args:
            T_inlet (float): Inlet temperature (K)
            T_outlet (float): Desired outlet (flame) temperature (K)
            combustor_efficiency (float): Combustor efficiency (0-1)
            
        Returns:
            float: Fuel-to-air ratio f (mass fuel / mass air)
            
        Raises:
            ValueError: If temperatures are invalid or efficiency out of range
        """
        if T_inlet <= 0 or T_outlet <= 0:
            raise ValueError("Temperatures must be positive")
        if T_outlet <= T_inlet:
            raise ValueError("Outlet temperature must exceed inlet temperature")
        if not (0 < combustor_efficiency <= 1):
            raise ValueError("Combustor efficiency must be between 0 and 1")
        
        delta_T = T_outlet - T_inlet
        numerator = self.cp * delta_T
        denominator = combustor_efficiency * AirProperties.FUEL_HEATING_VALUE - self.cp * T_inlet
        
        f = numerator / denominator
        
        if f < 0 or f > 0.1:  # Fuel-air ratio rarely exceeds 0.1
            raise ValueError(f"Calculated fuel-air ratio {f} is unrealistic")
        
        return f
    
    # ========== RAM EFFECT ==========
    
    def ram_effect_conditions(
        self,
        T_static: float,
        p_static: float,
        mach: float
    ) -> Tuple[float, float]:
        """
        Calculate total (stagnation) conditions from free stream.
        
        Formula:
        - T_t = T × (1 + ((γ-1)/2) × M²)
        - P_t = P × (T_t / T)^(γ/(γ-1))
        
        Args:
            T_static (float): Static temperature (K)
            p_static (float): Static pressure (Pa)
            mach (float): Mach number
            
        Returns:
            Tuple[T_total, P_total]:
                - T_total (float): Total temperature (K)
                - P_total (float): Total pressure (Pa)
                
        Raises:
            ValueError: If inputs are invalid
        """
        if T_static <= 0 or p_static <= 0 or mach < 0:
            raise ValueError("Temperatures, pressures must be positive; Mach >= 0")
        
        T_total = T_static * self.total_temperature_ratio_from_mach(mach)
        P_total = p_static * self.total_pressure_ratio_from_mach(mach)
        
        return T_total, P_total
    
    # ========== UTILITY FUNCTIONS ==========
    
    def speed_of_sound(self, T: float) -> float:
        """
        Calculate speed of sound at given temperature.
        
        Formula: a = √(γ × R × T)
        
        Args:
            T (float): Temperature (K)
            
        Returns:
            float: Speed of sound (m/s)
            
        Raises:
            ValueError: If temperature is invalid
        """
        if T <= 0:
            raise ValueError("Temperature must be positive")
        
        return math.sqrt(self.gamma * self.R * T)
    
    def density_from_pressure_temperature(self, p: float, T: float) -> float:
        """
        Calculate density from pressure and temperature.
        
        Formula: ρ = p / (R × T)
        
        Args:
            p (float): Pressure (Pa)
            T (float): Temperature (K)
            
        Returns:
            float: Density (kg/m³)
            
        Raises:
            ValueError: If pressure or temperature is invalid
        """
        if p <= 0 or T <= 0:
            raise ValueError("Pressure and temperature must be positive")
        
        return p / (self.R * T)