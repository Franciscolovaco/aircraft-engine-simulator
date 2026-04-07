"""
Shared test fixtures and utilities.

Provides baseline stations, component instances, and helper functions.
"""

import pytest
from src.physics.stations import ThermodynamicStation
from src.physics.thermodynamics import ThermodynamicsCalculator
from src.design.defaults import AllDefaults


@pytest.fixture
def calc():
    """Thermodynamics calculator instance."""
    return ThermodynamicsCalculator()


@pytest.fixture
def station_freestream():
    """Station 0: Freestream at cruise (10 km, M=0.85)."""
    return ThermodynamicStation(
        station_id="0",
        name="Freestream",
        p_t=41656,  # Pa (from ram effect)
        T_t=255.4,  # K
        m_dot=400,  # kg/s
        p=26496,
        T=223.15,
        M=0.85,
        V=254
    )


@pytest.fixture
def station_ideal_inlet():
    """Station at inlet (ideal recovery, no loss)."""
    return ThermodynamicStation(
        station_id="1",
        name="Inlet Exit",
        p_t=41656,  # Same as freestream (ideal, π_d=1.0)
        T_t=255.4,  # Same (adiabatic)
        m_dot=400
    )


@pytest.fixture
def station_realistic_inlet():
    """Station at inlet (realistic recovery, 1% loss)."""
    return ThermodynamicStation(
        station_id="1",
        name="Inlet Exit",
        p_t=41200,  # 1% loss from freestream
        T_t=255.4,  # Adiabatic
        m_dot=400
    )


@pytest.fixture
def station_fan_inlet():
    """Station 2: Fan inlet (same as inlet exit)."""
    return ThermodynamicStation(
        station_id="2",
        name="Fan Inlet",
        p_t=41200,
        T_t=255.4,
        m_dot=400
    )


@pytest.fixture
def station_after_compression():
    """Station after ideal compression (PR=2.0)."""
    return ThermodynamicStation(
        station_id="compressed",
        name="After Compression",
        p_t=82400,  # 2x inlet pressure
        T_t=321.3,  # From ideal polytropic formula
        m_dot=400
    )


@pytest.fixture
def station_combustor_inlet():
    """Station 4: HPC exit / Combustor inlet."""
    return ThermodynamicStation(
        station_id="4",
        name="HPC Exit",
        p_t=889000,  # Pa (9.7 bar)
        T_t=606.4,  # K
        m_dot=72.7  # kg/s (core flow)
    )


@pytest.fixture
def station_turbine_inlet():
    """Station 5: Combustor exit / HPT inlet."""
    return ThermodynamicStation(
        station_id="5",
        name="Combustor Exit",
        p_t=880000,  # Pa (1% loss from combustor)
        T_t=1690,  # K (design limit)
        m_dot=72.7
    )


@pytest.fixture
def station_low_pressure():
    """Station at low pressure for nozzle expansion."""
    return ThermodynamicStation(
        station_id="7",
        name="LPT Exit",
        p_t=55000,  # Pa (low pressure)
        T_t=904,  # K
        m_dot=72.7
    )


# Tolerances for comparisons
TOLERANCE_PRESSURE = 1000  # Pa
TOLERANCE_TEMPERATURE = 1.0  # K
TOLERANCE_VELOCITY = 1.0  # m/s
TOLERANCE_MACH = 0.01
TOLERANCE_PERCENTAGE = 0.01  # 1%