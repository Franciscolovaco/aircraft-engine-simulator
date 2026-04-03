"""
Engine State Module

Maintains the complete thermodynamic state of the engine cycle.
Stores all stations calculated so far, allowing access at any point
in the calculation pipeline.

This allows components (Fan, Compressor, Turbine, etc.) to read
previously calculated stations and add new ones.
"""

from typing import Dict, Optional
from src.physics.stations import ThermodynamicStation


class EngineState:
    """
    Stores all thermodynamic stations in the engine cycle.
    
    Acts as a central repository that grows as each component
    (fan, compressor, combustor, turbine, nozzle) performs its calculation.
    
    Station numbering follows European convention:
    - 0: Freestream
    - 1: Inlet
    - 2: Fan inlet
    - 2.5: Fan exit (bifurcation point)
    - 3: HPC inlet (core flow)
    - 4: HPC exit / Combustor inlet
    - 5: Combustor exit / HPT inlet
    - 6: HPT exit / LPT inlet
    - 7: LPT exit
    - 8-9: Core nozzle exit
    - 13: Bypass duct exit
    - 19: Bypass nozzle exit
    
    Attributes:
        stations (Dict[float, ThermodynamicStation]): All calculated stations
    """
    
    def __init__(self):
        """Initialize empty engine state."""
        self.stations: Dict[float, ThermodynamicStation] = {}
    
    def add_station(self, station_id: float, station: ThermodynamicStation) -> None:
        """
        Add or update a station in the cycle.
        
        Args:
            station_id (float): Station identifier (e.g., 0, 1, 2, 2.5, 3, etc.)
            station (ThermodynamicStation): The station to store
            
        Raises:
            ValueError: If station_id is negative
            TypeError: If station is not a ThermodynamicStation
        """
        if station_id < 0:
            raise ValueError(f"Station ID cannot be negative: {station_id}")
        
        if not isinstance(station, ThermodynamicStation):
            raise TypeError(
                f"Expected ThermodynamicStation, got {type(station).__name__}"
            )
        
        if station_id in self.stations:
            raise ValueError(
                f"Station {station_id} already calculated. "
                f"Cannot recalculate (prevent accidental overwrites)."
            )
        
        self.stations[station_id] = station
    
    def get_station(self, station_id: float) -> Optional[ThermodynamicStation]:
        """
        Retrieve a station by ID.
        
        Args:
            station_id (float): Station identifier
            
        Returns:
            ThermodynamicStation: The requested station, or None if not found
        """
        return self.stations.get(station_id)
    
    def station_exists(self, station_id: float) -> bool:
        """
        Check if a station has been calculated.
        
        Args:
            station_id (float): Station identifier
            
        Returns:
            bool: True if station exists, False otherwise
        """
        return station_id in self.stations
    
    def get_all_stations(self) -> Dict[float, ThermodynamicStation]:
        """
        Get all calculated stations.
        
        Returns:
            Dict: All stations keyed by station ID
        """
        return self.stations.copy()
    
    def summary(self) -> str:
        """
        Print summary of all calculated stations so far.
        
        Returns:
            str: Formatted summary of all stations
        """
        if not self.stations:
            return "No stations calculated yet."
        
        summary_str = "ENGINE CYCLE STATE\n"
        summary_str += "=" * 50 + "\n\n"
        
        # Sort stations by ID for readable output
        sorted_stations = sorted(self.stations.items(), key=lambda x: x[0])
        
        for station_id, station in sorted_stations:
            summary_str += f"Station {station_id}: {station.name}\n"
            summary_str += f"  p_t = {station.p_t:.1f} Pa ({station.p_t/1000:.2f} kPa)\n"
            summary_str += f"  T_t = {station.T_t:.2f} K\n"
            
            if station.p is not None:
                summary_str += f"  p = {station.p:.1f} Pa ({station.p/1000:.2f} kPa)\n"
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
        """Return string representation."""
        return f"EngineState(stations={len(self.stations)})"