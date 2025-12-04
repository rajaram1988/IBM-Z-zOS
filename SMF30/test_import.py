#!/usr/bin/env python3
"""Test basic Python functionality and module imports"""

import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

# Try importing our modules
try:
    from smf30_structures import SMF30SampleGenerator
    print("✓ smf30_structures imported successfully")
except Exception as e:
    print(f"✗ Failed to import smf30_structures: {e}")

try:
    from smf30_parser import SMF30Parser
    print("✓ smf30_parser imported successfully")
except Exception as e:
    print(f"✗ Failed to import smf30_parser: {e}")

print("\nTesting sample data generation...")
try:
    records = SMF30SampleGenerator.generate_all_records()
    total = sum(len(r) for r in records.values())
    print(f"✓ Generated {total} sample SMF-30 records across all subtypes")
    for subtype, recs in records.items():
        print(f"  - Subtype {subtype}: {len(recs)} records")
except Exception as e:
    print(f"✗ Sample generation failed: {e}")
