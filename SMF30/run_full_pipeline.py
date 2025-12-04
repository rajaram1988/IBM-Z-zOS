"""
SMF Type 30 Complete Pipeline
Generates sample records, creates CSV/JSON reports, and produces visualizations
Supports both sample data generation and binary SMF dump file parsing
"""

import sys
from pathlib import Path
from smf30_parser import SMF30Parser
from smf30_analysis import SMF30Analyzer
from smf30_binary_parser import SMFBinaryParser

def main():
    print("\n" + "="*70)
    print("SMF TYPE 30 RECORD ANALYSIS - COMPLETE PIPELINE")
    print("="*70)
    
    # Check if binary dump file is provided
    use_binary = False
    dump_file = None
    
    if len(sys.argv) > 1:
        dump_file = sys.argv[1]
        if Path(dump_file).exists():
            use_binary = True
            print(f"\nUsing binary SMF dump: {dump_file}")
        else:
            print(f"\nWarning: File not found: {dump_file}")
            print("Falling back to sample data generation")
    
    # Step 1: Parse and generate reports
    if use_binary:
        print("\nStep 1: Parsing Binary SMF-30 Dump File")
        print("-" * 70)
        binary_parser = SMFBinaryParser(dump_file)
        records = binary_parser.parse_dump_file()
        
        # Convert to parser format
        parser = SMF30Parser(output_dir="./reports")
        parser.records_by_subtype = records
        parser.generate_all_reports()
    else:
        print("\nStep 1: Generating SMF-30 Sample Records and Reports")
        print("-" * 70)
        parser = SMF30Parser(output_dir="./reports")
        parser.generate_sample_records()
        parser.generate_all_reports()
    
    # Step 2: Generate visualizations and analysis
    print("\nStep 2: Generating Visualizations and Analysis")
    print("-" * 70)
    analyzer = SMF30Analyzer(output_dir="./reports")
    analyzer.load_sample_data()
    analyzer.generate_all_visualizations()
    
    # Final summary
    print("\n" + "="*70)
    print("PIPELINE COMPLETE")
    print("="*70)
    print("\nGenerated Files:")
    print("  Reports:")
    print("    - smf30_subtype1.csv / smf30_subtype1.json  (Job Step Termination)")
    print("    - smf30_subtype2.csv / smf30_subtype2.json  (Job Termination)")
    print("    - smf30_subtype3.csv / smf30_subtype3.json  (Step Initiation)")
    print("    - smf30_subtype4.csv / smf30_subtype4.json  (Job Initiation)")
    print("    - smf30_subtype5.csv / smf30_subtype5.json  (NetStep Completion)")
    print("\n  Visualizations:")
    print("    - smf30_subtype1_analysis.png   (Job Step performance analysis)")
    print("    - smf30_subtype2_analysis.png   (Job-level resource usage)")
    print("    - smf30_subtype3_analysis.png   (Step initialization details)")
    print("    - smf30_subtype4_analysis.png   (Job scheduling details)")
    print("    - smf30_subtype5_analysis.png   (Network performance analysis)")
    print("    - smf30_summary_dashboard.png   (Overall system dashboard)")
    print("\nAll outputs saved to: ./reports/")

if __name__ == "__main__":
    main()
