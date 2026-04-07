"""
Combustor Component

Models fuel combustion with fuel-air ratio calculation.
See: docs/physics/COMBUSTOR.md
"""

from src.physics.stations import ThermodynamicStation
from src.physics.thermodynamics import ThermodynamicsCalculator
from src.design.defaults import ComponentDefaults


class Combustor:
    """Combustor with FAR calculation and pressure loss."""
    
    def __init__(self, target_T_t: float = None, efficiency: float = None, pressure_loss: float = None):
        """
        Args:
            target_T_t: Target outlet temperature (K). Design constraint.
                If None, uses ComponentDefaults.COMBUSTOR_TARGET_T_T
            efficiency: Combustor efficiency (0 < η ≤ 1).
                If None, uses ComponentDefaults.COMBUSTOR_EFFICIENCY
            pressure_loss: Fractional pressure drop (0 ≤ Δp/p < 1).
                If None, uses ComponentDefaults.COMBUSTOR_PRESSURE_LOSS
        """
        if target_T_t is None:
            target_T_t = ComponentDefaults.COMBUSTOR_TARGET_T_T
        if efficiency is None:
            efficiency = ComponentDefaults.COMBUSTOR_EFFICIENCY
        if pressure_loss is None:
            pressure_loss = ComponentDefaults.COMBUSTOR_PRESSURE_LOSS
        
        if target_T_t <= 0:
            raise ValueError(f"Target temperature {target_T_t} K must be positive")
        if not (0 < efficiency <= 1):
            raise ValueError(f"Combustor efficiency {efficiency} must be (0, 1]")
        if not (0 <= pressure_loss < 1):
            raise ValueError(f"Pressure loss {pressure_loss} must be [0, 1)")
        
        self.target_T_t = target_T_t
        self.efficiency = efficiency
        self.pressure_loss = pressure_loss
        self.calc = ThermodynamicsCalculator()
    
    def combust(self, station_inlet: ThermodynamicStation, station_id: str = "5") -> tuple:
        """
        Combust fuel, calculate FAR, return outlet station.
        
        Returns:
            (outlet_station, fuel_air_ratio)
        """
        if station_inlet.T_t is None or station_inlet.p_t is None:
            raise ValueError("Combustor inlet must have p_t and T_t")
        
        far = self.calc.fuel_air_ratio_from_temperature_rise(
            station_inlet.T_t,
            self.target_T_t,
            self.efficiency
        )
        
        p_t_outlet = station_inlet.p_t * (1 - self.pressure_loss)
        m_dot_outlet = station_inlet.m_dot
        
        station_outlet = ThermodynamicStation(
            station_id=station_id,
            name="Combustor Exit",
            p_t=p_t_outlet,
            T_t=self.target_T_t,
            m_dot=m_dot_outlet,
            fuel_air_ratio=far
        )
        
        return station_outlet, far
    
    def __repr__(self) -> str:
        return f"Combustor(T_target={self.target_T_t}K, η={self.efficiency}, loss={self.pressure_loss*100:.1f}%)"