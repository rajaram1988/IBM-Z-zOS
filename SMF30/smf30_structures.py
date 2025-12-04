"""
SMF Type 30 Record Structures - Based on IBM z/OS Manual
SMF Type 30 provides Job/Step/Delay completion records for z/OS systems
Subtypes: 1=Job Step, 2=Job, 3=Step Initiation, 4=Job Termination, 5=Netstep
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime, timedelta
import struct
import random

# ============ SMF 30 Record Header ============
@dataclass
class SMF30Header:
    """Common SMF header for Type 30 records"""
    record_type: int = 30  # Record type
    record_length: int = 0
    segment_number: int = 1
    flags: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    system_id: str = "SYSZ1"
    subsystem_id: str = "SYS1"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'record_type': self.record_type,
            'record_length': self.record_length,
            'segment_number': self.segment_number,
            'flags': self.flags,
            'timestamp': self.timestamp.isoformat(),
            'system_id': self.system_id,
            'subsystem_id': self.subsystem_id,
        }

# ============ Common Fields ============
@dataclass
class JobIdentification:
    """Job identification segment (JMJID)"""
    job_name: str = "MYJOB"
    job_number: str = "000001"
    owning_userid: str = "USERID"
    job_queue_name: str = "BATCH"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'job_name': self.job_name,
            'job_number': self.job_number,
            'owning_userid': self.owning_userid,
            'job_queue_name': self.job_queue_name,
        }

@dataclass
class TimingData:
    """Timing and resource consumption"""
    cpu_time_ms: int = 5000
    srvclass: str = "TSO"
    priority: int = 4
    service_units: int = 1000
    io_count: int = 500
    elapsed_time_ms: int = 10000
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'cpu_time_ms': self.cpu_time_ms,
            'srvclass': self.srvclass,
            'priority': self.priority,
            'service_units': self.service_units,
            'io_count': self.io_count,
            'elapsed_time_ms': self.elapsed_time_ms,
        }

# ============ Subtype 1: Job Step Termination ============
@dataclass
class SMF30Type1:
    """Subtype 1 - Job Step Termination Record (JMJST)"""
    header: SMF30Header = field(default_factory=SMF30Header)
    subtype: int = 1
    job_id: JobIdentification = field(default_factory=JobIdentification)
    step_name: str = "STEP001"
    program_name: str = "MYPROG"
    timing: TimingData = field(default_factory=TimingData)
    return_code: int = 0
    abnormal_termination_code: int = 0
    pages_read: int = 1000
    pages_written: int = 500
    excp_count: int = 250
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'subtype': self.subtype,
            'subtype_name': 'Job Step Termination',
            **self.header.to_dict(),
            **self.job_id.to_dict(),
            'step_name': self.step_name,
            'program_name': self.program_name,
            'return_code': self.return_code,
            'abnormal_termination_code': self.abnormal_termination_code,
            **self.timing.to_dict(),
            'pages_read': self.pages_read,
            'pages_written': self.pages_written,
            'excp_count': self.excp_count,
        }

# ============ Subtype 2: Job Termination ============
@dataclass
class SMF30Type2:
    """Subtype 2 - Job Termination Record (JMTERM)"""
    header: SMF30Header = field(default_factory=SMF30Header)
    subtype: int = 2
    job_id: JobIdentification = field(default_factory=JobIdentification)
    timing: TimingData = field(default_factory=TimingData)
    total_steps: int = 3
    failed_steps: int = 0
    total_excp_count: int = 800
    total_pages_read: int = 3500
    total_pages_written: int = 1800
    job_termination_code: int = 0
    memory_allocated_mb: int = 64
    memory_max_used_mb: int = 48
    job_class: str = "A"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'subtype': self.subtype,
            'subtype_name': 'Job Termination',
            **self.header.to_dict(),
            **self.job_id.to_dict(),
            'total_steps': self.total_steps,
            'failed_steps': self.failed_steps,
            'job_termination_code': self.job_termination_code,
            'memory_allocated_mb': self.memory_allocated_mb,
            'memory_max_used_mb': self.memory_max_used_mb,
            'job_class': self.job_class,
            'total_excp_count': self.total_excp_count,
            'total_pages_read': self.total_pages_read,
            'total_pages_written': self.total_pages_written,
            **self.timing.to_dict(),
        }

# ============ Subtype 3: Step Initiation ============
@dataclass
class SMF30Type3:
    """Subtype 3 - Step Initiation Record (JMINIT)"""
    header: SMF30Header = field(default_factory=SMF30Header)
    subtype: int = 3
    job_id: JobIdentification = field(default_factory=JobIdentification)
    step_name: str = "STEP001"
    program_name: str = "MYPROG"
    step_start_time: datetime = field(default_factory=datetime.now)
    procedure_step_name: str = "PROC01"
    accounting_code: str = "ACCT001"
    memory_region_size_mb: int = 64
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'subtype': self.subtype,
            'subtype_name': 'Step Initiation',
            **self.header.to_dict(),
            **self.job_id.to_dict(),
            'step_name': self.step_name,
            'program_name': self.program_name,
            'step_start_time': self.step_start_time.isoformat(),
            'procedure_step_name': self.procedure_step_name,
            'accounting_code': self.accounting_code,
            'memory_region_size_mb': self.memory_region_size_mb,
        }

# ============ Subtype 4: Job Initiation ============
@dataclass
class SMF30Type4:
    """Subtype 4 - Job Initiation Record (JMJINI)"""
    header: SMF30Header = field(default_factory=SMF30Header)
    subtype: int = 4
    job_id: JobIdentification = field(default_factory=JobIdentification)
    job_start_time: datetime = field(default_factory=datetime.now)
    job_class: str = "A"
    job_priority: int = 4
    scheduling_environment: str = "JES2"
    accounting_code: str = "ACCT001"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'subtype': self.subtype,
            'subtype_name': 'Job Initiation',
            **self.header.to_dict(),
            **self.job_id.to_dict(),
            'job_start_time': self.job_start_time.isoformat(),
            'job_class': self.job_class,
            'job_priority': self.job_priority,
            'scheduling_environment': self.scheduling_environment,
            'accounting_code': self.accounting_code,
        }

# ============ Subtype 5: NetStep ============
@dataclass
class SMF30Type5:
    """Subtype 5 - NetStep Completion Record (JMNET)"""
    header: SMF30Header = field(default_factory=SMF30Header)
    subtype: int = 5
    job_id: JobIdentification = field(default_factory=JobIdentification)
    netstep_name: str = "NETSTEP1"
    network_destination: str = "REMOTE.SYSTEM"
    network_protocol: str = "TCP/IP"
    bytes_transmitted: int = 50000
    bytes_received: int = 75000
    network_response_time_ms: int = 500
    return_code: int = 0
    timing: TimingData = field(default_factory=TimingData)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'subtype': self.subtype,
            'subtype_name': 'NetStep Completion',
            **self.header.to_dict(),
            **self.job_id.to_dict(),
            'netstep_name': self.netstep_name,
            'network_destination': self.network_destination,
            'network_protocol': self.network_protocol,
            'bytes_transmitted': self.bytes_transmitted,
            'bytes_received': self.bytes_received,
            'network_response_time_ms': self.network_response_time_ms,
            'return_code': self.return_code,
            **self.timing.to_dict(),
        }

# ============ Sample Data Generator ============
class SMF30SampleGenerator:
    """Generate realistic sample SMF-30 records"""
    
    JOB_NAMES = ["PAYDAY", "PAYROL", "BATCH", "RPTGEN", "BKPMAST", "ARCHIVE", "CLEANUP"]
    USERIDS = ["PAYROLL", "REPORTS", "ADMIN", "BATCH01", "OPS", "SYSTEM"]
    PROGRAMS = ["COBOL01", "COBOL02", "SORT", "SYNCSORT", "REXX", "CICS", "DB2CLI"]
    STEPS = ["INIT", "PROCESS", "SORT", "UPDATE", "REPORT", "ARCHIVE", "CLEANUP"]
    
    @staticmethod
    def generate_type1(count: int = 5) -> List[SMF30Type1]:
        """Generate Job Step Termination records"""
        records = []
        base_time = datetime.now() - timedelta(hours=8)
        
        for i in range(count):
            timing = TimingData(
                cpu_time_ms=random.randint(1000, 15000),
                service_units=random.randint(500, 3000),
                io_count=random.randint(100, 1000),
                elapsed_time_ms=random.randint(5000, 30000),
            )
            
            record = SMF30Type1(
                header=SMF30Header(timestamp=base_time + timedelta(minutes=i*15)),
                job_id=JobIdentification(
                    job_name=random.choice(SMF30SampleGenerator.JOB_NAMES),
                    job_number=f"{i+1:06d}",
                    owning_userid=random.choice(SMF30SampleGenerator.USERIDS),
                ),
                step_name=f"{random.choice(SMF30SampleGenerator.STEPS)}",
                program_name=random.choice(SMF30SampleGenerator.PROGRAMS),
                timing=timing,
                return_code=random.choice([0, 0, 0, 4, 8, 12]),  # Bias toward success
                pages_read=random.randint(500, 5000),
                pages_written=random.randint(100, 2000),
                excp_count=random.randint(50, 500),
            )
            records.append(record)
        
        return records
    
    @staticmethod
    def generate_type2(count: int = 3) -> List[SMF30Type2]:
        """Generate Job Termination records"""
        records = []
        base_time = datetime.now() - timedelta(hours=8)
        
        for i in range(count):
            timing = TimingData(
                cpu_time_ms=random.randint(5000, 45000),
                service_units=random.randint(2000, 8000),
                io_count=random.randint(500, 3000),
                elapsed_time_ms=random.randint(10000, 120000),
            )
            
            record = SMF30Type2(
                header=SMF30Header(timestamp=base_time + timedelta(hours=i*4)),
                job_id=JobIdentification(
                    job_name=random.choice(SMF30SampleGenerator.JOB_NAMES),
                    job_number=f"{10000+i:06d}",
                    owning_userid=random.choice(SMF30SampleGenerator.USERIDS),
                ),
                timing=timing,
                total_steps=random.randint(1, 8),
                failed_steps=random.choice([0, 0, 0, 1]),  # Mostly success
                total_excp_count=random.randint(200, 2000),
                total_pages_read=random.randint(2000, 10000),
                total_pages_written=random.randint(1000, 5000),
                memory_allocated_mb=random.choice([32, 64, 128, 256]),
                memory_max_used_mb=random.randint(16, 200),
                job_class=random.choice(["A", "B", "C"]),
            )
            records.append(record)
        
        return records
    
    @staticmethod
    def generate_type3(count: int = 5) -> List[SMF30Type3]:
        """Generate Step Initiation records"""
        records = []
        base_time = datetime.now() - timedelta(hours=8)
        
        for i in range(count):
            record = SMF30Type3(
                header=SMF30Header(timestamp=base_time + timedelta(minutes=i*20)),
                job_id=JobIdentification(
                    job_name=random.choice(SMF30SampleGenerator.JOB_NAMES),
                    job_number=f"{20000+i:06d}",
                    owning_userid=random.choice(SMF30SampleGenerator.USERIDS),
                ),
                step_name=f"{random.choice(SMF30SampleGenerator.STEPS)}",
                program_name=random.choice(SMF30SampleGenerator.PROGRAMS),
                memory_region_size_mb=random.choice([32, 64, 128, 256]),
            )
            records.append(record)
        
        return records
    
    @staticmethod
    def generate_type4(count: int = 3) -> List[SMF30Type4]:
        """Generate Job Initiation records"""
        records = []
        base_time = datetime.now() - timedelta(hours=8)
        
        for i in range(count):
            record = SMF30Type4(
                header=SMF30Header(timestamp=base_time + timedelta(hours=i*3)),
                job_id=JobIdentification(
                    job_name=random.choice(SMF30SampleGenerator.JOB_NAMES),
                    job_number=f"{30000+i:06d}",
                    owning_userid=random.choice(SMF30SampleGenerator.USERIDS),
                ),
                job_class=random.choice(["A", "B", "C"]),
                job_priority=random.randint(1, 15),
            )
            records.append(record)
        
        return records
    
    @staticmethod
    def generate_type5(count: int = 2) -> List[SMF30Type5]:
        """Generate NetStep Completion records"""
        records = []
        base_time = datetime.now() - timedelta(hours=8)
        
        for i in range(count):
            timing = TimingData(
                cpu_time_ms=random.randint(500, 5000),
                service_units=random.randint(100, 1000),
                io_count=random.randint(10, 100),
                elapsed_time_ms=random.randint(1000, 10000),
            )
            
            record = SMF30Type5(
                header=SMF30Header(timestamp=base_time + timedelta(hours=i*6)),
                job_id=JobIdentification(
                    job_name=random.choice(SMF30SampleGenerator.JOB_NAMES),
                    job_number=f"{40000+i:06d}",
                    owning_userid=random.choice(SMF30SampleGenerator.USERIDS),
                ),
                netstep_name=f"NETSTEP{i+1}",
                network_destination=random.choice(["SYS1.NETWORK", "REMOTE01", "ARCHIVE01"]),
                bytes_transmitted=random.randint(10000, 500000),
                bytes_received=random.randint(10000, 1000000),
                network_response_time_ms=random.randint(100, 2000),
                return_code=random.choice([0, 0, 4]),
                timing=timing,
            )
            records.append(record)
        
        return records
    
    @staticmethod
    def generate_all_records() -> Dict[int, List[Any]]:
        """Generate all record types"""
        return {
            1: SMF30SampleGenerator.generate_type1(8),
            2: SMF30SampleGenerator.generate_type2(4),
            3: SMF30SampleGenerator.generate_type3(8),
            4: SMF30SampleGenerator.generate_type4(4),
            5: SMF30SampleGenerator.generate_type5(3),
        }
