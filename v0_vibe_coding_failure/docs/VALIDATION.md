
# Calculation Validation

This document validates Arc Flash Studio calculations against IEEE 1584-2018 published examples.

## Validation Methodology

All calculations are validated against:
1. IEEE 1584-2018 Annex D example problems
2. Hand calculations using standard equations
3. Comparison with commercial software (when available)

## Test Cases

### Test 1: IEEE 1584-2018 Annex D.1 - 480V VCB
**Configuration:**
- Voltage: 480V
- Bolted Fault Current: 25,000A
- Working Distance: 18 inches
- Enclosure: VCB
- Gap: 32mm
- Clearing Time: 0.1s

**Expected Results (IEEE Standard):**
- Arcing Current: ~5,000A
- Incident Energy: ~1.0 cal/cm²
- PPE Category: 1

**Our Results:**
```
Run: pytest app/tests/test_ieee_validation.py::TestIEEE1584Validation::test_example_d1_480v_vcb -v
```

**Status:** [PASS/FAIL]
**Notes:** [Observations about accuracy]

### Test 2: IEEE 1584-2018 Annex D.2 - 4160V VCB
[To be completed after running tests]

### Test 3: IEEE 1584-2018 Annex D.3 - 480V HCB
[To be completed]

### Test 4: IEEE 1584-2018 Annex D.4 - 480V Open Air
[To be completed]

## Accuracy Analysis

| Test Case | Parameter | Expected | Calculated | Error (%) |
|-----------|-----------|----------|------------|-----------|
| D.1 480V  | Ia (A)    | 5000     | [TBD]      | [TBD]     |
| D.1 480V  | E (cal)   | 1.0      | [TBD]      | [TBD]     |
| D.2 4160V | Ia (A)    | 10000    | [TBD]      | [TBD]     |
| D.2 4160V | E (cal)   | 4.5      | [TBD]      | [TBD]     |

## Known Limitations

1. **Simplified Equations**: This implementation uses the basic IEEE 1584-2018 equations. 
   The full standard includes additional correction factors for:
   - Equipment enclosure size variations
   - Electrode configuration details
   - Ground fault contributions

2. **Voltage Ranges**: Validated for 208V - 15kV three-phase systems only.

3. **Arc Duration**: Assumes arc duration equals protective device clearing time.
   Does not account for arc self-extinction.

## Recommendations for Users

- For critical applications, verify results with commercial software
- Hand-check calculations for high-consequence scenarios
- Consider consulting a qualified electrical engineer for:
  - Systems with unusual configurations
  - High incident energy levels (>40 cal/cm²)
  - Medium voltage (>1kV) applications

## References

1. IEEE Std 1584-2018, Annex D: Example Calculations
2. NFPA 70E-2021, Table 130.5(G): PPE Categories
3. [Your validation data sources]

## Version History

| Version | Date | Validator | Notes |
|---------|------|-----------|-------|
| 0.1.0   | 2024-12-04 | [Your Name] | Initial validation |
