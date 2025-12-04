"""
SMF Type 110 CICS Visualization Engine
Creates comprehensive matplotlib charts for CICS performance analysis
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import List
import numpy as np

from smf110_structures import (
    SMF110Type1, SMF110Type2, SMF110Type3, SMF110Type4, SMF110Type5
)

class SMF110Visualizer:
    """Generate visualization charts for SMF 110 CICS statistics"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('default')
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    def create_transaction_analysis(self, records: List[SMF110Type1]):
        """Create transaction statistics visualizations"""
        if not records:
            print("No transaction records to visualize")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('SMF Type 110 Subtype 1 - CICS Transaction Analysis', 
                     fontsize=16, fontweight='bold')
        
        # Extract data
        trans_ids = [r.transaction_id for r in records]
        cpu_times = [r.cpu_time for r in records]
        response_times = [r.response_time for r in records]
        trans_counts = [r.transaction_count for r in records]
        file_reqs = [r.file_requests for r in records]
        abends = [r.abended for r in records]
        completed = [r.completed for r in records]
        
        # 1. CPU Time by Transaction
        axes[0, 0].bar(range(len(trans_ids)), cpu_times, color=self.colors[0])
        axes[0, 0].set_title('CPU Time by Transaction', fontweight='bold')
        axes[0, 0].set_xlabel('Transaction')
        axes[0, 0].set_ylabel('CPU Time (ms)')
        axes[0, 0].set_xticks(range(len(trans_ids)))
        axes[0, 0].set_xticklabels(trans_ids, rotation=45, ha='right')
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # 2. Response Time Distribution
        axes[0, 1].hist(response_times, bins=15, color=self.colors[1], edgecolor='black')
        axes[0, 1].set_title('Response Time Distribution', fontweight='bold')
        axes[0, 1].set_xlabel('Response Time (ms)')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].axvline(np.mean(response_times), color='red', linestyle='--', 
                          label=f'Mean: {np.mean(response_times):.1f}ms')
        axes[0, 1].legend()
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        # 3. Transaction Count by Transaction ID
        axes[0, 2].barh(range(len(trans_ids)), trans_counts, color=self.colors[2])
        axes[0, 2].set_title('Transaction Count by Transaction ID', fontweight='bold')
        axes[0, 2].set_xlabel('Count')
        axes[0, 2].set_ylabel('Transaction')
        axes[0, 2].set_yticks(range(len(trans_ids)))
        axes[0, 2].set_yticklabels(trans_ids)
        axes[0, 2].grid(axis='x', alpha=0.3)
        
        # 4. File Requests vs DB2 Requests
        db2_reqs = [r.db2_requests for r in records]
        x = np.arange(len(trans_ids))
        width = 0.35
        axes[1, 0].bar(x - width/2, file_reqs, width, label='File Requests', color=self.colors[3])
        axes[1, 0].bar(x + width/2, db2_reqs, width, label='DB2 Requests', color=self.colors[4])
        axes[1, 0].set_title('File vs DB2 Requests', fontweight='bold')
        axes[1, 0].set_xlabel('Transaction')
        axes[1, 0].set_ylabel('Request Count')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels(trans_ids, rotation=45, ha='right')
        axes[1, 0].legend()
        axes[1, 0].grid(axis='y', alpha=0.3)
        
        # 5. Completion Status (Stacked Bar)
        axes[1, 1].bar(range(len(trans_ids)), completed, label='Completed', color='green')
        axes[1, 1].bar(range(len(trans_ids)), abends, bottom=completed, 
                      label='Abended', color='red')
        axes[1, 1].set_title('Transaction Completion Status', fontweight='bold')
        axes[1, 1].set_xlabel('Transaction')
        axes[1, 1].set_ylabel('Count')
        axes[1, 1].set_xticks(range(len(trans_ids)))
        axes[1, 1].set_xticklabels(trans_ids, rotation=45, ha='right')
        axes[1, 1].legend()
        axes[1, 1].grid(axis='y', alpha=0.3)
        
        # 6. I/O Operations Summary
        io_types = ['Reads', 'Writes', 'Browses', 'Deletes']
        io_totals = [
            sum([r.reads for r in records]),
            sum([r.writes for r in records]),
            sum([r.browses for r in records]),
            sum([r.deletes for r in records])
        ]
        axes[1, 2].pie(io_totals, labels=io_types, autopct='%1.1f%%', 
                      colors=self.colors[:4], startangle=90)
        axes[1, 2].set_title('I/O Operations Distribution', fontweight='bold')
        
        plt.tight_layout()
        output_file = self.output_dir / "smf110_subtype1_transactions_analysis.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[OK] Saved transaction analysis to {output_file}")
    
    def create_file_analysis(self, records: List[SMF110Type2]):
        """Create file statistics visualizations"""
        if not records:
            print("No file records to visualize")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('SMF Type 110 Subtype 2 - CICS File Analysis', 
                     fontsize=16, fontweight='bold')
        
        # Extract data
        file_names = [r.file_name for r in records]
        reads = [r.reads for r in records]
        writes = [r.writes for r in records]
        updates = [r.updates for r in records]
        buffer_hit_ratios = [(r.buffer_hits / r.buffer_requests * 100) if r.buffer_requests > 0 else 0 
                            for r in records]
        avg_response = [r.avg_response_time for r in records]
        io_errors = [r.io_errors for r in records]
        
        # 1. File Operations by File
        x = np.arange(len(file_names))
        width = 0.25
        axes[0, 0].bar(x - width, reads, width, label='Reads', color=self.colors[0])
        axes[0, 0].bar(x, writes, width, label='Writes', color=self.colors[1])
        axes[0, 0].bar(x + width, updates, width, label='Updates', color=self.colors[2])
        axes[0, 0].set_title('File Operations by File', fontweight='bold')
        axes[0, 0].set_xlabel('File Name')
        axes[0, 0].set_ylabel('Operation Count')
        axes[0, 0].set_xticks(x)
        axes[0, 0].set_xticklabels(file_names, rotation=45, ha='right')
        axes[0, 0].legend()
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # 2. Buffer Hit Ratio
        axes[0, 1].barh(range(len(file_names)), buffer_hit_ratios, color=self.colors[3])
        axes[0, 1].set_title('Buffer Hit Ratio by File', fontweight='bold')
        axes[0, 1].set_xlabel('Hit Ratio (%)')
        axes[0, 1].set_ylabel('File Name')
        axes[0, 1].set_yticks(range(len(file_names)))
        axes[0, 1].set_yticklabels(file_names)
        axes[0, 1].axvline(80, color='red', linestyle='--', label='80% Target')
        axes[0, 1].legend()
        axes[0, 1].grid(axis='x', alpha=0.3)
        
        # 3. Average Response Time
        axes[0, 2].bar(range(len(file_names)), avg_response, color=self.colors[4])
        axes[0, 2].set_title('Average Response Time by File', fontweight='bold')
        axes[0, 2].set_xlabel('File Name')
        axes[0, 2].set_ylabel('Response Time (ms)')
        axes[0, 2].set_xticks(range(len(file_names)))
        axes[0, 2].set_xticklabels(file_names, rotation=45, ha='right')
        axes[0, 2].grid(axis='y', alpha=0.3)
        
        # 4. Total I/O by File Type
        file_types = {}
        for r in records:
            ft = r.file_type
            total_io = r.reads + r.writes + r.updates + r.deletes
            file_types[ft] = file_types.get(ft, 0) + total_io
        
        axes[1, 0].pie(file_types.values(), labels=file_types.keys(), 
                      autopct='%1.1f%%', colors=self.colors, startangle=90)
        axes[1, 0].set_title('Total I/O by File Type', fontweight='bold')
        
        # 5. I/O Errors
        axes[1, 1].bar(range(len(file_names)), io_errors, color='red', alpha=0.7)
        axes[1, 1].set_title('I/O Errors by File', fontweight='bold')
        axes[1, 1].set_xlabel('File Name')
        axes[1, 1].set_ylabel('Error Count')
        axes[1, 1].set_xticks(range(len(file_names)))
        axes[1, 1].set_xticklabels(file_names, rotation=45, ha='right')
        axes[1, 1].grid(axis='y', alpha=0.3)
        
        # 6. String Waits vs Requests
        string_waits = [r.string_waits for r in records]
        string_reqs = [r.string_requests for r in records]
        x = np.arange(len(file_names))
        width = 0.35
        axes[1, 2].bar(x - width/2, string_reqs, width, label='Requests', color=self.colors[0])
        axes[1, 2].bar(x + width/2, string_waits, width, label='Waits', color=self.colors[1])
        axes[1, 2].set_title('String Requests vs Waits', fontweight='bold')
        axes[1, 2].set_xlabel('File Name')
        axes[1, 2].set_ylabel('Count')
        axes[1, 2].set_xticks(x)
        axes[1, 2].set_xticklabels(file_names, rotation=45, ha='right')
        axes[1, 2].legend()
        axes[1, 2].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "smf110_subtype2_files_analysis.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[OK] Saved file analysis to {output_file}")
    
    def create_program_analysis(self, records: List[SMF110Type3]):
        """Create program statistics visualizations"""
        if not records:
            print("No program records to visualize")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('SMF Type 110 Subtype 3 - CICS Program Analysis', 
                     fontsize=16, fontweight='bold')
        
        # Extract data
        prog_names = [r.program_name for r in records]
        use_counts = [r.use_count for r in records]
        cpu_times = [r.cpu_time for r in records]
        storage_used = [r.storage_used / 1024 for r in records]  # Convert to KB
        abends = [r.abends for r in records]
        
        # 1. Program Usage Count
        axes[0, 0].barh(range(len(prog_names)), use_counts, color=self.colors[0])
        axes[0, 0].set_title('Program Usage Count', fontweight='bold')
        axes[0, 0].set_xlabel('Use Count')
        axes[0, 0].set_ylabel('Program Name')
        axes[0, 0].set_yticks(range(len(prog_names)))
        axes[0, 0].set_yticklabels(prog_names)
        axes[0, 0].grid(axis='x', alpha=0.3)
        
        # 2. CPU Time per Program
        axes[0, 1].bar(range(len(prog_names)), cpu_times, color=self.colors[1])
        axes[0, 1].set_title('CPU Time by Program', fontweight='bold')
        axes[0, 1].set_xlabel('Program Name')
        axes[0, 1].set_ylabel('CPU Time (ms)')
        axes[0, 1].set_xticks(range(len(prog_names)))
        axes[0, 1].set_xticklabels(prog_names, rotation=45, ha='right')
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        # 3. Storage Usage
        axes[0, 2].bar(range(len(prog_names)), storage_used, color=self.colors[2])
        axes[0, 2].set_title('Storage Usage by Program', fontweight='bold')
        axes[0, 2].set_xlabel('Program Name')
        axes[0, 2].set_ylabel('Storage (KB)')
        axes[0, 2].set_xticks(range(len(prog_names)))
        axes[0, 2].set_xticklabels(prog_names, rotation=45, ha='right')
        axes[0, 2].grid(axis='y', alpha=0.3)
        
        # 4. Language Distribution
        languages = {}
        for r in records:
            languages[r.language] = languages.get(r.language, 0) + 1
        
        axes[1, 0].pie(languages.values(), labels=languages.keys(), 
                      autopct='%1.1f%%', colors=self.colors, startangle=90)
        axes[1, 0].set_title('Program Language Distribution', fontweight='bold')
        
        # 5. Abends by Program
        axes[1, 1].bar(range(len(prog_names)), abends, color='red', alpha=0.7)
        axes[1, 1].set_title('Abends by Program', fontweight='bold')
        axes[1, 1].set_xlabel('Program Name')
        axes[1, 1].set_ylabel('Abend Count')
        axes[1, 1].set_xticks(range(len(prog_names)))
        axes[1, 1].set_xticklabels(prog_names, rotation=45, ha='right')
        axes[1, 1].grid(axis='y', alpha=0.3)
        
        # 6. Load Count vs Use Count
        load_counts = [r.load_count for r in records]
        x = np.arange(len(prog_names))
        width = 0.35
        axes[1, 2].bar(x - width/2, load_counts, width, label='Load Count', color=self.colors[3])
        axes[1, 2].bar(x + width/2, use_counts, width, label='Use Count', color=self.colors[4])
        axes[1, 2].set_title('Load Count vs Use Count', fontweight='bold')
        axes[1, 2].set_xlabel('Program Name')
        axes[1, 2].set_ylabel('Count')
        axes[1, 2].set_xticks(x)
        axes[1, 2].set_xticklabels(prog_names, rotation=45, ha='right')
        axes[1, 2].legend()
        axes[1, 2].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "smf110_subtype3_programs_analysis.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[OK] Saved program analysis to {output_file}")
    
    def create_terminal_analysis(self, records: List[SMF110Type4]):
        """Create terminal statistics visualizations"""
        if not records:
            print("No terminal records to visualize")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('SMF Type 110 Subtype 4 - CICS Terminal Analysis', 
                     fontsize=16, fontweight='bold')
        
        # Extract data
        term_ids = [r.terminal_id for r in records]
        transactions = [r.total_transactions for r in records]
        msg_sent = [r.messages_sent for r in records]
        msg_recv = [r.messages_received for r in records]
        bytes_sent = [r.bytes_sent / 1024 for r in records]  # Convert to KB
        errors = [r.transmission_errors + r.timeout_errors for r in records]
        
        # 1. Total Transactions by Terminal
        axes[0, 0].bar(range(len(term_ids)), transactions, color=self.colors[0])
        axes[0, 0].set_title('Total Transactions by Terminal', fontweight='bold')
        axes[0, 0].set_xlabel('Terminal ID')
        axes[0, 0].set_ylabel('Transaction Count')
        axes[0, 0].set_xticks(range(len(term_ids)))
        axes[0, 0].set_xticklabels(term_ids, rotation=45, ha='right')
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # 2. Messages Sent vs Received
        x = np.arange(len(term_ids))
        width = 0.35
        axes[0, 1].bar(x - width/2, msg_sent, width, label='Sent', color=self.colors[1])
        axes[0, 1].bar(x + width/2, msg_recv, width, label='Received', color=self.colors[2])
        axes[0, 1].set_title('Messages Sent vs Received', fontweight='bold')
        axes[0, 1].set_xlabel('Terminal ID')
        axes[0, 1].set_ylabel('Message Count')
        axes[0, 1].set_xticks(x)
        axes[0, 1].set_xticklabels(term_ids, rotation=45, ha='right')
        axes[0, 1].legend()
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        # 3. Data Volume (KB)
        axes[1, 0].bar(range(len(term_ids)), bytes_sent, color=self.colors[3])
        axes[1, 0].set_title('Data Volume Sent (KB)', fontweight='bold')
        axes[1, 0].set_xlabel('Terminal ID')
        axes[1, 0].set_ylabel('Kilobytes')
        axes[1, 0].set_xticks(range(len(term_ids)))
        axes[1, 0].set_xticklabels(term_ids, rotation=45, ha='right')
        axes[1, 0].grid(axis='y', alpha=0.3)
        
        # 4. Transmission Errors
        axes[1, 1].bar(range(len(term_ids)), errors, color='red', alpha=0.7)
        axes[1, 1].set_title('Transmission Errors by Terminal', fontweight='bold')
        axes[1, 1].set_xlabel('Terminal ID')
        axes[1, 1].set_ylabel('Error Count')
        axes[1, 1].set_xticks(range(len(term_ids)))
        axes[1, 1].set_xticklabels(term_ids, rotation=45, ha='right')
        axes[1, 1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "smf110_subtype4_terminals_analysis.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[OK] Saved terminal analysis to {output_file}")
    
    def create_storage_analysis(self, records: List[SMF110Type5]):
        """Create storage statistics visualizations"""
        if not records:
            print("No storage records to visualize")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('SMF Type 110 Subtype 5 - CICS Storage Analysis', 
                     fontsize=16, fontweight='bold')
        
        # Extract data
        pool_names = [r.pool_name for r in records]
        used_mb = [r.used_storage / (1024*1024) for r in records]
        free_mb = [r.free_storage / (1024*1024) for r in records]
        utilization = [(r.used_storage / r.total_storage * 100) if r.total_storage > 0 else 0 
                      for r in records]
        failed_getmains = [r.failed_getmains for r in records]
        
        # 1. Storage Utilization by Pool
        x = np.arange(len(pool_names))
        width = 0.35
        axes[0, 0].bar(x - width/2, used_mb, width, label='Used', color='orange')
        axes[0, 0].bar(x + width/2, free_mb, width, label='Free', color='green')
        axes[0, 0].set_title('Storage Utilization by Pool (MB)', fontweight='bold')
        axes[0, 0].set_xlabel('Storage Pool')
        axes[0, 0].set_ylabel('Storage (MB)')
        axes[0, 0].set_xticks(x)
        axes[0, 0].set_xticklabels(pool_names, rotation=45, ha='right')
        axes[0, 0].legend()
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # 2. Utilization Percentage
        colors = ['green' if u < 70 else 'orange' if u < 85 else 'red' for u in utilization]
        axes[0, 1].barh(range(len(pool_names)), utilization, color=colors)
        axes[0, 1].set_title('Storage Utilization (%)', fontweight='bold')
        axes[0, 1].set_xlabel('Utilization (%)')
        axes[0, 1].set_ylabel('Storage Pool')
        axes[0, 1].set_yticks(range(len(pool_names)))
        axes[0, 1].set_yticklabels(pool_names)
        axes[0, 1].axvline(70, color='orange', linestyle='--', alpha=0.5, label='70% Warning')
        axes[0, 1].axvline(85, color='red', linestyle='--', alpha=0.5, label='85% Critical')
        axes[0, 1].legend()
        axes[0, 1].grid(axis='x', alpha=0.3)
        
        # 3. GETMAIN/FREEMAIN Activity
        getmains = [r.getmain_requests for r in records]
        freemains = [r.freemain_requests for r in records]
        x = np.arange(len(pool_names))
        width = 0.35
        axes[1, 0].bar(x - width/2, getmains, width, label='GETMAIN', color=self.colors[0])
        axes[1, 0].bar(x + width/2, freemains, width, label='FREEMAIN', color=self.colors[1])
        axes[1, 0].set_title('GETMAIN/FREEMAIN Activity', fontweight='bold')
        axes[1, 0].set_xlabel('Storage Pool')
        axes[1, 0].set_ylabel('Request Count')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels(pool_names, rotation=45, ha='right')
        axes[1, 0].legend()
        axes[1, 0].grid(axis='y', alpha=0.3)
        
        # 4. Failed GETMAIN Requests
        axes[1, 1].bar(range(len(pool_names)), failed_getmains, color='red', alpha=0.7)
        axes[1, 1].set_title('Failed GETMAIN Requests', fontweight='bold')
        axes[1, 1].set_xlabel('Storage Pool')
        axes[1, 1].set_ylabel('Failure Count')
        axes[1, 1].set_xticks(range(len(pool_names)))
        axes[1, 1].set_xticklabels(pool_names, rotation=45, ha='right')
        axes[1, 1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "smf110_subtype5_storage_analysis.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[OK] Saved storage analysis to {output_file}")
    
    def create_summary_dashboard(self, 
                                 type1_records: List[SMF110Type1],
                                 type2_records: List[SMF110Type2],
                                 type3_records: List[SMF110Type3],
                                 type4_records: List[SMF110Type4],
                                 type5_records: List[SMF110Type5]):
        """Create overall CICS summary dashboard"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('SMF Type 110 - CICS Overall Performance Summary', 
                     fontsize=16, fontweight='bold')
        
        # 1. Record Count by Subtype
        subtypes = ['Trans', 'Files', 'Programs', 'Terms', 'Storage']
        counts = [len(type1_records), len(type2_records), len(type3_records), 
                 len(type4_records), len(type5_records)]
        axes[0, 0].bar(subtypes, counts, color=self.colors[:5])
        axes[0, 0].set_title('Record Count by Subtype', fontweight='bold')
        axes[0, 0].set_ylabel('Count')
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # 2. Total CPU Time by Transaction (if available)
        if type1_records:
            trans_cpu = {}
            for r in type1_records:
                trans_cpu[r.transaction_id] = trans_cpu.get(r.transaction_id, 0) + r.cpu_time
            
            axes[0, 1].pie(trans_cpu.values(), labels=trans_cpu.keys(), 
                          autopct='%1.1f%%', colors=self.colors, startangle=90)
            axes[0, 1].set_title('CPU Time by Transaction', fontweight='bold')
        else:
            axes[0, 1].text(0.5, 0.5, 'No Transaction Data', 
                           ha='center', va='center', fontsize=12)
        
        # 3. File I/O Summary (if available)
        if type2_records:
            total_reads = sum([r.reads for r in type2_records])
            total_writes = sum([r.writes for r in type2_records])
            total_updates = sum([r.updates for r in type2_records])
            total_deletes = sum([r.deletes for r in type2_records])
            
            io_ops = ['Reads', 'Writes', 'Updates', 'Deletes']
            io_counts = [total_reads, total_writes, total_updates, total_deletes]
            axes[0, 2].bar(io_ops, io_counts, color=self.colors[:4])
            axes[0, 2].set_title('Total File I/O Operations', fontweight='bold')
            axes[0, 2].set_ylabel('Operation Count')
            axes[0, 2].grid(axis='y', alpha=0.3)
        else:
            axes[0, 2].text(0.5, 0.5, 'No File Data', 
                           ha='center', va='center', fontsize=12)
        
        # 4. Program Language Distribution (if available)
        if type3_records:
            languages = {}
            for r in type3_records:
                languages[r.language] = languages.get(r.language, 0) + 1
            
            axes[1, 0].pie(languages.values(), labels=languages.keys(), 
                          autopct='%1.1f%%', colors=self.colors, startangle=90)
            axes[1, 0].set_title('Program Language Distribution', fontweight='bold')
        else:
            axes[1, 0].text(0.5, 0.5, 'No Program Data', 
                           ha='center', va='center', fontsize=12)
        
        # 5. Terminal Activity (if available)
        if type4_records:
            term_trans = [r.total_transactions for r in type4_records]
            term_ids = [r.terminal_id for r in type4_records]
            axes[1, 1].barh(range(len(term_ids)), term_trans, color=self.colors[0])
            axes[1, 1].set_title('Transactions by Terminal', fontweight='bold')
            axes[1, 1].set_xlabel('Transaction Count')
            axes[1, 1].set_yticks(range(len(term_ids)))
            axes[1, 1].set_yticklabels(term_ids)
            axes[1, 1].grid(axis='x', alpha=0.3)
        else:
            axes[1, 1].text(0.5, 0.5, 'No Terminal Data', 
                           ha='center', va='center', fontsize=12)
        
        # 6. Storage Pool Utilization (if available)
        if type5_records:
            pool_names = [r.pool_name for r in type5_records]
            utilization = [(r.used_storage / r.total_storage * 100) if r.total_storage > 0 else 0 
                          for r in type5_records]
            colors = ['green' if u < 70 else 'orange' if u < 85 else 'red' for u in utilization]
            axes[1, 2].bar(range(len(pool_names)), utilization, color=colors)
            axes[1, 2].set_title('Storage Pool Utilization (%)', fontweight='bold')
            axes[1, 2].set_xlabel('Storage Pool')
            axes[1, 2].set_ylabel('Utilization (%)')
            axes[1, 2].set_xticks(range(len(pool_names)))
            axes[1, 2].set_xticklabels(pool_names, rotation=45, ha='right')
            axes[1, 2].axhline(70, color='orange', linestyle='--', alpha=0.5)
            axes[1, 2].axhline(85, color='red', linestyle='--', alpha=0.5)
            axes[1, 2].grid(axis='y', alpha=0.3)
        else:
            axes[1, 2].text(0.5, 0.5, 'No Storage Data', 
                           ha='center', va='center', fontsize=12)
        
        plt.tight_layout()
        output_file = self.output_dir / "smf110_summary_dashboard.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[OK] Saved summary dashboard to {output_file}")
    
    def generate_all_visualizations(self,
                                   type1_records: List[SMF110Type1],
                                   type2_records: List[SMF110Type2],
                                   type3_records: List[SMF110Type3],
                                   type4_records: List[SMF110Type4],
                                   type5_records: List[SMF110Type5]):
        """Generate all visualization charts"""
        print("\n" + "="*60)
        print("Generating SMF Type 110 CICS Visualizations")
        print("="*60)
        
        self.create_transaction_analysis(type1_records)
        self.create_file_analysis(type2_records)
        self.create_program_analysis(type3_records)
        self.create_terminal_analysis(type4_records)
        self.create_storage_analysis(type5_records)
        self.create_summary_dashboard(type1_records, type2_records, type3_records, 
                                      type4_records, type5_records)
        
        print("\n" + "="*60)
        print("All visualizations generated successfully!")
        print(f"Output directory: {self.output_dir.absolute()}")
        print("="*60)

def main():
    """Generate sample visualizations for testing"""
    from smf110_structures import SMF110SampleGenerator
    
    print("SMF Type 110 CICS Visualization Engine - Test Mode")
    print("Generating sample CICS statistics visualizations...")
    
    # Generate sample data
    type1_records = SMF110SampleGenerator.generate_type1_records(15)
    type2_records = SMF110SampleGenerator.generate_type2_records(10)
    type3_records = SMF110SampleGenerator.generate_type3_records(12)
    type4_records = SMF110SampleGenerator.generate_type4_records(8)
    type5_records = SMF110SampleGenerator.generate_type5_records(6)
    
    # Generate visualizations
    visualizer = SMF110Visualizer()
    visualizer.generate_all_visualizations(
        type1_records,
        type2_records,
        type3_records,
        type4_records,
        type5_records
    )

if __name__ == "__main__":
    main()
