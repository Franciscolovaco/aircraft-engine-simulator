# Thermodynamic Station Properties

## Overview

Each station in the engine cycle has a set of thermodynamic properties that define its state. This document defines each property and shows relationships.

---

## Property Classification

### Total (Stagnation) Properties

**Total Temperature** ($T_t$ or $T^0$):
- Temperature if air were brought to rest **adiabatically** (zero velocity)
- Units: Kelvin (K)
- Role: Constant through isentropic processes → fundamental for design
- Example: Freestream M=0.85 at 223 K → $T_t$ ≈ 255 K

**Total Pressure** ($P_t$ or $P^0$):
- Pressure if air were brought to rest isentropically
- Units: Pascals (Pa) or bar
- Role: Constant through isentropic processes
- Decreases only with friction/heat transfer

### Static Properties

**Static Temperature** ($T$):
- Thermometer reading (temperature in air's reference frame)
- Units: Kelvin (K)
- Example: At cruise (10 km), T ≈ 223 K (very cold!)

**Static Pressure** ($P$):
- Pressure measured by a sensor moving with the air
- Units: Pascals (Pa)
- Example: At cruise (10 km), P ≈ 26.5 kPa (1/4 sea-level)

### Flow Properties

**Mach Number** ($M$):
- Dimensionless velocity ratio: $M = V / a$
- Ranges: 0 (stationary) → 1 (sonic) → >1 (supersonic)
- Typical values: Cruise M ≈ 0.85, compressor outlet M ≈ 0.2–0.4

**Velocity** ($V$):
- Air velocity in reference frame
- Units: m/s
- Typical values: Freestream M=0.85 at cruise → V ≈ 254 m/s

**Speed of Sound** ($a$):
- Propagation speed of pressure waves: $a = \sqrt{γ × R × T}$
- Units: m/s
- Depends on temperature only
- Example: At 288.15 K (sea level), a ≈ 661 m/s

### Mass Flow Properties

**Mass Flow Rate** ($\dot{m}$):
- Mass of air per unit time: $\dot{m} = ρ × V × A$
- Units: kg/s
- Conservation: $\dot{m}$ constant through engine (continuity equation)
- Typical: Commercial turbofan ≈ 300–900 kg/s

**Density** ($ρ$):
- From ideal gas law: $ρ = P / (R × T)$
- Units: kg/m³
- Typical: Sea level ≈ 1.225 kg/m³, cruise (10 km) ≈ 0.38 kg/m³

### Derived Properties

**Total Enthalpy** ($h_t$):
- $h_t = c_p × T_t$
- Role: Constant through adiabatic processes (energy balance)
- Units: J/kg

**Entropy** ($s$):
- Increases through irreversible processes (compressor/turbine)
- Units: J/(kg·K)
- Isentropic process: Δs = 0

**Fuel-Air Ratio** ($f$):
- Mass fraction: f = m_fuel / m_air
- Range: 0 (no combustion) → 0.05 (peak efficiency) → 0.08 (max thrust)
- Defined from station 3 (combustor inlet) onwards

---

## European Turbofan Station Numbering (TURBOFAN-SPECIFIC)

```
Station 0: Freestream (far upstream)
    ↓
Station 1: Inlet exit
    ↓
Station 2: Fan inlet (core flow splitter)
    ↓
Station 2.5: Fan exit (bifurcation point)
    ├→ CORE: Station 3 (HPC inlet)
    │   ├→ Station 4 (HPC exit / Combustor inlet)
    │   ├→ Station 5 (Combustor exit / HPT inlet)
    │   ├→ Station 6 (HPT exit / LPT inlet)
    │   ├→ Station 7 (LPT exit)
    │   └→ Station 8 (Core nozzle exit)
    └→ BYPASS: Station 13 (Bypass duct exit)
        └→ Station 19 (Bypass nozzle exit)
```

---

## Station Definitions

### Station 0: Freestream
- **Location:** Far upstream, unaffected by engine inlet
- **Properties:**
  - Static: ambient T, P at freestream
  - Total: T_t, P_t (with ram effect at M > 0)
  - Flow: M (freestream Mach)
  - Mass flow: design input
- **Role:** Design input; defines ambient condition
- **Typical Values (cruise at 10 km, M=0.85):**
  - T = 223.15 K, P = 26.5 kPa
  - T_t ≈ 255 K, P_t ≈ 41.6 kPa
  - V ≈ 254 m/s

### Station 1: Inlet Exit
- **Location:** After inlet duct, before fan
- **Properties:**
  - Total: T_t ≈ T_t0 (adiabatic), P_t < P_t0 (pressure recovery loss)
  - Static: T ≈ T0, P ≈ P0 (approximately)
- **Role:** Feed to fan with small pressure loss
- **Typical Values:**
  - P_t ≈ 0.99 × P_t0 (inlet recovery factor ≈ 0.99)
  - M ≈ 0.5–0.6 (slowed slightly by inlet)

### Station 2: Fan Inlet
- **Location:** At core compressor inlet (after fan inlet geometry)
- **Role:** Where compressor core flow begins
- **Properties:** Similar to Station 1 (upstream of fan)

### Station 2.5: Fan Exit (Bifurcation)
- **Location:** After fan, flow splits to core and bypass
- **Properties:**
  - Total: T_t2.5, P_t2.5 (increased by fan compression)
  - Static: M2.5 ≈ 0.4–0.5 (subsonic after fan)
- **Role:** Split point; divides flow into core and bypass
- **Typical Values (PR_fan ≈ 2.2):**
  - T_t ≈ 377 K, P_t ≈ 2.2 × P_t1
  - Core mass flow: ~25% of total (bypass ratio ~4)
  - Bypass mass flow: ~75% of total

### Station 3: HPC Inlet (High-Pressure Compressor)
- **Location:** Core compressor inlet (from bifurcation)
- **Properties:** Same as Station 2.5 core flow
- **Role:** Feed to high-pressure compressor

### Station 4: HPC Exit / Combustor Inlet
- **Location:** After HPC, before combustor
- **Properties:**
  - Total: T_t4 elevated from compression
  - Static: M4 ≈ 0.2–0.3 (decelerated before combustor)
- **Typical Values (HPC PR ≈ 9.7):**
  - T_t ≈ 813 K, P_t ≈ 37 bar
  - T ≈ 600–650 K (static)

### Station 5: Combustor Exit / HPT Inlet
- **Location:** After combustion, before HPT
- **Properties:**
  - Total: T_t5 elevated by heat release (peak temperature point)
  - **Constraint:** T_t5 limited by turbine blade materials (~1700 K for commercial engines)
  - **Fuel-air ratio:** Calculated to achieve desired T_t5
- **Typical Values (Commercial turbofan):**
  - T_t ≈ 1690 K (design point limit)
  - P_t ≈ 36.5 bar (combustor pressure loss ~1% to 2%)
  - Fuel-air ratio: ~0.022 (2.2% fuel by mass)

### Station 6: HPT Exit / LPT Inlet
- **Location:** After HPT, before LPT
- **Properties:**
  - Total: T_t6 reduced by turbine expansion
  - Pressure ratio: Determined by power balance (HPT work = HPC work)
- **Typical Values:**
  - T_t ≈ 1068 K, P_t ≈ 9.5 bar

### Station 7: LPT Exit
- **Location:** After LPT
- **Properties:**
  - Total: T_t7 further reduced
  - Pressure ratio: Determined by power balance (LPT work = Fan work)
- **Typical Values:**
  - T_t ≈ 400 K, P_t ≈ 2.0 bar

### Station 8/9: Core Nozzle Exit
- **Location:** After core nozzle (downstream exhaust)
- **Properties:**
  - Total at inlet: T_t, P_t from Station 7
  - Static at exit: T8, P8 ≈ P_atm (ambient)
  - Velocity: V8 calculated from expansion
  - Mach: M8 subsonic (typical) to sonic (choked)
- **Typical Values (at sea level):**
  - V8 ≈ 515–600 m/s (subsonic for takeoff, sonic for cruise)
  - M8 ≈ 0.9–1.0

### Station 13: Bypass Duct Exit
- **Location:** After bypass duct (minimal temperature change)
- **Properties:**
  - Total: T_t13 ≈ T_t2.5 (adiabatic duct, small loss)
  - Pressure: P_t13 slightly reduced (friction loss ~1%)
  - Static: M13 ≈ 0.3–0.4 (subsonic)
- **Typical Values:**
  - T_t ≈ 377 K (same as fan exit)
  - P_t ≈ 2.14 bar

### Station 19: Bypass Nozzle Exit
- **Location:** After bypass nozzle (exhaust)
- **Properties:**
  - Total: T_t from Station 13
  - Static at exit: T19 ≈ 300 K (subsonic)
  - Velocity: V19 ≈ 200–300 m/s
  - Mach: M19 subsonic (typically 0.4–0.6)
- **Role:** Low-speed exhaust (high bypass ratio favors cold thrust)
- **Typical Values:**
  - V19 ≈ 200–300 m/s
  - Thrust from bypass: ~80% of total (modern turbofans)

---

## Property Relationships

### Static ↔ Total (Mach known)

$$T_t = T × \left(1 + \frac{\gamma-1}{2} M^2\right)$$

$$P_t = P × \left(1 + \frac{\gamma-1}{2} M^2\right)^{\gamma/(\gamma-1)}$$

Inverse:

$$T = T_t / \left(1 + \frac{\gamma-1}{2} M^2\right)$$

$$P = P_t / \left(1 + \frac{\gamma-1}{2} M^2\right)^{\gamma/(\gamma-1)}$$

### Temperature ↔ Velocity (adiabatic, no heat transfer)

$$V = \sqrt{2 c_p (T_t - T)}$$

Or equivalently:

$$M = \sqrt{\frac{2}{\gamma - 1} \left[\left(\frac{T_t}{T}\right) - 1\right]}$$

### Density (ideal gas law)

$$ρ = \frac{P}{R T}$$

### Continuity (mass flow conservation)

$$\dot{m} = ρ × V × A = \text{constant}$$

---

## Code Examples

### Access station properties

```python
from src.physics.stations import ThermodynamicStation

station_5 = ThermodynamicStation(
    station_id="5",
    name="Combustor Exit",
    p_t=36.5e5,      # Pa
    T_t=1690,        # K
    m_dot=100,       # kg/s
    fuel_air_ratio=0.0220
)

print(f"Total pressure: {station_5.p_t / 1e5:.1f} bar")
print(f"Total temperature: {station_5.T_t:.0f} K")
print(f"Mass flow: {station_5.m_dot:.0f} kg/s")
print(f"FAR: {station_5.fuel_air_ratio:.4f}")

# Calculate static properties if we know Mach
station_5.M = 0.25  # subsonic in combustor

# Speed of sound
station_5.calculate_speed_of_sound()
print(f"Speed of sound: {station_5.a:.0f} m/s")

# Static temperature (from Mach)
from src.physics.thermodynamics import ThermodynamicsCalculator
calc = ThermodynamicsCalculator()
T_t_to_T_ratio = calc.total_temperature_ratio_from_mach(0.25)
station_5.T = station_5.T_t / T_t_to_T_ratio
print(f"Static temperature: {station_5.T:.0f} K")

# Velocity
station_5.V = station_5.M * station_5.a
print(f"Velocity: {station_5.V:.0f} m/s")
```
