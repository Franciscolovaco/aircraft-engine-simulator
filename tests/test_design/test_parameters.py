"""
Tests for DesignCase parameters.

Verifies:
- Getters return explicit value if set
- Getters return default if not set
- Validation works
- All parameter types work
"""

import pytest
from src.design.parameters import DesignCase
from src.design.defaults import AllDefaults


class TestDesignCaseDefaults:
    """Test default fallback behavior."""
    
    def test_altitude_uses_default_when_none(self):
        """get_altitude() returns default if altitude not specified."""
        case = DesignCase()
        assert case.get_altitude() == AllDefaults.ALTITUDE
    
    def test_altitude_explicit_overrides(self):
        """get_altitude() returns explicit value if specified."""
        case = DesignCase(altitude=5000)
        assert case.get_altitude() == 5000
    
    def test_all_parameters_have_getters(self):
        """Each parameter has corresponding getter."""
        case = DesignCase()
        
        # Flight conditions
        assert case.get_altitude() is not None
        assert case.get_M0() is not None
        assert case.get_m_dot_total() is not None
        
        # Design point
        assert case.get_PR_fan() is not None
        assert case.get_PR_HPC() is not None
        assert case.get_bypass_ratio() is not None
        
        # Components
        assert case.get_inlet_recovery() is not None
        assert case.get_compressor_efficiency() is not None
        assert case.get_combustor_target_T_t() is not None
        assert case.get_turbine_efficiency() is not None
        assert case.get_nozzle_efficiency() is not None


class TestDesignCaseValidation:
    """Test input validation."""
    
    def test_altitude_must_be_in_range(self):
        """Altitude must be 0-11,000 m (ISA range)."""
        with pytest.raises(ValueError, match="outside ISA range"):
            DesignCase(altitude=-100)
        
        with pytest.raises(ValueError, match="outside ISA range"):
            DesignCase(altitude=15000)
    
    def test_mach_must_be_in_range(self):
        """Mach must be 0-2.0 (realistic range)."""
        with pytest.raises(ValueError, match="outside realistic range"):
            DesignCase(M0=-0.5)
        
        with pytest.raises(ValueError, match="outside realistic range"):
            DesignCase(M0=3.0)
    
    def test_mass_flow_must_be_positive(self):
        """Mass flow must be > 0."""
        with pytest.raises(ValueError, match="must be positive"):
            DesignCase(m_dot_total=-100)
        
        with pytest.raises(ValueError, match="must be positive"):
            DesignCase(m_dot_total=0)
    
    def test_pressure_ratios_must_be_gt_1(self):
        """PRs must be > 1."""
        with pytest.raises(ValueError, match="must be > 1"):
            DesignCase(PR_fan=0.5)
        
        with pytest.raises(ValueError, match="must be > 1"):
            DesignCase(PR_HPC=1.0)
    
    def test_bypass_ratio_must_be_positive(self):
        """Bypass ratio must be > 0."""
        with pytest.raises(ValueError, match="must be > 0"):
            DesignCase(bypass_ratio=-1.0)
        
        with pytest.raises(ValueError, match="must be > 0"):
            DesignCase(bypass_ratio=0)


class TestDesignCaseMixedOverride:
    """Test partial parameter override."""
    
    def test_override_flight_only(self):
        """Override flight conditions, use default design point."""
        case = DesignCase(
            altitude=5000,
            M0=0.7,
            m_dot_total=300
        )
        
        # Flight overridden
        assert case.get_altitude() == 5000
        assert case.get_M0() == 0.7
        assert case.get_m_dot_total() == 300
        
        # Design defaults
        assert case.get_PR_fan() == AllDefaults.PR_FAN
        assert case.get_PR_HPC() == AllDefaults.PR_HPC
    
    def test_override_components_only(self):
        """Override components, use default flight."""
        case = DesignCase(
            compressor_efficiency=0.90,
            turbine_efficiency=0.89
        )
        
        # Flight defaults
        assert case.get_altitude() == AllDefaults.ALTITUDE
        assert case.get_M0() == AllDefaults.MACH_NUMBER
        
        # Components overridden
        assert case.get_compressor_efficiency() == 0.90
        assert case.get_turbine_efficiency() == 0.89


class TestDesignCaseMetadata:
    """Test case metadata."""
    
    def test_case_has_name_and_description(self):
        """Case can have name and description."""
        case = DesignCase(
            name="My Design",
            description="Test case for validation"
        )
        
        assert case.name == "My Design"
        assert case.description == "Test case for validation"
    
    def test_case_default_name(self):
        """Case has default name."""
        case = DesignCase()
        assert case.name == "Design Case"