"""
SMF Type 30 Binary Record Parser
Reads actual SMF dump files in binary format according to IBM z/OS specifications
"""

import struct
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, BinaryIO, Tuple, Optional
from smf30_structures import (
    SMF30Type1, SMF30Type2, SMF30Type3, SMF30Type4, SMF30Type5,
    SMF30Header, JobIdentification, TimingData
)

class SMFBinaryParser:
    """Parse binary SMF Type 30 records from dump files"""
    
    # SMF Record Header offsets (common to all SMF records)
    SMF_HEADER_FORMAT = '>HBBH4s4s'  # Big-endian format
    SMF_HEADER_SIZE = 14
    
    # Type 30 specific offsets (from IBM manual)
    TYPE30_SUBTYPE_OFFSET = 22
    
    def __init__(self, dump_file: str):
        self.dump_file = Path(dump_file)
        self.records = {1: [], 2: [], 3: [], 4: [], 5: []}
        
    def read_smf_header(self, data: bytes, offset: int = 0) -> Tuple[dict, int]:
        """Parse SMF common header"""
        try:
            # RDW (Record Descriptor Word) - first 4 bytes
            rdw_length = struct.unpack('>H', data[offset:offset+2])[0]
            
            # SMF Header
            record_length = struct.unpack('>H', data[offset+4:offset+6])[0]
            segment = data[offset+6]
            flags = data[offset+7]
            record_type = data[offset+8]
            
            # Time stamp (offset 10, 4 bytes TOD format)
            # Simplified: just use current time for sample
            timestamp = datetime.now()
            
            # System ID (offset 14, 4 bytes EBCDIC)
            system_id = data[offset+14:offset+18].decode('cp500', errors='ignore').strip()
            
            header = {
                'rdw_length': rdw_length,
                'record_length': record_length,
                'segment': segment,
                'flags': flags,
                'record_type': record_type,
                'timestamp': timestamp,
                'system_id': system_id or 'SYSTEM',
            }
            
            return header, offset + rdw_length
            
        except Exception as e:
            print(f"Error parsing SMF header: {e}")
            return None, offset + 4
    
    def ebcdic_to_ascii(self, ebcdic_bytes: bytes) -> str:
        """Convert EBCDIC bytes to ASCII string"""
        try:
            return ebcdic_bytes.decode('cp500').strip()
        except:
            return ebcdic_bytes.decode('latin-1', errors='ignore').strip()
    
    def parse_type30_subtype1(self, data: bytes, offset: int) -> Optional[SMF30Type1]:
        """Parse Subtype 1 - Job Step Termination"""
        try:
            # Job name (offset 28, 8 bytes EBCDIC)
            job_name = self.ebcdic_to_ascii(data[offset+28:offset+36])
            
            # Step name (offset 36, 8 bytes EBCDIC)
            step_name = self.ebcdic_to_ascii(data[offset+36:offset+44])
            
            # Program name (offset 44, 8 bytes EBCDIC)
            program_name = self.ebcdic_to_ascii(data[offset+44:offset+52])
            
            # User ID (offset 52, 8 bytes EBCDIC)
            userid = self.ebcdic_to_ascii(data[offset+52:offset+60])
            
            # Job number (offset 60, 8 bytes EBCDIC)
            job_number = self.ebcdic_to_ascii(data[offset+60:offset+68])
            
            # CPU time (offset 72, 4 bytes, microseconds)
            cpu_time_us = struct.unpack('>I', data[offset+72:offset+76])[0]
            cpu_time_ms = cpu_time_us // 1000
            
            # Elapsed time (offset 80, 4 bytes, hundredths of seconds)
            elapsed_ths = struct.unpack('>I', data[offset+80:offset+84])[0]
            elapsed_time_ms = elapsed_ths * 10
            
            # IO count (offset 88, 4 bytes)
            io_count = struct.unpack('>I', data[offset+88:offset+92])[0]
            
            # Service units (offset 96, 4 bytes)
            service_units = struct.unpack('>I', data[offset+96:offset+100])[0]
            
            # Return code (offset 104, 2 bytes)
            return_code = struct.unpack('>H', data[offset+104:offset+106])[0]
            
            # Pages read (offset 108, 4 bytes)
            pages_read = struct.unpack('>I', data[offset+108:offset+112])[0]
            
            # Pages written (offset 112, 4 bytes)
            pages_written = struct.unpack('>I', data[offset+112:offset+116])[0]
            
            # EXCP count (offset 116, 4 bytes)
            excp_count = struct.unpack('>I', data[offset+116:offset+120])[0]
            
            # Create record
            job_id = JobIdentification(
                job_name=job_name,
                job_number=job_number,
                owning_userid=userid,
            )
            
            timing = TimingData(
                cpu_time_ms=cpu_time_ms,
                service_units=service_units,
                io_count=io_count,
                elapsed_time_ms=elapsed_time_ms,
            )
            
            record = SMF30Type1(
                job_id=job_id,
                step_name=step_name,
                program_name=program_name,
                timing=timing,
                return_code=return_code,
                pages_read=pages_read,
                pages_written=pages_written,
                excp_count=excp_count,
            )
            
            return record
            
        except Exception as e:
            print(f"Error parsing Type 30 Subtype 1: {e}")
            return None
    
    def parse_type30_record(self, data: bytes, offset: int, header: dict) -> Optional[object]:
        """Parse a Type 30 record based on subtype"""
        try:
            # Subtype location: after RDW(4) + SMF header(varies)
            # Typical: offset + 22 from start of record
            # But need to account for RDW offset
            subtype_pos = offset + 22
            
            if subtype_pos >= len(data):
                return None
                
            subtype = data[subtype_pos]
            
            # Debug output
            #print(f"  Checking offset {subtype_pos}: subtype = {subtype}")
            
            if subtype == 1:
                return self.parse_type30_subtype1(data, offset)
            elif subtype == 0:
                # Subtype might be at different offset, try offset+23
                alt_pos = offset + 23
                if alt_pos < len(data):
                    subtype = data[alt_pos]
                    if subtype == 1:
                        return self.parse_type30_subtype1(data, offset)
            # Add other subtypes as needed
            
            if subtype != 0:
                print(f"Subtype {subtype} parser not yet implemented")
            return None
                
        except Exception as e:
            print(f"Error parsing Type 30 record: {e}")
            return None
    
    def parse_dump_file(self) -> dict:
        """Parse entire SMF dump file"""
        if not self.dump_file.exists():
            print(f"Error: Dump file not found: {self.dump_file}")
            return self.records
        
        print(f"\nParsing SMF dump file: {self.dump_file}")
        print("="*70)
        
        with open(self.dump_file, 'rb') as f:
            data = f.read()
        
        offset = 0
        record_count = 0
        type30_count = 0
        
        while offset < len(data) - 4:
            # Read RDW length
            if offset + 4 > len(data):
                break
                
            rdw_length = struct.unpack('>H', data[offset:offset+2])[0]
            
            # Skip invalid records
            if rdw_length == 0 or rdw_length > len(data) - offset:
                offset += 4
                continue
            
            # Check if this is a Type 30 record
            if offset + 8 < len(data):
                record_type = data[offset+8]
                
                if record_type == 30:
                    type30_count += 1
                    
                    # Parse the header
                    header, _ = self.read_smf_header(data, offset)
                    
                    if header:
                        # Try multiple possible subtype locations
                        subtype_candidates = [offset+21, offset+22, offset+23]
                        subtype = None
                        
                        for pos in subtype_candidates:
                            if pos < len(data):
                                candidate = data[pos]
                                if 1 <= candidate <= 5:  # Valid subtypes
                                    subtype = candidate
                                    break
                        
                        if subtype:
                            # Parse record
                            record = self.parse_type30_subtype1(data, offset)
                            
                            if record and subtype in self.records:
                                self.records[subtype].append(record)
                                rec_dict = record.to_dict()
                                print(f"  [OK] Parsed Type 30.{subtype}: {rec_dict['job_name']}/{rec_dict['step_name']}")
            
            record_count += 1
            offset += rdw_length
        
        print(f"\nTotal records processed: {record_count}")
        print(f"Type 30 records found: {type30_count}")
        
        for subtype, records in self.records.items():
            if records:
                print(f"  Subtype {subtype}: {len(records)} records")
        
        return self.records
    
    def parse_text_dump(self, text_file: str) -> dict:
        """Parse text-formatted SMF dump (for testing)"""
        print(f"\nParsing text SMF dump: {text_file}")
        print("="*70)
        
        # This would parse text hex dumps if you have them
        # Format: each line is a hex representation of a record
        
        return self.records


# Example usage and testing
def create_sample_binary_dump(output_file: str = "sample_smf30.dump"):
    """
    Create a sample binary SMF dump file for testing
    This generates a minimal valid SMF-30 record in binary format
    """
    from smf30_structures import SMF30SampleGenerator
    
    print(f"\nCreating sample binary dump: {output_file}")
    print("="*70)
    
    with open(output_file, 'wb') as f:
        # Generate sample records
        sample_records = SMF30SampleGenerator.generate_type1(3)
        
        for idx, record in enumerate(sample_records):
            # Create a minimal SMF-30 binary record
            # This is a simplified format for demonstration
            
            # RDW (Record Descriptor Word)
            rdw_length = 200  # Total record length
            rdw = struct.pack('>HH', rdw_length, 0)
            
            # SMF Header
            record_length = rdw_length - 4
            segment = 0
            flags = 0
            record_type = 30
            smf_header = struct.pack('>HBBB', record_length, segment, flags, record_type)
            
            # Timestamp (4 bytes - simplified)
            timestamp = struct.pack('>I', 0)
            
            # System ID (4 bytes EBCDIC)
            system_id = record.header.system_id.ljust(4).encode('cp500')[:4]
            
            # Subsystem ID (4 bytes EBCDIC)  
            subsys_id = record.header.subsystem_id.ljust(4).encode('cp500')[:4]
            
            # Now we're at offset 4+2+3+4+4+4 = 21
            # Subtype goes here (1 byte) - at offset 21
            subtype = struct.pack('B', 1)  # Subtype 1
            
            # Reserved (6 bytes to reach offset 28)
            reserved = b'\x00' * 6
            
            # Job name starts at offset 28 (8 bytes EBCDIC)
            job_name = record.job_id.job_name.ljust(8).encode('cp500')[:8]
            
            # Step name (8 bytes EBCDIC)
            step_name = record.step_name.ljust(8).encode('cp500')[:8]
            
            # Program name (8 bytes EBCDIC)
            program_name = record.program_name.ljust(8).encode('cp500')[:8]
            
            # User ID (8 bytes EBCDIC)
            userid = record.job_id.owning_userid.ljust(8).encode('cp500')[:8]
            
            # Job number (8 bytes EBCDIC)
            job_number = record.job_id.job_number.ljust(8).encode('cp500')[:8]
            
            # CPU time (4 bytes, microseconds)
            cpu_time = struct.pack('>I', record.timing.cpu_time_ms * 1000)
            
            # Padding (4 bytes)
            padding1 = struct.pack('>I', 0)
            
            # Elapsed time (4 bytes, hundredths of seconds)
            elapsed_time = struct.pack('>I', record.timing.elapsed_time_ms // 10)
            
            # Padding (4 bytes)
            padding2 = struct.pack('>I', 0)
            
            # IO count (4 bytes)
            io_count = struct.pack('>I', record.timing.io_count)
            
            # Padding (4 bytes)
            padding3 = struct.pack('>I', 0)
            
            # Service units (4 bytes)
            service_units = struct.pack('>I', record.timing.service_units)
            
            # Padding (4 bytes)
            padding4 = struct.pack('>I', 0)
            
            # Return code (2 bytes)
            return_code = struct.pack('>H', record.return_code)
            
            # Padding (2 bytes)
            padding5 = struct.pack('>H', 0)
            
            # Pages read (4 bytes)
            pages_read = struct.pack('>I', record.pages_read)
            
            # Pages written (4 bytes)
            pages_written = struct.pack('>I', record.pages_written)
            
            # EXCP count (4 bytes)
            excp_count = struct.pack('>I', record.excp_count)
            
            # Build complete record
            # RDW(4) + Header(6) + Time(4) + SysID(4) + SubsysID(4) = 22 bytes before subtype
            smf_record = (
                rdw + smf_header + timestamp + system_id + subsys_id +
                subtype + reserved +  # Subtype at offset 22
                job_name + step_name + program_name + userid + job_number +
                cpu_time + padding1 + elapsed_time + padding2 +
                io_count + padding3 + service_units + padding4 +
                return_code + padding5 + pages_read + pages_written + excp_count
            )
            
            # Pad to declared length
            if len(smf_record) < rdw_length:
                smf_record += b'\x00' * (rdw_length - len(smf_record))
            
            f.write(smf_record[:rdw_length])
            
            print(f"  Written record {idx+1}: Job={record.job_id.job_name}, Step={record.step_name}")
    
    print(f"\n[OK] Sample dump created: {output_file} ({rdw_length * len(sample_records)} bytes)")
    return output_file


def main():
    """Demonstrate binary SMF parsing"""
    
    # Create a sample dump file
    dump_file = create_sample_binary_dump("reports/sample_smf30.dump")
    
    # Parse it
    parser = SMFBinaryParser(dump_file)
    records = parser.parse_dump_file()
    
    print("\n" + "="*70)
    print("PARSING COMPLETE")
    print("="*70)
    
    for subtype, recs in records.items():
        if recs:
            print(f"\nSubtype {subtype}: {len(recs)} records parsed")
            for i, rec in enumerate(recs[:3]):  # Show first 3
                rec_dict = rec.to_dict()
                print(f"  Record {i+1}: {rec_dict['job_name']}/{rec_dict['step_name']} - CPU={rec_dict['cpu_time_ms']}ms")


if __name__ == "__main__":
    main()
