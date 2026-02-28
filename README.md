---
title: "OpenArcs: An Open-Source Arc Flash Hazard Modeling Library"
authors:
  - name: Shankar Ramharack
    orcid: 0000-0003-3759-7333
    affiliation: "Independent Researcher"
---

# Summary

**OpenArcs** is an open-source Python library for calculating arc flash hazards in industrial electrical systems. It implements the **IEEE 1584-2018 standard** for three-phase AC systems (208 V–15 kV) and provides a reproducible framework for evaluating **incident energy and arc flash boundaries**. OpenArcs is designed for **researchers, engineers, and safety practitioners** who require validated, reproducible calculations for fault and hazard analysis. The library includes modular components, interactive Jupyter notebooks, and unit tests to support reproducibility and extensibility.

# Statement of need

Arc flash is a critical electrical hazard that can cause severe injury or equipment damage. Despite the existence of IEEE 1584-2018, there are **few open-source, research-ready software tools** that allow reproducible calculations of arc flash hazards across industrial settings. Existing solutions are often proprietary, lack reproducibility, or are tied to specific commercial platforms.

**OpenArcs** fills this gap by providing:

- **IEEE 1584-2018 compliant calculations** for incident energy and arc flash boundary.  
- **Open-source, modular Python framework**, enabling reproducibility and integration with other analysis tools.  
- **Validation and test cases** for engineers and researchers to verify calculations.  
- **Extensibility** to future fault scenarios, single-phase AC, and DC systems.  

This software allows both researchers and industrial practitioners to **reproduce hazard assessments, test different scenarios, and benchmark against industry standards**, enhancing safety and reliability in power systems.

# References

1. IEEE Std 1584-2018, "IEEE Guide for Performing Arc-Flash Hazard Calculations," IEEE, 2018.  
2. D. M. Mitra, "Arc Flash Hazard Assessment in Industrial Power Systems," *Electric Power Systems Research*, 2019.  
3. Shankar Ramharack, "OpenArcs GitHub Repository," 2026, [https://github.com/sramharack/OpenArcs](https://github.com/sramharack/OpenArcs)  
4. R. M. Hughes, "Industrial Safety and Electrical Fault Modeling," *Reliability Engineering & System Safety*, 2020.  
