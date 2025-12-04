"""
SMF Type 110 CICS Report Generator
Generates CSV and JSON reports for SMF 110 CICS statistics records
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any
from smf110_structures import (
    SMF110Type1, SMF110Type2, SMF110Type3, SMF110Type4, SMF110Type5
)

class SMF110ReportGenerator:
    """Generate CSV and JSON reports for SMF 110 CICS records"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save_csv_report(self, records: List[Any], subtype: int, filename: str):
        """Save records to CSV file"""
        if not records:
            print(f"No records to save for subtype {subtype}")
            return
        
        filepath = self.output_dir / filename
        
        # Convert all records to dictionaries
        dict_records = [rec.to_dict() for rec in records]
        
        # Get field names from first record
        fieldnames = list(dict_records[0].keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(dict_records)
        
        print(f"[OK] Saved {len(records)} records to {filepath}")
    
    def save_json_report(self, records: List[Any], subtype: int, filename: str):
        """Save records to JSON file"""
        if not records:
            print(f"No records to save for subtype {subtype}")
            return
        
        filepath = self.output_dir / filename
        
        # Convert all records to dictionaries
        dict_records = [rec.to_dict() for rec in records]
        
        # Create summary statistics
        report = {
            'summary': {
                'record_type': 110,
                'subtype': subtype,
                'total_records': len(records),
                'generated_at': dict_records[0]['timestamp'] if dict_records else None,
            },
            'records': dict_records
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"[OK] Saved {len(records)} records to {filepath}")
    
    def generate_all_reports(self, 
                            type1_records: List[SMF110Type1],
                            type2_records: List[SMF110Type2],
                            type3_records: List[SMF110Type3],
                            type4_records: List[SMF110Type4],
                            type5_records: List[SMF110Type5]):
        """Generate all CSV and JSON reports for all subtypes"""
        
        print("\n" + "="*60)
        print("Generating SMF Type 110 CICS Statistics Reports")
        print("="*60)
        
        # Subtype 1: Transaction Statistics
        if type1_records:
            print(f"\nSubtype 1: Transaction Statistics ({len(type1_records)} records)")
            self.save_csv_report(type1_records, 1, "smf110_subtype1_transactions.csv")
            self.save_json_report(type1_records, 1, "smf110_subtype1_transactions.json")
        
        # Subtype 2: File Statistics
        if type2_records:
            print(f"\nSubtype 2: File Statistics ({len(type2_records)} records)")
            self.save_csv_report(type2_records, 2, "smf110_subtype2_files.csv")
            self.save_json_report(type2_records, 2, "smf110_subtype2_files.json")
        
        # Subtype 3: Program Statistics
        if type3_records:
            print(f"\nSubtype 3: Program Statistics ({len(type3_records)} records)")
            self.save_csv_report(type3_records, 3, "smf110_subtype3_programs.csv")
            self.save_json_report(type3_records, 3, "smf110_subtype3_programs.json")
        
        # Subtype 4: Terminal Statistics
        if type4_records:
            print(f"\nSubtype 4: Terminal Statistics ({len(type4_records)} records)")
            self.save_csv_report(type4_records, 4, "smf110_subtype4_terminals.csv")
            self.save_json_report(type4_records, 4, "smf110_subtype4_terminals.json")
        
        # Subtype 5: Storage Statistics
        if type5_records:
            print(f"\nSubtype 5: Storage Statistics ({len(type5_records)} records)")
            self.save_csv_report(type5_records, 5, "smf110_subtype5_storage.csv")
            self.save_json_report(type5_records, 5, "smf110_subtype5_storage.json")
        
        print("\n" + "="*60)
        print("All reports generated successfully!")
        print(f"Output directory: {self.output_dir.absolute()}")
        print("="*60)

def main():
    """Generate sample reports for testing"""
    from smf110_structures import SMF110SampleGenerator
    
    print("SMF Type 110 CICS Report Generator - Test Mode")
    print("Generating sample CICS statistics records...")
    
    # Generate sample data
    type1_records = SMF110SampleGenerator.generate_type1_records(15)
    type2_records = SMF110SampleGenerator.generate_type2_records(10)
    type3_records = SMF110SampleGenerator.generate_type3_records(12)
    type4_records = SMF110SampleGenerator.generate_type4_records(8)
    type5_records = SMF110SampleGenerator.generate_type5_records(6)
    
    # Generate reports
    generator = SMF110ReportGenerator()
    generator.generate_all_reports(
        type1_records,
        type2_records,
        type3_records,
        type4_records,
        type5_records
    )

if __name__ == "__main__":
    main()
