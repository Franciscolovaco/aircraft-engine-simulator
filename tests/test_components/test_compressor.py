"""
Tests for Compressor component.

Verifies:
- Default polytropic efficiency used when None passed
- Explicit efficiency overrides default
- Polytropic formula correct
- Pressure ratio applied correctly
- Mass flow conserved
- Invalid inputs raise errors
"""

import pytest
import math
from src.components.compressor import Compressor
from src.design.defaults import ComponentDefaults
from tests.conftest import TOLERANCE_TEMPERATURE, TOLERANCE_PRESSURE


class TestCompressorDefaults:
    """Test default parameter behavior."""
    
    def test_compressor_uses_default_efficiency(self):
        """Compressor with no efficiency arg uses ComponentDefaults."""
        comp = Compressor("Fan", pressure_ratio=2.0)
        assert comp.polytropic_efficiency == ComponentDefaults.COMPRESSOR_POLYTROPIC_EFFICIENCY
        assert comp.polytropic_efficiency == 1.0  # Ideal
    
    def test_compressor_explicit_efficiency(self):
        """Compressor with explicit efficiency overrides default."""
        comp = Compressor("Fan", pressure_ratio=2.0, polytropic_efficiency=0.91)
        assert comp.polytropic_efficiency == 0.91


class TestCompressorPhysics:
    """Test physics correctness (polytropic formula)."""
    
    def test_ideal_compression_formula(self, station_fan_inlet):
        """Ideal compression (η_p=1.0) follows isentropic formula."""
        comp = Compressor("Fan", pressure_ratio=2.2, polytropic_efficiency=1.0)
        station_out = comp.compress(station_fan_inlet, station_id="2.5")
        
        # Isentropic: T_out = T_in × PR^((γ-1)/γ)
        gamma = 1.4
        T_ideal = station_fan_inlet.T_t * (2.2 ** ((gamma - 1) / gamma))
        
        assert abs(station_out.T_t - T_ideal) < TOLERANCE_TEMPERATURE
    
    def test_realistic_compression_higher_temp(self, station_fan_inlet):
        """Real compression (η_p<1.0) produces higher outlet temp than ideal."""
        comp_ideal = Compressor("Fan", pressure_ratio=2.2, polytropic_efficiency=1.0)
        comp_real = Compressor("Fan", pressure_ratio=2.2, polytropic_efficiency=0.91)
        
        station_ideal = comp_ideal.compress(station_fan_inlet, station_id="ideal")
        station_real = comp_real.compress(station_fan_inlet, station_id="real")
        
        # Real outlet temp > ideal outlet temp (more work needed)
        assert station_real.T_t > station_ideal.T_t
    
    def test_pressure_ratio_applied(self, station_fan_inlet):
        """Output pressure = inlet pressure × PR."""
        comp = Compressor("Fan", pressure_ratio=2.2)
        station_out = comp.compress(station_fan_inlet, station_id="out")
        
        expected_p = station_fan_inlet.p_t * 2.2
        assert abs(station_out.p_t - expected_p) < TOLERANCE_PRESSURE
    
    def test_mass_flow_conserved(self, station_fan_inlet):
        """Mass flow unchanged through compressor."""
        comp = Compressor("Fan", pressure_ratio=2.2)
        station_out = comp.compress(station_fan_inlet, station_id="out")
        
        assert station_out.m_dot == station_fan_inlet.m_dot


class TestCompressorValidation:
    """Test input validation."""
    
    def test_compressor_pressure_ratio_must_be_gt_1(self):
        """Pressure ratio must be > 1 for compression."""
        with pytest.raises(ValueError, match="must be > 1"):
            Compressor("Fan", pressure_ratio=1.0)
        
        with pytest.raises(ValueError, match="must be > 1"):
            Compressor("Fan", pressure_ratio=0.5)
    
    def test_compressor_efficiency_must_be_in_range(self):
        """Efficiency must be (0, 1]."""
        with pytest.raises(ValueError, match="must be"):
            Compressor("Fan", pressure_ratio=2.0, polytropic_efficiency=0.0)
        
        with pytest.raises(ValueError, match="must be"):
            Compressor("Fan", pressure_ratio=2.0, polytropic_efficiency=1.5)
    
    def test_compressor_station_must_have_pressure_temperature(self, station_fan_inlet):
        """Compressor inlet must have p_t and T_t."""
        comp = Compressor("Fan", pressure_ratio=2.0)
        
        station_fan_inlet.p_t = None
        with pytest.raises(ValueError, match="p_t and T_t"):
            comp.compress(station_fan_inlet)


class TestCompressorMultiStage:
    """Test chaining compressors (multi-stage behavior)."""
    
    def test_fan_then_hpc(self, station_fan_inlet):
        """Chain Fan → HPC to simulate multi-stage."""
        fan = Compressor("Fan", pressure_ratio=2.2, polytropic_efficiency=0.91)
        hpc = Compressor("HPC", pressure_ratio=9.7, polytropic_efficiency=0.90)
        
        # After fan
        station_25 = fan.compress(station_fan_inlet, station_id="2.5")
        
        # After HPC (core flow only)
        station_4 = hpc.compress(station_25, station_id="4")
        
        # Overall PR = 2.2 × 9.7 = 21.34
        overall_pr = station_4.p_t / station_fan_inlet.p_t
        assert abs(overall_pr - 21.34) < 1.0  # Within tolerance
    
    def test_multi_stage_temperature(self, station_fan_inlet):
        """Temperature rises through multi-stage compression."""
        temps = [station_fan_inlet.T_t]
        
        for i, pr in enumerate([2.2, 9.7]):
            comp = Compressor(f"Stage{i}", pressure_ratio=pr, polytropic_efficiency=0.91)
            station = comp.compress(station_fan_inlet if i == 0 else station, station_id=f"s{i}")
            temps.append(station.T_t)
            if i > 0:
                station_fan_inlet = station
        
        # Each stage increases temperature
        assert temps[1] > temps[0]
        assert temps[2] > temps[1]


class TestCompressorRealism:
    """Test realistic values."""
    
    def test_fan_realistic_parameters(self):
        """Fan typical values: PR=1.5-2.5, η_p=0.88-0.92."""
        fan = Compressor("Fan", pressure_ratio=2.2, polytropic_efficiency=0.91)
        assert 1.5 <= fan.pressure_ratio <= 2.5
        assert 0.88 <= fan.polytropic_efficiency <= 0.92
    
    def test_hpc_realistic_parameters(self):
        """HPC typical values: PR=8-40, η_p=0.87-0.92."""
        hpc = Compressor("HPC", pressure_ratio=9.7, polytropic_efficiency=0.90)
        assert 8 <= hpc.pressure_ratio <= 40
        assert 0.87 <= hpc.polytropic_efficiency <= 0.92
    
    def test_temperature_rise_quantitative(self, station_fan_inlet):
        """Verify typical temperature rise magnitude."""
        comp = Compressor("Fan", pressure_ratio=2.2, polytropic_efficiency=0.91)
        station_out = comp.compress(station_fan_inlet, station_id="out")
        
        delta_T = station_out.T_t - station_fan_inlet.T_t
        # Typical rise for PR=2.2: 70-90 K
        assert 70 < delta_T < 90


class TestCompressorIntegration:
    """Test integration with other components."""
    
    def test_compressor_output_ready_for_next_stage(self, station_fan_inlet):
        """Compressor output has all fields needed by next stage."""
        comp = Compressor("Fan", pressure_ratio=2.2)
        station_out = comp.compress(station_fan_inlet, station_id="2.5")
        
        assert station_out.p_t is not None
        assert station_out.T_t is not None
        assert station_out.m_dot is not None
        assert station_out.station_id == "2.5"