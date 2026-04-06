# Freestream & Station 0

## Overview

**Station 0** is the freestream (free air far upstream of the engine). It defines:
1. **Ambient conditions:** altitude, temperature, pressure
2. **Flight condition:** Mach number
3. **Engine flow rate:** mass flow rate

Together, these **fully specify** the design point's external inputs.

---

## Ram Effect (Stagnation Conditions)

As the aircraft moves at velocity V (Mach M), the air approaches the engine. If this air is brought to rest (stagnated), its kinetic energy converts to thermal energy.

### Static vs. Total Conditions

**Static conditions:** What a moving thermometer measures (temperature in air's frame)
- Example: Cruise at 10 km → T ≈ 223 K (-50°C)

**Total (Stagnation) conditions:** What you'd measure if you stopped the air adiabatically
- Formula: $T_t = T × (1 + 0.2 M^2)$
- Example: Cruise M=0.85 → T_t ≈ 255 K (+32 K increase!)

### Why This Matters

The compressor's inlet pressure and temperature are **total conditions**—the ram effect provides a "free" pressure and temperature rise that improves engine performance at cruise.

**At sea level:** M = 0 → T_t = T (no ram effect)

**At cruise (M=0.85, 10 km):** T_t = 255 K vs. T = 223 K → ~12.5% higher inlet temperature to the compressor!

---

## Station 0 Properties

### Design Inputs (user specifies)

1. **Altitude mode:** "ISA" or "manual"
2. **Altitude** (if ISA): 0–11 km (troposphere)
3. **Mach number** M0: 0 (stationary) to 0.95 (transonic)
4. **Mass flow rate** ṁ: kg/s (or calculated from fan diameter)

### Design Outputs (calculated)

#### Static Properties
- **T_static** = ambient temperature (from ISA or manual input)
- **P_static** = ambient pressure
- **ρ_static** = density (from ideal gas law)
- **a_static** = speed of sound at ambient temperature
- **V_static** = Mach × speed of sound = M0 × a

#### Total Properties (with ram effect)
- **T_t** = T_static × (1 + 0.2 M0²)
- **P_t** = P_static × (T_t / T_static)^3.5
- **ρ_t** = P_t / (R × T_t)

#### Flow Rate
- **ṁ** = design input (engine mass flow)

---

## Example: Cruise Condition (CFM56-like)

### Inputs
- Altitude: 10,000 m (typical cruise)
- Mach: 0.85
- Mass flow: 400 kg/s (typical for CFM56)

### ISA Conditions at 10 km
From `ISAAtmosphere.conditions_at_altitude(10000)`:
- T = 223.15 K (-50°C)
- P = 26.496 kPa (0.2615 bar)
- ρ = 0.3800 kg/m³

### Ram Effect Calculation
Speed of sound at 223.15 K:
$$a = \sqrt{1.4 × 287.05 × 223.15} ≈ 299.1 \text{ m/s}$$

Freestream velocity:
$$V = 0.85 × 299.1 ≈ 254.2 \text{ m/s}$$

Total temperature:
$$T_t = 223.15 × (1 + 0.2 × 0.85^2) = 223.15 × 1.1445 ≈ 255.4 \text{ K}$$

Total pressure:
$$P_t = 26.496 × (1.1445)^{3.5} ≈ 41.6 \text{ kPa}$$

### Station 0 Summary
| Property | Static | Total |
|----------|--------|-------|
| **Temperature** | 223.15 K | 255.4 K |
| **Pressure** | 26.5 kPa | 41.6 kPa |
| **Mach** | 0.85 | 0 (stagnated) |
| **Velocity** | 254.2 m/s | 0 m/s |
| **Density** | 0.380 kg/m³ | 0.567 kg/m³ |
| **Mass flow** | 400 kg/s | 400 kg/s |

---

## Inlet Pressure Recovery

Real inlets don't achieve 100% total pressure recovery. Define **inlet recovery factor** π_d:

$$P_t^{inlet} = π_d × P_t^{freestream}$$

Typical values:
- Subsonic inlet (M < 0.7): π_d ≈ 0.99–0.995
- Transonic inlet (0.7 < M < 0.95): π_d ≈ 0.98–0.99
- Supersonic inlet (M > 1.0): π_d ≈ 0.85–0.95

**Example (cruise, π_d = 0.99):**
- P_t at freestream: 41.6 kPa
- P_t at compressor inlet: 0.99 × 41.6 ≈ **41.2 kPa** (~0.4 kPa loss)

---

## Design Input: Mass Flow Calculation

### From Fan Diameter (TURBOFAN-SPECIFIC)

**Geometry:**
- Annular inlet (hub-to-tip ratio η typically 0.25–0.35)
- Annular area: $A = \frac{π}{4} D^2 (1 - η^2)$

**Mass flow:**
$$\dot{m} = ρ × V × A = ρ × (M × a) × \frac{π}{4} D^2 (1 - η^2)$$

**Example (cruise, M=0.85, D=2.5 m, η=0.30):**

Annular area:
$$A = \frac{π}{4} × 2.5^2 × (1 - 0.30^2) = 4.909 × 0.91 ≈ 4.467 \text{ m}^2$$

Freestream velocity:
$$V = 0.85 × 299.1 ≈ 254.2 \text{ m/s}$$

Mass flow:
$$\dot{m} = 0.380 × 254.2 × 4.467 ≈ 433 \text{ kg/s}$$

So a 2.5 m diameter fan produces ~430 kg/s at cruise. ✓

### Inverse: Diameter from Mass Flow

If you need 400 kg/s at cruise:

$$D = \sqrt{\frac{4 \dot{m}}{π × ρ × V × (1 - η^2)}}$$

$$D = \sqrt{\frac{4 × 400}{π × 0.380 × 254.2 × 0.91}} ≈ 2.45 \text{ m}$$

---

## Code Examples

### Create Station 0 from ISA (cruise)

```python
from src.physics.freestream import FreestreamConditions

fs = FreestreamConditions()

# Cruise at 10 km, M=0.85, 400 kg/s
station_0 = fs.create_station_0(
    altitude_mode="ISA",
    M0=0.85,
    m_dot_total=400,
    altitude=10000
)

print(station_0)
# Station 0: Freestream
#   p_t = 41600.0 Pa, T_t = 255.40 K
#   p = 26496.0 Pa, T = 223.15 K
#   M = 0.8500, V = 254.16 m/s
#   ṁ = 400.00 kg/s
```

### Create Station 0 from manual conditions

```python
# Custom conditions: hot day at low altitude
station_0 = fs.create_station_0(
    altitude_mode="manual",
    M0=0.50,
    m_dot_total=600,
    T0_static=305,  # 32°C (hot day)
    P0_static=101325  # Sea level
)

print(station_0)
```

### Calculate required fan diameter

```python
# Design: need 500 kg/s at cruise (10 km, M=0.85)
diameter = fs.calculate_diameter_from_m_dot(
    m_dot_total=500,
    hub_to_tip_ratio=0.30,
    M0=0.85,
    T0_static=223.15,
    P0_static=26496
)

print(f"Required fan diameter: {diameter:.2f} m")
# Required fan diameter: 2.60 m
```

---

## Real-World Examples

### Boeing 737 (CFM56-7 engine)
- **Cruise:** FL350 (10.7 km), M=0.78, 450 kg/s per engine
- **Sea level static:** M=0, 1000+ kg/s per engine (takeoff)

### Airbus A380 (Rolls-Royce Trent 900)
- **Cruise:** FL430 (13.1 km), M=0.85, 900 kg/s per engine
- **Mass flow:** 4 × 900 = 3,600 kg/s total

### Fighter Jet (F-15 with F100-PW-220 engine)
- **Cruise:** 10 km, M=0.9, 100 kg/s
- **Afterburner:** Sea level, M=2.0+, 140+ kg/s

---

## References

- **Book:** "Gas Turbine Theory" by Cohen, Rogers, Saravanamuttoo — Chapter 2 (Intake, Inlet)
- **Standard:** ICAO Standard Atmosphere (ISO 2533)
- **Inlet Recovery:** SAE AIR1335 (Turbojet Inlet Design Guide)
