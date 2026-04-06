"""
Thermodynamic Station Module

Represents engine cycle station with all properties.
European notation: p_t/T_t (total), p/T (static).
See: docs/physics/STATION_PROPERTIES.md
"""

from dataclasses import dataclass
from typing import Optional

from src.physics.thermodynamics import AirProperties


@dataclass
class ThermodynamicStation:
    """
    Single station in engine cycle (0, 1, 2, 2.5, 3, 4, 5, 6, 7, 8, 13, 19...).
    
    Use European notation: suffix 't' → total, no suffix → static.
    Example: p_t3 (total pressure at station 3), T_t5 (total temp at station 5).
    
    See: docs/physics/NOTATION_CONVENTIONS.md
    """
    
    station_id: str
    name: str
    
    # TOTAL (STAGNATION) PROPERTIES
    p_t: Optional[float] = None
    T_t: Optional[float] = None
    
    # STATIC PROPERTIES
    p: Optional[float] = None
    T: Optional[float] = None
    
    # FLOW PROPERTIES
    M: Optional[float] = None
    V: Optional[float] = None
    a: Optional[float] = None
    
    # MASS FLOW & DENSITY
    m_dot: Optional[float] = None
    rho: Optional[float] = None
    
    # DERIVED
    h_t: Optional[float] = None
    s: Optional[float] = None
    
    # COMPOSITION (combustor outlet onwards)
    fuel_air_ratio: Optional[float] = None
    
    def __str__(self) -> str:
        """Formatted output."""
        p_t_str = f"{self.p_t:.1f}" if self.p_t is not None else "N/A"
        T_t_str = f"{self.T_t:.2f}" if self.T_t is not None else "N/A"
        p_str = f"{self.p:.1f}" if self.p is not None else "N/A"
        T_str = f"{self.T:.2f}" if self.T is not None else "N/A"
        M_str = f"{self.M:.4f}" if self.M is not None else "N/A"
        V_str = f"{self.V:.2f}" if self.V is not None else "N/A"
        m_dot_str = f"{self.m_dot:.2f}" if self.m_dot is not None else "N/A"
        
        return (
            f"Station {self.station_id}: {self.name}\n"
            f"  p_t = {p_t_str} Pa, T_t = {T_t_str} K\n"
            f"  p = {p_str} Pa, T = {T_str} K\n"
            f"  M = {M_str}, V = {V_str} m/s\n"
            f"  ṁ = {m_dot_str} kg/s"
        )
    
    def is_complete(self) -> bool:
        """Check if critical properties (p_t, T_t, m_dot) are defined."""
        return all(x is not None for x in [self.p_t, self.T_t, self.m_dot])
    
    def calculate_speed_of_sound(
        self,
        gamma: float = AirProperties.GAMMA,
        R: float = AirProperties.R_SPECIFIC
    ) -> float:
        """a = √(γ × R × T)."""
        if self.T is None:
            raise ValueError(f"Static temperature not defined at station {self.station_id}")
        
        self.a = (gamma * R * self.T) ** 0.5
        return self.a
    
    def calculate_mach(self) -> float:
        """M = V / a."""
        if self.V is None or self.a is None:
            raise ValueError(f"Velocity or speed of sound not defined at station {self.station_id}")
        
        self.M = self.V / self.a
        return self.M
    
    def calculate_density(self, R: float = AirProperties.R_SPECIFIC) -> float:
        """ρ = p / (R × T)."""
        if self.p is None or self.T is None:
            raise ValueError(f"Static p or T not defined at station {self.station_id}")
        
        self.rho = self.p / (R * self.T)
        return self.rho