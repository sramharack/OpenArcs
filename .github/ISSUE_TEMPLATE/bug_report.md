---
name: Bug Report
about: Report incorrect calculation or unexpected behavior
title: '[BUG] '
labels: bug
assignees: ''
---

## Description
<!-- What's wrong? Be specific. -->

## Expected Behavior
<!-- What should happen according to IEEE 1584-2018? -->

## Actual Behavior
<!-- What actually happens? Include actual values. -->

## Steps to Reproduce
```python
from arc_flash_studio.ieee1584 import calculate_arc_flash, ElectrodeConfig

result = calculate_arc_flash(
    ibf_ka=...,
    voc_kv=...,
    # ... minimal example
)
print(result.incident_energy_cal_cm2)
```

## Environment
- Python version: 
- OS: 

## IEEE 1584-2018 Reference
<!-- Section number, equation, table, or Annex reference -->
