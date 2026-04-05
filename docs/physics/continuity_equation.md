# Continuity Equation (Mass Flow Conservation)

## Physical Concept

The continuity equation is a statement of mass conservation: **mass cannot be created or destroyed** in a flow.

At any cross-section of the flow, the amount of mass entering per unit time equals the amount leaving per unit time.

## Formula

$$\dot{m} = \rho \times V \times A$$

Where:
- **ṁ** = mass flow rate (kg/s)
- **ρ** = air density at that section (kg/m³)
- **V** = velocity at that section (m/s)
- **A** = cross-sectional area (m²)

## Physical Interpretation

Think of it as:
- **ρ × A** = mass per unit length of the flow column
- **V** = how fast that column moves (length per unit time)
- **ṁ = (mass/length) × (length/time) = mass/time**

## Where It's Used

### Engine Cycle
- **Station 0 (Freestream):** ṁ = ρ₀ × V₀ × A₀
  - Entry point into the engine
  - Calculated from ambient conditions and aircraft Mach
  
- **Station 2 (Fan inlet):** ṁ = ρ₂ × V₂ × A₂
  - After inlet recovery
  - Density slightly different due to deceleration
  
- **Station 2.5 (Fan exit):** ṁ = ṁ_bypass + ṁ_core
  - Splits into two streams
  
- **Entire engine:** ṁ is constant (no fuel added until combustor)

### Key Insight
In a turbofan engine, the mass flow through each station is **the same** (continuity). However:
- Density changes (pressure and temperature change)
- Velocity changes (Mach number changes)
- Area changes to maintain constant ṁ

## Code Implementation

**Location:** `src/physics/thermodynamics.py`

```python
def mass_flow_from_continuity(self, density: float, velocity: float, area: float) -> float:
    """Calculate mass flow rate from continuity equation: ṁ = ρ × V × A"""
    # Validation...
    return density * velocity * area
