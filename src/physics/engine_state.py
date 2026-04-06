"""
Engine State Module

Central repository for all stations in engine cycle.
Grows as components calculate stations.
See: docs/physics/DESIGN_METHODOLOGY.md
"""

from typing import Dict, Optional
from src.physics.stations import ThermodynamicStation


class EngineState:
    """
    Stores all stations: 0 (freestream), 1 (inlet), 2 (fan inlet), 2.5 (fan exit),
    3 (HPC inlet), 4 (combustor inlet), 5 (combustor outlet), 6 (HPT inlet),
    7 (LPT exit), 8 (core nozzle), 13 (bypass nozzle), 19 (bypass exit), etc.
    
    TURBOFAN-SPECIFIC: Stations follow European turbofan numbering convention.
    """
    
    def __init__(self):
        self.stations: Dict[float, ThermodynamicStation] = {}
    
    def add_station(self, station_id: float, station: ThermodynamicStation) -> None:
        """Add station (prevents accidental overwrites)."""
        if station_id < 0:
            raise ValueError("Station ID cannot be negative")
        
        if not isinstance(station, ThermodynamicStation):
            raise TypeError(f"Expected ThermodynamicStation, got {type(station).__name__}")
        
        if station_id in self.stations:
            raise ValueError(f"Station {station_id} already exists")
        
        self.stations[station_id] = station
    
    def get_station(self, station_id: float) -> Optional[ThermodynamicStation]:
        """Retrieve station by ID."""
        return self.stations.get(station_id)
    
    def station_exists(self, station_id: float) -> bool:
        """Check if station calculated."""
        return station_id in self.stations
    
    def get_all_stations(self) -> Dict[float, ThermodynamicStation]:
        """Get all stations."""
        return self.stations.copy()
    
    def summary(self) -> str:
        """Formatted summary of all stations."""
        if not self.stations:
            return "No stations calculated yet."
        
        summary_str = "ENGINE CYCLE STATE\n" + "=" * 50 + "\n\n"
        
        for station_id, station in sorted(self.stations.items()):
            summary_str += f"Station {station_id}: {station.name}\n"
            summary_str += f"  p_t = {station.p_t:.1f} Pa ({station.p_t/1000:.2f} kPa)\n"
            summary_str += f"  T_t = {station.T_t:.2f} K\n"
            
            if station.p is not None:
                summary_str += f"  p = {station.p:.1f} Pa\n"
            if station.T is not None:
                summary_str += f"  T = {station.T:.2f} K\n"
            if station.M is not None:
                summary_str += f"  M = {station.M:.4f}\n"
            if station.V is not None:
                summary_str += f"  V = {station.V:.2f} m/s\n"
            if station.m_dot is not None:
                summary_str += f"  ṁ = {station.m_dot:.2f} kg/s\n"
            
            summary_str += "\n"
        
        return summary_str
    
    def __repr__(self) -> str:
        return f"EngineState(stations={len(self.stations)})"