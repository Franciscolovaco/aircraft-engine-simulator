"""
Atmosphere Module - ISA Model

Provides International Standard Atmosphere (ICAO) calculations for 0-11 km.
See: docs/physics/ATMOSPHERE_ISA.md for derivations and examples.
"""

import math


class ISAAtmosphere:
    """
    ISA Model (troposphere, 0-11 km).
    
    Constants from ICAO Standard Atmosphere (ISO 2533).
    """
    
    T0_SEA_LEVEL = 288.15
    P0_SEA_LEVEL = 101325
    LAPSE_RATE = 0.0065
    R = 287.05
    G = 9.81
    
    MIN_ALTITUDE = 0
    MAX_ALTITUDE = 11000
    
    @staticmethod
    def temperature_at_altitude(altitude: float) -> float:
        """T(h) = T0 - L × h. See ATMOSPHERE_ISA.md."""
        if not (ISAAtmosphere.MIN_ALTITUDE <= altitude <= ISAAtmosphere.MAX_ALTITUDE):
            raise ValueError(f"Altitude {altitude} m outside valid range")
        
        return ISAAtmosphere.T0_SEA_LEVEL - ISAAtmosphere.LAPSE_RATE * altitude
    
    @staticmethod
    def pressure_at_altitude(altitude: float) -> float:
        """P(h) = P0 × (T(h)/T0)^(g/(L×R)). See ATMOSPHERE_ISA.md."""
        if not (ISAAtmosphere.MIN_ALTITUDE <= altitude <= ISAAtmosphere.MAX_ALTITUDE):
            raise ValueError(f"Altitude {altitude} m outside valid range")
        
        T = ISAAtmosphere.temperature_at_altitude(altitude)
        exponent = ISAAtmosphere.G / (ISAAtmosphere.LAPSE_RATE * ISAAtmosphere.R)
        
        return ISAAtmosphere.P0_SEA_LEVEL * (T / ISAAtmosphere.T0_SEA_LEVEL) ** exponent
    
    @staticmethod
    def conditions_at_altitude(altitude: float) -> tuple:
        """Returns (T_static, P_static) at altitude."""
        T = ISAAtmosphere.temperature_at_altitude(altitude)
        P = ISAAtmosphere.pressure_at_altitude(altitude)
        return T, P
    
    @staticmethod
    def density_at_altitude(altitude: float) -> float:
        """ρ = P / (R × T)."""
        if not (ISAAtmosphere.MIN_ALTITUDE <= altitude <= ISAAtmosphere.MAX_ALTITUDE):
            raise ValueError(f"Altitude {altitude} m outside valid range")
        
        T = ISAAtmosphere.temperature_at_altitude(altitude)
        P = ISAAtmosphere.pressure_at_altitude(altitude)
        
        return P / (ISAAtmosphere.R * T)
    
    @staticmethod
    def altitude_from_pressure(P: float) -> float:
        """Inverse: h = (T0/L) × [1 - (P/P0)^(L×R/g)]. See ATMOSPHERE_ISA.md."""
        if P <= 0 or P > ISAAtmosphere.P0_SEA_LEVEL:
            raise ValueError("Pressure must be (0, P0]")
        
        exp = ISAAtmosphere.LAPSE_RATE * ISAAtmosphere.R / ISAAtmosphere.G
        h = (ISAAtmosphere.T0_SEA_LEVEL / ISAAtmosphere.LAPSE_RATE) * (
            1 - (P / ISAAtmosphere.P0_SEA_LEVEL) ** exp
        )
        
        return h
    
    @staticmethod
    def validate_altitude(altitude: float) -> bool:
        """Check if altitude is valid (0-11 km)."""
        return ISAAtmosphere.MIN_ALTITUDE <= altitude <= ISAAtmosphere.MAX_ALTITUDE