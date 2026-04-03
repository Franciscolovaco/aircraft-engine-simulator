"""
Atmosphere Module

Provides International Standard Atmosphere (ISA) calculations.
Allows conversion from altitude to pressure and temperature.

Reference: ICAO Standard Atmosphere (ISO 2533)
Valid from 0 to 11,000 m (troposphere layer).
"""

import math


class ISAAtmosphere:
    """
    International Standard Atmosphere (ISA) model.
    
    Provides standard atmosphere conditions at any altitude.
    Based on ICAO Standard Atmosphere specifications.
    
    Valid range: 0 to 11,000 m (troposphere)
    Beyond 11 km, stratosphere model would be needed (constant temperature).
    
    Attributes:
        T0_SEA_LEVEL (float): Sea level standard temperature (K)
        P0_SEA_LEVEL (float): Sea level standard pressure (Pa)
        LAPSE_RATE (float): Temperature decrease rate with altitude (K/m)
        R (float): Specific gas constant for dry air (J/(kg·K))
        G (float): Gravitational acceleration (m/s²)
    """
    
    # ISA Constants (from ICAO Standard Atmosphere)
    T0_SEA_LEVEL = 288.15  # K (15°C at sea level)
    P0_SEA_LEVEL = 101325  # Pa (standard sea level pressure)
    LAPSE_RATE = 0.0065    # K/m (temperature decreases 6.5 K per km)
    R = 287.05             # J/(kg·K) (specific gas constant for dry air)
    G = 9.81               # m/s² (gravitational acceleration)
    
    # Validity limits
    MIN_ALTITUDE = 0        # m
    MAX_ALTITUDE = 11000    # m (troposphere limit)
    
    @staticmethod
    def temperature_at_altitude(altitude: float) -> float:
        """
        Calculate static temperature at given altitude using ISA.
        
        In the troposphere (0-11 km), temperature decreases linearly with altitude.
        
        Formula: T(h) = T0 - L × h
        
        Where:
        - T0 = 288.15 K (sea level standard temperature)
        - L = 0.0065 K/m (lapse rate - positive number)
        - h = altitude (m)
        
        Examples:
        - At sea level (0 m): T = 288.15 K (15°C)
        - At 5 km: T = 288.15 - 0.0065×5000 = 255.65 K (-17.5°C)
        - At 10 km: T = 288.15 - 0.0065×10000 = 223.15 K (-50°C)
        
        Args:
            altitude (float): Altitude above sea level (m)
        
        Returns:
            float: Static temperature (K)
        
        Raises:
            ValueError: If altitude outside valid range (0 to 11,000 m)
        """
        if altitude < ISAAtmosphere.MIN_ALTITUDE:
            raise ValueError(
                f"Altitude cannot be negative: {altitude} m"
            )
        
        if altitude > ISAAtmosphere.MAX_ALTITUDE:
            raise ValueError(
                f"Altitude {altitude} m exceeds ISA troposphere limit "
                f"({ISAAtmosphere.MAX_ALTITUDE} m). "
                f"Stratosphere (h > 11 km) has different lapse rate."
            )
        
        # Linear temperature decrease with altitude
        T = ISAAtmosphere.T0_SEA_LEVEL - ISAAtmosphere.LAPSE_RATE * altitude
        
        return T
    
    @staticmethod
    def pressure_at_altitude(altitude: float) -> float:
        """
        Calculate static pressure at given altitude using ISA.
        
        In the troposphere, pressure decreases exponentially with altitude.
        
        Barometric Formula: P(h) = P0 × (T(h) / T0)^(g / (L × R))
        
        Where:
        - P0 = 101325 Pa (sea level pressure)
        - T0 = 288.15 K (sea level temperature)
        - T(h) = temperature at altitude h (calculated from linear lapse rate)
        - g = 9.81 m/s² (gravitational acceleration)
        - L = 0.0065 K/m (lapse rate - positive, temperature decreases with altitude)
        - R = 287.05 J/(kg·K) (specific gas constant for dry air)
        
        Note: This form uses all positive quantities, which is numerically stable.
        It's mathematically equivalent to the "textbook" form with a negative 
        exponent and inverted temperature ratio.
        
        Exponent: g / (L × R) = 9.81 / (0.0065 × 287.05) ≈ +5.256
        
        Example at 10 km:
        - T(10000) = 288.15 - 0.0065×10000 = 223.15 K
        - Exponent = +5.256
        - Ratio = T / T0 = 223.15 / 288.15 ≈ 0.7738
        - P = 101325 × (0.7738)^(5.256) ≈ 26,500 Pa ✓
        
        Args:
            altitude (float): Altitude above sea level (m)
        
        Returns:
            float: Static pressure (Pa)
        
        Raises:
            ValueError: If altitude outside valid range (0 to 11,000 m)
        """
        if altitude < ISAAtmosphere.MIN_ALTITUDE:
            raise ValueError(
                f"Altitude cannot be negative: {altitude} m"
            )
        
        if altitude > ISAAtmosphere.MAX_ALTITUDE:
            raise ValueError(
                f"Altitude {altitude} m exceeds ISA troposphere limit "
                f"({ISAAtmosphere.MAX_ALTITUDE} m)."
            )
        
        # Get temperature at this altitude
        T = ISAAtmosphere.temperature_at_altitude(altitude)

        # Calculate exponent: g / (L × R) - all positive quantities
        exponent = ISAAtmosphere.G / (
            ISAAtmosphere.LAPSE_RATE * ISAAtmosphere.R
        )

        # Apply barometric formula with positive exponent
        # Works because T < T0 at altitude, so (T/T0) < 1
        # Raising a number < 1 to positive power gives result < 1
        # Therefore P < P0 (pressure decreases with altitude) ✓
        P = ISAAtmosphere.P0_SEA_LEVEL * (
            T / ISAAtmosphere.T0_SEA_LEVEL
        ) ** exponent

        return P
    
    @staticmethod
    def conditions_at_altitude(altitude: float) -> tuple:
        """
        Get both temperature and pressure at a given altitude.
        
        Convenience method to avoid redundant calculations when both
        temperature and pressure are needed.
        
        Args:
            altitude (float): Altitude above sea level (m)
        
        Returns:
            tuple: (T_static, P_static) in Kelvin and Pascals
        
        Raises:
            ValueError: If altitude outside valid range (0 to 11,000 m)
            
        Example:
            >>> T, P = ISAAtmosphere.conditions_at_altitude(10000)
            >>> print(f"At 10 km: T={T:.2f} K, P={P:.1f} Pa")
            At 10 km: T=223.15 K, P=26496.0 Pa
        """
        T = ISAAtmosphere.temperature_at_altitude(altitude)
        P = ISAAtmosphere.pressure_at_altitude(altitude)
        return T, P
    
    @staticmethod
    def density_at_altitude(altitude: float) -> float:
        """
        Calculate air density at given altitude using ISA.
        
        Uses the ideal gas law: ρ = P / (R × T)
        
        Where:
        - ρ = air density (kg/m³)
        - P = static pressure at altitude (Pa)
        - R = 287.05 J/(kg·K) (specific gas constant for dry air)
        - T = static temperature at altitude (K)
        
        Examples:
        - At sea level (0 m): ρ ≈ 1.225 kg/m³
        - At 5 km: ρ ≈ 0.736 kg/m³
        - At 10 km: ρ ≈ 0.38 kg/m³
        
        Args:
            altitude (float): Altitude above sea level (m)
        
        Returns:
            float: Air density (kg/m³)
        
        Raises:
            ValueError: If altitude outside valid range (0 to 11,000 m)
        """
        if altitude < ISAAtmosphere.MIN_ALTITUDE or altitude > ISAAtmosphere.MAX_ALTITUDE:
            raise ValueError(
                f"Altitude {altitude} m outside valid range "
                f"({ISAAtmosphere.MIN_ALTITUDE} to {ISAAtmosphere.MAX_ALTITUDE} m)"
            )
        
        # Get temperature and pressure at this altitude
        T = ISAAtmosphere.temperature_at_altitude(altitude)
        P = ISAAtmosphere.pressure_at_altitude(altitude)
        
        # Calculate density from ideal gas law
        rho = P / (ISAAtmosphere.R * T)
        
        return rho
    
    @staticmethod
    def altitude_from_pressure(P: float) -> float:
        """
        Calculate altitude from measured static pressure (inverse function).
        
        Inverts the barometric formula to find altitude when pressure is known.
        
        Starting from: P = P0 × (T0 / T)^(g/(L×R))
        
        Where T = T0 - L×h, solving for h gives:
        h = (T0 / L) × [1 - (P / P0)^(L×R / g)]
        
        Where exponent for inversion: L×R / g ≈ 0.1903
        
        Args:
            P (float): Static pressure (Pa)
        
        Returns:
            float: Altitude (m)
        
        Raises:
            ValueError: If pressure is invalid or exceeds sea level
        """
        if P <= 0:
            raise ValueError(
                f"Pressure must be positive: {P} Pa"
            )
        
        if P > ISAAtmosphere.P0_SEA_LEVEL:
            raise ValueError(
                f"Pressure {P} Pa exceeds sea level pressure "
                f"({ISAAtmosphere.P0_SEA_LEVEL} Pa). "
                f"Altitude cannot be negative."
            )
        
        # Calculate exponent for inversion: L×R / g
        exp = ISAAtmosphere.LAPSE_RATE * ISAAtmosphere.R / ISAAtmosphere.G
        
        # Solve for altitude from inverted barometric formula
        h = (ISAAtmosphere.T0_SEA_LEVEL / ISAAtmosphere.LAPSE_RATE) * (
            1 - (P / ISAAtmosphere.P0_SEA_LEVEL) ** exp
        )
        
        return h
    
    @staticmethod
    def validate_altitude(altitude: float) -> bool:
        """
        Check if altitude is within valid ISA range.
        
        The ISA model is valid only in the troposphere (0 to 11 km).
        
        Args:
            altitude (float): Altitude to check (m)
        
        Returns:
            bool: True if altitude is valid, False otherwise
        """
        return ISAAtmosphere.MIN_ALTITUDE <= altitude <= ISAAtmosphere.MAX_ALTITUDE