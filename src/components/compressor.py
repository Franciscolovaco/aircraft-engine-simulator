"""
Compressor Component

Models polytropic compression for Fan, HPC, LPC.
See: docs/physics/COMPRESSOR.md
"""

from src.physics.stations import ThermodynamicStation
from src.physics.thermodynamics import ThermodynamicsCalculator
from src.design.defaults import ComponentDefaults


class Compressor:
    """Generic compressor: polytropic compression with efficiency."""
    
    def __init__(self, name: str, pressure_ratio: float, polytropic_efficiency: float = None):
        """
        Args:
            name: Component name ("Fan", "HPC", "LPC")
            pressure_ratio: P_out / P_in (must be > 1)
            polytropic_efficiency: 0 < η_p ≤ 1.
                If None, uses ComponentDefaults.COMPRESSOR_POLYTROPIC_EFFICIENCY
        """
        if polytropic_efficiency is None:
            polytropic_efficiency = ComponentDefaults.COMPRESSOR_POLYTROPIC_EFFICIENCY
        
        if pressure_ratio <= 1:
            raise ValueError(f"Pressure ratio {pressure_ratio} must be > 1")
        if not (0 < polytropic_efficiency <= 1):
            raise ValueError(f"Polytropic efficiency {polytropic_efficiency} must be (0, 1]")
        
        self.name = name
        self.pressure_ratio = pressure_ratio
        self.polytropic_efficiency = polytropic_efficiency
        self.calc = ThermodynamicsCalculator()
    
    def compress(self, station_inlet: ThermodynamicStation, station_id: str = "outlet") -> ThermodynamicStation:
        """
        Compress air using polytropic relation.
        
        Returns outlet station with higher pressure and temperature.
        """
        if station_inlet.T_t is None or station_inlet.p_t is None:
            raise ValueError(f"{self.name} inlet must have T_t and p_t")
        
        T_t_outlet = self.calc.polytropic_compression(
            station_inlet.T_t,
            self.pressure_ratio,
            self.polytropic_efficiency
        )
        
        p_t_outlet = station_inlet.p_t * self.pressure_ratio
        m_dot_outlet = station_inlet.m_dot
        
        return ThermodynamicStation(
            station_id=station_id,
            name=f"{self.name} Exit",
            p_t=p_t_outlet,
            T_t=T_t_outlet,
            m_dot=m_dot_outlet
        )
    
    def __repr__(self) -> str:
        return f"{self.name}(PR={self.pressure_ratio}, η_p={self.polytropic_efficiency})"