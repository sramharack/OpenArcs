"""
Demonstration: What Pydantic Gives You For Free
================================================

Run this to see the new capabilities of the Pydantic-based UtilitySource.
"""

from components.utility_source import UtilitySource
import json

print("=" * 70)
print("1. BASIC CREATION (same as before)")
print("=" * 70)

source = UtilitySource(
    id="UTIL-001",
    name="Main Utility Feed",
    short_circuit_mva=500.0,
    voltage_nominal=13.8,
    x_r_ratio=15.0
)

print(f"Created: {source}")
print(f"Z_pu = {source.z_pu:.4f} pu")
print(f"Z_ohms = {source.z_ohms:.6f} Ω")


print("\n" + "=" * 70)
print("2. TYPE COERCION (strings become floats automatically)")
print("=" * 70)

# This would FAIL with dataclass, but Pydantic converts automatically
source2 = UtilitySource(
    id="UTIL-002",
    name="From Strings",
    short_circuit_mva="250",      # String!
    voltage_nominal="4.16",       # String!
    x_r_ratio="12"                # String!
)

print(f"Input was strings, but got floats:")
print(f"  short_circuit_mva = {source2.short_circuit_mva} (type: {type(source2.short_circuit_mva).__name__})")
print(f"  voltage_nominal = {source2.voltage_nominal} (type: {type(source2.voltage_nominal).__name__})")


print("\n" + "=" * 70)
print("3. JSON EXPORT (built-in, no extra code)")
print("=" * 70)

json_output = source.model_dump_json(indent=2)
print(json_output)


print("\n" + "=" * 70)
print("4. JSON IMPORT (built-in, no extra code)")
print("=" * 70)

json_input = '''
{
    "id": "UTIL-FROM-JSON",
    "name": "Created from JSON",
    "short_circuit_mva": 350.0,
    "voltage_nominal": 13.8,
    "x_r_ratio": 18.0
}
'''

source_from_json = UtilitySource.model_validate_json(json_input)
print(f"Created from JSON: {source_from_json}")
print(f"  Z_pu = {source_from_json.z_pu:.4f} pu")


print("\n" + "=" * 70)
print("5. DICTIONARY EXPORT (for pandas, databases, etc.)")
print("=" * 70)

data_dict = source.model_dump()
print("As dictionary:")
for key, value in list(data_dict.items())[:8]:  # First 8 items
    print(f"  {key}: {value}")
print("  ...")


print("\n" + "=" * 70)
print("6. VALIDATION ERROR MESSAGES (much better than before)")
print("=" * 70)

print("\nTrying to create with negative MVA:")
try:
    bad_source = UtilitySource(
        id="BAD",
        name="Invalid",
        short_circuit_mva=-500,
        voltage_nominal=13.8,
        x_r_ratio=15
    )
except Exception as e:
    print(f"  Error type: {type(e).__name__}")
    print(f"  Message: {e}")

print("\nTrying to create with X/R ratio too low:")
try:
    bad_source = UtilitySource(
        id="BAD",
        name="Invalid",
        short_circuit_mva=500,
        voltage_nominal=13.8,
        x_r_ratio=0.5  # We set ge=1.0
    )
except Exception as e:
    print(f"  Error type: {type(e).__name__}")
    print(f"  Message: {e}")


print("\n" + "=" * 70)
print("7. JSON SCHEMA (auto-generated documentation)")
print("=" * 70)

schema = UtilitySource.model_json_schema()
print(json.dumps(schema, indent=2)[:1500] + "\n  ... (truncated)")


print("\n" + "=" * 70)
print("8. VALIDATE ASSIGNMENT (catches bad updates)")
print("=" * 70)

print(f"Original short_circuit_mva: {source.short_circuit_mva}")
print("Trying to set it to -100...")
try:
    source.short_circuit_mva = -100
except Exception as e:
    print(f"  Blocked! {type(e).__name__}: {e}")

print(f"Value unchanged: {source.short_circuit_mva}")


print("\n" + "=" * 70)
print("9. COPYING WITH CHANGES")
print("=" * 70)

# Create a copy with some fields changed
source_copy = source.model_copy(update={"short_circuit_mva": 750.0, "name": "Upgraded Feed"})
print(f"Original: {source.short_circuit_mva} MVA, '{source.name}'")
print(f"Copy:     {source_copy.short_circuit_mva} MVA, '{source_copy.name}'")