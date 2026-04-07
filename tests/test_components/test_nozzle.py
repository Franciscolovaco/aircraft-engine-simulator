"""
Tests for Nozzle component.

Verifies:
- Default efficiency used when None passed
- Explicit efficiency overrides default
- Isentropic expansion formula correct (physics relationships)
- Exit velocity increases with pressure ratio
- Real nozzle (η<1) lower velocity than ideal (η=1) — efficiency effect
- Exit static temp < inlet total temp (energy conservation)
- Larger pressure ratio → higher exit Mach (subsonic regime)
- Nozzle chokes (M≈1) at critical pressure ratio
- Invalid inputs raise errors
- Mass flow conservation through nozzle
- Output station complete for thrust calculation

DESIGN PHILOSOPHY:
- Tests work with ANY default values (altitude, M0, m_dot, pressures)
- Tests verify RELATIONSHIPS (physics laws) not absolute values
- Tests use generated realistic data from fixtures, not hardcoded assumptions
- Tests allow parameter overrides for sensitivity studies

See: docs/physics/NOZZLE.md
"""

import pytest
from src.components.nozzle import Nozzle
from src.design.defaults import ComponentDefaults


class TestNozzleDefaults:
    """Test default parameter behavior."""
    
    def test_nozzle_uses_default_efficiency(self):
        """Nozzle with no efficiency arg uses ComponentDefaults.NOZZLE_EFFICIENCY."""
        nozzle = Nozzle("Core")
        assert nozzle.efficiency == ComponentDefaults.NOZZLE_EFFICIENCY
        assert nozzle.efficiency == 1.0  # Ideal (no losses)
    
    def test_nozzle_explicit_efficiency(self):
        """Nozzle with explicit efficiency overrides ComponentDefaults."""
        nozzle = Nozzle("Core", efficiency=0.98)
        assert nozzle.efficiency == 0.98


class TestNozzlePhysics:
    """Test physics correctness using generated data (no hardcoded assumptions)."""
    
    def test_expansion_creates_velocity(self, station_low_pressure):
        """Nozzle expands (p↓) and accelerates flow (V↑) — fundamental nozzle law."""
        nozzle = Nozzle("Core", efficiency=1.0)
        
        # Generate valid exit pressure: fraction of inlet
        inlet_p_t = station_low_pressure.p_t
        P_exit = inlet_p_t * 0.5  # 50% expansion ratio (generic, works for any inlet)
        
        station_out, V_exit, M_exit = nozzle.expand(
            station_low_pressure,
            exit_pressure=P_exit,
            station_id="8"
        )
        
        # Physics law: expansion always creates positive velocity
        assert V_exit > 0, "Expansion must produce positive exit velocity"
    
    def test_ideal_vs_real_efficiency_effect(self, station_low_pressure):
        """Real nozzle (η<1) produces lower velocity than ideal (η=1) — efficiency loss."""
        nozzle_ideal = Nozzle("Core", efficiency=1.0)
        nozzle_real = Nozzle("Core", efficiency=0.95)  # 5% efficiency loss
        
        inlet_p_t = station_low_pressure.p_t
        P_exit = inlet_p_t * 0.5
        
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
        
        # Physics law: efficiency loss reduces exit velocity
        assert V_real < V_ideal, "Real nozzle must have lower velocity than ideal"
        
        # Quantify efficiency loss: velocity loss ≈ √(efficiency loss) due to V ∝ √(ΔT)
        # For η=0.95 (5% loss): velocity loss ≈ √(5%) ≈ 2.2%
        efficiency_loss = (V_ideal - V_real) / V_ideal
        assert 0.015 < efficiency_loss < 0.035, \
            f"Efficiency loss {efficiency_loss:.2%} (expected ~2.2% for η=0.95)"
    
    def test_exit_temperature_lower_than_total(self, station_low_pressure):
        """Exit static temp < inlet total temp (energy conservation in expansion)."""
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
        
        # Two expansion ratios (both subsonic regime)
        P_exit_small = inlet_p_t * 0.8  # Small expansion (20%)
        P_exit_large = inlet_p_t * 0.5  # Moderate expansion (50%)
        
        _, V_small, _ = nozzle.expand(
            station_low_pressure,
            exit_pressure=P_exit_small,
            station_id="8a"
        )
        _, V_large, _ = nozzle.expand(
            station_low_pressure,
            exit_pressure=P_exit_large,
            station_id="8b"
        )
        
        # Physics law: larger pressure ratio → higher velocity
        assert V_large > V_small, "Larger pressure ratio must produce higher velocity"
    
    def test_exit_mach_increases_with_pressure_ratio(self, station_low_pressure):
        """Larger pressure ratio → higher exit Mach (subsonic nozzle stays M < 1)."""
        nozzle = Nozzle("Core")
        
        inlet_p_t = station_low_pressure.p_t
        
        # Pressure ratios chosen to stay SUBSONIC (avoid choking)
        # Critical pressure ratio for sonic: p_crit/p_t ≈ 0.528
        P_exit_small = inlet_p_t * 0.8  # M ≈ 0.4 (subsonic)
        P_exit_large = inlet_p_t * 0.6  # M ≈ 0.7 (subsonic, closer to sonic)
        
        _, _, M_small = nozzle.expand(
            station_low_pressure,
            exit_pressure=P_exit_small,
            station_id="8a"
        )
        _, _, M_large = nozzle.expand(
            station_low_pressure,
            exit_pressure=P_exit_large,
            station_id="8b"
        )
        
        # Physics: more expansion → higher Mach
        assert M_large > M_small, "Larger pressure ratio must produce higher Mach"
        
        # Convergent nozzle stays subsonic (pressure ratios chosen carefully)
        assert M_small < 1.0, f"Small expansion should stay subsonic: M={M_small:.3f}"
        assert M_large < 1.0, f"Moderate expansion should stay subsonic: M={M_large:.3f}"
    
    def test_nozzle_chokes_at_critical_pressure_ratio(self, station_low_pressure):
        """Nozzle chokes (M≈1) when pressure ratio reaches critical value (~0.528)."""
        nozzle = Nozzle("Core")
        
        inlet_p_t = station_low_pressure.p_t
        
        # Critical pressure ratio for isentropic flow (γ=1.4):
        # p_crit / p_t = (2/(γ+1))^(γ/(γ-1)) ≈ 0.528
        # Below this ratio: choking occurs (M ≥ 1.0, with shock waves in real flow)
        
        # Test just above and below critical ratio
        P_exit_subsonic = inlet_p_t * 0.55  # Above critical (0.55 > 0.528), subsonic
        P_exit_choked = inlet_p_t * 0.50   # Below critical (0.50 < 0.528), choked
        
        _, _, M_subsonic = nozzle.expand(
            station_low_pressure,
            exit_pressure=P_exit_subsonic,
            station_id="subsonic"
        )
        _, _, M_choked = nozzle.expand(
            station_low_pressure,
            exit_pressure=P_exit_choked,
            station_id="choked"
        )
        
        # Physics of choking:
        # - M_subsonic < 1.0 (stays subsonic, convergent nozzle works normally)
        # - M_choked ≥ 1.0 (chokes, sonic condition reached; M>1.0 shows shock behavior)
        # Note: Real convergent nozzles can't sustain M > 1.0 (shock dissipates energy)
        
        assert M_subsonic < 1.0, f"Below critical ratio, should be subsonic: M={M_subsonic:.3f}"
        assert M_choked >= 0.95, f"At/below critical ratio, should approach sonic: M={M_choked:.3f}"


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
        
        # Try to "expand" to higher pressure (physically impossible)
        with pytest.raises(ValueError, match="cannot exceed"):
            nozzle.expand(station_low_pressure, exit_pressure=inlet_p_t * 1.5)
    
    def test_nozzle_inlet_must_have_pressure_temperature(self, station_low_pressure):
        """Inlet must have p_t and T_t defined."""
        nozzle = Nozzle("Core")
        station_low_pressure.p_t = None
        
        with pytest.raises(ValueError, match="p_t and T_t"):
            nozzle.expand(station_low_pressure, exit_pressure=40000)


class TestNozzleRealism:
    """Test realistic behavior (relationships and monotonicity)."""
    
    def test_velocity_increases_monotonically_with_expansion(self, station_low_pressure):
        """Velocity monotonically increases as we expand more (pressure decreases)."""
        nozzle = Nozzle("Core")
        inlet_p_t = station_low_pressure.p_t
        
        # Test multiple expansion ratios: 90%, 70%, 50%, 30%
        # Stay below sonic (0.528) for convergent nozzle
        expansion_ratios = [0.90, 0.70, 0.50]
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
    
    def test_efficiency_effect_consistent_across_expansions(self, station_low_pressure):
        """Efficiency loss is consistent across different expansion ratios."""
        inlet_p_t = station_low_pressure.p_t
        nozzle_ideal = Nozzle("Core", efficiency=1.0)
        nozzle_real = Nozzle("Core", efficiency=0.96)  # 4% efficiency loss
        
        expansion_ratios = [0.8, 0.6, 0.5]
        
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
            assert 0.015 < efficiency_loss < 0.040, \
                f"Efficiency loss {efficiency_loss:.2%} inconsistent at ratio {ratio}"


class TestNozzleIntegration:
    """Test integration with cycle (station properties, continuity, etc.)."""
    
    def test_nozzle_conserves_mass_flow(self, station_low_pressure):
        """Mass flow unchanged through nozzle (continuity equation)."""
        nozzle = Nozzle("Core")
        inlet_p_t = station_low_pressure.p_t
        P_exit = inlet_p_t * 0.5
        
        station_out, _, _ = nozzle.expand(
            station_low_pressure,
            exit_pressure=P_exit,
            station_id="8"
        )
        
        # Mass flow conservation (neglect fuel mass)
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
        
        # All required fields for thrust calculation
        assert station_out.p is not None  # Static pressure (exit plane)
        assert station_out.T is not None  # Static temperature (exit plane)
        assert station_out.V is not None  # Velocity (exit plane)
        assert station_out.M is not None  # Mach number (exit plane)
        assert station_out.a is not None  # Speed of sound (exit plane)
        assert station_out.m_dot is not None  # Mass flow rate
        
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