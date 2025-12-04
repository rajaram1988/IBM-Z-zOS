"""
SMF Type 110 Record Structures - CICS Statistics Records
SMF Type 110 provides CICS statistics for transactions, files, programs, and resources
Common subtypes: 1=Transaction, 2=File, 3=Program, 4=Terminal, 5=Storage
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime, timedelta
import random

# ============ SMF 110 Record Header ============
@dataclass
class SMF110Header:
    """Common SMF header for Type 110 CICS records"""
    record_type: int = 110
    record_length: int = 0
    segment_number: int = 1
    flags: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    system_id: str = "SYSZ1"
    subsystem_id: str = "CICS"
    cics_applid: str = "CICSRGN1"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'record_type': self.record_type,
            'record_length': self.record_length,
            'segment_number': self.segment_number,
            'flags': self.flags,
            'timestamp': self.timestamp.isoformat(),
            'system_id': self.system_id,
            'subsystem_id': self.subsystem_id,
            'cics_applid': self.cics_applid,
        }

# ============ Common Fields ============
@dataclass
class CICSIdentification:
    """CICS region identification"""
    applid: str = "CICSRGN1"
    jobname: str = "CICSJOB1"
    release: str = "0660"
    smf_release: str = "01"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'applid': self.applid,
            'jobname': self.jobname,
            'release': self.release,
            'smf_release': self.smf_release,
        }

@dataclass
class PerformanceMetrics:
    """Common performance metrics"""
    cpu_time: float = 0.0  # CPU time in milliseconds
    elapsed_time: float = 0.0  # Elapsed time in milliseconds
    wait_time: float = 0.0  # Wait time in milliseconds
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'cpu_time_ms': round(self.cpu_time, 3),
            'elapsed_time_ms': round(self.elapsed_time, 3),
            'wait_time_ms': round(self.wait_time, 3),
        }

# ============ Subtype 1: Transaction Statistics ============
@dataclass
class SMF110Type1:
    """Subtype 1 - CICS Transaction Statistics"""
    header: SMF110Header = field(default_factory=SMF110Header)
    identification: CICSIdentification = field(default_factory=CICSIdentification)
    
    # Transaction identification
    transaction_id: str = "TRN1"
    program_name: str = "PROG001"
    userid: str = "USER001"
    terminal_id: str = "T001"
    
    # Performance metrics
    transaction_count: int = 0
    cpu_time: float = 0.0  # milliseconds
    elapsed_time: float = 0.0
    response_time: float = 0.0
    
    # Resource usage
    file_requests: int = 0
    db2_requests: int = 0
    ts_requests: int = 0  # Temporary storage
    td_requests: int = 0  # Transient data
    
    # I/O metrics
    reads: int = 0
    writes: int = 0
    browses: int = 0
    deletes: int = 0
    
    # Transaction completion
    completed: int = 0
    abended: int = 0
    errors: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.header.to_dict(),
            **self.identification.to_dict(),
            'subtype': 1,
            'subtype_name': 'Transaction Statistics',
            'transaction_id': self.transaction_id,
            'program_name': self.program_name,
            'userid': self.userid,
            'terminal_id': self.terminal_id,
            'transaction_count': self.transaction_count,
            'cpu_time_ms': round(self.cpu_time, 3),
            'elapsed_time_ms': round(self.elapsed_time, 3),
            'response_time_ms': round(self.response_time, 3),
            'file_requests': self.file_requests,
            'db2_requests': self.db2_requests,
            'ts_requests': self.ts_requests,
            'td_requests': self.td_requests,
            'reads': self.reads,
            'writes': self.writes,
            'browses': self.browses,
            'deletes': self.deletes,
            'completed': self.completed,
            'abended': self.abended,
            'errors': self.errors,
        }

# ============ Subtype 2: File Statistics ============
@dataclass
class SMF110Type2:
    """Subtype 2 - CICS File Statistics"""
    header: SMF110Header = field(default_factory=SMF110Header)
    identification: CICSIdentification = field(default_factory=CICSIdentification)
    
    # File identification
    file_name: str = "FILE001"
    dataset_name: str = "USER.CICS.FILE001"
    file_type: str = "VSAM"
    
    # File operations
    reads: int = 0
    writes: int = 0
    updates: int = 0
    deletes: int = 0
    browses: int = 0
    
    # Performance
    avg_response_time: float = 0.0  # milliseconds
    max_response_time: float = 0.0
    total_io_time: float = 0.0
    
    # Buffer metrics
    buffer_requests: int = 0
    buffer_hits: int = 0
    buffer_misses: int = 0
    
    # String metrics (VSAM)
    string_waits: int = 0
    string_requests: int = 0
    
    # Errors
    io_errors: int = 0
    record_not_found: int = 0
    duplicate_key: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        buffer_hit_ratio = 0.0
        if self.buffer_requests > 0:
            buffer_hit_ratio = (self.buffer_hits / self.buffer_requests) * 100
            
        return {
            **self.header.to_dict(),
            **self.identification.to_dict(),
            'subtype': 2,
            'subtype_name': 'File Statistics',
            'file_name': self.file_name,
            'dataset_name': self.dataset_name,
            'file_type': self.file_type,
            'reads': self.reads,
            'writes': self.writes,
            'updates': self.updates,
            'deletes': self.deletes,
            'browses': self.browses,
            'avg_response_time_ms': round(self.avg_response_time, 3),
            'max_response_time_ms': round(self.max_response_time, 3),
            'total_io_time_ms': round(self.total_io_time, 3),
            'buffer_requests': self.buffer_requests,
            'buffer_hits': self.buffer_hits,
            'buffer_misses': self.buffer_misses,
            'buffer_hit_ratio_pct': round(buffer_hit_ratio, 2),
            'string_waits': self.string_waits,
            'string_requests': self.string_requests,
            'io_errors': self.io_errors,
            'record_not_found': self.record_not_found,
            'duplicate_key': self.duplicate_key,
        }

# ============ Subtype 3: Program Statistics ============
@dataclass
class SMF110Type3:
    """Subtype 3 - CICS Program Statistics"""
    header: SMF110Header = field(default_factory=SMF110Header)
    identification: CICSIdentification = field(default_factory=CICSIdentification)
    
    # Program identification
    program_name: str = "PROG001"
    program_length: int = 0  # bytes
    language: str = "COBOL"
    
    # Execution metrics
    load_count: int = 0
    use_count: int = 0
    fetch_count: int = 0
    
    # Performance
    cpu_time: float = 0.0  # milliseconds
    elapsed_time: float = 0.0
    
    # Storage
    storage_used: int = 0  # bytes
    storage_violations: int = 0
    
    # Program location
    library: str = "DFHRPL"
    location: str = "MAIN"
    
    # Errors
    abends: int = 0
    compression_errors: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.header.to_dict(),
            **self.identification.to_dict(),
            'subtype': 3,
            'subtype_name': 'Program Statistics',
            'program_name': self.program_name,
            'program_length_bytes': self.program_length,
            'language': self.language,
            'load_count': self.load_count,
            'use_count': self.use_count,
            'fetch_count': self.fetch_count,
            'cpu_time_ms': round(self.cpu_time, 3),
            'elapsed_time_ms': round(self.elapsed_time, 3),
            'storage_used_bytes': self.storage_used,
            'storage_violations': self.storage_violations,
            'library': self.library,
            'location': self.location,
            'abends': self.abends,
            'compression_errors': self.compression_errors,
        }

# ============ Subtype 4: Terminal Statistics ============
@dataclass
class SMF110Type4:
    """Subtype 4 - CICS Terminal Statistics"""
    header: SMF110Header = field(default_factory=SMF110Header)
    identification: CICSIdentification = field(default_factory=CICSIdentification)
    
    # Terminal identification
    terminal_id: str = "T001"
    netname: str = "TERM001"
    terminal_type: str = "3270"
    
    # Session metrics
    sessions_started: int = 0
    sessions_ended: int = 0
    total_transactions: int = 0
    
    # I/O metrics
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    
    # Performance
    avg_response_time: float = 0.0  # milliseconds
    max_response_time: float = 0.0
    
    # Errors
    transmission_errors: int = 0
    timeout_errors: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.header.to_dict(),
            **self.identification.to_dict(),
            'subtype': 4,
            'subtype_name': 'Terminal Statistics',
            'terminal_id': self.terminal_id,
            'netname': self.netname,
            'terminal_type': self.terminal_type,
            'sessions_started': self.sessions_started,
            'sessions_ended': self.sessions_ended,
            'total_transactions': self.total_transactions,
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'avg_response_time_ms': round(self.avg_response_time, 3),
            'max_response_time_ms': round(self.max_response_time, 3),
            'transmission_errors': self.transmission_errors,
            'timeout_errors': self.timeout_errors,
        }

# ============ Subtype 5: Storage Statistics ============
@dataclass
class SMF110Type5:
    """Subtype 5 - CICS Storage Statistics"""
    header: SMF110Header = field(default_factory=SMF110Header)
    identification: CICSIdentification = field(default_factory=CICSIdentification)
    
    # Storage pool identification
    pool_name: str = "CDSA"  # CICS Dynamic Storage Area
    pool_type: str = "DYNAMIC"
    
    # Storage metrics
    total_storage: int = 0  # bytes
    used_storage: int = 0
    free_storage: int = 0
    peak_storage: int = 0
    
    # Allocation metrics
    getmain_requests: int = 0
    freemain_requests: int = 0
    failed_getmains: int = 0
    
    # Performance
    avg_allocation_time: float = 0.0  # microseconds
    max_allocation_time: float = 0.0
    
    # Fragmentation
    fragments: int = 0
    largest_fragment: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        utilization = 0.0
        if self.total_storage > 0:
            utilization = (self.used_storage / self.total_storage) * 100
            
        return {
            **self.header.to_dict(),
            **self.identification.to_dict(),
            'subtype': 5,
            'subtype_name': 'Storage Statistics',
            'pool_name': self.pool_name,
            'pool_type': self.pool_type,
            'total_storage_bytes': self.total_storage,
            'used_storage_bytes': self.used_storage,
            'free_storage_bytes': self.free_storage,
            'peak_storage_bytes': self.peak_storage,
            'utilization_pct': round(utilization, 2),
            'getmain_requests': self.getmain_requests,
            'freemain_requests': self.freemain_requests,
            'failed_getmains': self.failed_getmains,
            'avg_allocation_time_us': round(self.avg_allocation_time, 3),
            'max_allocation_time_us': round(self.max_allocation_time, 3),
            'fragments': self.fragments,
            'largest_fragment_bytes': self.largest_fragment,
        }

# ============ Sample Data Generator ============
class SMF110SampleGenerator:
    """Generate sample SMF Type 110 records for testing"""
    
    TRANSACTION_IDS = ["TRN1", "TRN2", "TRN3", "ACCT", "INV", "ORD", "PAY"]
    PROGRAM_NAMES = ["PROG001", "PROG002", "COBOL01", "PL1PROG", "ASMPROG"]
    FILE_NAMES = ["CUSTFILE", "INVFILE", "ORDFILE", "PAYFILE", "TEMPFILE"]
    TERMINAL_IDS = ["T001", "T002", "T003", "T004", "T005"]
    STORAGE_POOLS = ["CDSA", "ERDSA", "ECDSA", "UDSA", "EUDSA"]
    
    @staticmethod
    def generate_type1_records(count: int = 10) -> List[SMF110Type1]:
        """Generate sample Transaction Statistics records"""
        records = []
        for i in range(count):
            rec = SMF110Type1(
                transaction_id=random.choice(SMF110SampleGenerator.TRANSACTION_IDS),
                program_name=random.choice(SMF110SampleGenerator.PROGRAM_NAMES),
                userid=f"USER{random.randint(1, 100):03d}",
                terminal_id=random.choice(SMF110SampleGenerator.TERMINAL_IDS),
                transaction_count=random.randint(1, 500),
                cpu_time=random.uniform(0.5, 150.0),
                elapsed_time=random.uniform(10.0, 500.0),
                response_time=random.uniform(5.0, 300.0),
                file_requests=random.randint(0, 50),
                db2_requests=random.randint(0, 30),
                ts_requests=random.randint(0, 20),
                td_requests=random.randint(0, 10),
                reads=random.randint(5, 100),
                writes=random.randint(0, 50),
                browses=random.randint(0, 30),
                deletes=random.randint(0, 10),
                completed=random.randint(90, 100),
                abended=random.randint(0, 5),
                errors=random.randint(0, 3),
            )
            records.append(rec)
        return records
    
    @staticmethod
    def generate_type2_records(count: int = 10) -> List[SMF110Type2]:
        """Generate sample File Statistics records"""
        records = []
        for i in range(count):
            buffer_requests = random.randint(100, 5000)
            buffer_hits = random.randint(int(buffer_requests * 0.7), buffer_requests)
            
            rec = SMF110Type2(
                file_name=random.choice(SMF110SampleGenerator.FILE_NAMES),
                dataset_name=f"CICS.{random.choice(SMF110SampleGenerator.FILE_NAMES)}",
                file_type=random.choice(["VSAM", "BDAM", "DB2"]),
                reads=random.randint(100, 2000),
                writes=random.randint(50, 1000),
                updates=random.randint(10, 500),
                deletes=random.randint(0, 100),
                browses=random.randint(20, 300),
                avg_response_time=random.uniform(0.5, 50.0),
                max_response_time=random.uniform(50.0, 200.0),
                total_io_time=random.uniform(100.0, 5000.0),
                buffer_requests=buffer_requests,
                buffer_hits=buffer_hits,
                buffer_misses=buffer_requests - buffer_hits,
                string_waits=random.randint(0, 50),
                string_requests=random.randint(100, 500),
                io_errors=random.randint(0, 5),
                record_not_found=random.randint(0, 20),
                duplicate_key=random.randint(0, 10),
            )
            records.append(rec)
        return records
    
    @staticmethod
    def generate_type3_records(count: int = 10) -> List[SMF110Type3]:
        """Generate sample Program Statistics records"""
        records = []
        for i in range(count):
            rec = SMF110Type3(
                program_name=random.choice(SMF110SampleGenerator.PROGRAM_NAMES),
                program_length=random.randint(10000, 500000),
                language=random.choice(["COBOL", "PL/I", "ASM", "C", "JAVA"]),
                load_count=random.randint(1, 100),
                use_count=random.randint(10, 5000),
                fetch_count=random.randint(1, 100),
                cpu_time=random.uniform(1.0, 500.0),
                elapsed_time=random.uniform(10.0, 1000.0),
                storage_used=random.randint(50000, 1000000),
                storage_violations=random.randint(0, 3),
                library=random.choice(["DFHRPL", "USERLIB", "SYSLIB"]),
                location=random.choice(["MAIN", "LPA", "EXTENDED"]),
                abends=random.randint(0, 5),
                compression_errors=random.randint(0, 2),
            )
            records.append(rec)
        return records
    
    @staticmethod
    def generate_type4_records(count: int = 10) -> List[SMF110Type4]:
        """Generate sample Terminal Statistics records"""
        records = []
        for i in range(count):
            rec = SMF110Type4(
                terminal_id=random.choice(SMF110SampleGenerator.TERMINAL_IDS),
                netname=f"TERM{random.randint(1, 100):03d}",
                terminal_type=random.choice(["3270", "3290", "WEB"]),
                sessions_started=random.randint(1, 50),
                sessions_ended=random.randint(1, 50),
                total_transactions=random.randint(10, 1000),
                messages_sent=random.randint(50, 2000),
                messages_received=random.randint(50, 2000),
                bytes_sent=random.randint(10000, 500000),
                bytes_received=random.randint(10000, 500000),
                avg_response_time=random.uniform(50.0, 500.0),
                max_response_time=random.uniform(500.0, 2000.0),
                transmission_errors=random.randint(0, 10),
                timeout_errors=random.randint(0, 5),
            )
            records.append(rec)
        return records
    
    @staticmethod
    def generate_type5_records(count: int = 10) -> List[SMF110Type5]:
        """Generate sample Storage Statistics records"""
        records = []
        for i in range(count):
            total = random.randint(10485760, 104857600)  # 10MB to 100MB
            used = random.randint(int(total * 0.3), int(total * 0.9))
            
            rec = SMF110Type5(
                pool_name=random.choice(SMF110SampleGenerator.STORAGE_POOLS),
                pool_type=random.choice(["DYNAMIC", "FIXED", "SHARED"]),
                total_storage=total,
                used_storage=used,
                free_storage=total - used,
                peak_storage=random.randint(used, total),
                getmain_requests=random.randint(1000, 50000),
                freemain_requests=random.randint(1000, 50000),
                failed_getmains=random.randint(0, 50),
                avg_allocation_time=random.uniform(1.0, 100.0),
                max_allocation_time=random.uniform(100.0, 1000.0),
                fragments=random.randint(10, 500),
                largest_fragment=random.randint(1024, 1048576),
            )
            records.append(rec)
        return records
