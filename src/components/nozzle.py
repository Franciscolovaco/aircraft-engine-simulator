"""
Nozzle Component

Models isentropic expansion and exit velocity calculation.
See: docs/physics/NOZZLE.md
"""

from src.physics.stations import ThermodynamicStation
from src.physics.thermodynamics import ThermodynamicsCalculator
from src.design.defaults import ComponentDefaults


class Nozzle:
    """Nozzle: isentropic expansion to exit velocity."""
    
    def __init__(self, name: str, efficiency: float = None):
        """
        Args:
            name: Nozzle name ("Core Nozzle", "Bypass Nozzle")
            efficiency: Nozzle efficiency (0 < η ≤ 1).
                If None, uses ComponentDefaults.NOZZLE_EFFICIENCY
        """
        if efficiency is None:
            efficiency = ComponentDefaults.NOZZLE_EFFICIENCY
        
        if not (0 < efficiency <= 1):
            raise ValueError(f"Nozzle efficiency {efficiency} must be (0, 1]")
        
        self.name = name
        self.efficiency = efficiency
        self.calc = ThermodynamicsCalculator()
    
    def expand(self, station_inlet: ThermodynamicStation, exit_pressure: float, station_id: str = "exit") -> tuple:
        """
        Expand air in nozzle to exit pressure, calculate velocity and Mach.
        
        Returns:
            (outlet_station, exit_velocity, exit_mach)
        """
        if station_inlet.T_t is None or station_inlet.p_t is None:
            raise ValueError(f"{self.name} inlet must have p_t and T_t")
        if exit_pressure <= 0:
            raise ValueError(f"Exit pressure {exit_pressure} Pa must be positive")
        
        T_exit, V_exit, M_exit = self.calc.isentropic_nozzle_expansion(
            station_inlet.T_t,
            station_inlet.p_t,
            exit_pressure,
            self.efficiency
        )
        
        a_exit = self.calc.speed_of_sound(T_exit)
        m_dot_exit = station_inlet.m_dot
        
        station_outlet = ThermodynamicStation(
            station_id=station_id,
            name=f"{self.name} Exit",
            p=exit_pressure,
            T=T_exit,
            V=V_exit,
            a=a_exit,
            M=M_exit,
            m_dot=m_dot_exit
        )
        
        return station_outlet, V_exit, M_exit
    
    def __repr__(self) -> str:
        return f"{self.name}(η={self.efficiency})"