"""
Unit tests for ISA Atmosphere calculations.

Tests verify accuracy against known ISA standard values.
Reference: ICAO Standard Atmosphere tables.
"""

import pytest
import math
from src.physics.atmosphere import ISAAtmosphere


class TestISATemperature:
    """Test temperature calculations at various altitudes."""
    
    def test_temperature_at_sea_level(self):
        """At sea level, temperature should be 288.15 K (15°C)."""
        T = ISAAtmosphere.temperature_at_altitude(0)
        assert T == 288.15
    
    def test_temperature_at_5km(self):
        """At 5 km, ISA temperature should be ~255.65 K (-17.5°C)."""
        T = ISAAtmosphere.temperature_at_altitude(5000)
        expected = 288.15 - 0.0065 * 5000
        assert abs(T - expected) < 0.01
        assert 255 < T < 256
    
    def test_temperature_at_10km(self):
        """At 10 km, ISA temperature should be ~223.15 K (-50°C)."""
        T = ISAAtmosphere.temperature_at_altitude(10000)
        expected = 288.15 - 0.0065 * 10000
        assert abs(T - expected) < 0.01
        assert 223 < T < 224
    
    def test_temperature_decreases_with_altitude(self):
        """Temperature should decrease as altitude increases."""
        T_0km = ISAAtmosphere.temperature_at_altitude(0)
        T_5km = ISAAtmosphere.temperature_at_altitude(5000)
        T_10km = ISAAtmosphere.temperature_at_altitude(10000)
        
        assert T_0km > T_5km > T_10km
    
    def test_temperature_negative_altitude_raises_error(self):
        """Negative altitude should raise ValueError."""
        with pytest.raises(ValueError):
            ISAAtmosphere.temperature_at_altitude(-1000)
    
    def test_temperature_above_stratosphere_raises_error(self):
        """Altitude above 11 km should raise ValueError."""
        with pytest.raises(ValueError):
            ISAAtmosphere.temperature_at_altitude(12000)


class TestISAPressure:
    """Test pressure calculations at various altitudes."""
    
    def test_pressure_at_sea_level(self):
        """At sea level, pressure should be 101325 Pa."""
        P = ISAAtmosphere.pressure_at_altitude(0)
        assert abs(P - 101325) < 1
    
    def test_pressure_at_5km(self):
        """At 5 km, ISA pressure should be ~54050 Pa."""
        P = ISAAtmosphere.pressure_at_altitude(5000)
        # Typical value around 54,050 Pa (about 0.53 atm)
        assert 53000 < P < 55000
    
    def test_pressure_at_10km(self):
        """At 10 km, ISA pressure should be ~26500 Pa."""
        P = ISAAtmosphere.pressure_at_altitude(10000)
        # Typical cruise altitude: ~26,500 Pa (about 0.26 atm)
        assert 26000 < P < 27000
    
    def test_pressure_decreases_with_altitude(self):
        """Pressure should decrease exponentially with altitude."""
        P_0km = ISAAtmosphere.pressure_at_altitude(0)
        P_5km = ISAAtmosphere.pressure_at_altitude(5000)
        P_10km = ISAAtmosphere.pressure_at_altitude(10000)
        
        assert P_0km > P_5km > P_10km
    
    def test_pressure_decreases_exponentially_not_linearly(self):
        """Pressure reduction should be exponential (not linear)."""
        P_0km = ISAAtmosphere.pressure_at_altitude(0)
        P_5km = ISAAtmosphere.pressure_at_altitude(5000)
        P_10km = ISAAtmosphere.pressure_at_altitude(10000)
        
        # Ratio should decrease exponentially
        ratio_0_5 = P_5km / P_0km
        ratio_5_10 = P_10km / P_5km
        
        # Each 5 km step should have similar ratio
        assert abs(ratio_0_5 - ratio_5_10) < 0.05
    
    def test_pressure_negative_altitude_raises_error(self):
        """Negative altitude should raise ValueError."""
        with pytest.raises(ValueError):
            ISAAtmosphere.pressure_at_altitude(-1000)
    
    def test_pressure_above_stratosphere_raises_error(self):
        """Altitude above 11 km should raise ValueError."""
        with pytest.raises(ValueError):
            ISAAtmosphere.pressure_at_altitude(12000)


class TestISAConditions:
    """Test combined temperature and pressure calculations."""
    
    def test_conditions_at_sea_level(self):
        """At sea level, should get standard conditions."""
        T, P = ISAAtmosphere.conditions_at_altitude(0)
        assert T == 288.15
        assert abs(P - 101325) < 1
    
    def test_conditions_consistency(self):
        """Combined conditions should match individual calculations."""
        altitude = 8000
        T_combined, P_combined = ISAAtmosphere.conditions_at_altitude(altitude)
        T_individual = ISAAtmosphere.temperature_at_altitude(altitude)
        P_individual = ISAAtmosphere.pressure_at_altitude(altitude)
        
        assert T_combined == T_individual
        assert P_combined == P_individual
    
    def test_conditions_at_10km_realistic(self):
        """At typical cruise altitude (10 km), conditions should be realistic."""
        T, P = ISAAtmosphere.conditions_at_altitude(10000)
        
        # Expected: cold and low pressure
        assert 220 < T < 225  # Around -50°C
        assert 26000 < P < 27000  # About 0.26 atm


class TestISAInverse:
    """Test altitude calculation from pressure."""
    
    def test_altitude_from_pressure_sea_level(self):
        """From sea level pressure, should get 0 m altitude."""
        h = ISAAtmosphere.altitude_from_pressure(101325)
        assert abs(h) < 1
    
    def test_altitude_from_pressure_consistency(self):
        """Pressure→Altitude→Pressure should give back original."""
        original_altitude = 8000
        P = ISAAtmosphere.pressure_at_altitude(original_altitude)
        recovered_altitude = ISAAtmosphere.altitude_from_pressure(P)
        
        assert abs(recovered_altitude - original_altitude) < 1
    
    def test_altitude_from_pressure_negative_raises_error(self):
        """Negative pressure should raise ValueError."""
        with pytest.raises(ValueError):
            ISAAtmosphere.altitude_from_pressure(-100)
    
    def test_altitude_from_pressure_zero_raises_error(self):
        """Zero pressure should raise ValueError."""
        with pytest.raises(ValueError):
            ISAAtmosphere.altitude_from_pressure(0)
    
    def test_altitude_from_pressure_above_sea_level_raises_error(self):
        """Pressure above sea level should raise ValueError."""
        with pytest.raises(ValueError):
            ISAAtmosphere.altitude_from_pressure(110000)


class TestISADensity:
    """Test air density calculations."""
    
    def test_density_at_sea_level(self):
        """At sea level, density should be ~1.225 kg/m³."""
        rho = ISAAtmosphere.density_at_altitude(0)
        # Standard sea level density
        assert 1.2 < rho < 1.3
    
    def test_density_at_10km(self):
        """At 10 km, density should be ~0.414 kg/m³ (ISA standard)."""
        rho = ISAAtmosphere.density_at_altitude(10000)
        expected = 0.4135  # ISA standard value
        assert abs(rho - expected) < 0.001  # Within 0.1%
    
    def test_density_decreases_with_altitude(self):
        """Density should decrease with altitude."""
        rho_0 = ISAAtmosphere.density_at_altitude(0)
        rho_5 = ISAAtmosphere.density_at_altitude(5000)
        rho_10 = ISAAtmosphere.density_at_altitude(10000)
        
        assert rho_0 > rho_5 > rho_10
    
    def test_density_from_ideal_gas_law(self):
        """Verify density matches ρ = P / (R × T)."""
        altitude = 8000
        T = ISAAtmosphere.temperature_at_altitude(altitude)
        P = ISAAtmosphere.pressure_at_altitude(altitude)
        
        rho_calculated = ISAAtmosphere.density_at_altitude(altitude)
        rho_expected = P / (ISAAtmosphere.R * T)
        
        assert abs(rho_calculated - rho_expected) < 1e-10


class TestISAValidation:
    """Test altitude validation."""
    
    def test_validate_altitude_sea_level(self):
        """Sea level should be valid."""
        assert ISAAtmosphere.validate_altitude(0) is True
    
    def test_validate_altitude_cruise(self):
        """Cruise altitude (10 km) should be valid."""
        assert ISAAtmosphere.validate_altitude(10000) is True
    
    def test_validate_altitude_max(self):
        """Maximum altitude (11 km) should be valid."""
        assert ISAAtmosphere.validate_altitude(11000) is True
    
    def test_validate_altitude_negative(self):
        """Negative altitude should be invalid."""
        assert ISAAtmosphere.validate_altitude(-1000) is False
    
    def test_validate_altitude_above_max(self):
        """Altitude above 11 km should be invalid."""
        assert ISAAtmosphere.validate_altitude(12000) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

