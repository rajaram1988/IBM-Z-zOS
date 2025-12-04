"""
SMF Dump Diagnostic Tool
Analyzes raw SMF dump file structure to identify format issues
"""

import struct
import sys
from pathlib import Path

def analyze_smf_dump(dump_file: str, max_records: int = 10):
    """Analyze SMF dump file structure"""
    
    path = Path(dump_file)
    if not path.exists():
        print(f"ERROR: File not found: {dump_file}")
        return
    
    print("="*80)
    print("SMF DUMP DIAGNOSTIC TOOL")
    print("="*80)
    print(f"File: {path}")
    print(f"Size: {path.stat().st_size:,} bytes\n")
    
    with open(dump_file, 'rb') as f:
        data = f.read()
    
    if len(data) < 100:
        print("ERROR: File too small to be valid SMF dump")
        return
    
    # Show first 128 bytes
    print("First 128 bytes (hex):")
    print("Offset  | Hex                                             | ASCII")
    print("-"*80)
    for i in range(0, min(128, len(data)), 16):
        hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f"{i:06x}  | {hex_str:47s} | {ascii_str}")
    
    print("\n" + "="*80)
    print("ANALYZING RECORDS")
    print("="*80)
    
    offset = 0
    record_num = 0
    
    while offset < len(data) - 4 and record_num < max_records:
        record_num += 1
        print(f"\nRecord #{record_num} at offset {offset} (0x{offset:x}):")
        print("-"*80)
        
        # RDW (Record Descriptor Word)
        if offset + 4 > len(data):
            print("  ERROR: Not enough data for RDW")
            break
        
        rdw_length = struct.unpack('>H', data[offset:offset+2])[0]
        rdw_reserved = struct.unpack('>H', data[offset+2:offset+4])[0]
        
        print(f"  RDW Length: {rdw_length} bytes (0x{rdw_length:04x})")
        print(f"  RDW Reserved: {rdw_reserved} (0x{rdw_reserved:04x})")
        
        if rdw_length == 0 or rdw_length > len(data) - offset:
            print(f"  ERROR: Invalid RDW length")
            break
        
        # SMF Header (after RDW)
        if offset + 10 > len(data):
            print("  ERROR: Not enough data for SMF header")
            break
        
        smf_offset = offset + 4
        record_length = struct.unpack('>H', data[smf_offset:smf_offset+2])[0]
        segment = data[smf_offset+2]
        flags = data[smf_offset+3]
        record_type = data[smf_offset+4]
        
        print(f"  SMF Record Length: {record_length}")
        print(f"  SMF Segment: {segment}")
        print(f"  SMF Flags: {flags} (0x{flags:02x})")
        print(f"  SMF Record Type: {record_type}")
        
        if record_type == 30:
            print("  *** TYPE 30 RECORD DETECTED ***")
            
            # Show bytes 14-30 where subtype typically is
            print(f"\n  Bytes 14-30 from SMF header start:")
            for i in range(14, min(30, rdw_length)):
                pos = smf_offset + i
                if pos < len(data):
                    val = data[pos]
                    # Try EBCDIC decode
                    try:
                        ebcdic_char = bytes([val]).decode('cp500')
                        if 32 <= ord(ebcdic_char) < 127:
                            char_display = ebcdic_char
                        else:
                            char_display = '.'
                    except:
                        char_display = '.'
                    
                    print(f"    Offset {i:2d} (absolute {pos:6d}): 0x{val:02x} ({val:3d}) [{char_display}]", end='')
                    
                    # Highlight possible subtype values
                    if 1 <= val <= 5:
                        print(f"  <-- Possible Subtype {val}")
                    else:
                        print()
            
            # Try to find job identification section
            print(f"\n  Looking for Job Name (EBCDIC text):")
            for test_offset in [26, 28, 30, 32, 34, 36]:
                pos = smf_offset + test_offset
                if pos + 8 <= len(data):
                    try:
                        candidate = data[pos:pos+8].decode('cp500', errors='ignore').strip()
                        hex_display = ' '.join(f'{b:02x}' for b in data[pos:pos+8])
                        print(f"    Offset {test_offset}: '{candidate}' (hex: {hex_display})")
                    except:
                        print(f"    Offset {test_offset}: decode error")
        
        # Show first 64 bytes of record
        print(f"\n  First 64 bytes of record:")
        for i in range(0, min(64, rdw_length), 16):
            pos = offset + i
            if pos + 16 <= len(data):
                hex_str = ' '.join(f'{b:02x}' for b in data[pos:pos+16])
                print(f"    {i:04x}: {hex_str}")
        
        offset += rdw_length
    
    print("\n" + "="*80)
    print(f"Analyzed {record_num} records")
    print("="*80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_smf_dump.py <dump_file> [max_records]")
        print("\nExample:")
        print("  python diagnose_smf_dump.py smf30.dump 5")
        sys.exit(1)
    
    dump_file = sys.argv[1]
    max_records = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    analyze_smf_dump(dump_file, max_records)
