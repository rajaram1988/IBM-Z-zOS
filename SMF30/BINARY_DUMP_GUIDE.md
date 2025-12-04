# Using Real SMF Dump Files

## Quick Start

### Option 1: Use Your Own Binary SMF Dump
```powershell
# Parse your actual SMF dump file
python run_full_pipeline.py "C:\path\to\your\smf_dump.bin"
```

### Option 2: Create a Test Binary Dump
```powershell
# Generate a sample binary dump file for testing
python smf30_binary_parser.py
# This creates: reports/sample_smf30.dump

# Then parse it
python run_full_pipeline.py "reports/sample_smf30.dump"
```

### Option 3: Continue Using Sample Data
```powershell
# No arguments = sample data generator
python run_full_pipeline.py
```

---

## Binary SMF Format Details

### SMF Record Structure (IBM z/OS)

```
Offset  Length  Field Name              Format
------  ------  ----------------------  --------------------
0       2       RDW Length              Binary (big-endian)
2       2       RDW Reserved            Binary
4       2       Record Length           Binary
6       1       Segment Descriptor      Binary
7       1       Flags                   Binary
8       1       Record Type (30)        Binary
9       1       Reserved                Binary
10      4       Timestamp (TOD)         Binary (z/OS TOD clock)
14      4       System ID               EBCDIC
18      4       Subsystem ID            EBCDIC
22      1       Subtype                 Binary (1-5)
23      ...     Type-specific data      Various

Type 30 Subtype 1 Fields:
28      8       Job Name                EBCDIC
36      8       Step Name               EBCDIC
44      8       Program Name            EBCDIC
52      8       User ID                 EBCDIC
60      8       Job Number              EBCDIC
72      4       CPU Time                Binary (microseconds)
80      4       Elapsed Time            Binary (1/100 seconds)
88      4       IO Count                Binary
96      4       Service Units           Binary
104     2       Return Code             Binary
108     4       Pages Read              Binary
112     4       Pages Written           Binary
116     4       EXCP Count              Binary
```

---

## Customizing the Parser

### Adding Support for Your SMF Format

Edit `smf30_binary_parser.py` to match your exact record layout:

```python
def parse_type30_subtype1(self, data: bytes, offset: int):
    # Adjust offsets to match your SMF format
    
    # Example: If your job name is at offset 30 instead of 28:
    job_name = self.ebcdic_to_ascii(data[offset+30:offset+38])
    
    # Example: If CPU time is in milliseconds instead of microseconds:
    cpu_time_ms = struct.unpack('>I', data[offset+72:offset+76])[0]
    # (remove the "// 1000" conversion)
    
    # Add custom fields:
    custom_field = struct.unpack('>I', data[offset+200:offset+204])[0]
```

### Adding More Subtypes

Add parsers for subtypes 2-5:

```python
def parse_type30_subtype2(self, data: bytes, offset: int) -> Optional[SMF30Type2]:
    """Parse Subtype 2 - Job Termination"""
    try:
        # Total steps (offset X, 4 bytes)
        total_steps = struct.unpack('>I', data[offset+X:offset+X+4])[0]
        
        # Failed steps (offset Y, 4 bytes)
        failed_steps = struct.unpack('>I', data[offset+Y:offset+Y+4])[0]
        
        # ... add all fields ...
        
        record = SMF30Type2(
            total_steps=total_steps,
            failed_steps=failed_steps,
            # ... other fields ...
        )
        
        return record
    except Exception as e:
        print(f"Error parsing Type 30 Subtype 2: {e}")
        return None

# Then update parse_type30_record():
def parse_type30_record(self, data: bytes, offset: int, header: dict):
    subtype = data[offset+22]
    
    if subtype == 1:
        return self.parse_type30_subtype1(data, offset)
    elif subtype == 2:
        return self.parse_type30_subtype2(data, offset)
    elif subtype == 3:
        return self.parse_type30_subtype3(data, offset)
    # ... etc
```

---

## Working with Different SMF Sources

### 1. FTP from Mainframe
```powershell
# Transfer in binary mode
ftp mainframe.company.com
binary
get SMF.DUMP.D1204 smf_dump.bin
quit

# Parse it
python run_full_pipeline.py smf_dump.bin
```

### 2. Convert EBCDIC Text Dump
If you have a hex text dump:

```python
# Create convert_hex_dump.py
with open('smf_hex.txt', 'r') as f:
    hex_data = f.read().replace(' ', '').replace('\n', '')

binary_data = bytes.fromhex(hex_data)

with open('smf_dump.bin', 'wb') as f:
    f.write(binary_data)
```

### 3. Extract from SMF Dataset
Using IBM IFASMFDP utility on z/OS:
```jcl
//STEP1   EXEC PGM=IFASMFDP
//DUMPIN  DD DSN=SYS1.MAN.SMF,DISP=SHR
//DUMPOUT DD DSN=USER.SMF.DUMP,DISP=(NEW,CATLG),
//           SPACE=(CYL,(10,5)),
//           DCB=(RECFM=VBS,LRECL=32760,BLKSIZE=32764)
//SYSIN   DD *
  INDD(DUMPIN,OPTIONS(DUMP))
  OUTDD(DUMPOUT,TYPE(30))
/*
```

Then download DUMPOUT in binary.

---

## Validating Parsed Data

### Check Record Counts
```python
from smf30_binary_parser import SMFBinaryParser

parser = SMFBinaryParser("your_dump.bin")
records = parser.parse_dump_file()

# Verify counts match expected
for subtype, recs in records.items():
    if recs:
        print(f"Subtype {subtype}: {len(recs)} records")
        
        # Sample first record
        first = recs[0].to_dict()
        print(f"  Job: {first['job_name']}")
        print(f"  CPU: {first['cpu_time_ms']} ms")
```

### Compare with IBM Reports
Cross-reference with existing SMF reports from MICS, SAS, or other tools to validate:
- Record counts per subtype
- CPU time totals
- Job names and counts
- Time ranges

---

## Performance Tips

### Large Dump Files (>1GB)
```python
# Process in chunks instead of loading entire file
def parse_dump_file_chunked(self, chunk_size=10*1024*1024):  # 10MB chunks
    with open(self.dump_file, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            # Process chunk
```

### Filter by Date Range
```python
# Add date filtering in parse_type30_record()
from datetime import datetime, timedelta

def parse_type30_record(self, data: bytes, offset: int, header: dict):
    # Parse timestamp
    record_date = header['timestamp']
    
    # Only process last 7 days
    if record_date < datetime.now() - timedelta(days=7):
        return None
    
    # Continue normal parsing
```

### Process Specific Subtypes Only
```python
# In parse_dump_file(), add filter:
wanted_subtypes = [1, 2]  # Only parse subtypes 1 and 2

if subtype not in wanted_subtypes:
    offset += rdw_length
    continue
```

---

## Troubleshooting

### "Record type not 30"
- Your dump may contain multiple SMF record types (30, 70, 80, etc.)
- The parser automatically skips non-Type 30 records
- Check total records processed vs Type 30 records found

### "EBCDIC decode errors"
- Ensure file transferred in BINARY mode (not ASCII)
- Try different code pages: `'cp500'` (US), `'cp037'` (US), `'cp273'` (Germany)

### "Offset out of range"
- Record length (RDW) may be incorrect
- Check if your dump has a different format (RECFM=VB vs VBS)
- Validate first record manually with hex editor

### "All fields are zero"
- Wrong byte order (try little-endian: `<` instead of `>` in struct format)
- Wrong offsets for your SMF version
- Fields may be in different sections (productized sections, optional segments)

---

## Example: Complete Workflow

```powershell
# 1. Get your SMF dump from mainframe
# (via FTP, file transfer, etc.)

# 2. Create a test binary dump first
python smf30_binary_parser.py

# 3. Parse the test dump to verify
python run_full_pipeline.py reports/sample_smf30.dump

# 4. Check the output
dir reports\

# 5. Parse your real dump
python run_full_pipeline.py "C:\mainframe\smf_prod_20251204.bin"

# 6. View results
# - Check reports\*.csv for data
# - Open reports\*.png for visualizations
```

---

## Reference: IBM Documentation

- **z/OS MVS System Management Facilities (SMF)**  
  IBM manual SA22-7630
  
- **SMF Type 30 Record Layout**  
  Section describing all subtypes and field offsets
  
- **IFASMFDP Dump Utility**  
  For extracting SMF records from datasets

---

## Need Help?

Check:
1. README.md - General project documentation
2. smf30_structures.py - Record field definitions
3. smf30_binary_parser.py - Parser implementation with comments
4. IBM SMF manuals for your specific z/OS version
