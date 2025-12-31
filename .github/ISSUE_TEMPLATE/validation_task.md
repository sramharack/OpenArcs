---
name: Validation Task
about: Validate implementation against IEEE 1584-2018 standard
title: '[VALIDATION] '
labels: validation
assignees: ''
---

## What to Validate
<!-- e.g., "Table 3 coefficients for HCB configuration" -->

## IEEE 1584-2018 Reference
- Section: 
- Page: 
- Equation/Table: 

## Current Implementation
- File: `arc_flash_studio/ieee1584/...`
- Function/Variable: 

## Validation Method
<!-- How will you verify? Hand calculation, Annex D example, commercial software comparison? -->

## Test Case
<!-- If applicable, include input values and expected outputs -->

**Inputs:**
- Ibf = 
- Voc = 
- Gap = 
- Config = 

**Expected Outputs:**
- Iarc = 
- E = 
- AFB = 

## Acceptance Criteria
- [ ] Values match IEEE 1584-2018 exactly
- [ ] Unit test added to `tests/test_ieee1584.py`
- [ ] Edge cases considered
