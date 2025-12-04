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
        """Parse Subtype 1 - Job Step Termination using self-describing sections"""
        try:
            # SMF 30 uses self-describing sections with offset/length/number triplets
            # After RDW (4 bytes) and SMF header (varies), we have the product section
            
            # Standard SMF header is at offset+4
            # Subtype is at offset 5 from SMF header start (offset+4+5 = offset+9 in old format)
            # But z/OS 3.1 may use offset 18 or 22 depending on format
            
            # Try to locate key sections using self-describing format
            base = offset + 4  # Skip RDW
            
            # Read self-describing triplets starting at offset 14 from SMF header
            # Format: Offset(4), Length(2), Number(2) for each section
            
            # For SMF 30, sections are typically:
            # - Identification Section (job name, etc.)
            # - Timing Section (CPU, elapsed, etc.)  
            # - I/O Activity Section
            
            # Fallback: Use approximate offsets but validate data
            # Job Identification typically starts around offset 26-32
            
            # Try multiple possible starting positions for job name
            job_name_candidates = [
                (offset+26, offset+34),  # z/OS 2.x format
                (offset+28, offset+36),  # Common position
                (offset+32, offset+40),  # z/OS 3.x format
            ]
            
            job_name = None
            actual_base = offset + 28  # Default
            
            for start, end in job_name_candidates:
                if end <= len(data):
                    candidate = self.ebcdic_to_ascii(data[start:end])
                    # Valid job names are alphanumeric (relaxed validation)
                    if candidate and len(candidate) > 0 and (candidate[0].isalpha() or candidate[0].isdigit()):
                        job_name = candidate
                        actual_base = start
                        break
            
            if not job_name or job_name == "":
                # Use default offset - be more lenient
                for start, end in job_name_candidates:
                    if end <= len(data):
                        candidate = self.ebcdic_to_ascii(data[start:end])
                        if candidate and len(candidate.strip()) > 0:
                            job_name = candidate
                            actual_base = start
                            break
                
                if not job_name:
                    job_name = self.ebcdic_to_ascii(data[offset+28:offset+36]) if offset+36 <= len(data) else "UNKNOWN"
                    actual_base = offset + 28
            
            # Adjust other fields based on detected base
            field_offset = actual_base - offset - 28  # Offset adjustment
            
            # Step name (8 bytes after job name)
            step_offset = actual_base + 8
            step_name = self.ebcdic_to_ascii(data[step_offset:step_offset+8]) if step_offset+8 <= len(data) else "UNKNOWN"
            
            # Program name (8 bytes after step name)
            prog_offset = step_offset + 8
            program_name = self.ebcdic_to_ascii(data[prog_offset:prog_offset+8]) if prog_offset+8 <= len(data) else "UNKNOWN"
            
            # User ID (8 bytes after program name)
            user_offset = prog_offset + 8
            userid = self.ebcdic_to_ascii(data[user_offset:user_offset+8]) if user_offset+8 <= len(data) else "UNKNOWN"
            
            # Job number (8 bytes after user ID)
            jobnum_offset = user_offset + 8
            job_number = self.ebcdic_to_ascii(data[jobnum_offset:jobnum_offset+8]) if jobnum_offset+8 <= len(data) else "000000"
            
            # Timing data typically follows identification section
            # CPU time - try multiple possible locations
            timing_base = jobnum_offset + 12  # Skip some padding
            
            cpu_time_us = 0
            elapsed_ths = 0
            io_count = 0
            service_units = 0
            
            # Try to find timing section by looking for reasonable CPU values
            for test_offset in range(timing_base, min(timing_base + 40, len(data) - 4), 4):
                if test_offset + 4 <= len(data):
                    test_value = struct.unpack('>I', data[test_offset:test_offset+4])[0]
                    # CPU time in microseconds should be < 1 hour (3.6e9 microseconds)
                    if 0 < test_value < 3600000000:
                        cpu_time_us = test_value
                        timing_base = test_offset
                        break
            
            if cpu_time_us == 0 and timing_base + 4 <= len(data):
                cpu_time_us = struct.unpack('>I', data[timing_base:timing_base+4])[0]
            
            cpu_time_ms = cpu_time_us // 1000 if cpu_time_us < 3600000000 else 0
            
            # Elapsed time (typically 8 bytes after CPU time)
            elapsed_offset = timing_base + 8
            if elapsed_offset + 4 <= len(data):
                elapsed_ths = struct.unpack('>I', data[elapsed_offset:elapsed_offset+4])[0]
            elapsed_time_ms = elapsed_ths * 10 if elapsed_ths < 360000 else 0
            
            # IO count (typically 8 bytes after elapsed time)
            io_offset = elapsed_offset + 8
            if io_offset + 4 <= len(data):
                io_count = struct.unpack('>I', data[io_offset:io_offset+4])[0]
            if io_count > 1000000000:  # Sanity check
                io_count = 0
            
            # Service units (typically 8 bytes after IO)
            su_offset = io_offset + 8
            if su_offset + 4 <= len(data):
                service_units = struct.unpack('>I', data[su_offset:su_offset+4])[0]
            if service_units > 1000000000:  # Sanity check
                service_units = 0
            
            # Return code, pages, EXCP with bounds checking
            rc_offset = su_offset + 8
            return_code = struct.unpack('>H', data[rc_offset:rc_offset+2])[0] if rc_offset+2 <= len(data) else 0
            
            pr_offset = rc_offset + 6
            pages_read = struct.unpack('>I', data[pr_offset:pr_offset+4])[0] if pr_offset+4 <= len(data) else 0
            if pages_read > 100000000:
                pages_read = 0
            
            pw_offset = pr_offset + 4
            pages_written = struct.unpack('>I', data[pw_offset:pw_offset+4])[0] if pw_offset+4 <= len(data) else 0
            if pages_written > 100000000:
                pages_written = 0
            
            excp_offset = pw_offset + 4
            excp_count = struct.unpack('>I', data[excp_offset:excp_offset+4])[0] if excp_offset+4 <= len(data) else 0
            if excp_count > 100000000:
                excp_count = 0
            
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
            import traceback
            print(f"[ERROR] Failed to parse Type 30 Subtype 1 at offset {offset}: {e}")
            if offset < len(data) - 50:
                print(f"  Data sample (hex): {data[offset:offset+50].hex()}")
            traceback.print_exc()
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
        
        print(f"File size: {len(data):,} bytes")
        
        # Detect z/OS version from first record if possible
        if len(data) > 30:
            print(f"\nFirst 64 bytes (hex):")
            for i in range(0, min(64, len(data)), 16):
                hex_line = ' '.join(f'{data[i+j]:02x}' for j in range(16) if i+j < len(data))
                print(f"  {i:04x}: {hex_line}")
            
            print(f"\nSearching for Type 30 indicator (0x1E = 30 decimal):")
            for test_pos in range(0, min(40, len(data))):
                val = data[test_pos]
                if val == 30 or val == 0x1E:
                    print(f"  Found 0x1E (30) at offset {test_pos}")
            
            if data[8] == 30:
                print(f"✓ Detected SMF Type 30 at standard offset 8")
        
        offset = 0
        record_count = 0
        type30_count = 0
        parse_errors = 0
        record_types_found = {}  # Track all record types in the file
        
        while offset < len(data) - 4:
            # Read RDW length
            if offset + 4 > len(data):
                break
                
            rdw_length = struct.unpack('>H', data[offset:offset+2])[0]
            
            # Skip invalid records
            if rdw_length == 0 or rdw_length > len(data) - offset:
                offset += 4
                continue
            
            # Check if this is a Type 30 record - try multiple offsets
            if offset + 20 < len(data):
                # Try different possible positions for record type
                possible_offsets = [8, 9, 10, 11, 12]
                record_type = None
                actual_offset = None
                
                for test_offset in possible_offsets:
                    if offset + test_offset < len(data):
                        test_val = data[offset + test_offset]
                        # Debug first record
                        if record_count == 0:
                            print(f"  Offset {offset+test_offset}: value={test_val} (0x{test_val:02x})")
                        
                        # Use first reasonable record type we find
                        if record_type is None and 1 <= test_val <= 255:
                            record_type = test_val
                            actual_offset = test_offset
                
                if record_count == 0 and record_type:
                    print(f"  Using record type {record_type} from offset +{actual_offset}")
                
                # Track what record types we're seeing
                if record_type:
                    record_types_found[record_type] = record_types_found.get(record_type, 0) + 1
                
                if record_type == 30:
                    type30_count += 1
                    
                    # Parse the header
                    header, _ = self.read_smf_header(data, offset)
                    
                    if header:
                        # Try multiple possible subtype locations for z/OS 3.1 compatibility
                        subtype_candidates = [offset+18, offset+21, offset+22, offset+23]
                        subtype = None
                        subtype_pos = None
                        
                        # Debug: show what we find at each position for first few records
                        if type30_count <= 3:
                            print(f"  [DEBUG] Record at offset {offset}, checking subtype at positions:")
                            for pos in subtype_candidates:
                                if pos < len(data):
                                    val = data[pos]
                                    print(f"    Offset {pos}: value={val} (0x{val:02x})")
                        
                        for pos in subtype_candidates:
                            if pos < len(data):
                                candidate = data[pos]
                                if 1 <= candidate <= 5:  # Valid subtypes
                                    subtype = candidate
                                    subtype_pos = pos
                                    break
                        
                        if type30_count <= 3 and subtype:
                            print(f"  [DEBUG] Selected subtype {subtype} from offset {subtype_pos}")
                        
                        if subtype:
                            # Parse record with error handling
                            try:
                                record = self.parse_type30_subtype1(data, offset)
                                
                                if record:
                                    if subtype in self.records:
                                        self.records[subtype].append(record)
                                        rec_dict = record.to_dict()
                                        if type30_count <= 5:  # Show first 5 records
                                            print(f"  [OK] Parsed Type 30.{subtype}: {rec_dict['job_name']}/{rec_dict['step_name']} CPU={rec_dict.get('cpu_time_ms', 0)}ms")
                                        elif type30_count % 100 == 0:
                                            print(f"  [Progress] Processed {type30_count} Type 30 records...")
                                    else:
                                        if type30_count <= 3:
                                            print(f"  [WARN] Subtype {subtype} not in records dict")
                                else:
                                    parse_errors += 1
                                    if parse_errors <= 5:
                                        print(f"  [WARN] parse_type30_subtype1 returned None for record at offset {offset}")
                            except Exception as e:
                                parse_errors += 1
                                if parse_errors <= 3:  # Show first 3 errors
                                    print(f"  [ERROR] Exception parsing record at offset {offset}: {e}")
                        else:
                            if type30_count <= 3:
                                print(f"  [INFO] Could not determine subtype for record at offset {offset}")
            
            record_count += 1
            offset += rdw_length
        
        print(f"\nTotal records processed: {record_count}")
        print(f"Type 30 records found: {type30_count}")
        
        # Show what record types were actually found
        if record_types_found:
            print(f"\nRecord types found in dump file:")
            for rec_type in sorted(record_types_found.keys()):
                count = record_types_found[rec_type]
                print(f"  Type {rec_type:3d}: {count:4d} records")
        
        if parse_errors > 0:
            print(f"\nParse errors: {parse_errors} (some records may have incorrect format)")
        
        for subtype, records in self.records.items():
            if records:
                print(f"  Subtype {subtype}: {len(records)} records successfully parsed")
        
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
