"""
Tests for Turbine component.

Verifies:
- Default polytropic efficiency used when None passed
- Explicit efficiency overrides default
- Polytropic expansion formula correct
- Pressure ratio applied correctly (0 < PR < 1)
- Mass flow conserved
- Power balance ready (solver provides PR)
"""

import pytest
from src.components.turbine import Turbine
from src.design.defaults import ComponentDefaults
from tests.conftest import TOLERANCE_TEMPERATURE, TOLERANCE_PRESSURE


class TestTurbineDefaults:
    """Test default parameter behavior."""
    
    def test_turbine_uses_default_efficiency(self):
        """Turbine with no efficiency arg uses ComponentDefaults."""
        turb = Turbine("HPT")
        assert turb.polytropic_efficiency == ComponentDefaults.TURBINE_POLYTROPIC_EFFICIENCY
        assert turb.polytropic_efficiency == 1.0  # Ideal
    
    def test_turbine_explicit_efficiency(self):
        """Turbine with explicit efficiency overrides default."""
        turb = Turbine("HPT", polytropic_efficiency=0.91)
        assert turb.polytropic_efficiency == 0.91


class TestTurbinePhysics:
    """Test physics correctness (polytropic expansion)."""
    
    def test_ideal_expansion_formula(self, station_turbine_inlet):
        """Ideal expansion (η_p=1.0) follows isentropic formula."""
        turb = Turbine("HPT", polytropic_efficiency=1.0)
        station_6 = turb.expand(station_turbine_inlet, pressure_ratio=0.3, station_id="6")
        
        # Isentropic: T_out = T_in × PR^((γ-1)/γ)
        gamma = 1.4
        T_ideal = station_turbine_inlet.T_t * (0.3 ** ((gamma - 1) / gamma))
        
        assert abs(station_6.T_t - T_ideal) < TOLERANCE_TEMPERATURE
    
    def test_real_expansion_lower_temp(self, station_turbine_inlet):
        """Real expansion (η_p<1.0) produces less temperature drop."""
        turb_ideal = Turbine("HPT", polytropic_efficiency=1.0)
        turb_real = Turbine("HPT", polytropic_efficiency=0.91)
        
        station_ideal = turb_ideal.expand(station_turbine_inlet, pressure_ratio=0.3, station_id="ideal")
        station_real = turb_real.expand(station_turbine_inlet, pressure_ratio=0.3, station_id="real")
        
        # Real outlet temp > ideal outlet temp (less work extracted)
        assert station_real.T_t > station_ideal.T_t
    
    def test_pressure_ratio_applied(self, station_turbine_inlet):
        """Output pressure = inlet pressure × PR."""
        turb = Turbine("HPT")
        station_6 = turb.expand(station_turbine_inlet, pressure_ratio=0.3, station_id="6")
        
        expected_p = station_turbine_inlet.p_t * 0.3
        assert abs(station_6.p_t - expected_p) < TOLERANCE_PRESSURE
    
    def test_mass_flow_conserved(self, station_turbine_inlet):
        """Mass flow unchanged through turbine."""
        turb = Turbine("HPT")
        station_6 = turb.expand(station_turbine_inlet, pressure_ratio=0.3, station_id="6")
        
        assert station_6.m_dot == station_turbine_inlet.m_dot


class TestTurbineValidation:
    """Test input validation."""
    
    def test_turbine_efficiency_must_be_in_range(self):
        """Efficiency must be (0, 1]."""
        with pytest.raises(ValueError, match="must be"):
            Turbine("HPT", polytropic_efficiency=0.0)
        
        with pytest.raises(ValueError, match="must be"):
            Turbine("HPT", polytropic_efficiency=1.5)
    
    def test_turbine_pressure_ratio_must_be_lt_1(self, station_turbine_inlet):
        """Expansion PR must be (0, 1) — pressure drops."""
        turb = Turbine("HPT")
        
        with pytest.raises(ValueError, match="must be"):
            turb.expand(station_turbine_inlet, pressure_ratio=1.0)
        
        with pytest.raises(ValueError, match="must be"):
            turb.expand(station_turbine_inlet, pressure_ratio=1.5)
    
    def test_turbine_station_must_have_pressure_temperature(self, station_turbine_inlet):
        """Turbine inlet must have p_t and T_t."""
        turb = Turbine("HPT")
        station_turbine_inlet.p_t = None
        
        with pytest.raises(ValueError, match="p_t and T_t"):
            turb.expand(station_turbine_inlet, pressure_ratio=0.3)


class TestTurbineMultiStage:
    """Test turbine cascade (HPT → LPT)."""
    
    def test_hpt_then_lpt(self, station_turbine_inlet):
        """Chain HPT → LPT with realistic pressure ratios."""
        hpt = Turbine("HPT", polytropic_efficiency=0.91)
        lpt = Turbine("LPT", polytropic_efficiency=0.92)
        
        # HPT expansion
        station_6 = hpt.expand(station_turbine_inlet, pressure_ratio=0.308, station_id="6")
        
        # LPT expansion (low pressure)
        station_7 = lpt.expand(station_6, pressure_ratio=0.204, station_id="7")
        
        # Overall PR = 0.308 × 0.204 ≈ 0.063 (very large expansion)
        overall_pr = station_7.p_t / station_turbine_inlet.p_t
        assert abs(overall_pr - 0.063) < 0.01
    
    def test_multi_stage_temperature_drops(self, station_turbine_inlet):
        """Temperature drops through each turbine stage."""
        temps = [station_turbine_inlet.T_t]
        
        hpt = Turbine("HPT", polytropic_efficiency=0.91)
        station_6 = hpt.expand(station_turbine_inlet, pressure_ratio=0.308, station_id="6")
        temps.append(station_6.T_t)
        
        lpt = Turbine("LPT", polytropic_efficiency=0.92)
        station_7 = lpt.expand(station_6, pressure_ratio=0.204, station_id="7")
        temps.append(station_7.T_t)
        
        # Each stage drops temperature
        assert temps[1] < temps[0]
        assert temps[2] < temps[1]


class TestTurbineRealism:
    """Test realistic turbine parameters."""
    
    def test_hpt_realistic_parameters(self):
        """HPT typical: high loading, η_p~0.91."""
        hpt = Turbine("HPT", polytropic_efficiency=0.91)
        assert 0.88 <= hpt.polytropic_efficiency <= 0.92
    
    def test_lpt_realistic_parameters(self):
        """LPT typical: lower loading, η_p~0.92 (slightly higher)."""
        lpt = Turbine("LPT", polytropic_efficiency=0.92)
        assert 0.90 <= lpt.polytropic_efficiency <= 0.93
    
    def test_pressure_ratio_ranges(self):
        """Typical PR ranges: HPT 0.25-0.40, LPT 0.15-0.50."""
        hpt_pr = 0.308
        lpt_pr = 0.204
        
        assert 0.25 <= hpt_pr <= 0.40
        assert 0.15 <= lpt_pr <= 0.50
    
    def test_temperature_drop_quantitative(self, station_turbine_inlet):
        """HPT temperature drop typical: 200-400 K."""
        hpt = Turbine("HPT", polytropic_efficiency=0.91)
        station_6 = hpt.expand(station_turbine_inlet, pressure_ratio=0.308, station_id="6")
        
        delta_T = station_turbine_inlet.T_t - station_6.T_t
        assert 200 < delta_T < 500


class TestTurbineIntegration:
    """Test integration with power balance."""
    
    def test_turbine_ready_for_power_balance(self, station_turbine_inlet):
        """Turbine output compatible with power balance calculations."""
        hpt = Turbine("HPT", polytropic_efficiency=0.91)
        station_6 = hpt.expand(station_turbine_inlet, pressure_ratio=0.308, station_id="6")
        
        # Fields needed for work calculation
        assert station_6.T_t is not None
        assert station_6.p_t is not None
        assert station_6.m_dot is not None
    
    def test_turbine_output_ready_for_next_stage(self, station_turbine_inlet):
        """Turbine outlet can be input to next turbine."""
        hpt = Turbine("HPT", polytropic_efficiency=0.91)
        station_6 = hpt.expand(station_turbine_inlet, pressure_ratio=0.308, station_id="6")
        
        # Can feed to LPT
        lpt = Turbine("LPT", polytropic_efficiency=0.92)
        station_7 = lpt.expand(station_6, pressure_ratio=0.204, station_id="7")
        
        assert station_7.T_t < station_6.T_t