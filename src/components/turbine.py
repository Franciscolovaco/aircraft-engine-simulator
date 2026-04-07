"""
Turbine Component

Models polytropic expansion. Pressure ratio set by solver (power balance).
See: docs/physics/TURBINE.md
"""

from src.physics.stations import ThermodynamicStation
from src.physics.thermodynamics import ThermodynamicsCalculator
from src.design.defaults import ComponentDefaults


class Turbine:
    """Generic turbine: polytropic expansion with efficiency."""
    
    def __init__(self, name: str, polytropic_efficiency: float = None):
        """
        Args:
            name: Component name ("HPT", "LPT")
            polytropic_efficiency: 0 < η_p ≤ 1.
                If None, uses ComponentDefaults.TURBINE_POLYTROPIC_EFFICIENCY
        """
        if polytropic_efficiency is None:
            polytropic_efficiency = ComponentDefaults.TURBINE_POLYTROPIC_EFFICIENCY
        
        if not (0 < polytropic_efficiency <= 1):
            raise ValueError(f"Polytropic efficiency {polytropic_efficiency} must be (0, 1]")
        
        self.name = name
        self.polytropic_efficiency = polytropic_efficiency
        self.calc = ThermodynamicsCalculator()
    
    def expand(self, station_inlet: ThermodynamicStation, pressure_ratio: float, station_id: str = "outlet") -> ThermodynamicStation:
        """
        Expand air using polytropic relation.
        
        Pressure ratio calculated by solver from power balance.
        
        Returns:
            outlet_station with lower pressure and temperature
        """
        if station_inlet.T_t is None or station_inlet.p_t is None:
            raise ValueError(f"{self.name} inlet must have p_t and T_t")
        if not (0 < pressure_ratio < 1):
            raise ValueError(f"{self.name} PR {pressure_ratio} must be (0, 1) for expansion")
        
        T_t_outlet = self.calc.polytropic_expansion(
            station_inlet.T_t,
            pressure_ratio,
            self.polytropic_efficiency
        )
        
        p_t_outlet = station_inlet.p_t * pressure_ratio
        m_dot_outlet = station_inlet.m_dot
        
        return ThermodynamicStation(
            station_id=station_id,
            name=f"{self.name} Exit",
            p_t=p_t_outlet,
            T_t=T_t_outlet,
            m_dot=m_dot_outlet
        )
    
    def __repr__(self) -> str:
        return f"{self.name}(η_p={self.polytropic_efficiency})"