# SMF Type 30 Record Analysis Tool

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Complete IBM z/OS SMF Type 30 record analysis system with binary dump parsing, report generation, and comprehensive visualizations.

## Features

- ✅ **Parse Binary SMF Dumps** - Read actual SMF Type 30 records from mainframe dump files
- ✅ **Generate Sample Data** - Create realistic test data for development/testing
- ✅ **5 Subtypes Supported** - Job Step, Job Termination, Step Init, Job Init, NetStep
- ✅ **CSV/JSON Reports** - Export records to standard formats
- ✅ **Rich Visualizations** - Matplotlib charts with performance analysis
- ✅ **Interactive Notebook** - Jupyter notebook for exploration
- ✅ **EBCDIC Support** - Automatic conversion from mainframe encoding

## Quick Start

### Installation

```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/SMF.git
cd SMF

# Install dependencies
pip install -r requirements.txt
```

### Usage

**Option 1: Use Sample Data**
```powershell
python run_full_pipeline.py
```

**Option 2: Parse Real SMF Dump**
```powershell
python run_full_pipeline.py "path/to/smf_dump.bin"
```

**Option 3: Interactive Notebook**
```powershell
# Open SMF30_Analysis.ipynb in VS Code or Jupyter
```

## Project Structure

```
SMF/
├── smf30_structures.py           # Record definitions (all 5 subtypes)
├── smf30_binary_parser.py        # Binary dump file parser
├── smf30_parser.py               # CSV/JSON report generator
├── smf30_analysis.py             # Visualization engine
├── run_full_pipeline.py          # Complete pipeline runner
├── SMF30_Analysis.ipynb          # Interactive Jupyter notebook
├── standalone_generate_reports.py # Standalone report generator
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── BINARY_DUMP_GUIDE.md         # Binary dump usage guide
└── reports/                      # Output directory
```

## SMF Type 30 Subtypes

| Subtype | Name | Description | Key Metrics |
|---------|------|-------------|-------------|
| 1 | Job Step Termination | Step-level completion | CPU, I/O, Pages, Return Code |
| 2 | Job Termination | Overall job completion | Total Resources, Memory, Steps |
| 3 | Step Initiation | Step startup | Memory Allocation, Start Time |
| 4 | Job Initiation | Job startup | Priority, Class, Scheduling |
| 5 | NetStep Completion | Network step | Data Transfer, Response Time |

## Output Examples

### CSV Reports
- `smf30_subtype1.csv` - Job step performance data
- `smf30_subtype2.csv` - Job-level resource usage
- etc.

### Visualizations
- `smf30_subtype1_analysis.png` - CPU time, I/O, return codes
- `smf30_subtype2_analysis.png` - Memory efficiency, job metrics
- `smf30_summary_dashboard.png` - Cross-subtype dashboard

## Documentation

- **[README.md](README.md)** - This file (project overview)
- **[BINARY_DUMP_GUIDE.md](BINARY_DUMP_GUIDE.md)** - Using real SMF dumps
- **Inline code comments** - Detailed implementation notes

## Requirements

- Python 3.7+
- matplotlib 3.8+
- pandas 2.1+
- numpy 1.26+

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - see LICENSE file for details

## Author

Created for SMF Type 30 analysis and mainframe performance monitoring.

## Acknowledgments

- IBM z/OS SMF documentation
- Python data science community
