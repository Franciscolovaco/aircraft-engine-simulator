"""
Thermodynamic Station Module

Represents a single station in the turbofan engine with all associated
thermodynamic properties: pressure, temperature, velocity, mass flow, etc.

European Notation (ISO/EASA):
- Total properties: p_t, T_t (superscript 't' or '0')
- Static properties: p, T
- Subscripts represent station numbers: p_t3, T_t5, etc.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ThermodynamicStation:
    """
    Represents a thermodynamic station in the turbofan engine.
    
    A station is a point along the engine flowpath where we track all
    thermodynamic and flow properties.
    
    Attributes:
        station_id (str): Unique identifier (e.g., "2.5", "13", "19")
        name (str): Descriptive name (e.g., "Fan Exit", "Combustor Inlet")
        
        # TOTAL (STAGNATION) PROPERTIES
        p_t (float): Total pressure (Pa) - [p⁰ᵢ or pₜᵢ]
        T_t (float): Total temperature (K) - [T⁰ᵢ or Tₜᵢ]
        
        # STATIC PROPERTIES
        p (float): Static pressure (Pa) - [pᵢ]
        T (float): Static temperature (K) - [Tᵢ]
        
        # FLOW PROPERTIES
        M (float): Mach number - [Mᵢ]
        V (float): Velocity (m/s) - [Vᵢ]
        a (float): Speed of sound (m/s)
        
        # MASS FLOW
        m_dot (float): Mass flow rate (kg/s) - [ṁᵢ]
        
        # DERIVED PROPERTIES
        rho (float): Density (kg/m³) - [ρᵢ]
        h_t (float): Total enthalpy (J/kg) - [hₜᵢ]
        s (float): Entropy (J/kg·K) - [sᵢ]
        
        # COMPOSITION (for combustor outlet onwards)
        fuel_air_ratio (float): Fuel to air mass ratio - [f] (optional)
    """
    
    # IDENTIFICATION
    station_id: str
    name: str
    
    # TOTAL PROPERTIES (always calculated)
    p_t: Optional[float] = None  # Total pressure (Pa)
    T_t: Optional[float] = None  # Total temperature (K)
    
    # STATIC PROPERTIES (calculated when velocity known)
    p: Optional[float] = None    # Static pressure (Pa)
    T: Optional[float] = None    # Static temperature (K)
    
    # FLOW PROPERTIES
    M: Optional[float] = None    # Mach number
    V: Optional[float] = None    # Velocity (m/s)
    a: Optional[float] = None    # Speed of sound (m/s)
    
    # MASS FLOW
    m_dot: Optional[float] = None  # Mass flow rate (kg/s)
    
    # DERIVED PROPERTIES
    rho: Optional[float] = None   # Density (kg/m³)
    h_t: Optional[float] = None   # Total enthalpy (J/kg)
    s: Optional[float] = None     # Entropy (J/kg·K)
    
    # COMPOSITION
    fuel_air_ratio: Optional[float] = None  # f (fuel/air ratio)
    
    def __str__(self) -> str:
        """Return formatted string representation of station."""
        return f"Station {self.station_id}: {self.name}\n" \
               f"  p_t = {self.p_t:.1f} Pa, T_t = {self.T_t:.2f} K\n" \
               f"  p = {self.p:.1f} Pa, T = {self.T:.2f} K\n" \
               f"  M = {self.M:.4f}, V = {self.V:.2f} m/s\n" \
               f"  ṁ = {self.m_dot:.2f} kg/s"
    
    def is_complete(self) -> bool:
        """Check if all critical properties are defined."""
        critical_props = [self.p_t, self.T_t, self.m_dot]
        return all(prop is not None for prop in critical_props)
    
    def calculate_speed_of_sound(self, gamma: float = 1.4, R: float = 287.0) -> float:
        """
        Calculate speed of sound at this station.
        
        Formula: a = √(γ × R × T)
        
        Args:
            gamma (float): Specific heat ratio (default 1.4 for air)
            R (float): Specific gas constant (default 287 J/kg·K for air)
            
        Returns:
            float: Speed of sound (m/s)
            
        Raises:
            ValueError: If static temperature is not defined
        """
        if self.T is None:
            raise ValueError(f"Static temperature not defined at station {self.station_id}")
        
        self.a = (gamma * R * self.T) ** 0.5
        return self.a
    
    def calculate_mach(self) -> float:
        """
        Calculate Mach number at this station.
        
        Formula: M = V / a
        
        Returns:
            float: Mach number (dimensionless)
            
        Raises:
            ValueError: If velocity or speed of sound not defined
        """
        if self.V is None or self.a is None:
            raise ValueError(f"Velocity or speed of sound not defined at station {self.station_id}")
        
        self.M = self.V / self.a
        return self.M
    
    def calculate_density(self, R: float = 287.0) -> float:
        """
        Calculate density at this station.
        
        Formula: ρ = p / (R × T)
        
        Args:
            R (float): Specific gas constant (default 287 J/kg·K for air)
            
        Returns:
            float: Density (kg/m³)
            
        Raises:
            ValueError: If static pressure or temperature not defined
        """
        if self.p is None or self.T is None:
            raise ValueError(f"Static pressure or temperature not defined at station {self.station_id}")
        
        self.rho = self.p / (R * self.T)
        return self.rho