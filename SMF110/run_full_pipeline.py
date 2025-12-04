"""
SMF Type 110 CICS Complete Pipeline Runner
Orchestrates parsing, report generation, and visualization
"""

import sys
from pathlib import Path

from smf110_structures import SMF110SampleGenerator
from smf110_parser import SMF110ReportGenerator
from smf110_analysis import SMF110Visualizer

def run_full_pipeline_sample():
    """Run complete pipeline with sample data"""
    print("="*70)
    print("SMF TYPE 110 CICS STATISTICS ANALYSIS - SAMPLE DATA MODE")
    print("="*70)
    
    print("\n[1/3] Generating Sample CICS Statistics Records...")
    type1_records = SMF110SampleGenerator.generate_type1_records(15)
    type2_records = SMF110SampleGenerator.generate_type2_records(10)
    type3_records = SMF110SampleGenerator.generate_type3_records(12)
    type4_records = SMF110SampleGenerator.generate_type4_records(8)
    type5_records = SMF110SampleGenerator.generate_type5_records(6)
    
    total_records = (len(type1_records) + len(type2_records) + 
                    len(type3_records) + len(type4_records) + len(type5_records))
    print(f"[OK] Generated {total_records} sample records")
    print(f"  - Subtype 1 (Transactions): {len(type1_records)} records")
    print(f"  - Subtype 2 (Files): {len(type2_records)} records")
    print(f"  - Subtype 3 (Programs): {len(type3_records)} records")
    print(f"  - Subtype 4 (Terminals): {len(type4_records)} records")
    print(f"  - Subtype 5 (Storage): {len(type5_records)} records")
    
    print("\n[2/3] Generating CSV and JSON Reports...")
    generator = SMF110ReportGenerator()
    generator.generate_all_reports(
        type1_records,
        type2_records,
        type3_records,
        type4_records,
        type5_records
    )
    
    print("\n[3/3] Creating Visualizations...")
    visualizer = SMF110Visualizer()
    visualizer.generate_all_visualizations(
        type1_records,
        type2_records,
        type3_records,
        type4_records,
        type5_records
    )
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nGenerated Files:")
    print("  CSV Reports:")
    print("    - smf110_subtype1_transactions.csv")
    print("    - smf110_subtype2_files.csv")
    print("    - smf110_subtype3_programs.csv")
    print("    - smf110_subtype4_terminals.csv")
    print("    - smf110_subtype5_storage.csv")
    print("\n  JSON Reports:")
    print("    - smf110_subtype1_transactions.json")
    print("    - smf110_subtype2_files.json")
    print("    - smf110_subtype3_programs.json")
    print("    - smf110_subtype4_terminals.json")
    print("    - smf110_subtype5_storage.json")
    print("\n  Visualizations:")
    print("    - smf110_subtype1_transactions_analysis.png")
    print("    - smf110_subtype2_files_analysis.png")
    print("    - smf110_subtype3_programs_analysis.png")
    print("    - smf110_subtype4_terminals_analysis.png")
    print("    - smf110_subtype5_storage_analysis.png")
    print("    - smf110_summary_dashboard.png")
    print("="*70)

def run_full_pipeline_binary(dump_file: str):
    """Run complete pipeline with binary dump file"""
    print("="*70)
    print("SMF TYPE 110 CICS STATISTICS ANALYSIS - BINARY DUMP MODE")
    print("="*70)
    print(f"\nInput file: {dump_file}")
    
    dump_path = Path(dump_file)
    if not dump_path.exists():
        print(f"[ERROR] Dump file not found: {dump_file}")
        return
    
    print("\n[1/3] Parsing Binary SMF 110 Dump File...")
    print("[INFO] Binary parser not yet implemented for SMF 110")
    print("[INFO] Using sample data instead...")
    
    # TODO: Implement binary parser
    # For now, fall back to sample data
    run_full_pipeline_sample()

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Binary dump file provided
        dump_file = sys.argv[1]
        run_full_pipeline_binary(dump_file)
    else:
        # Use sample data
        run_full_pipeline_sample()

if __name__ == "__main__":
    main()
