"""
Tests for Inlet component.

Verifies:
- Default recovery factor used when None passed
- Explicit recovery factor overrides default
- Pressure loss calculated correctly
- Temperature unchanged
- Mass flow conserved
- Invalid inputs raise errors
"""

import pytest
from src.components.inlet import Inlet
from src.design.defaults import ComponentDefaults, AllDefaults
from tests.conftest import TOLERANCE_PRESSURE, TOLERANCE_PERCENTAGE


class TestInletDefaults:
    """Test default parameter behavior."""
    
    def test_inlet_uses_default_recovery(self):
        """Inlet with no args uses ComponentDefaults.INLET_RECOVERY_FACTOR."""
        inlet = Inlet()
        assert inlet.recovery_factor == ComponentDefaults.INLET_RECOVERY_FACTOR
        assert inlet.recovery_factor == 1.0  # Ideal
    
    def test_inlet_explicit_recovery(self):
        """Inlet with explicit recovery_factor overrides default."""
        inlet = Inlet(recovery_factor=0.99)
        assert inlet.recovery_factor == 0.99


class TestInletPhysics:
    """Test physics correctness."""
    
    def test_ideal_inlet_no_pressure_loss(self, station_freestream):
        """Ideal inlet (π_d=1.0) produces no pressure loss."""
        inlet = Inlet(recovery_factor=1.0)
        station_1 = inlet.process(station_freestream, station_id="1")
        
        # Pressure unchanged
        assert abs(station_1.p_t - station_freestream.p_t) < TOLERANCE_PRESSURE
        assert station_1.p_t == station_freestream.p_t
    
    def test_realistic_inlet_pressure_loss(self, station_freestream):
        """Realistic inlet (π_d=0.99) produces 1% pressure loss."""
        inlet = Inlet(recovery_factor=0.99)
        station_1 = inlet.process(station_freestream, station_id="1")
        
        # Pressure reduced by 1%
        expected_p_t = 0.99 * station_freestream.p_t
        assert abs(station_1.p_t - expected_p_t) < TOLERANCE_PRESSURE
    
    def test_inlet_temperature_unchanged(self, station_freestream):
        """Inlet is adiabatic: temperature unchanged."""
        inlet = Inlet(recovery_factor=0.99)
        station_1 = inlet.process(station_freestream, station_id="1")
        
        # Temperature unchanged (adiabatic)
        assert station_1.T_t == station_freestream.T_t
    
    def test_inlet_mass_flow_conserved(self, station_freestream):
        """Mass flow conserved through inlet."""
        inlet = Inlet(recovery_factor=0.99)
        station_1 = inlet.process(station_freestream, station_id="1")
        
        # Mass flow unchanged (continuity)
        assert station_1.m_dot == station_freestream.m_dot
    
    def test_inlet_custom_station_id(self, station_freestream):
        """Outlet station has correct station_id."""
        inlet = Inlet()
        station_1 = inlet.process(station_freestream, station_id="custom_1")
        
        assert station_1.station_id == "custom_1"


class TestInletValidation:
    """Test input validation."""
    
    def test_inlet_recovery_must_be_positive(self):
        """Recovery factor must be > 0."""
        with pytest.raises(ValueError, match="must be"):
            Inlet(recovery_factor=0.0)
    
    def test_inlet_recovery_must_be_le_1(self):
        """Recovery factor must be ≤ 1."""
        with pytest.raises(ValueError, match="must be"):
            Inlet(recovery_factor=1.5)
    
    def test_inlet_station_must_have_pressure_temperature(self, station_freestream):
        """Inlet station must have p_t and T_t."""
        inlet = Inlet()
        
        # Remove pressure
        station_freestream.p_t = None
        with pytest.raises(ValueError, match="p_t and T_t"):
            inlet.process(station_freestream)


class TestInletIntegration:
    """Test integration with other components."""
    
    def test_inlet_output_ready_for_compressor(self, station_freestream):
        """Inlet output has all fields needed by compressor."""
        inlet = Inlet(recovery_factor=0.99)
        station_1 = inlet.process(station_freestream, station_id="1")
        
        # Has required fields for compressor
        assert station_1.p_t is not None
        assert station_1.T_t is not None
        assert station_1.m_dot is not None
        assert station_1.station_id == "1"
        assert station_1.name == "Inlet Exit"


class TestInletRealism:
    """Test realistic values."""
    
    def test_typical_inlet_loss_range(self):
        """Typical inlet losses are 0.5-2%."""
        # Modern inlet: 0.99 (1% loss)
        inlet_good = Inlet(recovery_factor=0.99)
        assert inlet_good.recovery_factor == 0.99
        
        # Excellent inlet: 0.995 (0.5% loss)
        inlet_excellent = Inlet(recovery_factor=0.995)
        assert inlet_excellent.recovery_factor == 0.995
        
        # Rough inlet: 0.98 (2% loss)
        inlet_rough = Inlet(recovery_factor=0.98)
        assert inlet_rough.recovery_factor == 0.98
    
    def test_pressure_loss_quantitative(self, station_freestream):
        """Quantify pressure loss at cruise conditions."""
        inlet = Inlet(recovery_factor=0.99)
        station_1 = inlet.process(station_freestream, station_id="1")
        
        loss_percent = (1 - station_1.p_t / station_freestream.p_t) * 100
        assert abs(loss_percent - 1.0) < 0.1  # Should be ~1%