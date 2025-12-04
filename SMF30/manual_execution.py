"""
SMF Type 30 - Manual Execution Guide
For systems where Python environment needs to be configured manually
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# ============================================================================
# PART 1: IMPORT ALL REQUIRED COMPONENTS
# ============================================================================

print("=" * 80)
print("SMF TYPE 30 RECORD ANALYSIS - MANUAL EXECUTION")
print("=" * 80)
print(f"\nExecution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}\n")

# Import our custom modules
try:
    from smf30_structures import SMF30SampleGenerator
    print("✓ Loaded SMF-30 record structures")
except ImportError as e:
    print(f"✗ ERROR: Could not import smf30_structures.py")
    print(f"  Make sure the file is in the same directory")
    sys.exit(1)

# ============================================================================
# PART 2: GENERATE SAMPLE RECORDS
# ============================================================================

print("\n" + "-" * 80)
print("STEP 1: Generating Sample SMF-30 Records")
print("-" * 80)

try:
    all_records = SMF30SampleGenerator.generate_all_records()
    print("\n✓ Sample records generated successfully:\n")
    
    for subtype in sorted(all_records.keys()):
        records = all_records[subtype]
        subtype_names = {
            1: "Job Step Termination",
            2: "Job Termination",
            3: "Step Initiation",
            4: "Job Initiation",
            5: "NetStep Completion",
        }
        print(f"  Subtype {subtype} ({subtype_names[subtype]}): {len(records)} records")
    
    total_records = sum(len(r) for r in all_records.values())
    print(f"\n  TOTAL: {total_records} records")
    
except Exception as e:
    print(f"✗ ERROR generating records: {e}")
    sys.exit(1)

# ============================================================================
# PART 3: CREATE REPORTS DIRECTORY
# ============================================================================

print("\n" + "-" * 80)
print("STEP 2: Setting up Reports Directory")
print("-" * 80)

reports_dir = Path("./reports")
try:
    reports_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Reports directory ready: {reports_dir.absolute()}")
except Exception as e:
    print(f"✗ ERROR creating reports directory: {e}")
    sys.exit(1)

# ============================================================================
# PART 4: GENERATE CSV REPORTS
# ============================================================================

print("\n" + "-" * 80)
print("STEP 3: Generating CSV Reports")
print("-" * 80)

import csv
from datetime import datetime

subtype_names = {
    1: "Job Step Termination",
    2: "Job Termination",
    3: "Step Initiation",
    4: "Job Initiation",
    5: "NetStep Completion",
}

for subtype, records in sorted(all_records.items()):
    try:
        # Convert to dict format
        records_dict = [r.to_dict() for r in records]
        
        # Get fieldnames from first record
        if records_dict:
            fieldnames = list(records_dict[0].keys())
            
            # Write CSV
            csv_path = reports_dir / f"smf30_subtype{subtype}.csv"
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records_dict)
            
            print(f"✓ Subtype {subtype}: {csv_path.name} ({len(records_dict)} records)")
    
    except Exception as e:
        print(f"✗ ERROR for subtype {subtype}: {e}")

# ============================================================================
# PART 5: GENERATE JSON REPORTS
# ============================================================================

print("\n" + "-" * 80)
print("STEP 4: Generating JSON Reports")
print("-" * 80)

import json

for subtype, records in sorted(all_records.items()):
    try:
        # Convert to dict format
        records_dict = [r.to_dict() for r in records]
        
        # Write JSON
        json_path = reports_dir / f"smf30_subtype{subtype}.json"
        with open(json_path, 'w') as f:
            json.dump(records_dict, f, indent=2, default=str)
        
        print(f"✓ Subtype {subtype}: {json_path.name}")
    
    except Exception as e:
        print(f"✗ ERROR for subtype {subtype}: {e}")

# ============================================================================
# PART 6: DISPLAY STATISTICAL SUMMARIES
# ============================================================================

print("\n" + "-" * 80)
print("STEP 5: Statistical Summaries")
print("-" * 80)

def print_subtype_summary(subtype, records):
    """Print summary statistics for a subtype"""
    if not records:
        return
    
    records_dict = [r.to_dict() for r in records]
    
    print(f"\n  Subtype {subtype}: {subtype_names[subtype]}")
    print(f"  {'─' * 70}")
    print(f"    Record Count: {len(records_dict)}")
    
    # Sample data from first record
    first = records_dict[0]
    print(f"    Sample Fields: {', '.join(list(first.keys())[:6])}...")
    
    # CPU time stats (if available)
    if 'cpu_time_ms' in first:
        cpu_times = [r.get('cpu_time_ms', 0) for r in records_dict]
        print(f"    CPU Time Stats (ms): min={min(cpu_times)}, max={max(cpu_times)}, avg={sum(cpu_times)//len(cpu_times)}")
    
    # Memory stats (if available)
    if 'memory_allocated_mb' in first:
        mems = [r.get('memory_allocated_mb', 0) for r in records_dict]
        print(f"    Memory Stats (MB): min={min(mems)}, max={max(mems)}, avg={sum(mems)//len(mems)}")
    
    # Success rate (if available)
    if 'return_code' in first:
        success = sum(1 for r in records_dict if r.get('return_code', 0) == 0)
        success_rate = (success / len(records_dict) * 100) if records_dict else 0
        print(f"    Success Rate: {success}/{len(records_dict)} ({success_rate:.1f}%)")

for subtype in sorted(all_records.keys()):
    print_subtype_summary(subtype, all_records[subtype])

# ============================================================================
# PART 7: DISPLAY DETAILED SAMPLE RECORDS
# ============================================================================

print("\n" + "-" * 80)
print("STEP 6: Sample Records Detail")
print("-" * 80)

def print_record_detail(subtype, record, index):
    """Print detailed information for a record"""
    record_dict = record.to_dict()
    print(f"\n  Record {index + 1}:")
    for key, value in list(record_dict.items())[:10]:  # First 10 fields
        print(f"    {key}: {value}")
    if len(record_dict) > 10:
        print(f"    ... and {len(record_dict) - 10} more fields")

# Show one sample record per subtype
for subtype in [1, 2, 5]:  # Show subtypes with most detailed data
    if subtype in all_records and all_records[subtype]:
        print(f"\n  Subtype {subtype} - Sample Record:")
        record = all_records[subtype][0]
        for key, value in list(record.to_dict().items())[:8]:
            print(f"    {key}: {value}")

# ============================================================================
# PART 8: FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("GENERATION COMPLETE")
print("=" * 80)

print("\nGenerated Files:")
print("  CSV Reports:")
for i in range(1, 6):
    csv_file = reports_dir / f"smf30_subtype{i}.csv"
    if csv_file.exists():
        size_kb = csv_file.stat().st_size / 1024
        print(f"    ✓ {csv_file.name} ({size_kb:.1f} KB)")

print("\n  JSON Reports:")
for i in range(1, 6):
    json_file = reports_dir / f"smf30_subtype{i}.json"
    if json_file.exists():
        size_kb = json_file.stat().st_size / 1024
        print(f"    ✓ {json_file.name} ({size_kb:.1f} KB)")

print(f"\nAll reports saved to: {reports_dir.absolute()}")

# ============================================================================
# PART 9: VISUALIZATION INSTRUCTIONS
# ============================================================================

print("\n" + "=" * 80)
print("NEXT STEPS: Visualizations")
print("=" * 80)

print("""
To generate charts and visualizations, install matplotlib:

  pip install matplotlib pandas numpy

Then run the analysis:

  python smf30_analysis.py

This will create PNG charts for each subtype showing:
  - Subtype 1: CPU time, IO counts, return codes, resource usage
  - Subtype 2: Total resources, memory efficiency, success rates
  - Subtype 3: Step initialization patterns, memory allocation
  - Subtype 4: Job scheduling, priority distribution
  - Subtype 5: Network performance, data transfer efficiency
  - Summary: Cross-subtype dashboard
""")

print("=" * 80)
print(f"Execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
