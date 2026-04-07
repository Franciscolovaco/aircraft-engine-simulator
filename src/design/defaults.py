"""
Component and Cycle Default Values

Single source of truth for all default parameters.
All defaults assume IDEAL behavior (no losses, perfect efficiency).

Used when DesignCase doesn't specify a parameter.
Modify here to globally change assumptions.

TURBOFAN-SPECIFIC: These defaults apply to turbofan cycle.
For turboprop/turbojet, create TurbopropDefaults, TurbojetDefaults subclasses.
"""


class ComponentDefaults:
    """Default values for component instantiation (IDEAL behavior)."""
    
    # ===== INLET =====
    INLET_RECOVERY_FACTOR = 1.0  # No pressure loss (perfect inlet)
    
    # ===== COMPRESSOR =====
    COMPRESSOR_POLYTROPIC_EFFICIENCY = 1.0  # Isentropic (reversible)
    
    # ===== COMBUSTOR =====
    COMBUSTOR_TARGET_T_T = 2000  # K (very high, no constraint)
    COMBUSTOR_EFFICIENCY = 1.0  # All fuel energy to air
    COMBUSTOR_PRESSURE_LOSS = 0.0  # No friction
    
    # ===== TURBINE =====
    TURBINE_POLYTROPIC_EFFICIENCY = 1.0  # Isentropic (reversible)
    
    # ===== NOZZLE =====
    NOZZLE_EFFICIENCY = 1.0  # Perfect expansion
    
    # ===== DUCTS =====
    BYPASS_DUCT_PRESSURE_LOSS = 0.0  # No friction


class CycleDefaults:
    """Default values for cycle parameters (IDEAL operation)."""
    
    # ===== FLIGHT CONDITIONS =====
    ALTITUDE = 0  # m (sea level)
    MACH_NUMBER = 0.0  # Stationary
    MASS_FLOW_TOTAL = 100  # kg/s (small baseline)
    
    # ===== DESIGN POINT =====
    PR_FAN = 1.5  # Low pressure ratio (ideal fan)
    PR_HPC = 3.0  # Low pressure ratio (ideal HPC)
    BYPASS_RATIO = 1.0  # 50% core, 50% bypass (equal split)


class AllDefaults:
    """Convenience: both component and cycle defaults."""
    
    # Component defaults
    INLET_RECOVERY_FACTOR = ComponentDefaults.INLET_RECOVERY_FACTOR
    COMPRESSOR_POLYTROPIC_EFFICIENCY = ComponentDefaults.COMPRESSOR_POLYTROPIC_EFFICIENCY
    COMBUSTOR_TARGET_T_T = ComponentDefaults.COMBUSTOR_TARGET_T_T
    COMBUSTOR_EFFICIENCY = ComponentDefaults.COMBUSTOR_EFFICIENCY
    COMBUSTOR_PRESSURE_LOSS = ComponentDefaults.COMBUSTOR_PRESSURE_LOSS
    TURBINE_POLYTROPIC_EFFICIENCY = ComponentDefaults.TURBINE_POLYTROPIC_EFFICIENCY
    NOZZLE_EFFICIENCY = ComponentDefaults.NOZZLE_EFFICIENCY
    BYPASS_DUCT_PRESSURE_LOSS = ComponentDefaults.BYPASS_DUCT_PRESSURE_LOSS
    
    # Cycle defaults
    ALTITUDE = CycleDefaults.ALTITUDE
    MACH_NUMBER = CycleDefaults.MACH_NUMBER
    MASS_FLOW_TOTAL = CycleDefaults.MASS_FLOW_TOTAL
    PR_FAN = CycleDefaults.PR_FAN
    PR_HPC = CycleDefaults.PR_HPC
    BYPASS_RATIO = CycleDefaults.BYPASS_RATIO