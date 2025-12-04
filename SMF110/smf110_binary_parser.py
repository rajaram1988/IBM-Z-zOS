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
    
    def parse_type3_program(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type3:
        """Parse Subtype 3 - Program Statistics"""
        base = offset + 50
        
        program_name = self.ebcdic_to_ascii(data[base:base+8])
        language = self.ebcdic_to_ascii(data[base+8:base+12])
        
        load_count = struct.unpack('>I', data[base+12:base+16])[0] if len(data) >= base+16 else 0
        execution_count = struct.unpack('>I', data[base+16:base+20])[0] if len(data) >= base+20 else 0
        
        avg_cpu_us = struct.unpack('>I', data[base+20:base+24])[0] if len(data) >= base+24 else 0
        max_cpu_us = struct.unpack('>I', data[base+24:base+28])[0] if len(data) >= base+28 else 0
        avg_elapsed_cs = struct.unpack('>I', data[base+28:base+32])[0] if len(data) >= base+32 else 0
        max_elapsed_cs = struct.unpack('>I', data[base+32:base+36])[0] if len(data) >= base+36 else 0
        
        storage_used = struct.unpack('>I', data[base+36:base+40])[0] if len(data) >= base+40 else 0
        max_storage = struct.unpack('>I', data[base+40:base+44])[0] if len(data) >= base+44 else 0
        compression = struct.unpack('>I', data[base+44:base+48])[0] if len(data) >= base+48 else 0
        
        return SMF110Type3(
            header=header,
            identification=ident,
            program_name=program_name,
            language=language,
            load_count=load_count,
            execution_count=execution_count,
            avg_cpu_time=avg_cpu_us / 1000.0,
            max_cpu_time=max_cpu_us / 1000.0,
            avg_elapsed_time=avg_elapsed_cs * 10.0,
            max_elapsed_time=max_elapsed_cs * 10.0,
            storage_used=storage_used,
            max_storage=max_storage,
            compression_ratio=compression / 100.0
        )
    
    def parse_type4_terminal(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type4:
        """Parse Subtype 4 - Terminal Statistics"""
        base = offset + 50
        
        terminal_id = self.ebcdic_to_ascii(data[base:base+4])
        netname = self.ebcdic_to_ascii(data[base+4:base+12])
        terminal_type = self.ebcdic_to_ascii(data[base+12:base+20])
        
        transactions = struct.unpack('>I', data[base+20:base+24])[0] if len(data) >= base+24 else 0
        messages_in = struct.unpack('>I', data[base+24:base+28])[0] if len(data) >= base+28 else 0
        messages_out = struct.unpack('>I', data[base+28:base+32])[0] if len(data) >= base+32 else 0
        
        bytes_in = struct.unpack('>I', data[base+32:base+36])[0] if len(data) >= base+36 else 0
        bytes_out = struct.unpack('>I', data[base+36:base+40])[0] if len(data) >= base+40 else 0
        
        avg_response_cs = struct.unpack('>I', data[base+40:base+44])[0] if len(data) >= base+44 else 0
        max_response_cs = struct.unpack('>I', data[base+44:base+48])[0] if len(data) >= base+48 else 0
        
        errors = struct.unpack('>I', data[base+48:base+52])[0] if len(data) >= base+52 else 0
        timeouts = struct.unpack('>I', data[base+52:base+56])[0] if len(data) >= base+56 else 0
        
        return SMF110Type4(
            header=header,
            identification=ident,
            terminal_id=terminal_id,
            netname=netname,
            terminal_type=terminal_type,
            transactions=transactions,
            messages_in=messages_in,
            messages_out=messages_out,
            bytes_in=bytes_in,
            bytes_out=bytes_out,
            avg_response_time=avg_response_cs * 10.0,
            max_response_time=max_response_cs * 10.0,
            errors=errors,
            timeouts=timeouts
        )
    
    def parse_type5_storage(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type5:
        """Parse Subtype 5 - Storage Statistics"""
        base = offset + 50
        
        storage_type = self.ebcdic_to_ascii(data[base:base+8])
        
        total_storage = struct.unpack('>I', data[base+8:base+12])[0] if len(data) >= base+12 else 0
        used_storage = struct.unpack('>I', data[base+12:base+16])[0] if len(data) >= base+16 else 0
        free_storage = struct.unpack('>I', data[base+16:base+20])[0] if len(data) >= base+20 else 0
        peak_usage = struct.unpack('>I', data[base+20:base+24])[0] if len(data) >= base+24 else 0
        
        getmain_count = struct.unpack('>I', data[base+24:base+28])[0] if len(data) >= base+28 else 0
        freemain_count = struct.unpack('>I', data[base+28:base+32])[0] if len(data) >= base+32 else 0
        cushion_size = struct.unpack('>I', data[base+32:base+36])[0] if len(data) >= base+36 else 0
        
        storage_violations = struct.unpack('>I', data[base+36:base+40])[0] if len(data) >= base+40 else 0
        shortage_count = struct.unpack('>I', data[base+40:base+44])[0] if len(data) >= base+44 else 0
        
        return SMF110Type5(
            header=header,
            identification=ident,
            storage_type=storage_type,
            total_storage=total_storage,
            used_storage=used_storage,
            free_storage=free_storage,
            peak_usage=peak_usage,
            getmain_count=getmain_count,
            freemain_count=freemain_count,
            cushion_size=cushion_size,
            storage_violations=storage_violations,
            shortage_count=shortage_count
        )
    
    def parse_type6_dispatcher(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type6:
        """Parse Subtype 6 - Dispatcher Statistics"""
        base = offset + 50
        
        task_count = struct.unpack('>I', data[base:base+4])[0] if len(data) >= base+4 else 0
        total_cpu_us = struct.unpack('>I', data[base+4:base+8])[0] if len(data) >= base+8 else 0
        avg_dispatch_us = struct.unpack('>I', data[base+8:base+12])[0] if len(data) >= base+12 else 0
        max_dispatch_us = struct.unpack('>I', data[base+12:base+16])[0] if len(data) >= base+16 else 0
        wait_time_us = struct.unpack('>I', data[base+16:base+20])[0] if len(data) >= base+20 else 0
        
        suspend_count = struct.unpack('>I', data[base+20:base+24])[0] if len(data) >= base+24 else 0
        dispatch_count = struct.unpack('>I', data[base+24:base+28])[0] if len(data) >= base+28 else 0
        ready_queue_depth = struct.unpack('>I', data[base+28:base+32])[0] if len(data) >= base+32 else 0
        active_tasks = struct.unpack('>I', data[base+32:base+36])[0] if len(data) >= base+36 else 0
        
        return SMF110Type6(
            header=header,
            identification=ident,
            task_count=task_count,
            total_cpu_time=total_cpu_us / 1000.0,
            avg_dispatch_time=avg_dispatch_us / 1000.0,
            max_dispatch_time=max_dispatch_us / 1000.0,
            wait_time=wait_time_us / 1000.0,
            suspend_count=suspend_count,
            dispatch_count=dispatch_count,
            ready_queue_depth=ready_queue_depth,
            active_tasks=active_tasks
        )
    
    def parse_type7_loader(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type7:
        """Parse Subtype 7 - Loader Statistics"""
        base = offset + 50
        
        program_name = self.ebcdic_to_ascii(data[base:base+8])
        library = self.ebcdic_to_ascii(data[base+8:base+52])
        
        load_count = struct.unpack('>I', data[base+52:base+56])[0] if len(data) >= base+56 else 0
        delete_count = struct.unpack('>I', data[base+56:base+60])[0] if len(data) >= base+60 else 0
        
        avg_load_us = struct.unpack('>I', data[base+60:base+64])[0] if len(data) >= base+64 else 0
        max_load_us = struct.unpack('>I', data[base+64:base+68])[0] if len(data) >= base+68 else 0
        
        cache_hits = struct.unpack('>I', data[base+68:base+72])[0] if len(data) >= base+72 else 0
        cache_misses = struct.unpack('>I', data[base+72:base+76])[0] if len(data) >= base+76 else 0
        load_failures = struct.unpack('>I', data[base+76:base+80])[0] if len(data) >= base+80 else 0
        
        return SMF110Type7(
            header=header,
            identification=ident,
            program_name=program_name,
            library=library,
            load_count=load_count,
            delete_count=delete_count,
            avg_load_time=avg_load_us / 1000.0,
            max_load_time=max_load_us / 1000.0,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            load_failures=load_failures
        )
    
    def parse_type8_tempstorage(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type8:
        """Parse Subtype 8 - Temporary Storage Statistics"""
        base = offset + 50
        
        queue_name = self.ebcdic_to_ascii(data[base:base+8])
        
        reads = struct.unpack('>I', data[base+8:base+12])[0] if len(data) >= base+12 else 0
        writes = struct.unpack('>I', data[base+12:base+16])[0] if len(data) >= base+16 else 0
        deletes = struct.unpack('>I', data[base+16:base+20])[0] if len(data) >= base+20 else 0
        rewrites = struct.unpack('>I', data[base+20:base+24])[0] if len(data) >= base+24 else 0
        
        avg_read_us = struct.unpack('>I', data[base+24:base+28])[0] if len(data) >= base+28 else 0
        avg_write_us = struct.unpack('>I', data[base+28:base+32])[0] if len(data) >= base+32 else 0
        
        peak_items = struct.unpack('>I', data[base+32:base+36])[0] if len(data) >= base+36 else 0
        peak_storage = struct.unpack('>I', data[base+36:base+40])[0] if len(data) >= base+40 else 0
        recoveries = struct.unpack('>I', data[base+40:base+44])[0] if len(data) >= base+44 else 0
        
        return SMF110Type8(
            header=header,
            identification=ident,
            queue_name=queue_name,
            reads=reads,
            writes=writes,
            deletes=deletes,
            rewrites=rewrites,
            avg_read_time=avg_read_us / 1000.0,
            avg_write_time=avg_write_us / 1000.0,
            peak_items=peak_items,
            peak_storage=peak_storage,
            recoveries=recoveries
        )
    
    def parse_type9_transientdata(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type9:
        """Parse Subtype 9 - Transient Data Statistics"""
        base = offset + 50
        
        queue_name = self.ebcdic_to_ascii(data[base:base+4])
        destination_type = self.ebcdic_to_ascii(data[base+4:base+12])
        
        reads = struct.unpack('>I', data[base+12:base+16])[0] if len(data) >= base+16 else 0
        writes = struct.unpack('>I', data[base+16:base+20])[0] if len(data) >= base+20 else 0
        
        avg_read_us = struct.unpack('>I', data[base+20:base+24])[0] if len(data) >= base+24 else 0
        avg_write_us = struct.unpack('>I', data[base+24:base+28])[0] if len(data) >= base+28 else 0
        
        queue_depth = struct.unpack('>I', data[base+28:base+32])[0] if len(data) >= base+32 else 0
        peak_depth = struct.unpack('>I', data[base+32:base+36])[0] if len(data) >= base+36 else 0
        trigger_count = struct.unpack('>I', data[base+36:base+40])[0] if len(data) >= base+40 else 0
        purge_count = struct.unpack('>I', data[base+40:base+44])[0] if len(data) >= base+44 else 0
        
        return SMF110Type9(
            header=header,
            identification=ident,
            queue_name=queue_name,
            destination_type=destination_type,
            reads=reads,
            writes=writes,
            avg_read_time=avg_read_us / 1000.0,
            avg_write_time=avg_write_us / 1000.0,
            queue_depth=queue_depth,
            peak_depth=peak_depth,
            trigger_count=trigger_count,
            purge_count=purge_count
        )
    
    def parse_type10_journal(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type10:
        """Parse Subtype 10 - Journal Statistics"""
        base = offset + 50
        
        journal_name = self.ebcdic_to_ascii(data[base:base+8])
        
        writes = struct.unpack('>I', data[base+8:base+12])[0] if len(data) >= base+12 else 0
        waits = struct.unpack('>I', data[base+12:base+16])[0] if len(data) >= base+16 else 0
        
        avg_write_us = struct.unpack('>I', data[base+16:base+20])[0] if len(data) >= base+20 else 0
        max_write_us = struct.unpack('>I', data[base+20:base+24])[0] if len(data) >= base+24 else 0
        
        buffer_writes = struct.unpack('>I', data[base+24:base+28])[0] if len(data) >= base+28 else 0
        physical_writes = struct.unpack('>I', data[base+28:base+32])[0] if len(data) >= base+32 else 0
        bytes_written = struct.unpack('>I', data[base+32:base+36])[0] if len(data) >= base+36 else 0
        archiving_count = struct.unpack('>I', data[base+36:base+40])[0] if len(data) >= base+40 else 0
        
        return SMF110Type10(
            header=header,
            identification=ident,
            journal_name=journal_name,
            writes=writes,
            waits=waits,
            avg_write_time=avg_write_us / 1000.0,
            max_write_time=max_write_us / 1000.0,
            buffer_writes=buffer_writes,
            physical_writes=physical_writes,
            bytes_written=bytes_written,
            archiving_count=archiving_count
        )
    
    def parse_type11_database(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type11:
        """Parse Subtype 11 - Database Statistics"""
        base = offset + 50
        
        db_type = self.ebcdic_to_ascii(data[base:base+8])
        plan_name = self.ebcdic_to_ascii(data[base+8:base+16])
        
        calls = struct.unpack('>I', data[base+16:base+20])[0] if len(data) >= base+20 else 0
        commits = struct.unpack('>I', data[base+20:base+24])[0] if len(data) >= base+24 else 0
        rollbacks = struct.unpack('>I', data[base+24:base+28])[0] if len(data) >= base+28 else 0
        
        avg_response_us = struct.unpack('>I', data[base+28:base+32])[0] if len(data) >= base+32 else 0
        max_response_us = struct.unpack('>I', data[base+32:base+36])[0] if len(data) >= base+36 else 0
        
        sql_errors = struct.unpack('>I', data[base+36:base+40])[0] if len(data) >= base+40 else 0
        deadlocks = struct.unpack('>I', data[base+40:base+44])[0] if len(data) >= base+44 else 0
        timeouts = struct.unpack('>I', data[base+44:base+48])[0] if len(data) >= base+48 else 0
        
        return SMF110Type11(
            header=header,
            identification=ident,
            db_type=db_type,
            plan_name=plan_name,
            calls=calls,
            commits=commits,
            rollbacks=rollbacks,
            avg_response_time=avg_response_us / 1000.0,
            max_response_time=max_response_us / 1000.0,
            sql_errors=sql_errors,
            deadlocks=deadlocks,
            timeouts=timeouts
        )
    
    def parse_type12_mq(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type12:
        """Parse Subtype 12 - MQ Statistics"""
        base = offset + 50
        
        queue_name = self.ebcdic_to_ascii(data[base:base+48])
        queue_manager = self.ebcdic_to_ascii(data[base+48:base+52])
        
        messages_put = struct.unpack('>I', data[base+52:base+56])[0] if len(data) >= base+56 else 0
        messages_get = struct.unpack('>I', data[base+56:base+60])[0] if len(data) >= base+60 else 0
        browse_count = struct.unpack('>I', data[base+60:base+64])[0] if len(data) >= base+64 else 0
        
        avg_put_us = struct.unpack('>I', data[base+64:base+68])[0] if len(data) >= base+68 else 0
        avg_get_us = struct.unpack('>I', data[base+68:base+72])[0] if len(data) >= base+72 else 0
        
        persistent_msgs = struct.unpack('>I', data[base+72:base+76])[0] if len(data) >= base+76 else 0
        syncpoint_msgs = struct.unpack('>I', data[base+76:base+80])[0] if len(data) >= base+80 else 0
        
        return SMF110Type12(
            header=header,
            identification=ident,
            queue_name=queue_name,
            queue_manager=queue_manager,
            messages_put=messages_put,
            messages_get=messages_get,
            browse_count=browse_count,
            avg_put_time=avg_put_us / 1000.0,
            avg_get_time=avg_get_us / 1000.0,
            persistent_msgs=persistent_msgs,
            syncpoint_msgs=syncpoint_msgs
        )
    
    def parse_type13_webservices(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type13:
        """Parse Subtype 13 - Web Services Statistics"""
        base = offset + 50
        
        service_name = self.ebcdic_to_ascii(data[base:base+32])
        operation = self.ebcdic_to_ascii(data[base+32:base+64])
        
        request_count = struct.unpack('>I', data[base+64:base+68])[0] if len(data) >= base+68 else 0
        success_count = struct.unpack('>I', data[base+68:base+72])[0] if len(data) >= base+72 else 0
        error_count = struct.unpack('>I', data[base+72:base+76])[0] if len(data) >= base+76 else 0
        
        avg_response_us = struct.unpack('>I', data[base+76:base+80])[0] if len(data) >= base+80 else 0
        max_response_us = struct.unpack('>I', data[base+80:base+84])[0] if len(data) >= base+84 else 0
        
        avg_request_size = struct.unpack('>I', data[base+84:base+88])[0] if len(data) >= base+88 else 0
        avg_response_size = struct.unpack('>I', data[base+88:base+92])[0] if len(data) >= base+92 else 0
        
        return SMF110Type13(
            header=header,
            identification=ident,
            service_name=service_name,
            operation=operation,
            request_count=request_count,
            success_count=success_count,
            error_count=error_count,
            avg_response_time=avg_response_us / 1000.0,
            max_response_time=max_response_us / 1000.0,
            avg_request_size=avg_request_size,
            avg_response_size=avg_response_size
        )
    
    def parse_type14_isc(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type14:
        """Parse Subtype 14 - ISC Statistics"""
        base = offset + 50
        
        connection_name = self.ebcdic_to_ascii(data[base:base+8])
        remote_system = self.ebcdic_to_ascii(data[base+8:base+16])
        
        sessions = struct.unpack('>I', data[base+16:base+20])[0] if len(data) >= base+20 else 0
        messages_sent = struct.unpack('>I', data[base+20:base+24])[0] if len(data) >= base+24 else 0
        messages_received = struct.unpack('>I', data[base+24:base+28])[0] if len(data) >= base+28 else 0
        
        avg_send_us = struct.unpack('>I', data[base+28:base+32])[0] if len(data) >= base+32 else 0
        avg_receive_us = struct.unpack('>I', data[base+32:base+36])[0] if len(data) >= base+36 else 0
        
        transmission_errors = struct.unpack('>I', data[base+36:base+40])[0] if len(data) >= base+40 else 0
        session_failures = struct.unpack('>I', data[base+40:base+44])[0] if len(data) >= base+44 else 0
        
        return SMF110Type14(
            header=header,
            identification=ident,
            connection_name=connection_name,
            remote_system=remote_system,
            sessions=sessions,
            messages_sent=messages_sent,
            messages_received=messages_received,
            avg_send_time=avg_send_us / 1000.0,
            avg_receive_time=avg_receive_us / 1000.0,
            transmission_errors=transmission_errors,
            session_failures=session_failures
        )
    
    def parse_type15_coupling_facility(self, data: bytes, offset: int, header: SMF110Header, ident: CICSIdentification) -> SMF110Type15:
        """Parse Subtype 15 - Coupling Facility Statistics"""
        base = offset + 50
        
        structure_name = self.ebcdic_to_ascii(data[base:base+16])
        cf_name = self.ebcdic_to_ascii(data[base+16:base+24])
        
        requests = struct.unpack('>I', data[base+24:base+28])[0] if len(data) >= base+28 else 0
        
        avg_response_us = struct.unpack('>I', data[base+28:base+32])[0] if len(data) >= base+32 else 0
        max_response_us = struct.unpack('>I', data[base+32:base+36])[0] if len(data) >= base+36 else 0
        
        lock_contentions = struct.unpack('>I', data[base+36:base+40])[0] if len(data) >= base+40 else 0
        force_reconnects = struct.unpack('>I', data[base+40:base+44])[0] if len(data) >= base+44 else 0
        failed_requests = struct.unpack('>I', data[base+44:base+48])[0] if len(data) >= base+48 else 0
        async_requests = struct.unpack('>I', data[base+48:base+52])[0] if len(data) >= base+52 else 0
        
        return SMF110Type15(
            header=header,
            identification=ident,
            structure_name=structure_name,
            cf_name=cf_name,
            requests=requests,
            avg_response_time=avg_response_us / 1000.0,
            max_response_time=max_response_us / 1000.0,
            lock_contentions=lock_contentions,
            force_reconnects=force_reconnects,
            failed_requests=failed_requests,
            async_requests=async_requests
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
            elif subtype == 3:
                record = self.parse_type3_program(data, offset, header, identification)
            elif subtype == 4:
                record = self.parse_type4_terminal(data, offset, header, identification)
            elif subtype == 5:
                record = self.parse_type5_storage(data, offset, header, identification)
            elif subtype == 6:
                record = self.parse_type6_dispatcher(data, offset, header, identification)
            elif subtype == 7:
                record = self.parse_type7_loader(data, offset, header, identification)
            elif subtype == 8:
                record = self.parse_type8_tempstorage(data, offset, header, identification)
            elif subtype == 9:
                record = self.parse_type9_transientdata(data, offset, header, identification)
            elif subtype == 10:
                record = self.parse_type10_journal(data, offset, header, identification)
            elif subtype == 11:
                record = self.parse_type11_database(data, offset, header, identification)
            elif subtype == 12:
                record = self.parse_type12_mq(data, offset, header, identification)
            elif subtype == 13:
                record = self.parse_type13_webservices(data, offset, header, identification)
            elif subtype == 14:
                record = self.parse_type14_isc(data, offset, header, identification)
            elif subtype == 15:
                record = self.parse_type15_coupling_facility(data, offset, header, identification)
            else:
                print(f"[WARN] Subtype {subtype} parser not implemented, skipping...")
            
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
