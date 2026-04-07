"""
Design Case Parameters

Specific design inputs for cycle calculation.
User modifies THIS FILE for different design cases.

All parameters are optional — if not specified (None), components/cycle use AllDefaults.

See: docs/design/PARAMETERS.md
"""

from dataclasses import dataclass
from typing import Optional
from src.design.defaults import AllDefaults


@dataclass
class DesignCase:
    """
    Generic design case for turbofan cycle.
    
    All parameters optional. If None, uses corresponding default from AllDefaults.
    User specifies only what differs from ideal.
    
    TURBOFAN-SPECIFIC: This dataclass assumes turbofan architecture.
    For turboprop/turbojet, create TurbopropDesignCase, TurbojetDesignCase subclasses.
    """
    
    name: str = "Design Case"
    description: str = ""
    
    # ===== FLIGHT CONDITIONS (Optional) =====
    altitude: Optional[float] = None  # m
    M0: Optional[float] = None  # Mach number
    m_dot_total: Optional[float] = None  # kg/s
    
    # ===== DESIGN POINT (Optional) =====
    PR_fan: Optional[float] = None  # Fan pressure ratio
    PR_HPC: Optional[float] = None  # HPC pressure ratio
    bypass_ratio: Optional[float] = None  # Bypass ratio
    
    # ===== COMPONENT PARAMETERS (Optional) =====
    inlet_recovery: Optional[float] = None
    compressor_efficiency: Optional[float] = None
    combustor_target_T_t: Optional[float] = None
    combustor_efficiency: Optional[float] = None
    combustor_pressure_loss: Optional[float] = None
    turbine_efficiency: Optional[float] = None
    nozzle_efficiency: Optional[float] = None
    bypass_duct_loss: Optional[float] = None
    
    def __post_init__(self):
        """Validate design case."""
        if self.altitude is not None:
            if self.altitude < 0 or self.altitude > 11000:
                raise ValueError(f"Altitude {self.altitude} outside ISA range (0–11 km)")
        
        if self.M0 is not None:
            if self.M0 < 0 or self.M0 > 2.0:
                raise ValueError(f"Mach {self.M0} outside realistic range (0–2.0)")
        
        if self.m_dot_total is not None:
            if self.m_dot_total <= 0:
                raise ValueError(f"Mass flow {self.m_dot_total} must be positive")
        
        if self.PR_fan is not None:
            if self.PR_fan <= 1:
                raise ValueError(f"Fan PR {self.PR_fan} must be > 1")
        
        if self.PR_HPC is not None:
            if self.PR_HPC <= 1:
                raise ValueError(f"HPC PR {self.PR_HPC} must be > 1")
        
        if self.bypass_ratio is not None:
            if self.bypass_ratio <= 0:
                raise ValueError(f"Bypass ratio {self.bypass_ratio} must be > 0")
    
    # ===== GETTERS: Return value or default =====
    
    def get_altitude(self) -> float:
        return self.altitude if self.altitude is not None else AllDefaults.ALTITUDE
    
    def get_M0(self) -> float:
        return self.M0 if self.M0 is not None else AllDefaults.MACH_NUMBER
    
    def get_m_dot_total(self) -> float:
        return self.m_dot_total if self.m_dot_total is not None else AllDefaults.MASS_FLOW_TOTAL
    
    def get_PR_fan(self) -> float:
        return self.PR_fan if self.PR_fan is not None else AllDefaults.PR_FAN
    
    def get_PR_HPC(self) -> float:
        return self.PR_HPC if self.PR_HPC is not None else AllDefaults.PR_HPC
    
    def get_bypass_ratio(self) -> float:
        return self.bypass_ratio if self.bypass_ratio is not None else AllDefaults.BYPASS_RATIO
    
    def get_inlet_recovery(self) -> float:
        return self.inlet_recovery if self.inlet_recovery is not None else AllDefaults.INLET_RECOVERY_FACTOR
    
    def get_compressor_efficiency(self) -> float:
        return self.compressor_efficiency if self.compressor_efficiency is not None else AllDefaults.COMPRESSOR_POLYTROPIC_EFFICIENCY
    
    def get_combustor_target_T_t(self) -> float:
        return self.combustor_target_T_t if self.combustor_target_T_t is not None else AllDefaults.COMBUSTOR_TARGET_T_T
    
    def get_combustor_efficiency(self) -> float:
        return self.combustor_efficiency if self.combustor_efficiency is not None else AllDefaults.COMBUSTOR_EFFICIENCY
    
    def get_combustor_pressure_loss(self) -> float:
        return self.combustor_pressure_loss if self.combustor_pressure_loss is not None else AllDefaults.COMBUSTOR_PRESSURE_LOSS
    
    def get_turbine_efficiency(self) -> float:
        return self.turbine_efficiency if self.turbine_efficiency is not None else AllDefaults.TURBINE_POLYTROPIC_EFFICIENCY
    
    def get_nozzle_efficiency(self) -> float:
        return self.nozzle_efficiency if self.nozzle_efficiency is not None else AllDefaults.NOZZLE_EFFICIENCY
    
    def get_bypass_duct_loss(self) -> float:
        return self.bypass_duct_loss if self.bypass_duct_loss is not None else AllDefaults.BYPASS_DUCT_PRESSURE_LOSS
    
    def __repr__(self) -> str:
        return (
            f"DesignCase('{self.name}')\n"
            f"  Flight: h={self.get_altitude()}m, M={self.get_M0()}, m_dot={self.get_m_dot_total()}kg/s\n"
            f"  Design: PR_fan={self.get_PR_fan()}, PR_HPC={self.get_PR_HPC()}, BPR={self.get_bypass_ratio()}\n"
            f"  Components: inlet={self.get_inlet_recovery():.2f}, comp_eff={self.get_compressor_efficiency():.2f}, "
            f"turb_eff={self.get_turbine_efficiency():.2f}"
        )