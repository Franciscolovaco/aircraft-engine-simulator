# Thermodynamics Reference Guide

## Overview
This guide covers all thermodynamic processes in the engine simulator: isentropic relations, polytropic processes (compressor/turbine), nozzle expansion, and combustor energy balance.

**Key Assumption:** Perfect gas law with constant specific heats (γ = 1.4, R = 287.05 J/kg·K for air).

---

## Isentropic Relations

### Total-to-Static Temperature Ratio (from Mach number)

**Formula:**
$$T_t / T = 1 + \frac{\gamma - 1}{2} M^2$$

**Where:**
- $T_t$ = total (stagnation) temperature (K)
- $T$ = static temperature (K)
- $M$ = Mach number
- $\gamma$ = 1.4 (specific heat ratio for air)

**Physics Interpretation:**
As air flows at velocity (Mach M), its thermal energy converts to kinetic energy. If you bring the air to rest adiabatically (stagnate it), the kinetic energy converts back to thermal energy, increasing temperature. This is the **ram effect** — crucial for high-speed flight.

**Example (Cruise at 10 km, M=0.85):**
- Static temperature: T = 223.15 K
- Mach: M = 0.85
- $T_t / T = 1 + (0.4/2) × (0.85)^2 = 1.1445$
- Total temperature: $T_t = 223.15 × 1.1445 ≈ 255.4$ K ← **32 K increase!**

### Total-to-Static Pressure Ratio (from Mach number)

**Formula:**
$$P_t / P = \left(T_t / T\right)^{\gamma / (\gamma - 1)}$$

**Substituting Mach:**
$$P_t / P = \left(1 + \frac{\gamma - 1}{2} M^2\right)^{\gamma / (\gamma - 1)}$$

With γ = 1.4:
$$P_t / P = \left(1 + 0.2 M^2\right)^{3.5}$$

**Example (M=0.85 at 10 km):**
- $P_t / P = (1 + 0.2 × 0.7225)^{3.5} = (1.1445)^{3.5} ≈ 1.574$
- Pressure amplification: ~57% ← also significant!

### Isentropic Temperature Ratio (across compression/expansion)

**Formula:**
$$\frac{T_2}{T_1} = \left(\frac{P_2}{P_1}\right)^{(\gamma - 1) / \gamma}$$

With γ = 1.4:
$$\frac{T_2}{T_1} = \left(\frac{P_2}{P_1}\right)^{0.2857}$$

**Physics:** For **isentropic** (adiabatic reversible) process, pressure and temperature relate through this exponent.

**Example (Fan compression, PR=2):**
- Isentropic: $T_2 / T_1 = 2^{0.2857} ≈ 1.2599$ → **26% temperature increase**
- Real (polytropic efficiency η=0.90): Temperature higher due to irreversibilities

---

## Polytropic Processes (Real Compressor/Turbine)

Real components have **polytropic efficiency** accounting for irreversibilities (friction, turbulence, heat loss).

### Polytropic Compression

**Formula:**
$$T_{out} = T_{in} \times \left(PR\right)^{(\gamma - 1) / (\gamma × η_p)}$$

**Where:**
- $PR = P_{out} / P_{in}$ = pressure ratio
- $η_p$ = polytropic efficiency (0 < η_p ≤ 1)
- η_p = 1 → isentropic (ideal)
- η_p < 1 → real (entropy increases)

**Typical Values:**
- Fan: η_p ≈ 0.88–0.92
- HPC: η_p ≈ 0.87–0.92
- LPC: η_p ≈ 0.90–0.93

**Example (Fan: inlet T₁ = 288.15 K, PR = 2.0, η_p = 0.90):**

Isentropic: $T_{out} = 288.15 × 2^{0.2857} = 288.15 × 1.2599 ≈ 363.0$ K

Polytropic: $T_{out} = 288.15 × 2^{(0.4 / (1.4 × 0.90))} = 288.15 × 2^{0.3175} ≈ 373.4$ K

**Difference: +10.4 K** due to polytropic inefficiency.

### Polytropic Expansion (Turbine)

**Formula:**
$$T_{out} = T_{in} \times \left(PR\right)^{(\gamma - 1) × η_p / \gamma}$$

**Where:**
- $PR = P_{out} / P_{in}$ < 1 (expansion)
- η_p = polytropic efficiency

**Typical Values:**
- HPT: η_p ≈ 0.88–0.92
- LPT: η_p ≈ 0.90–0.93

**Example (HPT: inlet T₅ = 1700 K, PR = 0.25, η_p = 0.90):**

Isentropic: $T_6 = 1700 × 0.25^{0.2857} = 1700 × 0.6597 ≈ 1121$ K

Polytropic: $T_6 = 1700 × 0.25^{(0.4 × 0.90 / 1.4)} = 1700 × 0.25^{0.2571} ≈ 1081$ K

**Difference: -40 K** — turbine produces less work due to inefficiency, lower outlet temperature.

---

## Nozzle Expansion

### Exit Velocity (Ideal Nozzle)

**Formula:**
$$V_{exit} = \sqrt{2 c_p (T_t - T_{exit})}$$

**Where:**
- $T_t$ = inlet total temperature (K)
- $T_{exit}$ = outlet static temperature (K)
- $c_p$ = 1005 J/kg·K (specific heat at constant pressure)

**Physics:** Enthalpy balance: all thermal energy (except what remains as $T_{exit}$) converts to kinetic energy.

**Example (Core nozzle: T_t = 850 K, T_exit = 280 K at sea level):**
$$V = \sqrt{2 × 1005 × (850 - 280)} = \sqrt{1,145,700} ≈ 1,070 \text{ m/s}$$

### Isentropic Nozzle Expansion

**Process:**
1. Expand from $(P_t, T_t)$ to static pressure $P_{exit}$ (usually ambient)
2. Calculate isentropic exit temperature: $T_{isentropic} = T_t × (P_{exit} / P_t)^{0.2857}$
3. Apply nozzle efficiency (η ≈ 0.98): $T_{exit} = T_t - η × (T_t - T_{isentropic})$
4. Calculate exit velocity and Mach

**Example (Core nozzle at sea level):**
- Inlet: $P_t = 200$ kPa, $T_t = 850$ K
- Exit: $P = 101$ kPa (ambient)
- Isentropic: $T_{iso} = 850 × (0.505)^{0.2857} = 850 × 0.8396 ≈ 714$ K
- Real (η=0.98): $T_{exit} = 850 - 0.98 × (850 - 714) = 850 - 133.7 ≈ 716$ K
- Exit velocity: $V = \sqrt{2 × 1005 × (850 - 716)} ≈ 515$ m/s
- Speed of sound at exit: $a = \sqrt{1.4 × 287 × 716} ≈ 537$ m/s
- Exit Mach: $M = 515 / 537 ≈ 0.96$ (subsonic, typical for bypass nozzle)

---

## Combustor Energy Balance

### Fuel-Air Ratio Calculation

**Formula:**
$$f = \frac{c_p (T_4 - T_3)}{η_{comb} \times q_r - c_p \times T_4}$$

**Where:**
- $f$ = fuel-to-air mass ratio (kg fuel / kg air)
- $T_3$ = compressor outlet (inlet to combustor) (K)
- $T_4$ = flame temperature (combustor outlet) (K)
- $q_r$ = 43 × 10⁶ J/kg (heat release rate from Jet A fuel)
- $η_{comb}$ = 0.98 (combustor efficiency)
- $c_p$ = 1005 J/kg·K

**Physics:** Energy released by fuel = energy increase of air + losses.

**Example (Design point):**
- Inlet: $T_3 = 600$ K
- Target outlet: $T_4 = 1500$ K
- $ΔT = 900$ K

$$f = \frac{1005 × 900}{0.98 × 43 × 10^6 - 1005 × 1500}$$

$$f = \frac{904,500}{42.14 × 10^6 - 1,507,500} = \frac{904,500}{40,632,500} ≈ 0.0223$$

**Interpretation:** ~2.23% fuel by mass → realistic for typical turbofan (1.5–3%).

---

## Code Examples

### Calculate polytropic compression temperature

```python
from src.physics.thermodynamics import ThermodynamicsCalculator

calc = ThermodynamicsCalculator()

# Fan inlet: 288.15 K, pressure ratio 2.0, polytropic efficiency 0.90
T_inlet = 288.15
PR = 2.0
eta_poly = 0.90

T_outlet = calc.polytropic_compression(T_inlet, PR, eta_poly)
print(f"Outlet temp: {T_outlet:.2f} K")  # ~373.4 K
```

### Calculate nozzle exit velocity and Mach

```python
# Core nozzle: total temp 850 K, total pressure 200 kPa, exit pressure 101 kPa
T_total = 850
P_total = 200000
P_exit = 101325

T_exit, V_exit, M_exit = calc.isentropic_nozzle_expansion(
    T_total, P_total, P_exit, nozzle_efficiency=0.98
)

print(f"Exit temp: {T_exit:.2f} K")
print(f"Exit velocity: {V_exit:.2f} m/s")
print(f"Exit Mach: {M_exit:.4f}")
```

### Calculate fuel-air ratio

```python
T_inlet = 600   # K
T_outlet = 1500  # K (flame temperature)
eta_comb = 0.98

f = calc.fuel_air_ratio_from_temperature_rise(T_inlet, T_outlet, eta_comb)
print(f"Fuel-air ratio: {f:.5f} ({f*100:.2f}%)")
```

---

## References

- **Book:** "Gas Turbine Theory" by Cohen, Rogers, Saravanamuttoo (6th ed.)
- **Standard:** ISO 3977 (Gas Turbines — Nomenclature and Terminology)
- **Values:** ICAO Standard Atmosphere (ISO 2533)
