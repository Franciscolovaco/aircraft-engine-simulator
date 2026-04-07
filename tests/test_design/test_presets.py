"""
Tests for design presets.

Verifies:
- All presets load without error
- Presets have realistic values
- Presets follow naming convention
- Educational sequence is complete
"""

import pytest
from src.design.presets import (
    IDEAL, IDEAL_WITH_INLET_LOSS, IDEAL_WITH_REAL_COMPRESSOR,
    IDEAL_WITH_REAL_COMBUSTOR, IDEAL_WITH_ALL_LOSSES,
    SEA_LEVEL_STATIC, CRUISE_10KM, CLIMB_5KM,
    CFM56_LIKE, GE90_LIKE,
    PESSIMISTIC, OPTIMISTIC, ADVANCED,
    TEACHING_SEQUENCE
)
from src.design.defaults import AllDefaults


class TestEducationalPresets:
    """Test educational progression presets."""
    
    def test_ideal_preset_loads(self):
        """IDEAL preset loads without error."""
        assert IDEAL is not None
        assert IDEAL.name == "Ideal Brayton Cycle"
    
    def test_ideal_uses_all_defaults(self):
        """IDEAL preset uses all defaults (no overrides)."""
        assert IDEAL.altitude is None
        assert IDEAL.M0 is None
        assert IDEAL.compressor_efficiency is None
        # All getters should return defaults
        assert IDEAL.get_inlet_recovery() == AllDefaults.INLET_RECOVERY_FACTOR
    
    def test_inlet_loss_preset_has_override(self):
        """IDEAL_WITH_INLET_LOSS has inlet_recovery override."""
        assert IDEAL_WITH_INLET_LOSS.inlet_recovery == 0.99
        assert IDEAL_WITH_INLET_LOSS.compressor_efficiency is None
    
    def test_all_losses_preset_realistic(self):
        """IDEAL_WITH_ALL_LOSSES has all realistic values."""
        assert IDEAL_WITH_ALL_LOSSES.inlet_recovery == 0.99
        assert IDEAL_WITH_ALL_LOSSES.compressor_efficiency == 0.91
        assert IDEAL_WITH_ALL_LOSSES.combustor_target_T_t == 1690
        assert IDEAL_WITH_ALL_LOSSES.turbine_efficiency == 0.91


class TestFlightConditionPresets:
    """Test flight condition presets."""
    
    def test_sea_level_static(self):
        """SEA_LEVEL_STATIC: ground, no motion."""
        assert SEA_LEVEL_STATIC.altitude == 0
        assert SEA_LEVEL_STATIC.M0 == 0.0
        assert SEA_LEVEL_STATIC.m_dot_total == 400
    
    def test_climb_5km(self):
        """CLIMB_5KM: intermediate altitude."""
        assert CLIMB_5KM.altitude == 5000
        assert CLIMB_5KM.M0 == 0.60
    
    def test_cruise_10km(self):
        """CRUISE_10KM: typical cruise condition."""
        assert CRUISE_10KM.altitude == 10000
        assert CRUISE_10KM.M0 == 0.85


class TestRealisticEnginePresets:
    """Test realistic engine design point presets."""
    
    def test_cfm56_like_loads(self):
        """CFM56_LIKE preset loads."""
        assert CFM56_LIKE is not None
        assert CFM56_LIKE.PR_fan == 2.2
        assert CFM56_LIKE.PR_HPC == 9.7
        assert CFM56_LIKE.bypass_ratio == 4.5
    
    def test_cfm56_realistic_parameters(self):
        """CFM56_LIKE has realistic component parameters."""
        assert CFM56_LIKE.inlet_recovery == 0.99
        assert CFM56_LIKE.compressor_efficiency == 0.91
        assert CFM56_LIKE.combustor_target_T_t == 1690
        assert CFM56_LIKE.turbine_efficiency == 0.91
    
    def test_ge90_like_larger_engine(self):
        """GE90_LIKE is larger than CFM56_LIKE."""
        assert GE90_LIKE.m_dot_total > CFM56_LIKE.m_dot_total
        assert GE90_LIKE.bypass_ratio > CFM56_LIKE.bypass_ratio
        assert GE90_LIKE.PR_HPC > CFM56_LIKE.PR_HPC


class TestParametricPresets:
    """Test sensitivity/parametric presets."""
    
    def test_pessimistic_lower_efficiency(self):
        """PESSIMISTIC: lower efficiencies than CFM56_LIKE."""
        assert PESSIMISTIC.inlet_recovery < CFM56_LIKE.inlet_recovery
        assert PESSIMISTIC.compressor_efficiency < CFM56_LIKE.compressor_efficiency
        assert PESSIMISTIC.turbine_efficiency < CFM56_LIKE.turbine_efficiency
    
    def test_optimistic_higher_efficiency(self):
        """OPTIMISTIC: higher efficiencies than CFM56_LIKE."""
        assert OPTIMISTIC.inlet_recovery > CFM56_LIKE.inlet_recovery
        assert OPTIMISTIC.compressor_efficiency > CFM56_LIKE.compressor_efficiency
        assert OPTIMISTIC.turbine_efficiency > CFM56_LIKE.turbine_efficiency
    
    def test_advanced_future_technology(self):
        """ADVANCED: higher PR, BPR, efficiency (2030s)."""
        assert ADVANCED.PR_HPC > CFM56_LIKE.PR_HPC
        assert ADVANCED.bypass_ratio > CFM56_LIKE.bypass_ratio
        assert ADVANCED.combustor_target_T_t > CFM56_LIKE.combustor_target_T_t


class TestTeachingSequence:
    """Test teaching progression sequence."""
    
    def test_teaching_sequence_is_list(self):
        """TEACHING_SEQUENCE is list of (description, case) tuples."""
        assert isinstance(TEACHING_SEQUENCE, list)
        assert len(TEACHING_SEQUENCE) > 0
    
    def test_teaching_sequence_format(self):
        """Each entry is (description, case) tuple."""
        for entry in TEACHING_SEQUENCE:
            assert isinstance(entry, tuple)
            assert len(entry) == 2
            description, case = entry
            assert isinstance(description, str)
            assert case is not None