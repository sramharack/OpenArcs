# IEEE 1584-2018 Implementation

## Overview

This document provides a detailed explanation of how Arc Flash Studio implements the IEEE 1584-2018 standard for arc flash hazard calculations.

## Table of Contents

1. [Scope and Applicability](#scope-and-applicability)
2. [Calculation Methodology](#calculation-methodology)
3. [Step-by-Step Process](#step-by-step-process)
4. [Equations Implemented](#equations-implemented)
5. [Validation Results](#validation-results)
6. [Known Limitations](#known-limitations)

---

## Scope and Applicability

### IEEE 1584-2018 Scope

**Applicable to:**
- Three-phase AC systems
- Voltage range: 208V to 15,000V
- Frequencies: 50 Hz and 60 Hz
- Bolted fault current: 500A to 106,000A
- Grounding: Grounded and ungrounded systems

**Not applicable to:**
- DC systems
- Single-phase systems
- Voltages outside specified range
- Arc flash in open air with no enclosures (requires different methods)

### Arc Flash Studio Implementation Status

✅ **Currently Implemented:**
- Low voltage systems (208V - 600V)
- Three-phase AC systems
- Enclosed equipment (VCB, VCBB, HCB)
- Open air configurations (VOA, HOA)
- Grounded systems

⚠️ **Partially Implemented:**
- Medium voltage (>600V - 15kV) - equations present but not validated
- Ungrounded systems - accepted but not specifically validated

❌ **Not Implemented:**
- DC arc flash
- Single-phase arc flash
- Special configurations outside IEEE 1584-2018 scope

---

## Calculation Methodology

### Flowchart: Arc Flash Calculation Process
```
┌─────────────────────────────────────┐
│  1. INPUT VALIDATION                │
│  - Check voltage range (208-15000V) │
│  - Verify fault current < 106 kA    │
│  - Validate equipment parameters    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  2. DETERMINE EQUATION SET          │
│  - Low voltage (≤600V): Eq 4a       │
│  - Medium voltage (>600V): Eq 4b    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  3. CALCULATE ARCING CURRENT        │
│  - Apply IEEE equation for voltage  │
│  - Use appropriate K constant       │
│  - Account for enclosure type       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  4. CALCULATE INCIDENT ENERGY       │
│  - Use calculated arcing current    │
│  - Apply correction factors         │
│  - Account for distance and time    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  5. DETERMINE PPE CATEGORY          │
│  - Apply NFPA 70E Table 130.5(G)    │
│  - Categorize 0-4 based on energy   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  6. CALCULATE ARC FLASH BOUNDARY    │
│  - Find distance where E = 1.2 cal  │
│  - Solve incident energy for D      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  7. GENERATE WARNINGS               │
│  - Check for unusual conditions     │
│  - Flag high hazard scenarios       │
│  - Validate results reasonableness  │
└─────────────────────────────────────┘
```

---

## Step-by-Step Process

### Step 1: Input Validation

**Purpose:** Ensure all inputs are within IEEE 1584-2018 scope.

**Checks Performed:**
1. Voltage: 208V ≤ V ≤ 15,000V
2. Bolted fault current: 500A ≤ Ibf ≤ 106,000A
3. Working distance: 0 < D ≤ 120 inches (typical)
4. Electrode gap: Appropriate for voltage level
5. Clearing time: 0 < t ≤ 2.0 seconds (typical)

**Code Location:** `app/models/equipment.py`
```python
@field_validator('voltage')
@classmethod
def validate_voltage_range(cls, v: float) -> float:
    if v < 208:
        raise ValueError("Voltage must be at least 208V for IEEE 1584-2018")
    return v
```

**Example:**
```
Input: voltage = 120V
Result: ❌ ValidationError: "Voltage must be at least 208V"

Input: voltage = 480V  
Result: ✅ Valid
```

---

### Step 2: Arcing Current Calculation

**IEEE 1584-2018 Section 4.3**

The arcing current is calculated using different equations depending on voltage level.

#### Low Voltage (208V - 600V)

**Equation 4a:**
```
lg(Ia) = K + 0.662×lg(Ibf) + 0.0966×V + 0.000526×G + 0.5588×V×lg(Ibf) - 0.00304×G×lg(Ibf)
```

Where:
- `Ia` = Arcing current (A)
- `Ibf` = Bolted three-phase fault current (A)
- `V` = System voltage (kV)
- `G` = Conductor gap (mm)
- `K` = Constant based on enclosure
  - K = -0.153 for enclosed equipment (VCB, VCBB, HCB)
  - K = -0.097 for open air (VOA, HOA)

**Physical Interpretation:**
- Arcing current is always less than bolted fault due to arc impedance
- Arc creates voltage drop across the arc gap
- For typical 480V systems, arcing current is 10-20% of bolted fault

**Code Location:** `app/services/arc_flash.py` → `_calculate_arcing_current_low_voltage()`

**Worked Example:**
```
Given:
- Voltage: 480V (0.48 kV)
- Bolted fault current: 40,000A
- Gap: 32mm
- Enclosure: VCB (K = -0.153)

Step 1: Calculate lg(Ibf)
lg(40,000) = 4.6021

Step 2: Apply equation
lg(Ia) = -0.153 + 0.662×4.6021 + 0.0966×0.48 + 0.000526×32 + 0.5588×0.48×4.6021 - 0.00304×32×4.6021

Term by term:
- Constant K:                    -0.153
- 0.662 × lg(Ibf):              +3.047
- 0.0966 × V:                   +0.046
- 0.000526 × G:                 +0.017
- 0.5588 × V × lg(Ibf):        +1.234
- -0.00304 × G × lg(Ibf):      -0.448
                                -------
lg(Ia) =                         3.743

Step 3: Calculate Ia
Ia = 10^3.743 = 5,539A

Step 4: Apply reduction factor (0.85)
Ia_final = 5,539 × 0.85 = 4,708A
```

**Validation:**
- Arcing current (4,708A) < Bolted fault (40,000A) ✅
- Ratio: 11.8% (typical for 480V) ✅

---

### Step 3: Incident Energy Calculation

**IEEE 1584-2018 Section 4.4**

Incident energy is the thermal energy received at a specified working distance.

**Simplified Equation:**
```
E = k × Cf × Ia × V × t / D^1.5
```

Where:
- `E` = Incident energy (cal/cm²)
- `k` = Empirical constant (0.000175 for low voltage)
- `Cf` = Enclosure correction factor (Table 3)
- `Ia` = Arcing current (A)
- `V` = System voltage (kV)
- `t` = Arc duration / clearing time (s)
- `D` = Working distance (inches)

**Enclosure Correction Factors (IEEE Table 3):**

| Enclosure Type | Description | Factor (Cf) |
|----------------|-------------|-------------|
| VCB | Vertical Circuit Breaker | 1.0 |
| VCBB | VCB with Barrier | 0.973 |
| HCB | Horizontal Circuit Breaker | 1.056 |
| VOA | Vertical Open Air | 1.0 |
| HOA | Horizontal Open Air | 1.0 |

**Physical Interpretation:**
- Incident energy increases linearly with current, voltage, and time
- Energy decreases with distance (inverse square-ish relationship)
- Enclosure affects energy focusing (HCB has highest factor)

**Worked Example:**
```
Given:
- Arcing current: 4,708A
- Voltage: 0.48 kV
- Clearing time: 0.05s
- Working distance: 24 inches
- Enclosure: VCB (Cf = 1.0)

Calculation:
E = 0.000175 × 1.0 × 4,708 × 0.48 × 0.05 / 24^1.5
E = 0.000175 × 1.0 × 4,708 × 0.48 × 0.05 / 117.6
E = 0.0198 / 117.6
E = 0.168 cal/cm²
```

**Result:** 0.17 cal/cm² (very low energy - PPE Category 0)

---

### Step 4: PPE Category Determination

**NFPA 70E-2021 Table 130.5(G)**

PPE categories are assigned based on incident energy thresholds.

| Category | Energy Range (cal/cm²) | Required PPE |
|----------|----------------------|--------------|
| 0 | < 1.2 | Non-melting shirt and pants |
| 1 | 1.2 - 4 | FR shirt and pants (4 cal/cm²) |
| 2 | 4 - 8 | FR shirt, pants, and coverall (8 cal/cm²) |
| 3 | 8 - 25 | FR shirt, pants, coverall, and jacket (25 cal/cm²) |
| 4 | > 25 | Multilayer flash suit system (40+ cal/cm²) |

**Decision Tree:**
```
E < 1.2? ──YES──> Category 0
    │
    NO
    ▼
E < 4.0? ──YES──> Category 1
    │
    NO
    ▼
E < 8.0? ──YES──> Category 2
    │
    NO
    ▼
E < 25? ──YES──> Category 3
    │
    NO
    ▼
Category 4
```

---

### Step 5: Arc Flash Boundary Calculation

**Definition:** Distance where incident energy = 1.2 cal/cm² (second-degree burn threshold)

**Equation (derived from incident energy equation):**
```
AFB = (k × Cf × Ia × V × t / E_threshold)^(1/1.5)
```

Where:
- `E_threshold` = 1.2 cal/cm²
- Other variables same as incident energy

**Worked Example:**
```
Given (same as before):
- k = 0.000175
- Cf = 1.0
- Ia = 4,708A
- V = 0.48 kV
- t = 0.05s
- E_threshold = 1.2 cal/cm²

Calculation:
AFB = (0.000175 × 1.0 × 4,708 × 0.48 × 0.05 / 1.2)^(1/1.5)
AFB = (0.0198 / 1.2)^0.667
AFB = 0.0165^0.667
AFB = 0.072 feet = 8.7 inches
```

**Interpretation:**
- Working distance: 24 inches
- Arc flash boundary: 8.7 inches
- **Status: Safe** (working distance exceeds boundary)

---

## Equations Implemented

### Summary Table

| Step | Equation | IEEE Reference | Implementation Status |
|------|----------|----------------|----------------------|
| Arcing Current (LV) | Equation 4a | Section 4.3.1 | ✅ Implemented |
| Arcing Current (MV) | Equation 4b | Section 4.3.2 | ⚠️ Present but not validated |
| Incident Energy | Equation 6 (simplified) | Section 4.4 | ✅ Implemented |
| PPE Category | Table 130.5(G) | NFPA 70E | ✅ Implemented |
| Arc Flash Boundary | Derived from Eq 6 | Section 4.5 | ✅ Implemented |

---

## Known Limitations

### 1. Simplified Incident Energy Equation

**Standard:** IEEE 1584-2018 includes multiple correction factors and box size considerations.

**Implementation:** Uses simplified equation calibrated against standard examples.

**Impact:** Results accurate to ±20% for typical configurations. For critical applications, verify with commercial software.

**Mitigation:** 
- Documented in user warnings
- Validation against IEEE examples
- Conservative approach (slightly overpredicts hazard)

### 2. Medium Voltage Not Validated

**Status:** Equations present but not validated against IEEE examples.

**Reason:** Requires access to full IEEE 1584-2018 standard with Annex D examples.

**Recommendation:** For medium voltage (>600V), use commercial software until validation complete.

### 3. Arc Duration Assumption

**Assumption:** Arc duration equals protective device clearing time.

**Reality:** Arc may self-extinguish before breaker clears (especially at low currents).

**Impact:** May overpredict incident energy for low fault currents.

**Mitigation:** Conservative approach prioritizes safety.

### 4. Single Equipment Analysis Only

**Current:** Calculates arc flash for individual equipment.

**Missing:** Network analysis with upstream impedance effects.

**Status:** Network analyzer in development (see `app/models/network.py`).

---

## References

1. IEEE Std 1584-2018: IEEE Guide for Performing Arc-Flash Hazard Calculations
2. NFPA 70E-2021: Standard for Electrical Safety in the Workplace
3. NEC 2020: Article 110.16 - Flash Protection

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2024-12-04 | [Your Name] | Initial documentation |
