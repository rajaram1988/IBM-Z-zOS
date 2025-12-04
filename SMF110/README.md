# SMF Type 110 CICS Statistics Analysis Tool

Complete IBM z/OS SMF Type 110 CICS statistics analysis system with report generation and comprehensive visualizations.

## Overview

SMF Type 110 records capture CICS (Customer Information Control System) performance statistics including:
- **Subtype 1**: Transaction Statistics
- **Subtype 2**: File Statistics  
- **Subtype 3**: Program Statistics
- **Subtype 4**: Terminal Statistics
- **Subtype 5**: Storage Statistics

## Features

- ✅ **5 CICS Subtypes Supported** - Transaction, File, Program, Terminal, Storage
- ✅ **CSV/JSON Reports** - Export statistics to standard formats
- ✅ **Rich Visualizations** - Matplotlib charts with performance analysis
- ✅ **Sample Data Generator** - Create realistic test data
- ⏳ **Binary Parser** - (Coming soon) Parse real SMF dumps

## Quick Start

### Installation

```powershell
# Install dependencies
pip install -r requirements.txt
```

### Usage

**Generate Reports with Sample Data:**
```powershell
python run_full_pipeline.py
```

This will create:
- 10 report files (5 CSV + 5 JSON)
- 6 visualization PNG files
- All outputs in `reports/` folder

### Output Files

**CSV Reports:**
- `smf110_subtype1_transactions.csv` - Transaction performance data
- `smf110_subtype2_files.csv` - File I/O statistics
- `smf110_subtype3_programs.csv` - Program execution metrics
- `smf110_subtype4_terminals.csv` - Terminal activity data
- `smf110_subtype5_storage.csv` - Storage pool utilization

**JSON Reports:**
- Same filenames with `.json` extension
- Includes summary statistics and detailed records

**Visualizations:**
- `smf110_subtype1_transactions_analysis.png` - Transaction charts (CPU, response time, I/O)
- `smf110_subtype2_files_analysis.png` - File performance (buffer hit ratio, response time)
- `smf110_subtype3_programs_analysis.png` - Program usage and efficiency
- `smf110_subtype4_terminals_analysis.png` - Terminal activity and errors
- `smf110_subtype5_storage_analysis.png` - Storage utilization and fragmentation
- `smf110_summary_dashboard.png` - Cross-subtype performance overview

## CICS Statistics Details

### Subtype 1: Transaction Statistics

Captures transaction-level performance:
- **Identification**: Transaction ID, Program, User, Terminal
- **Performance**: CPU time, Elapsed time, Response time
- **Resource Usage**: File requests, DB2 requests, TS/TD requests
- **I/O Metrics**: Reads, Writes, Browses, Deletes
- **Completion**: Completed, Abended, Errors

**Key Metrics:**
```python
transaction_id: str         # Transaction identifier (e.g., "TRN1")
cpu_time: float            # CPU time in milliseconds
response_time: float       # Response time in milliseconds
file_requests: int         # Number of file requests
completed: int             # Successfully completed transactions
abended: int              # Abnormally terminated transactions
```

### Subtype 2: File Statistics

File and dataset performance:
- **File Info**: File name, Dataset name, File type (VSAM/BDAM/DB2)
- **Operations**: Reads, Writes, Updates, Deletes, Browses
- **Performance**: Response times, Total I/O time
- **Buffer Metrics**: Requests, Hits, Misses, Hit ratio
- **VSAM**: String waits and requests
- **Errors**: I/O errors, Record not found, Duplicate key

**Key Metrics:**
```python
buffer_hit_ratio_pct: float    # Buffer efficiency (target: >80%)
avg_response_time_ms: float    # Average file response time
string_waits: int              # VSAM string contentions
io_errors: int                 # File I/O errors
```

### Subtype 3: Program Statistics

Program execution and resource usage:
- **Program Info**: Name, Length, Language (COBOL/PL/I/ASM/C/JAVA)
- **Execution**: Load count, Use count, Fetch count
- **Performance**: CPU time, Elapsed time
- **Storage**: Storage used, Violations
- **Location**: Library (DFHRPL), Location (MAIN/LPA/EXTENDED)
- **Errors**: Abends, Compression errors

**Key Metrics:**
```python
use_count: int               # Number of program invocations
cpu_time_ms: float          # Total CPU time
storage_used_bytes: int     # Memory consumption
abends: int                 # Program failures
```

### Subtype 4: Terminal Statistics

Terminal and session activity:
- **Terminal Info**: Terminal ID, Netname, Type (3270/3290/WEB)
- **Sessions**: Started, Ended
- **Transactions**: Total transaction count
- **I/O**: Messages sent/received, Bytes sent/received
- **Performance**: Average/Max response time
- **Errors**: Transmission errors, Timeout errors

**Key Metrics:**
```python
total_transactions: int        # Transactions from this terminal
messages_sent: int            # Output messages
bytes_sent: int              # Network data volume
transmission_errors: int      # Communication failures
```

### Subtype 5: Storage Statistics

CICS storage pool utilization:
- **Pool Info**: Pool name (CDSA/ERDSA/ECDSA/UDSA), Type
- **Storage**: Total, Used, Free, Peak
- **Allocation**: GETMAIN/FREEMAIN requests, Failures
- **Performance**: Allocation times
- **Fragmentation**: Fragment count, Largest fragment

**Key Metrics:**
```python
utilization_pct: float         # Storage usage percentage
failed_getmains: int          # Failed storage allocations
fragments: int                # Storage fragmentation level
peak_storage_bytes: int       # Maximum storage used
```

## Project Structure

```
SMF110/
├── smf110_structures.py       # Record definitions (all 5 subtypes)
├── smf110_parser.py           # CSV/JSON report generator
├── smf110_analysis.py         # Visualization engine
├── run_full_pipeline.py       # Complete pipeline runner
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── reports/                   # Output directory (auto-created)
```

## Sample Data

The sample generator creates realistic CICS statistics:

**Transaction IDs**: TRN1, TRN2, TRN3, ACCT, INV, ORD, PAY  
**Programs**: PROG001, PROG002, COBOL01, PL1PROG, ASMPROG  
**Files**: CUSTFILE, INVFILE, ORDFILE, PAYFILE, TEMPFILE  
**Terminals**: T001, T002, T003, T004, T005  
**Storage Pools**: CDSA, ERDSA, ECDSA, UDSA, EUDSA

## Visualization Charts

### Transaction Analysis (6 charts)
1. CPU Time by Transaction - Bar chart
2. Response Time Distribution - Histogram with mean line
3. Transaction Count by ID - Horizontal bar
4. File vs DB2 Requests - Grouped bar
5. Completion Status - Stacked bar (completed/abended)
6. I/O Operations Distribution - Pie chart

### File Analysis (6 charts)
1. File Operations by File - Grouped bar (read/write/update)
2. Buffer Hit Ratio - Horizontal bar with 80% target line
3. Average Response Time - Bar chart
4. Total I/O by File Type - Pie chart
5. I/O Errors - Red bar chart
6. String Waits vs Requests - Grouped bar

### Program Analysis (6 charts)
1. Program Usage Count - Horizontal bar
2. CPU Time by Program - Bar chart
3. Storage Usage - Bar chart (in KB)
4. Language Distribution - Pie chart
5. Abends by Program - Red bar chart
6. Load Count vs Use Count - Grouped bar

### Terminal Analysis (4 charts)
1. Total Transactions by Terminal - Bar chart
2. Messages Sent vs Received - Grouped bar
3. Data Volume Sent (KB) - Bar chart
4. Transmission Errors - Red bar chart

### Storage Analysis (4 charts)
1. Storage Utilization by Pool (MB) - Grouped bar (used/free)
2. Utilization Percentage - Horizontal bar with color coding (green<70%, orange<85%, red≥85%)
3. GETMAIN/FREEMAIN Activity - Grouped bar
4. Failed GETMAIN Requests - Red bar chart

### Summary Dashboard (6 panels)
1. Record Count by Subtype
2. CPU Time by Transaction - Pie chart
3. Total File I/O Operations - Bar chart
4. Program Language Distribution - Pie chart
5. Transactions by Terminal - Horizontal bar
6. Storage Pool Utilization - Color-coded bar (warning/critical thresholds)

## Customization

### Modify Sample Data

Edit `smf110_structures.py`:

```python
TRANSACTION_IDS = ["MYTRN", "CUSTOM", ...]
PROGRAM_NAMES = ["MYPROG", ...]
```

### Adjust Chart Colors

Edit `smf110_analysis.py`:

```python
self.colors = ['#1f77b4', '#ff7f0e', ...]  # Your color scheme
```

### Change Output Directory

```python
generator = SMF110ReportGenerator(output_dir="my_reports")
visualizer = SMF110Visualizer(output_dir="my_charts")
```

## Performance Thresholds

**Response Time:**
- Good: < 100ms
- Warning: 100-500ms
- Critical: > 500ms

**Buffer Hit Ratio:**
- Good: ≥ 80%
- Warning: 60-79%
- Critical: < 60%

**Storage Utilization:**
- Green: < 70%
- Orange: 70-84%
- Red: ≥ 85%

## Requirements

- Python 3.7+
- matplotlib 3.8+
- pandas 2.1+
- numpy 1.26+

## Future Enhancements

- [ ] Binary SMF dump parser (similar to SMF30)
- [ ] EBCDIC encoding support
- [ ] Additional CICS subtypes (6-10)
- [ ] Interactive dashboards
- [ ] Trend analysis across time periods
- [ ] Alerting based on thresholds

## Related Tools

- **SMF30** - Job/Step completion records (in ../SMF30/)
- **SMF113** - Hardware instrumentation (in ../SMF-Tools/SMF113Formatter/)

## License

MIT License - see LICENSE file for details

## Author

Created for CICS performance monitoring and mainframe statistics analysis.
