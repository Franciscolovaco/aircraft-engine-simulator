"""
Predefined Design Case Presets

Common configurations for learning and reference.
User can use these as starting points or templates.

TURBOFAN-SPECIFIC: All presets assume turbofan architecture.
For turboprop/turbojet, create separate preset files (presets_turboprop.py, etc.).

See: docs/design/PRESETS.md
"""

from src.design.parameters import DesignCase


# ===== EDUCATIONAL CASES =====

IDEAL = DesignCase(
    name="Ideal Brayton Cycle",
    description="Perfect thermodynamic cycle (no losses, efficiency=1.0)",
    # All parameters use AllDefaults (ideal)
)

IDEAL_WITH_INLET_LOSS = DesignCase(
    name="Ideal + Inlet Loss",
    description="Ideal cycle with 1% inlet pressure loss (learn inlet effect)",
    inlet_recovery=0.99
)

IDEAL_WITH_REAL_COMPRESSOR = DesignCase(
    name="Ideal + Real Compressor",
    description="Ideal cycle with realistic compressor efficiency (learn irreversibilities)",
    compressor_efficiency=0.91
)

IDEAL_WITH_REAL_COMBUSTOR = DesignCase(
    name="Ideal + Real Combustor",
    description="Ideal cycle with material limit and combustor losses",
    combustor_target_T_t=1690,
    combustor_efficiency=0.98,
    combustor_pressure_loss=0.01
)

IDEAL_WITH_ALL_LOSSES = DesignCase(
    name="Ideal + All Realistic Losses",
    description="Ideal cycle with all realistic component losses (learn cumulative effect)",
    inlet_recovery=0.99,
    compressor_efficiency=0.91,
    combustor_target_T_t=1690,
    combustor_efficiency=0.98,
    combustor_pressure_loss=0.01,
    turbine_efficiency=0.91,
    nozzle_efficiency=0.98,
    bypass_duct_loss=0.01
)


# ===== FLIGHT CONDITION VARIANTS =====

SEA_LEVEL_STATIC = DesignCase(
    name="Sea Level Static",
    description="Takeoff condition: ground, no forward motion",
    altitude=0,
    M0=0.0,
    m_dot_total=400
)

CRUISE_10KM = DesignCase(
    name="Cruise 10 km",
    description="Typical cruise altitude and Mach",
    altitude=10000,
    M0=0.85,
    m_dot_total=400
)

CLIMB_5KM = DesignCase(
    name="Climb 5 km",
    description="Intermediate altitude during climb",
    altitude=5000,
    M0=0.60,
    m_dot_total=400
)


# ===== DESIGN POINT VARIANTS (All losses) =====

CFM56_LIKE = DesignCase(
    name="CFM56 (Cruise Design Point)",
    description="Commercial turbofan (narrow-body: B737, A320)",
    altitude=10000,
    M0=0.85,
    m_dot_total=400,
    PR_fan=2.2,
    PR_HPC=9.7,
    bypass_ratio=4.5,
    inlet_recovery=0.99,
    compressor_efficiency=0.91,
    combustor_target_T_t=1690,
    combustor_efficiency=0.98,
    combustor_pressure_loss=0.01,
    turbine_efficiency=0.91,
    nozzle_efficiency=0.98,
    bypass_duct_loss=0.01
)

GE90_LIKE = DesignCase(
    name="GE90 (Large Turbofan)",
    description="High-bypass commercial turbofan (wide-body: B777)",
    altitude=10000,
    M0=0.85,
    m_dot_total=850,  # Much larger fan
    PR_fan=2.5,
    PR_HPC=23,  # Higher overall PR
    bypass_ratio=9.0,  # Very high bypass
    inlet_recovery=0.99,
    compressor_efficiency=0.92,  # Slightly higher (mature design)
    combustor_target_T_t=1700,
    combustor_efficiency=0.98,
    combustor_pressure_loss=0.01,
    turbine_efficiency=0.92,  # Slightly higher (lower pressure stages)
    nozzle_efficiency=0.98,
    bypass_duct_loss=0.01
)


# ===== PARAMETRIC STUDY VARIANTS =====

PESSIMISTIC = DesignCase(
    name="Pessimistic Case",
    description="Lower efficiencies, higher losses (conservative estimates)",
    altitude=10000,
    M0=0.85,
    m_dot_total=400,
    PR_fan=2.2,
    PR_HPC=9.7,
    bypass_ratio=4.5,
    inlet_recovery=0.98,  # Higher loss
    compressor_efficiency=0.88,  # Lower
    combustor_target_T_t=1690,
    combustor_efficiency=0.96,  # Lower (more unburned fuel)
    combustor_pressure_loss=0.015,  # Higher loss
    turbine_efficiency=0.88,  # Lower
    nozzle_efficiency=0.96,  # Lower
    bypass_duct_loss=0.015  # Higher loss
)

OPTIMISTIC = DesignCase(
    name="Optimistic Case",
    description="Higher efficiencies, lower losses (best case scenario)",
    altitude=10000,
    M0=0.85,
    m_dot_total=400,
    PR_fan=2.2,
    PR_HPC=9.7,
    bypass_ratio=4.5,
    inlet_recovery=0.995,  # Lower loss
    compressor_efficiency=0.93,  # Higher
    combustor_target_T_t=1690,
    combustor_efficiency=0.99,  # Higher
    combustor_pressure_loss=0.005,  # Lower loss
    turbine_efficiency=0.93,  # Higher
    nozzle_efficiency=0.99,  # Higher
    bypass_duct_loss=0.005  # Lower loss
)

ADVANCED = DesignCase(
    name="Advanced (Next-Gen)",
    description="Future engine with advanced materials and design (2030s)",
    altitude=10000,
    M0=0.85,
    m_dot_total=400,
    PR_fan=2.5,  # Higher (lighter materials)
    PR_HPC=12,  # Higher
    bypass_ratio=6.0,  # Higher (more efficient)
    inlet_recovery=0.995,
    compressor_efficiency=0.93,
    combustor_target_T_t=1800,  # Ceramic matrix composites
    combustor_efficiency=0.99,
    combustor_pressure_loss=0.005,
    turbine_efficiency=0.93,
    nozzle_efficiency=0.99,
    bypass_duct_loss=0.005
)


# ===== TEACHING PROGRESSION SEQUENCE =====

TEACHING_SEQUENCE = [
    ("Stage 1: Pure Physics", IDEAL),
    ("Stage 2: Add Inlet Loss", IDEAL_WITH_INLET_LOSS),
    ("Stage 3: Add Compressor Loss", IDEAL_WITH_REAL_COMPRESSOR),
    ("Stage 4: Add Combustor", IDEAL_WITH_REAL_COMBUSTOR),
    ("Stage 5: Complete Model", IDEAL_WITH_ALL_LOSSES),
    ("Stage 6: Flight Conditions", CRUISE_10KM),
    ("Stage 7: Realistic Design (CFM56)", CFM56_LIKE),
    ("Stage 8: Design Sensitivity (Pessimistic)", PESSIMISTIC),
    ("Stage 9: Design Sensitivity (Optimistic)", OPTIMISTIC),
]