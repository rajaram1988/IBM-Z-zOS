# SMF Type 30 Record Analysis - Complete Documentation

## Project Overview

This project provides a comprehensive solution for analyzing **IBM z/OS SMF Type 30 Records**. SMF (System Management Facilities) Type 30 records contain job/step completion information and are critical for:

- Performance analysis
- Resource capacity planning  
- Cost accounting
- Job execution tracking

## Project Structure

```
SMF/
├── smf30_structures.py      # SMF-30 record definitions and sample data generator
├── smf30_parser.py          # Parser for SMF-30 records, generates CSV/JSON reports
├── smf30_analysis.py        # Analysis engine with visualization generation
├── run_full_pipeline.py     # Complete execution pipeline
├── test_import.py           # Basic import tests
├── requirements.txt         # Python package dependencies
└── reports/                 # Output directory (created at runtime)
    ├── smf30_subtype1.csv     # Job Step Termination records
    ├── smf30_subtype2.csv     # Job Termination records
    ├── smf30_subtype3.csv     # Step Initiation records
    ├── smf30_subtype4.csv     # Job Initiation records
    ├── smf30_subtype5.csv     # NetStep Completion records
    ├── smf30_subtype1_analysis.png    # Step performance charts
    ├── smf30_subtype2_analysis.png    # Job resource usage charts
    ├── smf30_subtype3_analysis.png    # Step initialization charts
    ├── smf30_subtype4_analysis.png    # Job scheduling charts
    ├── smf30_subtype5_analysis.png    # Network performance charts
    └── smf30_summary_dashboard.png    # Overall system dashboard
```

## SMF Type 30 Record Subtypes

### Subtype 1: Job Step Termination (JMJST)
**Purpose:** Records step-level performance metrics when a step completes.

**Key Fields:**
- Step name and program name
- CPU time, elapsed time, I/O count
- Pages read/written, EXCP count
- Return code, termination code
- Service units consumed

**Analysis Focus:**
- Step performance characteristics
- Resource consumption per step
- Error detection and troubleshooting
- CPU to I/O ratio analysis

---

### Subtype 2: Job Termination (JMTERM)
**Purpose:** Records overall job metrics when the entire job completes.

**Key Fields:**
- Total steps executed and failed steps count
- Total CPU time, elapsed time, service units
- Memory allocated and maximum used
- Total pages and EXCP operations
- Job termination code

**Analysis Focus:**
- Overall job performance
- Memory utilization efficiency
- Total resource consumption
- Success vs. failure rates
- Job class characteristics

---

### Subtype 3: Step Initiation (JMINIT)
**Purpose:** Records step startup details when a step begins execution.

**Key Fields:**
- Step name and program name
- Step start time
- Procedure step name
- Memory region size
- Accounting code

**Analysis Focus:**
- Step initialization timing
- Memory allocation patterns
- Procedure flow analysis
- Accounting and chargeback

---

### Subtype 4: Job Initiation (JMJINI)
**Purpose:** Records job startup details when a job begins.

**Key Fields:**
- Job start time
- Job class and priority
- Scheduling environment (JES2/JES3)
- Accounting code
- Owning user ID

**Analysis Focus:**
- Job scheduling patterns
- Priority distribution
- User submission analysis
- Job class characteristics

---

### Subtype 5: NetStep Completion (JMNET)
**Purpose:** Records network communication for remote job steps.

**Key Fields:**
- NetStep name and network destination
- Network protocol (TCP/IP, etc.)
- Bytes transmitted and received
- Network response time
- Return code
- CPU time and service units

**Analysis Focus:**
- Network performance
- Data transfer efficiency
- Response time analysis
- Network protocol usage
- Remote job execution metrics

---

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation Steps

1. **Install Python packages:**
   ```powershell
   cd "C:\Users\Nalan\Desktop\SMF"
   pip install -r requirements.txt
   ```

2. **Dependencies:**
   - `matplotlib`: For creating charts and visualizations
   - `pandas`: For data analysis and CSV operations
   - `numpy`: For numerical computations

### Quick Start

Run the complete analysis pipeline:

```powershell
cd "C:\Users\Nalan\Desktop\SMF"
python run_full_pipeline.py
```

This will:
1. Generate sample SMF-30 records for all 5 subtypes
2. Create CSV and JSON report files for each subtype
3. Generate detailed analysis charts for each subtype
4. Create a comprehensive summary dashboard

## Usage Examples

### Option 1: Full Pipeline (Recommended)
```python
python run_full_pipeline.py
```
Generates everything: records, reports, and visualizations.

### Option 2: Records Only
```python
from smf30_structures import SMF30SampleGenerator
records = SMF30SampleGenerator.generate_all_records()
# Use records directly in memory
```

### Option 3: Parser Only
```python
from smf30_parser import SMF30Parser
parser = SMF30Parser(output_dir="./reports")
parser.generate_sample_records()
parser.generate_all_reports()
# Generates CSV/JSON files
```

### Option 4: Analysis Only
```python
from smf30_analysis import SMF30Analyzer
analyzer = SMF30Analyzer(output_dir="./reports")
analyzer.load_sample_data()
analyzer.generate_all_visualizations()
# Generates PNG charts
```

## Output Files

### CSV Reports
Each subtype generates a CSV file with all records and their fields.

**Example - Subtype 1:**
```
subtype,subtype_name,record_type,cpu_time_ms,elapsed_time_ms,io_count,...
1,Job Step Termination,30,5234,10500,750,...
1,Job Step Termination,30,3450,8200,620,...
```

### JSON Reports
Detailed JSON format with full data hierarchies.

### Visualizations

Each subtype gets custom visualizations highlighting key metrics:

**Subtype 1 (Step Termination):**
- CPU time distribution histogram
- Return code frequency chart
- CPU vs. I/O scatter plot
- Elapsed time per step
- Pages read/written comparison
- Service units bar chart
- Statistics table with min/max/mean

**Subtype 2 (Job Termination):**
- Total CPU time comparison
- Total vs. failed steps
- Memory allocation vs. usage
- Total EXCP operations
- Total pages read/written
- Job class distribution
- Statistics with success rates

**Subtype 3 (Step Initiation):**
- Memory region size distribution
- Step name frequency
- Program distribution (pie chart)
- Step initiation timeline
- Key statistics table

**Subtype 4 (Job Initiation):**
- Job class distribution
- Job priority levels scatter
- User ID distribution
- Job initiation timeline
- Statistics summary

**Subtype 5 (NetStep Completion):**
- Bytes transmitted vs. received
- Network response time
- Return code distribution
- CPU time per netstep
- Network destination distribution
- Data size vs. service units
- Network performance statistics

**Summary Dashboard:**
- Record counts by subtype
- Average CPU time comparison
- Success rates across subtypes
- Detailed subtype reference table

## Data Analysis & Insights

### Performance Metrics

**CPU Efficiency:**
- Compare CPU time to elapsed time (CPU% = CPU / Elapsed)
- Identify CPU-bound vs. I/O-bound jobs
- Track service unit consumption

**Memory Efficiency:**
- Memory allocation vs. actual usage
- Peak memory requirements
- Memory trend analysis over time

**I/O Performance:**
- Pages read/written per job
- EXCP count analysis (indicates I/O operations)
- I/O throughput estimation

**Network Performance:**
- Response time analysis
- Data transfer efficiency (bytes per unit time)
- Network protocol effectiveness

### Troubleshooting

Use the return codes to identify issues:
- **Return Code 0:** Success
- **Return Code 4:** Warning, job completed with issues
- **Return Code 8:** Error, job failed
- **Return Code 12+:** Severe error, likely abormal termination

## Example Analyses

### 1. Cost Attribution
```python
# Use Subtype 2 data to calculate job costs
cpu_cost_per_sec = 0.05  # $ per CPU second
job_cpu_seconds = df['cpu_time_ms'] / 1000
job_cost = job_cpu_seconds * cpu_cost_per_sec
```

### 2. Resource Capacity Planning
```python
# Use Subtype 2 for resource trends
avg_memory_per_job = df['memory_max_used_mb'].mean()
peak_memory = df['memory_allocated_mb'].max()
memory_headroom = peak_memory - avg_memory_per_job
```

### 3. Performance Bottleneck Detection
```python
# Use Subtype 1 to identify slow steps
df['cpu_io_ratio'] = df['cpu_time_ms'] / df['io_count']
# High ratio = CPU-bound
# Low ratio = I/O-bound
slow_steps = df[df['elapsed_time_ms'] > df['elapsed_time_ms'].quantile(0.9)]
```

### 4. Network Performance Monitoring
```python
# Use Subtype 5 for network analysis
avg_response = df['network_response_time_ms'].mean()
throughput = (df['bytes_received'] + df['bytes_transmitted']) / df['elapsed_time_ms']
```

## Customization

### Adding Custom Sample Data
Edit `SMF30SampleGenerator` class in `smf30_structures.py`:

```python
class SMF30SampleGenerator:
    JOB_NAMES = ["YOUR_JOB", ...]  # Add your job names
    USERIDS = ["YOUR_USER", ...]   # Add your user IDs
    PROGRAMS = ["YOUR_PROG", ...]  # Add your programs
```

### Modifying Record Fields
Update the dataclass definitions in `smf30_structures.py`:

```python
@dataclass
class SMF30Type1:
    your_new_field: int = 0  # Add new field
    # ... existing fields ...
```

### Creating Real Data Parser
Replace the sample generator with your actual SMF dump parser:

1. Parse binary SMF dump file format
2. Extract record segments using struct module
3. Map binary data to dataclass fields
4. Use existing parser/analysis pipeline

### Customizing Visualizations
Edit chart creation in `smf30_analysis.py`:

```python
def create_subtype1_visualization(self):
    # Modify colors
    self.colors = ['#FF6B6B', '#4ECDC4', ...]  # Use hex colors
    
    # Add new charts
    ax_new = fig.add_subplot(gs[new_row, new_col])
    ax_new.plot(...)
```

## File Format Reference

### Binary SMF-30 Record Layout (Conceptual)

```
Offset  Length  Field
------  ------  -----
0       4       Record Length
4       1       Record Type (30)
5       1       Segment Number
6       2       Flags
8       4       Time Stamp (TOD)
12      4       CPU Time (milliseconds)
16      4       I/O Count
...     ...     [Type-specific fields]
```

For detailed binary format specifications, refer to IBM z/OS System Management Facilities (SMF) documentation.

## Troubleshooting

### Issue: "Module not found" error
**Solution:** Ensure all dependencies are installed:
```powershell
pip install -r requirements.txt
```

### Issue: Output files not created
**Solution:** Check that `./reports` directory is writable:
```powershell
mkdir reports
```

### Issue: Charts look distorted
**Solution:** Ensure matplotlib is properly installed:
```powershell
pip install --upgrade matplotlib
```

## Performance Notes

- Sample data generation: ~100 records, <100ms
- CSV report generation: ~10ms per subtype
- JSON report generation: ~10ms per subtype
- Chart generation: ~500ms per subtype
- Total pipeline: ~3 seconds on modern hardware

## References

- IBM z/OS System Management Facilities (SMF) manuals
- SMF Type 30 Record User Documentation
- Performance and Capacity Planning guides

## License & Support

For questions or issues, refer to the inline code documentation and analysis output.

---

**Project Status:** Complete and functional with sample data

**Last Updated:** December 4, 2025
