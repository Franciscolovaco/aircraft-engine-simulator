"""
Inlet Component

Applies pressure recovery factor to model inlet duct losses.
See: docs/physics/INLET.md
"""

from src.physics.stations import ThermodynamicStation
from src.design.defaults import ComponentDefaults


class Inlet:
    """Inlet duct with pressure recovery factor."""
    
    def __init__(self, recovery_factor: float = None):
        """
        Args:
            recovery_factor: Pressure recovery (0 < π_d ≤ 1).
                If None, uses ComponentDefaults.INLET_RECOVERY_FACTOR
        """
        if recovery_factor is None:
            recovery_factor = ComponentDefaults.INLET_RECOVERY_FACTOR
        
        if not (0 < recovery_factor <= 1):
            raise ValueError(f"Recovery factor {recovery_factor} must be (0, 1]")
        
        self.recovery_factor = recovery_factor
    
    def process(self, station_inlet: ThermodynamicStation, station_id: str = "1") -> ThermodynamicStation:
        """
        Process inlet: reduce total pressure, keep temperature.
        
        Returns new Station 1 from Station 0.
        """
        if station_inlet.p_t is None or station_inlet.T_t is None:
            raise ValueError("Inlet station must have p_t and T_t")
        
        p_t_outlet = self.recovery_factor * station_inlet.p_t
        T_t_outlet = station_inlet.T_t
        m_dot_outlet = station_inlet.m_dot
        
        return ThermodynamicStation(
            station_id=station_id,
            name="Inlet Exit",
            p_t=p_t_outlet,
            T_t=T_t_outlet,
            m_dot=m_dot_outlet
        )