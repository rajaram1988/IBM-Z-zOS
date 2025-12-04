# Using Real SMF 110 Dump Files

This guide explains how to use the SMF 110 binary parser to analyze actual CICS statistics dumps from z/OS.

## Quick Start

```powershell
# Parse binary SMF 110 dump
python run_full_pipeline.py "path\to\smf110.dump"
```

## Binary SMF 110 Format Details

### SMF Record Structure (IBM z/OS CICS)

```
Offset  Length  Field Name              Format
------  ------  ----------------------  --------------------
0       2       RDW Length              Binary (big-endian)
2       2       RDW Reserved            Binary
4       2       Record Length           Binary
6       1       Segment Descriptor      Binary
7       1       Flags                   Binary
8       1       Record Type (110)       Binary
9       1       Reserved                Binary
10      4       Timestamp (TOD)         Binary (z/OS TOD clock)
14      4       System ID               EBCDIC
18      4       Subsystem ID            EBCDIC
22      1       Subtype                 Binary (1-15+)
23      8       CICS APPLID             EBCDIC
31      8       CICS Jobname            EBCDIC
39      4       CICS Release            EBCDIC
43      2       SMF Release             EBCDIC
45      ...     Subtype-specific data   Various
```

### Subtype 1: Transaction Statistics (Offset 50+)

```
Offset  Length  Field
------  ------  ----------------------
50      4       Transaction ID (EBCDIC)
54      8       Program Name (EBCDIC)
62      8       User ID (EBCDIC)
70      4       Terminal ID (EBCDIC)
74      4       Transaction Count (binary)
78      4       CPU Time (microseconds)
82      4       Elapsed Time (1/100 sec)
86      4       Response Time (1/100 sec)
90      4       File Requests
94      4       DB2 Requests
98      4       TS Requests
102     4       TD Requests
106     4       Reads
110     4       Writes
114     4       Browses
118     4       Deletes
122     4       Completed
126     4       Abended
130     4       Errors
```

### Subtype 2: File Statistics (Offset 50+)

```
Offset  Length  Field
------  ------  ----------------------
50      8       File Name (EBCDIC)
58      44      Dataset Name (EBCDIC)
102     4       File Type (EBCDIC)
106     4       Reads
110     4       Writes
114     4       Updates
118     4       Deletes
122     4       Browses
126     4       Avg Response Time (us)
130     4       Max Response Time (us)
134     4       Total I/O Time (us)
138     4       Buffer Requests
142     4       Buffer Hits
146     4       Buffer Misses
150     4       String Waits
154     4       String Requests
158     4       I/O Errors
162     4       Record Not Found
166     4       Duplicate Key
```

## Obtaining SMF 110 Dumps from z/OS

### Method 1: IFASMFDP (SMF Dump Program)

```jcl
//SMFDUMP  JOB  ...
//STEP1    EXEC PGM=IFASMFDP
//INDD     DD   DSN=SYS1.MAN1,DISP=SHR      Input SMF dataset
//OUTDD    DD   DSN=USER.SMF110.DUMP,       Output dump file
//              DISP=(NEW,CATLG,DELETE),
//              SPACE=(CYL,(10,5),RLSE),
//              DCB=(RECFM=VBS,LRECL=32760,BLKSIZE=32764)
//SYSIN    DD   *
  INDD(INDD,OPTIONS(DUMP))
  OUTDD(OUTDD,TYPE(110))                    Select Type 110 only
  DATE(2024335,2024336)                      Date range
/*
```

### Method 2: Direct SMF Dataset Extract

```jcl
//EXTRACT  JOB  ...
//STEP1    EXEC PGM=IEBGENER
//SYSUT1   DD   DSN=SYS1.MAN1,DISP=SHR
//SYSUT2   DD   DSN=USER.SMF110.BINARY,
//              DISP=(NEW,CATLG,DELETE),
//              SPACE=(CYL,(5,1),RLSE)
//SYSIN    DD   DUMMY
//SYSPRINT DD   SYSOUT=*
```

### Method 3: FTP Transfer to Windows

```
ftp mainframe.example.com
> binary
> quote site recfm=vbs lrecl=32760 blksize=32764
> get 'USER.SMF110.DUMP' smf110.dump
> quit
```

## Parser Features

### Supported Subtypes

Currently implemented:
- ✅ **Subtype 1** - Transaction Statistics (full parser)
- ✅ **Subtype 2** - File Statistics (full parser)
- ⏳ **Subtypes 3-15** - Structure defined, parsers TODO

### EBCDIC Encoding

The parser automatically converts EBCDIC (code page 500) to ASCII:
- System IDs
- CICS APPLID
- Jobnames
- Transaction IDs
- File names
- Program names
- User IDs

### Binary Field Formats

All binary fields use **big-endian** format (mainframe standard):
- 2-byte integers: `>H`
- 4-byte integers: `>I`
- Times in microseconds or 1/100 seconds

### Error Handling

The parser includes:
- RDW validation
- Record type verification
- Graceful skipping of unparseable records
- Progress indicators for large files
- Detailed error messages

## Example Usage

### Parse and Display Summary

```powershell
python smf110_binary_parser.py smf110.dump
```

Output:
```
[INFO] Parsing SMF 110 dump: smf110.dump
[INFO] File size: 524288 bytes
[INFO] Parsed 100 records...
[INFO] Parsed 200 records...

[OK] Parsed 247 total records
  - Subtype 1: 150 records
  - Subtype 2: 97 records

============================================================
Sample Subtype 1 Record:
============================================================
  record_type: 110
  system_id: SYSZ1
  cics_applid: CICSRGN1
  transaction_id: TRN1
  cpu_time_ms: 125.450
  ...
```

### Full Pipeline with Reports

```powershell
python run_full_pipeline.py smf110.dump
```

Generates:
- CSV reports for each subtype
- JSON reports with metadata
- PNG visualization charts

## Troubleshooting

### Issue: "Not an SMF Type 110 record"

**Cause:** Dump file contains mixed record types

**Solution:** Filter for Type 110 during dump extraction:
```jcl
OUTDD(OUTDD,TYPE(110))
```

### Issue: "Failed to parse record at offset X"

**Possible causes:**
1. **Incorrect RDW format** - Check RECFM=VBS
2. **Corrupted data** - Verify FTP used BINARY mode
3. **Wrong encoding** - Should be EBCDIC cp500

**Debug:**
```python
# View raw hex at problem offset
with open('smf110.dump', 'rb') as f:
    f.seek(offset)
    print(f.read(100).hex())
```

### Issue: "Subtype X parser not yet implemented"

**Expected:** Parsers for subtypes 3-15 are planned

**Current support:**
- Subtype 1 (Transaction): ✅ Full
- Subtype 2 (File): ✅ Full
- Subtypes 3-15: Structure defined, parser TODO

## Binary Format Notes

### RDW (Record Descriptor Word)

IBM z/OS variable-length records start with RDW:
- First 2 bytes: Total record length (including RDW)
- Must be even number (padding added if needed)
- Parser uses RDW to navigate between records

### EBCDIC Details

Common EBCDIC characters:
```
Space   = 0x40
A-Z     = 0xC1-0xE9
0-9     = 0xF0-0xF9
```

Parser uses `cp500` codec for conversion.

### Time Formats

CICS uses multiple time formats:
- **TOD Clock**: 8-byte z/OS timestamp (not fully implemented)
- **Microseconds**: 4-byte binary for CPU times
- **1/100 seconds**: 4-byte binary for elapsed/response times

Parser converts to milliseconds for consistency.

## Performance

Typical parsing speed:
- **Small dumps** (<1 MB): < 1 second
- **Medium dumps** (1-10 MB): 1-5 seconds
- **Large dumps** (10-100 MB): 5-30 seconds

Progress indicators show every 100 records.

## Next Steps

1. **Verify subtypes** - Check your dump has expected subtypes:
   ```powershell
   python smf110_binary_parser.py yourdump.dump
   ```

2. **Generate reports** - Run full pipeline:
   ```powershell
   python run_full_pipeline.py yourdump.dump
   ```

3. **Analyze charts** - Review PNG visualizations in `reports/`

## Related Documentation

- **README.md** - Main project documentation
- **smf110_structures.py** - Record definitions for all 15 subtypes
- **smf110_binary_parser.py** - Binary parser implementation
