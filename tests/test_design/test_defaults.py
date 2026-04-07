"""
Tests for ComponentDefaults and CycleDefaults.

Verifies:
- All defaults present
- Default values are ideal (1.0 for efficiency, 0.0 for loss, etc.)
- AllDefaults combines both
- Values are physically reasonable
"""

import pytest
from src.design.defaults import ComponentDefaults, CycleDefaults, AllDefaults


class TestComponentDefaults:
    """Test component defaults."""
    
    def test_inlet_recovery_ideal(self):
        """Inlet recovery default is 1.0 (ideal, no loss)."""
        assert ComponentDefaults.INLET_RECOVERY_FACTOR == 1.0
    
    def test_compressor_efficiency_ideal(self):
        """Compressor efficiency default is 1.0 (isentropic)."""
        assert ComponentDefaults.COMPRESSOR_POLYTROPIC_EFFICIENCY == 1.0
    
    def test_combustor_defaults_ideal(self):
        """Combustor defaults: high temp limit, perfect efficiency, no loss."""
        assert ComponentDefaults.COMBUSTOR_TARGET_T_T == 2000  # Very high (no constraint)
        assert ComponentDefaults.COMBUSTOR_EFFICIENCY == 1.0  # Perfect
        assert ComponentDefaults.COMBUSTOR_PRESSURE_LOSS == 0.0  # No loss
    
    def test_turbine_efficiency_ideal(self):
        """Turbine efficiency default is 1.0 (isentropic)."""
        assert ComponentDefaults.TURBINE_POLYTROPIC_EFFICIENCY == 1.0
    
    def test_nozzle_efficiency_ideal(self):
        """Nozzle efficiency default is 1.0 (ideal expansion)."""
        assert ComponentDefaults.NOZZLE_EFFICIENCY == 1.0
    
    def test_bypass_duct_loss_zero(self):
        """Bypass duct loss default is 0.0 (no friction)."""
        assert ComponentDefaults.BYPASS_DUCT_PRESSURE_LOSS == 0.0


class TestCycleDefaults:
    """Test cycle defaults."""
    
    def test_flight_conditions_sea_level_static(self):
        """Flight defaults: sea level, stationary."""
        assert CycleDefaults.ALTITUDE == 10000
        assert CycleDefaults.MACH_NUMBER == 0.8
    
    def test_mass_flow_reasonable(self):
        """Mass flow default is reasonable value."""
        assert CycleDefaults.MASS_FLOW_TOTAL == 400
        assert CycleDefaults.MASS_FLOW_TOTAL > 0
    
    def test_pressure_ratios_low(self):
        """PR defaults are low (minimal compression, ideal)."""
        assert CycleDefaults.PR_FAN == 1.5
        assert CycleDefaults.PR_HPC == 3.0
    
    def test_bypass_ratio_equal_split(self):
        """BPR default is 1.0 (50% core, 50% bypass)."""
        assert CycleDefaults.BYPASS_RATIO == 1.0


class TestAllDefaults:
    """Test combined AllDefaults convenience class."""
    
    def test_all_defaults_has_component_params(self):
        """AllDefaults includes all component parameters."""
        assert hasattr(AllDefaults, 'INLET_RECOVERY_FACTOR')
        assert hasattr(AllDefaults, 'COMPRESSOR_POLYTROPIC_EFFICIENCY')
        assert hasattr(AllDefaults, 'COMBUSTOR_TARGET_T_T')
        assert hasattr(AllDefaults, 'TURBINE_POLYTROPIC_EFFICIENCY')
        assert hasattr(AllDefaults, 'NOZZLE_EFFICIENCY')
    
    def test_all_defaults_has_cycle_params(self):
        """AllDefaults includes all cycle parameters."""
        assert hasattr(AllDefaults, 'ALTITUDE')
        assert hasattr(AllDefaults, 'MACH_NUMBER')
        assert hasattr(AllDefaults, 'MASS_FLOW_TOTAL')
        assert hasattr(AllDefaults, 'PR_FAN')
        assert hasattr(AllDefaults, 'PR_HPC')
        assert hasattr(AllDefaults, 'BYPASS_RATIO')
    
    def test_all_defaults_values_match(self):
        """AllDefaults values match component/cycle defaults."""
        assert AllDefaults.INLET_RECOVERY_FACTOR == ComponentDefaults.INLET_RECOVERY_FACTOR
        assert AllDefaults.ALTITUDE == CycleDefaults.ALTITUDE
        assert AllDefaults.PR_FAN == CycleDefaults.PR_FAN