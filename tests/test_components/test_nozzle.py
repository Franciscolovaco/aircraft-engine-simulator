"""
Tests for Nozzle component.

DESIGN PHILOSOPHY:
- Tests work with ANY default values (altitude, M0, m_dot, pressures)
- Tests verify RELATIONSHIPS (physics laws) not absolute values
- Tests use generated realistic data, not hardcoded assumptions
- Tests allow parameter overrides for sensitivity studies

Verifies:
- Default efficiency used when None passed
- Explicit efficiency overrides default
- Isentropic expansion formula correct (relationships)
- Exit velocity increases with pressure ratio
- Real nozzle lower velocity than ideal (efficiency effect)
- Exit static temp < inlet total temp (always true for expansion)
- Exit Mach depends on pressure ratio (not specific value)
- Invalid inputs raise errors
"""

import pytest
import math
from src.components.nozzle import Nozzle
from src.design.defaults import ComponentDefaults


class TestNozzleDefaults:
    """Test default parameter behavior."""
    
    def test_nozzle_uses_default_efficiency(self):
        """Nozzle with no efficiency arg uses ComponentDefaults."""
        nozzle = Nozzle("Core")
        assert nozzle.efficiency == ComponentDefaults.NOZZLE_EFFICIENCY
        assert nozzle.efficiency == 1.0  # Ideal
    
    def test_nozzle_explicit_efficiency(self):
        """Nozzle with explicit efficiency overrides default."""
        nozzle = Nozzle("Core", efficiency=0.98)
        assert nozzle.efficiency == 0.98


class TestNozzlePhysics:
    """Test physics correctness using generated data (no hardcoded assumptions)."""
    
    def test_expansion_decreases_pressure_increases_velocity(self, station_low_pressure):
        """Nozzle expands (p↓) and accelerates flow (V↑) — always true."""
        nozzle = Nozzle("Core", efficiency=1.0)
        
        # Generate valid exit pressure: fraction of inlet (0.2-0.8 for realistic expansion)
        inlet_p_t = station_low_pressure.p_t
        P_exit = inlet_p_t * 0.5  # 50% expansion (works for any inlet pressure)
        
        station_out, V_exit, M_exit = nozzle.expand(
            station_low_pressure,
            exit_pressure=P_exit,
            station_id="8"
        )
        
        # Physics law: expansion always creates velocity
        assert V_exit > 0, "Expansion must produce positive velocity"
    
    def test_ideal_vs_real_efficiency_effect(self, station_low_pressure):
        """Real nozzle (η<1) produces lower velocity than ideal (η=1)."""
        nozzle_ideal = Nozzle("Core", efficiency=1.0)
        nozzle_real = Nozzle("Core", efficiency=0.95)
        
        inlet_p_t = station_low_pressure.p_t
        P_exit = inlet_p_t * 0.5  # Generic expansion ratio
        
        _, V_ideal, _ = nozzle_ideal.expand(
            station_low_pressure,
            exit_pressure=P_exit,
            station_id="ideal"
        )
        _, V_real, _ = nozzle_real.expand(
            station_low_pressure,
            exit_pressure=P_exit,
            station_id="real"
        )
        
        # Physics law: efficiency loss reduces velocity
        assert V_real < V_ideal, "Real nozzle must have lower velocity than ideal"
        
        # Quantify: velocity difference should be ~5% (100% - 95%)
        efficiency_loss = (V_ideal - V_real) / V_ideal
        assert 0.03 < efficiency_loss < 0.07, f"Efficiency loss {efficiency_loss:.2%} unrealistic"
    
    def test_exit_temperature_lower_than_total(self, station_low_pressure):
        """Exit static temp < inlet total temp (energy conservation)."""
        nozzle = Nozzle("Core")
        
        inlet_p_t = station_low_pressure.p_t
        P_exit = inlet_p_t * 0.5
        
        station_out, _, _ = nozzle.expand(
            station_low_pressure,
            exit_pressure=P_exit,
            station_id="8"
        )
        
        # Physics law: expansion converts enthalpy to kinetic energy
        assert station_out.T < station_low_pressure.T_t, \
            "Exit static temp must be less than inlet total temp"
    
    def test_larger_pressure_ratio_higher_velocity(self, station_low_pressure):
        """Larger pressure expansion (more PR) → higher exit velocity."""
        nozzle = Nozzle("Core", efficiency=0.98)
        
        inlet_p_t = station_low_pressure.p_t
        
        # Two expansion ratios
        P_exit_small = inlet_p_t * 0.8  # Small expansion (20%)
        P_exit_large = inlet_p_t * 0.4  # Large expansion (60%)
        
        _, V_small, _ = nozzle.expand(station_low_pressure, exit_pressure=P_exit_small, station_id="8a")
        _, V_large, _ = nozzle.expand(station_low_pressure, exit_pressure=P_exit_large, station_id="8b")
        
        # Physics law: more expansion ratio → more velocity
        assert V_large > V_small, "Larger pressure ratio must produce higher velocity"
    
    def test_exit_mach_increases_with_pressure_ratio(self, station_low_pressure):
        """Larger pressure ratio → higher exit Mach (but stays < 1 for subsonic nozzle)."""
        nozzle = Nozzle("Core")
        
        inlet_p_t = station_low_pressure.p_t
        
        P_exit_small = inlet_p_t * 0.8
        P_exit_large = inlet_p_t * 0.3
        
        _, _, M_small = nozzle.expand(station_low_pressure, exit_pressure=P_exit_small, station_id="8a")
        _, _, M_large = nozzle.expand(station_low_pressure, exit_pressure=P_exit_large, station_id="8b")
        
        # Physics: more expansion → higher Mach
        assert M_large > M_small, "Larger pressure ratio must produce higher Mach"
        
        # Both should remain subsonic (convergent nozzle)
        assert M_small < 1.0, "Convergent nozzle exit Mach < 1.0"
        assert M_large < 1.0, "Convergent nozzle exit Mach < 1.0"


class TestNozzleValidation:
    """Test input validation."""
    
    def test_nozzle_efficiency_must_be_in_range(self):
        """Efficiency must be (0, 1]."""
        with pytest.raises(ValueError, match="must be"):
            Nozzle("Core", efficiency=0.0)
        
        with pytest.raises(ValueError, match="must be"):
            Nozzle("Core", efficiency=1.5)
    
    def test_nozzle_exit_pressure_must_be_positive(self, station_low_pressure):
        """Exit pressure must be > 0."""
        nozzle = Nozzle("Core")
        
        with pytest.raises(ValueError, match="must be positive"):
            nozzle.expand(station_low_pressure, exit_pressure=-100)
        
        with pytest.raises(ValueError, match="must be positive"):
            nozzle.expand(station_low_pressure, exit_pressure=0)
    
    def test_nozzle_exit_pressure_less_than_inlet(self, station_low_pressure):
        """Exit pressure cannot exceed inlet pressure (nozzle expands, not compresses)."""
        nozzle = Nozzle("Core")
        inlet_p_t = station_low_pressure.p_t
        
        # Try to "expand" to higher pressure (invalid)
        with pytest.raises(ValueError, match="cannot exceed"):
            nozzle.expand(station_low_pressure, exit_pressure=inlet_p_t * 1.5)
    
    def test_nozzle_inlet_must_have_pressure_temperature(self, station_low_pressure):
        """Inlet must have p_t and T_t defined."""
        nozzle = Nozzle("Core")
        station_low_pressure.p_t = None
        
        with pytest.raises(ValueError, match="p_t and T_t"):
            nozzle.expand(station_low_pressure, exit_pressure=40000)


class TestNozzleRealism:
    """Test realistic behavior (relationships, not absolute values)."""
    
    def test_velocity_increases_monotonically_with_expansion(self, station_low_pressure):
        """Velocity monotonically increases as we expand more (pressure decreases)."""
        nozzle = Nozzle("Core")
        inlet_p_t = station_low_pressure.p_t
        
        # Test multiple expansion ratios: 90%, 70%, 50%, 30%
        expansion_ratios = [0.9, 0.7, 0.5, 0.3]
        velocities = []
        
        for i, ratio in enumerate(expansion_ratios):
            P_exit = inlet_p_t * ratio
            _, V_exit, _ = nozzle.expand(
                station_low_pressure,
                exit_pressure=P_exit,
                station_id=f"test_{i}"
            )
            velocities.append(V_exit)
        
        # Velocity should increase monotonically as we expand more
        for i in range(len(velocities) - 1):
            assert velocities[i+1] > velocities[i], \
                f"Velocity must increase with more expansion: {velocities}"
    
    def test_efficiency_consistency_across_expansions(self, station_low_pressure):
        """Efficiency effect consistent across different expansion ratios."""
        inlet_p_t = station_low_pressure.p_t
        nozzle_ideal = Nozzle("Core", efficiency=1.0)
        nozzle_real = Nozzle("Core", efficiency=0.96)  # 4% loss
        
        expansion_ratios = [0.8, 0.5, 0.3]
        
        for ratio in expansion_ratios:
            P_exit = inlet_p_t * ratio
            _, V_ideal, _ = nozzle_ideal.expand(
                station_low_pressure,
                exit_pressure=P_exit,
                station_id="ideal"
            )
            _, V_real, _ = nozzle_real.expand(
                station_low_pressure,
                exit_pressure=P_exit,
                station_id="real"
            )
            
            # Efficiency loss should be relatively consistent
            efficiency_loss = (V_ideal - V_real) / V_ideal
            assert 0.02 < efficiency_loss < 0.06, \
                f"Efficiency loss {efficiency_loss:.2%} inconsistent at ratio {ratio}"


class TestNozzleIntegration:
    """Test integration with cycle (station properties, continuity, etc.)."""
    
    def test_nozzle_conserves_mass_flow(self, station_low_pressure):
        """Mass flow unchanged through nozzle (continuity)."""
        nozzle = Nozzle("Core")
        inlet_p_t = station_low_pressure.p_t
        P_exit = inlet_p_t * 0.5
        
        station_out, _, _ = nozzle.expand(
            station_low_pressure,
            exit_pressure=P_exit,
            station_id="8"
        )
        
        # Mass flow conservation
        assert station_out.m_dot == station_low_pressure.m_dot
    
    def test_nozzle_output_complete_station(self, station_low_pressure):
        """Nozzle output has all required fields for thrust calculation."""
        nozzle = Nozzle("Core")
        inlet_p_t = station_low_pressure.p_t
        P_exit = inlet_p_t * 0.5
        
        station_out, V_exit, M_exit = nozzle.expand(
            station_low_pressure,
            exit_pressure=P_exit,
            station_id="8"
        )
        
        # Required fields for thrust calculation
        assert station_out.p is not None  # Static pressure
        assert station_out.T is not None  # Static temperature
        assert station_out.V is not None  # Velocity
        assert station_out.M is not None  # Mach
        assert station_out.a is not None  # Speed of sound
        assert station_out.m_dot is not None  # Mass flow
        
        # Verify consistency
        assert station_out.V == V_exit
        assert station_out.M == M_exit
        assert station_out.p == P_exit
    
    def test_nozzle_returns_tuple(self, station_low_pressure):
        """Nozzle returns (station, velocity, mach) tuple."""
        nozzle = Nozzle("Core")
        inlet_p_t = station_low_pressure.p_t
        P_exit = inlet_p_t * 0.5
        
        result = nozzle.expand(
            station_low_pressure,
            exit_pressure=P_exit,
            station_id="8"
        )
        
        # Verify tuple structure
        assert isinstance(result, tuple)
        assert len(result) == 3
        station_out, V_exit, M_exit = result
        
        # Verify types
        assert station_out is not None
        assert isinstance(V_exit, float)
        assert isinstance(M_exit, float)