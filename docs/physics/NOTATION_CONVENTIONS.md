# Notation Conventions

This document standardizes notation across the simulator, following European (ISO/EASA) gas turbine conventions.

---

## Temperature

| Symbol | Meaning | Units | Example |
|--------|---------|-------|---------|
| $T$ | Static temperature | K | 223.15 K (at 10 km) |
| $T_t$ or $T^0$ | Total (stagnation) temperature | K | 255.4 K (cruise at M=0.85) |
| $T_i$ | Temperature at station i | K | $T_3$ = 600 K (HPC inlet) |
| $T_{ti}$ or $T_i^0$ | Total temperature at station i | K | $T_{t3}$ = 412 K (after fan) |

---

## Pressure

| Symbol | Meaning | Units | Example |
|--------|---------|-------|---------|
| $P$ | Static pressure | Pa | 26.5 kPa (at 10 km) |
| $P_t$ or $P^0$ | Total pressure | Pa | 41.6 kPa (cruise) |
| $P_i$ | Pressure at station i | Pa | $P_4$ = 6.5 bar (HPC exit) |
| $P_{ti}$ or $P_i^0$ | Total pressure at station i | Pa | $P_{t4}$ = 37 bar |
| $PR$ | Pressure ratio | dimensionless | PR = 2.2 (fan) |

---

## Temperature Ratio

| Symbol | Meaning | Formula | Range |
|--------|---------|---------|-------|
| $τ$ | Generic temperature ratio | $T_2 / T_1$ | 0 → ∞ |
| $τ_c$ | Compressor temp ratio | $(T_{out} - T_{in}) / T_{in}$ | 0.1 → 2.0 |
| $τ_t$ | Turbine temp ratio | $(T_{in} - T_{out}) / T_{in}$ | 0.2 → 0.6 |

---

## Efficiencies

| Symbol | Meaning | Range | Notes |
|--------|---------|-------|-------|
| $η$ | Generic efficiency | 0 → 1 | Dimensionless |
| $η_p$ | Polytropic efficiency | 0.85 → 0.95 | Used for design (component level) |
| $η_iso$ | Isentropic efficiency | 0.80 → 0.93 | Theoretical (single design point) |
| $η_th$ | Thermal efficiency | 0.35 → 0.50 | Cycle level (overall) |
| $η_prop$ | Propulsive efficiency | 0.40 → 0.80 | Thrust efficiency (bypass ratio effect) |
| $η_overall$ | Overall efficiency | $η_{th} × η_{prop}$ | Total propulsion |

---

## Mass Flow

| Symbol | Meaning | Units | Notes |
|--------|---------|-------|-------|
| $\dot{m}$ | Mass flow rate | kg/s | Constant through engine (continuity) |
| $\dot{m}_c$ | Core mass flow | kg/s | To compressor/combustor/turbine |
| $\dot{m}_{bypass}$ | Bypass mass flow | kg/s | Around compressor (TURBOFAN-SPECIFIC) |
| $\dot{m}_{total}$ | Total mass flow | kg/s | $\dot{m}_{total} = \dot{m}_c + \dot{m}_{bypass}$ |
| $f$ | Fuel-air ratio | kg_fuel / kg_air | 0.010 → 0.080 |

---

## Mach & Velocity

| Symbol | Meaning | Units | Range |
|--------|---------|-------|-------|
| $M$ | Mach number | dimensionless | 0 → >1 (supersonic) |
| $V$ | Velocity | m/s | 0 → 600 m/s (typical) |
| $a$ | Speed of sound | m/s | 290–350 m/s (engine range) |
| $V_e$ | Exit velocity | m/s | 400–800 m/s (nozzle) |

---

## Station Numbering (TURBOFAN-SPECIFIC)

Following **European convention** (ISO, EASA):

```
0: Freestream
1: Inlet exit
2: Fan inlet
2.5: Fan exit (bifurcation)
3: HPC inlet (core)
4: HPC exit / Combustor inlet
5: Combustor exit / HPT inlet ← PEAK TEMPERATURE
6: HPT exit / LPT inlet
7: LPT exit
8: Core nozzle exit
13: Bypass duct exit
19: Bypass nozzle exit
```

**US Convention (sometimes seen):**
- 0, 2, 2.5, 3, 4, 5, 6, 7 (SAME, mostly)
- But numbering may vary for single-spool or turboprop

---

## Thermodynamic Process Notation

| Process | Notation | Description |
|---------|----------|-------------|
| Isentropic | $s = \text{const}$ | Adiabatic reversible (ideal) |
| Polytropic | $Pv^n = \text{const}$ | Real compressor/turbine with efficiency |
| Isobaric | $P = \text{const}$ | Combustor (pressure ~constant) |
| Isothermal | $T = \text{const}$ | Cooler (rare in engines) |

---

## Dimensionless Parameters

| Parameter | Definition | Range | Notes |
|-----------|----------|-------|-------|
| Bypass Ratio | $\dot{m}_{bypass} / \dot{m}_{core}$ | 4–9 (modern) | Separates turbofan from turbojet |
| Overall PR | $P_{t0} / P_{t3}$ | 30–50 | Inlet + Fan + HPC total |
| Compression Ratio | $P_{t,out} / P_{t,in}$ | 1.5 → 9 (per stage) | Per compressor/stage |
| Temperature Rise Ratio | $ΔT / T_{in}$ | 0.1 → 1.0 | Normalized temp change |

---

## Subscript Convention

All properties at **station i** use subscript:
- $T_i$, $P_i$, $\dot{m}_i$, $ρ_i$, etc.

**Examples:**
- $T_3$ = static temperature at station 3 (HPC inlet)
- $T_{t3}$ = total temperature at station 3
- $P_{t5}$ = total pressure at station 5 (combustor exit)
- $\dot{m}_2$ = mass flow at station 2 (before fan)

---

## Chemical/Combustion Notation

| Symbol | Meaning | Units |
|--------|---------|-------|
| $f$ | Fuel-air ratio | kg_fuel / kg_air |
| $q_r$ | Heat release rate (fuel) | J/kg |
| $c_p$ | Specific heat (pressure) | J/kg·K |
| $h$ | Specific enthalpy | J/kg |
| $s$ | Specific entropy | J/kg·K |

---

## Code Implementation

All code uses these conventions:

```python
# Temperature
T_static = 223.15  # K
T_total = 255.4    # K, denoted p_t and T_t in code

# Pressure
P_static = 26496   # Pa
P_total = 41600    # Pa, denoted p_t and T_t in code

# Station indexing
station_3 = ThermodynamicStation(station_id="3", name="HPC Inlet")
station_3.T = 600      # Static temp
station_3.T_t = 412    # Total temp (suffix 't' = total)

# Mass flow
m_dot = 400  # kg/s (with dot notation in comments)

# Efficiency
eta_poly = 0.90  # Polytropic

# Mach/Velocity
M = 0.85  # Mach number
a = 299.1  # m/s, speed of sound
V = M * a  # Velocity
```

---

## LaTeX Rendering Guide

For equations in documentation:

- **Inline:** `$T_t = T(1 + 0.2M^2)$`
- **Display:** `$$T_t = T \left(1 + \frac{\gamma-1}{2} M^2\right)$$`
- **Fractions:** `\frac{numerator}{denominator}`
- **Superscript:** `^{exponent}`
- **Greek:** `\gamma`, `\eta`, `\rho`, `\dot{m}` (for derivative/flow)
