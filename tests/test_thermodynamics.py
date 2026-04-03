"""
Unit tests for thermodynamics calculations.

These tests verify that the ThermodynamicsCalculator produces
correct results for known inputs (based on standard thermodynamic relations).
"""

import pytest
import math
from src.physics.thermodynamics import ThermodynamicsCalculator, AirProperties


class TestAirProperties:
    """Test standard air properties."""
    
    def test_air_properties_constants(self):
        """Verify standard air properties are correctly defined."""
        assert AirProperties.GAMMA == 1.4
        assert AirProperties.R_SPECIFIC == 287.05
        assert AirProperties.C_P == 1005.0
        assert AirProperties.T0_KELVIN == 288.15
        assert AirProperties.P0_PASCAL == 101325


class TestIsentropicRelations:
    """Test isentropic thermodynamic relations."""
    
    def setup_method(self):
        """Initialize calculator for each test."""
        self.calc = ThermodynamicsCalculator()
    
    def test_isentropic_temperature_ratio_basic(self):
        """Test temperature ratio calculation."""
        # For PR = 2, should get specific ratio
        temp_ratio = self.calc.isentropic_temperature_ratio(2.0)
        expected = 2.0 ** (0.4 / 1.4)  # (γ-1)/γ = 0.4/1.4
        assert abs(temp_ratio - expected) < 0.001
    
    def test_isentropic_temperature_ratio_negative_pr(self):
        """Test that negative pressure ratio raises error."""
        with pytest.raises(ValueError):
            self.calc.isentropic_temperature_ratio(-1.0)
    
    def test_total_temperature_ratio_from_mach_zero(self):
        """At Mach 0, total and static temperature should be equal."""
        ratio = self.calc.total_temperature_ratio_from_mach(0.0)
        assert ratio == 1.0
    
    def test_total_temperature_ratio_from_mach_nonzero(self):
        """Test temperature ratio at M=0.85."""
        ratio = self.calc.total_temperature_ratio_from_mach(0.85)
        # T_t/T = 1 + 0.2 * 0.85^2 = 1 + 0.2 * 0.7225 = 1.1445
        expected = 1 + 0.2 * (0.85 ** 2)
        assert abs(ratio - expected) < 0.0001


class TestCompressionExpansion:
    """Test compression and expansion calculations."""
    
    def setup_method(self):
        """Initialize calculator for each test."""
        self.calc = ThermodynamicsCalculator()
    
    def test_polytropic_compression_basic(self):
        """Test basic fan compression calculation."""
        T_inlet = 288.15  # Sea level
        PR = 1.6  # Fan pressure ratio
        eta = 0.89  # Fan polytropic efficiency
        
        T_outlet = self.calc.polytropic_compression(T_inlet, PR, eta)
        
        # Should be higher than inlet
        assert T_outlet > T_inlet
        
        # With polytropic efficiency η=0.89:
        # exponent = (γ-1)/(γ×η) = 0.4/(1.4×0.89) = 0.3209
        # T_outlet = 288.15 × (1.6^0.3209) = 335.08 K
        assert 334 < T_outlet < 336
    
    def test_polytropic_compression_perfect_efficiency(self):
        """With 100% efficiency, should match isentropic."""
        T_inlet = 288.15
        PR = 2.0
        
        T_polytropic = self.calc.polytropic_compression(T_inlet, PR, 1.0)
        T_isentropic = T_inlet * (PR ** (0.4 / 1.4))
        
        assert abs(T_polytropic - T_isentropic) < 0.1


class TestNozzleCalculations:
    """Test nozzle exit property calculations."""
    
    def setup_method(self):
        """Initialize calculator for each test."""
        self.calc = ThermodynamicsCalculator()
    
    def test_nozzle_exit_velocity_basic(self):
        """Test exit velocity calculation."""
        T_total = 383.5  # K
        T_static = 286.0  # K
        
        V = self.calc.nozzle_exit_velocity(T_total, T_static)
        
        # Should be positive and reasonable
        assert V > 0
        # For these values, should be around 443 m/s
        assert 440 < V < 446
    
    def test_speed_of_sound_sea_level(self):
        """Test speed of sound at sea level standard conditions."""
        T = 288.15  # K (sea level)
        a = self.calc.speed_of_sound(T)
        
        # Standard sea level speed of sound ~340 m/s
        assert 330 < a < 350


class TestCombustorCalculations:
    """Test combustor calculations."""
    
    def setup_method(self):
        """Initialize calculator for each test."""
        self.calc = ThermodynamicsCalculator()
    
    def test_fuel_air_ratio_realistic_values(self):
        """Test fuel-air ratio calculation with realistic values."""
        T_inlet = 1031.6  # K (after HPC)
        T_outlet = 1600  # K (desired turbine inlet temp)
        eta_comb = 0.98
        
        f = self.calc.fuel_air_ratio_from_temperature_rise(T_inlet, T_outlet, eta_comb)
        
        # Fuel-air ratio should be small (typically 0.01-0.04)
        assert 0.01 < f < 0.02


if __name__ == "__main__":
    pytest.main([__file__, "-v"])