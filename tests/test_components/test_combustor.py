"""
Tests for Combustor component.

Verifies:
- Default parameters used when None passed
- Explicit parameters override defaults
- FAR calculation correct
- Pressure loss applied
- Temperature set to target
- Invalid inputs raise errors
"""

import pytest
from src.components.combustor import Combustor
from src.design.defaults import ComponentDefaults, AllDefaults
from tests.conftest import TOLERANCE_TEMPERATURE, TOLERANCE_PRESSURE, TOLERANCE_PERCENTAGE


class TestCombustorDefaults:
    """Test default parameter behavior."""
    
    def test_combustor_uses_all_defaults(self):
        """Combustor with no args uses all ComponentDefaults."""
        comb = Combustor()
        assert comb.target_T_t == ComponentDefaults.COMBUSTOR_TARGET_T_T
        assert comb.efficiency == ComponentDefaults.COMBUSTOR_EFFICIENCY
        assert comb.pressure_loss == ComponentDefaults.COMBUSTOR_PRESSURE_LOSS
    
    def test_combustor_partial_override(self):
        """Combustor can override specific parameters."""
        comb = Combustor(target_T_t=1690)
        assert comb.target_T_t == 1690
        assert comb.efficiency == ComponentDefaults.COMBUSTOR_EFFICIENCY
        assert comb.pressure_loss == ComponentDefaults.COMBUSTOR_PRESSURE_LOSS


class TestCombustorPhysics:
    """Test combustor physics."""
    
    def test_outlet_temperature_matches_target(self, station_combustor_inlet):
        """Outlet temperature set to target (design constraint)."""
        comb = Combustor(target_T_t=1690)
        station_5, far = comb.combust(station_combustor_inlet, station_id="5")
        
        assert station_5.T_t == 1690
    
    def test_pressure_loss_applied(self, station_combustor_inlet):
        """Pressure reduced by loss percentage."""
        comb = Combustor(target_T_t=1690, pressure_loss=0.01)
        station_5, far = comb.combust(station_combustor_inlet, station_id="5")
        
        # 1% loss: P_out = 0.99 × P_in
        expected_p = station_combustor_inlet.p_t * 0.99
        assert abs(station_5.p_t - expected_p) < TOLERANCE_PRESSURE
    
    def test_mass_flow_conserved(self, station_combustor_inlet):
        """Mass flow unchanged (neglect fuel mass ~2%)."""
        comb = Combustor()
        station_5, far = comb.combust(station_combustor_inlet, station_id="5")
        
        assert station_5.m_dot == station_combustor_inlet.m_dot
    
    def test_fuel_air_ratio_calculated(self, station_combustor_inlet):
        """FAR returned from combust()."""
        comb = Combustor(target_T_t=1690)
        station_5, far = comb.combust(station_combustor_inlet, station_id="5")
        
        # FAR should be positive and reasonable (0.01-0.05 for commercial)
        assert far > 0
        assert far < 0.1
    
    def test_combustor_stores_far_in_station(self, station_combustor_inlet):
        """Outlet station stores FAR in fuel_air_ratio field."""
        comb = Combustor(target_T_t=1690)
        station_5, far = comb.combust(station_combustor_inlet, station_id="5")
        
        assert station_5.fuel_air_ratio == far
        assert station_5.fuel_air_ratio is not None


class TestCombustorValidation:
    """Test input validation."""
    
    def test_combustor_target_T_must_be_positive(self):
        """Target temperature must be > 0."""
        with pytest.raises(ValueError, match="must be positive"):
            Combustor(target_T_t=-100)
        
        with pytest.raises(ValueError, match="must be positive"):
            Combustor(target_T_t=0)
    
    def test_combustor_efficiency_in_range(self):
        """Efficiency must be (0, 1]."""
        with pytest.raises(ValueError, match="must be"):
            Combustor(efficiency=0.0)
        
        with pytest.raises(ValueError, match="must be"):
            Combustor(efficiency=1.5)
    
    def test_combustor_pressure_loss_in_range(self):
        """Pressure loss must be [0, 1) — allow 0 (ideal) and realistic values."""
        # Should accept 0.0 (ideal) and typical values
        comb_ideal = Combustor(pressure_loss=0.0)
        assert comb_ideal.pressure_loss == 0.0
        
        comb_realistic = Combustor(pressure_loss=0.01)
        assert comb_realistic.pressure_loss == 0.01
        
        # Should reject ≥ 1.0 (100% loss is invalid)
        with pytest.raises(ValueError, match="must be"):
            Combustor(pressure_loss=1.0)
        
        with pytest.raises(ValueError, match="must be"):
            Combustor(pressure_loss=1.5)
    
    def test_combustor_inlet_must_have_pressure_temperature(self, station_combustor_inlet):
        """Inlet must have p_t and T_t."""
        comb = Combustor()
        station_combustor_inlet.p_t = None
        
        with pytest.raises(ValueError, match="p_t and T_t"):
            comb.combust(station_combustor_inlet)


class TestCombustorRealism:
    """Test realistic combustor values."""
    
    def test_typical_combustor_parameters(self):
        """Typical commercial combustor: T_t~1690K, η~0.98, loss~1%."""
        comb = Combustor(target_T_t=1690, efficiency=0.98, pressure_loss=0.01)
        assert comb.target_T_t == 1690
        assert comb.efficiency == 0.98
        assert comb.pressure_loss == 0.01
    
    def test_material_limit_range(self):
        """Turbine blade material limits: 1650-1800 K commercial."""
        for T_target in [1650, 1690, 1750]:
            comb = Combustor(target_T_t=T_target)
            assert comb.target_T_t == T_target
    
    def test_ideal_combustor_high_temperature(self):
        """Ideal combustor: very high target (no constraint)."""
        comb = Combustor(target_T_t=10000)  # Ideal default
        assert comb.target_T_t == 10000
    
    def test_far_quantitative(self, station_combustor_inlet):
        """FAR at cruise: typically 0.02-0.03 (2-3%)."""
        comb = Combustor(target_T_t=1690)
        station_5, far = comb.combust(station_combustor_inlet, station_id="5")
        
        # At cruise: FAR should be ~2-3%
        assert 0.02 < far < 0.05


class TestCombustorIntegration:
    """Test integration with cycle."""
    
    def test_combustor_output_ready_for_turbine(self, station_combustor_inlet):
        """Combustor output has all fields for turbine."""
        comb = Combustor(target_T_t=1690)
        station_5, far = comb.combust(station_combustor_inlet, station_id="5")
        
        assert station_5.p_t is not None
        assert station_5.T_t is not None
        assert station_5.m_dot is not None
        assert station_5.station_id == "5"
        assert station_5.fuel_air_ratio is not None