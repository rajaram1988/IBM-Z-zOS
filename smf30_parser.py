"""
SMF Type 30 Record Parser and Report Generator
Parses SMF-30 records and generates CSV reports for each subtype
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any
from smf30_structures import (
    SMF30SampleGenerator,
    SMF30Type1, SMF30Type2, SMF30Type3, SMF30Type4, SMF30Type5
)

class SMF30Parser:
    """Parse and process SMF Type 30 records"""
    
    SUBTYPE_NAMES = {
        1: "Job Step Termination",
        2: "Job Termination",
        3: "Step Initiation",
        4: "Job Initiation",
        5: "NetStep Completion",
    }
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.records_by_subtype = {}
    
    def generate_sample_records(self):
        """Load sample records from generator"""
        all_records = SMF30SampleGenerator.generate_all_records()
        self.records_by_subtype = all_records
        return all_records
    
    def get_subtype_records(self, subtype: int) -> List[Dict[str, Any]]:
        """Get all records for a specific subtype"""
        if subtype not in self.records_by_subtype:
            return []
        
        records = self.records_by_subtype[subtype]
        return [r.to_dict() for r in records]
    
    def save_json_report(self, subtype: int, filename: str = None):
        """Save subtype records as JSON"""
        if subtype not in self.records_by_subtype:
            print(f"No records found for subtype {subtype}")
            return
        
        if filename is None:
            filename = f"smf30_subtype{subtype}.json"
        
        filepath = self.output_dir / filename
        records_dict = self.get_subtype_records(subtype)
        
        with open(filepath, 'w') as f:
            json.dump(records_dict, f, indent=2, default=str)
        
        print(f"Saved JSON report: {filepath}")
    
    def save_csv_report(self, subtype: int, filename: str = None):
        """Save subtype records as CSV"""
        if subtype not in self.records_by_subtype:
            print(f"No records found for subtype {subtype}")
            return
        
        if filename is None:
            filename = f"smf30_subtype{subtype}.csv"
        
        filepath = self.output_dir / filename
        records = self.get_subtype_records(subtype)
        
        if not records:
            print(f"No records to export for subtype {subtype}")
            return
        
        # Get all field names from first record
        fieldnames = list(records[0].keys())
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        
        print(f"Saved CSV report: {filepath}")
    
    def generate_all_reports(self):
        """Generate reports for all subtypes"""
        print("\n" + "="*60)
        print("SMF Type 30 Record Reports")
        print("="*60)
        
        for subtype in sorted(self.records_by_subtype.keys()):
            records = self.get_subtype_records(subtype)
            subtype_name = self.SUBTYPE_NAMES.get(subtype, "Unknown")
            
            print(f"\nSubtype {subtype}: {subtype_name}")
            print(f"  Record Count: {len(records)}")
            
            if records:
                print(f"  Fields: {', '.join(list(records[0].keys())[:8])}...")
            
            # Save both JSON and CSV
            self.save_json_report(subtype)
            self.save_csv_report(subtype)
    
    def generate_summary(self) -> Dict[int, Dict[str, Any]]:
        """Generate summary statistics for each subtype"""
        summary = {}
        
        for subtype, records in self.records_by_subtype.items():
            records_dict = [r.to_dict() for r in records]
            
            summary[subtype] = {
                'subtype_name': self.SUBTYPE_NAMES.get(subtype, "Unknown"),
                'record_count': len(records_dict),
                'records': records_dict,
            }
        
        return summary

def main():
    """Main execution"""
    # Create parser and generate sample data
    parser = SMF30Parser(output_dir="./reports")
    parser.generate_sample_records()
    
    # Generate all reports
    parser.generate_all_reports()
    
    # Display summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    summary = parser.generate_summary()
    for subtype, info in summary.items():
        print(f"Subtype {subtype} ({info['subtype_name']}): {info['record_count']} records")
    
    print("\nReports saved to: ./reports/")

if __name__ == "__main__":
    main()
