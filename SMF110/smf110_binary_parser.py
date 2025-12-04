"""
SMF Type 110 Binary Dump Parser
Parses raw IBM z/OS SMF Type 110 CICS statistics records from binary dump files
Handles EBCDIC encoding, RDW headers, and binary field formats
"""

import struct
from pathlib import Path
from typing import List, Tuple, Optional
from smf110_structures import (
    SMF110Type1, SMF110Type2, SMF110Type3, SMF110Type4, SMF110Type5,
    SMF110Type6, SMF110Type7, SMF110Type8, SMF110Type9, SMF110Type10,
    SMF110Type11, SMF110Type12, SMF110Type13, SMF110Type14, SMF110Type15,
    SMF110Header, CICSIdentification
)

class SMF110BinaryParser:
    """Parse SMF Type 110 records from binary dump files"""
    
    def __init__(self, dump_file: str):
        self.dump_file = Path(dump_file)
        self.records_by_subtype = {i: [] for i in range(1, 16)}
        
    def ebcdic_to_ascii(self, data: bytes) -> str:
        """Convert EBCDIC bytes to ASCII string"""
        try:
            return data.decode('cp500').rstrip()
        except:
            return data.hex()
    
    def parse_header(self, data: bytes, offset: int) -> Tuple[SMF110Header, CICSIdentification, int]:
        """Parse SMF 110 common header and CICS identification
        
        SMF Header Format (z/OS):
        Offset  Length  Field
        0       2       RDW Length (big-endian)
        2       2       RDW Reserved
        4       2       Record Length
        6       1       Segment Descriptor
        7       1       Flags
        8       1       Record Type (110)
        9       1       Reserved
        10      4       Timestamp (TOD clock)
        14      4       System ID (EBCDIC)
        18      4       Subsystem ID (EBCDIC)
        22      1       Subtype
        23-48   ...     CICS Product Section
        """
        
        # Parse RDW (Record Descriptor Word)
        rdw_length = struct.unpack('>H', data[offset:offset+2])[0]
        
        # Parse SMF header
        record_length = struct.unpack('>H', data[offset+4:offset+6])[0]
        flags = data[offset+7]
        record_type = data[offset+8]
        
        # Verify this is SMF 110
        if record_type != 110:
            raise ValueError(f"Not an SMF Type 110 record (got type {record_type})")
        
        # Parse timestamp (simplified - just read as binary)
        timestamp_raw = struct.unpack('>I', data[offset+10:offset+14])[0]
        
        # Parse System ID and Subsystem ID (EBCDIC)
        system_id = self.ebcdic_to_ascii(data[offset+14:offset+18])
        subsystem_id = self.ebcdic_to_ascii(data[offset+18:offset+22])
        
        # Parse subtype
        subtype = data[offset+22]
        
        # Parse CICS Product Section (offset 23+)
        # CICS APPLID at offset 23 (8 bytes EBCDIC)
        cics_applid = self.ebcdic_to_ascii(data[offset+23:offset+31])
        
        # CICS Jobname at offset 31 (8 bytes EBCDIC)
        jobname = self.ebcdic_to_ascii(data[offset+31:offset+39])
        
        # CICS Release at offset 39 (4 bytes EBCDIC)
        release = self.ebcdic_to_ascii(data[offset+39:offset+43])
        
        # SMF Release at offset 43 (2 bytes EBCDIC)
        smf_release = self.ebcdic_to_ascii(data[offset+43:offset+45])
        
        header = SMF110Header(
            record_type=record_type,
            record_length=record_length,
            flags=flags,
            system_id=system_id,
            subsystem_id=subsystem_id,
            cics_applid=cics_applid
        )
        
        identification = CICSIdentification(
            applid=cics_applid,
            jobname=jobname,
            release=release,
            smf_release=smf_release
        )
        
        return header, identification, subtype
    
    def parse_type1_transaction(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type1:
        """Parse Subtype 1 - Transaction Statistics
        
        Transaction Section (typical offsets after header):
        Offset  Length  Field
        50      4       Transaction ID (EBCDIC)
        54      8       Program Name (EBCDIC)
        62      8       User ID (EBCDIC)
        70      4       Terminal ID (EBCDIC)
        74      4       Transaction Count (binary)
        78      4       CPU Time (microseconds, binary)
        82      4       Elapsed Time (1/100 sec, binary)
        86      4       Response Time (1/100 sec, binary)
        90      4       File Requests (binary)
        94      4       DB2 Requests (binary)
        98      4       TS Requests (binary)
        102     4       TD Requests (binary)
        106     4       Reads (binary)
        110     4       Writes (binary)
        114     4       Browses (binary)
        118     4       Deletes (binary)
        122     4       Completed (binary)
        126     4       Abended (binary)
        130     4       Errors (binary)
        """
        
        base = offset + 50  # Start of transaction data
        
        transaction_id = self.ebcdic_to_ascii(data[base:base+4])
        program_name = self.ebcdic_to_ascii(data[base+4:base+12])
        userid = self.ebcdic_to_ascii(data[base+12:base+20])
        terminal_id = self.ebcdic_to_ascii(data[base+20:base+24])
        
        transaction_count = struct.unpack('>I', data[base+24:base+28])[0] if len(data) >= base+28 else 0
        cpu_time_us = struct.unpack('>I', data[base+28:base+32])[0] if len(data) >= base+32 else 0
        elapsed_time_cs = struct.unpack('>I', data[base+32:base+36])[0] if len(data) >= base+36 else 0
        response_time_cs = struct.unpack('>I', data[base+36:base+40])[0] if len(data) >= base+40 else 0
        
        file_requests = struct.unpack('>I', data[base+40:base+44])[0] if len(data) >= base+44 else 0
        db2_requests = struct.unpack('>I', data[base+44:base+48])[0] if len(data) >= base+48 else 0
        ts_requests = struct.unpack('>I', data[base+48:base+52])[0] if len(data) >= base+52 else 0
        td_requests = struct.unpack('>I', data[base+52:base+56])[0] if len(data) >= base+56 else 0
        
        reads = struct.unpack('>I', data[base+56:base+60])[0] if len(data) >= base+60 else 0
        writes = struct.unpack('>I', data[base+60:base+64])[0] if len(data) >= base+64 else 0
        browses = struct.unpack('>I', data[base+64:base+68])[0] if len(data) >= base+68 else 0
        deletes = struct.unpack('>I', data[base+68:base+72])[0] if len(data) >= base+72 else 0
        
        completed = struct.unpack('>I', data[base+72:base+76])[0] if len(data) >= base+76 else 0
        abended = struct.unpack('>I', data[base+76:base+80])[0] if len(data) >= base+80 else 0
        errors = struct.unpack('>I', data[base+80:base+84])[0] if len(data) >= base+84 else 0
        
        return SMF110Type1(
            header=header,
            identification=ident,
            transaction_id=transaction_id,
            program_name=program_name,
            userid=userid,
            terminal_id=terminal_id,
            transaction_count=transaction_count,
            cpu_time=cpu_time_us / 1000.0,  # Convert to milliseconds
            elapsed_time=elapsed_time_cs * 10.0,  # Convert to milliseconds
            response_time=response_time_cs * 10.0,
            file_requests=file_requests,
            db2_requests=db2_requests,
            ts_requests=ts_requests,
            td_requests=td_requests,
            reads=reads,
            writes=writes,
            browses=browses,
            deletes=deletes,
            completed=completed,
            abended=abended,
            errors=errors
        )
    
    def parse_type2_file(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type2:
        """Parse Subtype 2 - File Statistics"""
        base = offset + 50
        
        file_name = self.ebcdic_to_ascii(data[base:base+8])
        dataset_name = self.ebcdic_to_ascii(data[base+8:base+52])
        file_type = self.ebcdic_to_ascii(data[base+52:base+56])
        
        reads = struct.unpack('>I', data[base+56:base+60])[0] if len(data) >= base+60 else 0
        writes = struct.unpack('>I', data[base+60:base+64])[0] if len(data) >= base+64 else 0
        updates = struct.unpack('>I', data[base+64:base+68])[0] if len(data) >= base+68 else 0
        deletes = struct.unpack('>I', data[base+68:base+72])[0] if len(data) >= base+72 else 0
        browses = struct.unpack('>I', data[base+72:base+76])[0] if len(data) >= base+76 else 0
        
        avg_response_us = struct.unpack('>I', data[base+76:base+80])[0] if len(data) >= base+80 else 0
        max_response_us = struct.unpack('>I', data[base+80:base+84])[0] if len(data) >= base+84 else 0
        total_io_us = struct.unpack('>I', data[base+84:base+88])[0] if len(data) >= base+88 else 0
        
        buffer_requests = struct.unpack('>I', data[base+88:base+92])[0] if len(data) >= base+92 else 0
        buffer_hits = struct.unpack('>I', data[base+92:base+96])[0] if len(data) >= base+96 else 0
        buffer_misses = struct.unpack('>I', data[base+96:base+100])[0] if len(data) >= base+100 else 0
        
        string_waits = struct.unpack('>I', data[base+100:base+104])[0] if len(data) >= base+104 else 0
        string_requests = struct.unpack('>I', data[base+104:base+108])[0] if len(data) >= base+108 else 0
        
        io_errors = struct.unpack('>I', data[base+108:base+112])[0] if len(data) >= base+112 else 0
        record_not_found = struct.unpack('>I', data[base+112:base+116])[0] if len(data) >= base+116 else 0
        duplicate_key = struct.unpack('>I', data[base+116:base+120])[0] if len(data) >= base+120 else 0
        
        return SMF110Type2(
            header=header,
            identification=ident,
            file_name=file_name,
            dataset_name=dataset_name,
            file_type=file_type,
            reads=reads,
            writes=writes,
            updates=updates,
            deletes=deletes,
            browses=browses,
            avg_response_time=avg_response_us / 1000.0,
            max_response_time=max_response_us / 1000.0,
            total_io_time=total_io_us / 1000.0,
            buffer_requests=buffer_requests,
            buffer_hits=buffer_hits,
            buffer_misses=buffer_misses,
            string_waits=string_waits,
            string_requests=string_requests,
            io_errors=io_errors,
            record_not_found=record_not_found,
            duplicate_key=duplicate_key
        )
    
    def parse_record(self, data: bytes, offset: int) -> Tuple[Optional[object], int]:
        """Parse a single SMF 110 record starting at offset
        
        Returns:
            (parsed_record, next_offset) or (None, next_offset) if parsing fails
        """
        try:
            # Get RDW length to determine record boundaries
            if len(data) < offset + 4:
                return None, len(data)
            
            rdw_length = struct.unpack('>H', data[offset:offset+2])[0]
            
            if rdw_length == 0 or offset + rdw_length > len(data):
                return None, len(data)
            
            # Parse header and determine subtype
            header, identification, subtype = self.parse_header(data, offset)
            
            # Parse subtype-specific data
            record = None
            if subtype == 1:
                record = self.parse_type1_transaction(data, offset, header, identification)
            elif subtype == 2:
                record = self.parse_type2_file(data, offset, header, identification)
            # Add parsers for subtypes 3-15 as needed
            else:
                print(f"[WARN] Subtype {subtype} parser not yet implemented, skipping...")
            
            # Store record by subtype
            if record:
                self.records_by_subtype[subtype].append(record)
            
            # Return next offset
            next_offset = offset + rdw_length
            return record, next_offset
            
        except Exception as e:
            print(f"[ERROR] Failed to parse record at offset {offset}: {e}")
            # Try to skip to next record by reading RDW
            try:
                rdw_length = struct.unpack('>H', data[offset:offset+2])[0]
                return None, offset + rdw_length if rdw_length > 0 else offset + 4
            except:
                return None, len(data)
    
    def parse_dump(self) -> dict:
        """Parse entire SMF dump file
        
        Returns:
            Dictionary with records organized by subtype
        """
        if not self.dump_file.exists():
            raise FileNotFoundError(f"Dump file not found: {self.dump_file}")
        
        print(f"\n[INFO] Parsing SMF 110 dump: {self.dump_file}")
        print(f"[INFO] File size: {self.dump_file.stat().st_size} bytes")
        
        with open(self.dump_file, 'rb') as f:
            data = f.read()
        
        offset = 0
        record_count = 0
        
        while offset < len(data):
            record, next_offset = self.parse_record(data, offset)
            
            if record:
                record_count += 1
                if record_count % 100 == 0:
                    print(f"[INFO] Parsed {record_count} records...")
            
            if next_offset <= offset:
                # Prevent infinite loop
                break
            
            offset = next_offset
        
        print(f"\n[OK] Parsed {record_count} total records")
        for subtype, records in self.records_by_subtype.items():
            if records:
                print(f"  - Subtype {subtype}: {len(records)} records")
        
        return self.records_by_subtype

def main():
    """Test the binary parser"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python smf110_binary_parser.py <dump_file>")
        print("\nExample:")
        print("  python smf110_binary_parser.py path/to/smf110.dump")
        return
    
    dump_file = sys.argv[1]
    parser = SMF110BinaryParser(dump_file)
    
    try:
        records = parser.parse_dump()
        
        # Display sample records
        for subtype, record_list in records.items():
            if record_list:
                print(f"\n{'='*60}")
                print(f"Sample Subtype {subtype} Record:")
                print('='*60)
                sample = record_list[0].to_dict()
                for key, value in list(sample.items())[:15]:
                    print(f"  {key}: {value}")
                if len(sample) > 15:
                    print(f"  ... and {len(sample) - 15} more fields")
    
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
