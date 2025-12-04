"""
SMF Type 30 Analysis and Visualization
Creates comprehensive charts and analysis dashboard for all subtypes
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
from smf30_structures import SMF30SampleGenerator

class SMF30Analyzer:
    """Analyze SMF Type 30 records and generate visualizations"""
    
    SUBTYPE_NAMES = {
        1: "Job Step Termination",
        2: "Job Termination",
        3: "Step Initiation",
        4: "Job Initiation",
        5: "NetStep Completion",
    }
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.records_by_subtype = {}
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    def load_sample_data(self):
        """Load sample records"""
        all_records = SMF30SampleGenerator.generate_all_records()
        for subtype, records in all_records.items():
            self.records_by_subtype[subtype] = [r.to_dict() for r in records]
        return self.records_by_subtype
    
    def analyze_subtype1(self) -> pd.DataFrame:
        """Analyze Job Step Termination records"""
        if 1 not in self.records_by_subtype:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.records_by_subtype[1])
        return df
    
    def analyze_subtype2(self) -> pd.DataFrame:
        """Analyze Job Termination records"""
        if 2 not in self.records_by_subtype:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.records_by_subtype[2])
        return df
    
    def analyze_subtype3(self) -> pd.DataFrame:
        """Analyze Step Initiation records"""
        if 3 not in self.records_by_subtype:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.records_by_subtype[3])
        return df
    
    def analyze_subtype4(self) -> pd.DataFrame:
        """Analyze Job Initiation records"""
        if 4 not in self.records_by_subtype:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.records_by_subtype[4])
        return df
    
    def analyze_subtype5(self) -> pd.DataFrame:
        """Analyze NetStep records"""
        if 5 not in self.records_by_subtype:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.records_by_subtype[5])
        return df
    
    def create_subtype1_visualization(self):
        """Subtype 1: Job Step Termination Analysis"""
        df = self.analyze_subtype1()
        if df.empty:
            return
        
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle('SMF Type 30 Subtype 1: Job Step Termination Analysis', 
                     fontsize=16, fontweight='bold')
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. CPU Time Distribution
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.hist(df['cpu_time_ms'], bins=10, color=self.colors[0], edgecolor='black', alpha=0.7)
        ax1.set_xlabel('CPU Time (ms)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('CPU Time Distribution')
        ax1.grid(True, alpha=0.3)
        
        # 2. Return Codes
        ax2 = fig.add_subplot(gs[0, 1])
        rc_counts = df['return_code'].value_counts()
        ax2.bar(rc_counts.index.astype(str), rc_counts.values, color=self.colors[1], alpha=0.7)
        ax2.set_xlabel('Return Code')
        ax2.set_ylabel('Count')
        ax2.set_title('Return Code Distribution')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. IO Count vs CPU Time
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.scatter(df['cpu_time_ms'], df['io_count'], color=self.colors[2], s=100, alpha=0.6)
        ax3.set_xlabel('CPU Time (ms)')
        ax3.set_ylabel('IO Count')
        ax3.set_title('CPU Time vs IO Count')
        ax3.grid(True, alpha=0.3)
        
        # 4. Elapsed Time
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.barh(range(len(df)), df['elapsed_time_ms'].values, color=self.colors[3], alpha=0.7)
        ax4.set_xlabel('Elapsed Time (ms)')
        ax4.set_ylabel('Step Index')
        ax4.set_title('Elapsed Time per Step')
        ax4.grid(True, alpha=0.3, axis='x')
        
        # 5. Pages Read vs Written
        ax5 = fig.add_subplot(gs[1, 1])
        x_pos = np.arange(len(df))
        width = 0.35
        ax5.bar(x_pos - width/2, df['pages_read'], width, label='Pages Read', 
                color=self.colors[0], alpha=0.7)
        ax5.bar(x_pos + width/2, df['pages_written'], width, label='Pages Written', 
                color=self.colors[1], alpha=0.7)
        ax5.set_xlabel('Step Index')
        ax5.set_ylabel('Pages')
        ax5.set_title('Pages Read vs Written')
        ax5.legend()
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 6. Service Units
        ax6 = fig.add_subplot(gs[1, 2])
        ax6.bar(range(len(df)), df['service_units'].values, color=self.colors[4], alpha=0.7)
        ax6.set_xlabel('Step Index')
        ax6.set_ylabel('Service Units')
        ax6.set_title('Service Units Consumed')
        ax6.grid(True, alpha=0.3, axis='y')
        
        # 7. Statistics table
        ax7 = fig.add_subplot(gs[2, :])
        ax7.axis('tight')
        ax7.axis('off')
        
        stats = [
            ['Metric', 'Min', 'Max', 'Mean', 'Std Dev'],
            ['CPU Time (ms)', f"{df['cpu_time_ms'].min()}", f"{df['cpu_time_ms'].max()}", 
             f"{df['cpu_time_ms'].mean():.0f}", f"{df['cpu_time_ms'].std():.0f}"],
            ['Elapsed Time (ms)', f"{df['elapsed_time_ms'].min()}", f"{df['elapsed_time_ms'].max()}", 
             f"{df['elapsed_time_ms'].mean():.0f}", f"{df['elapsed_time_ms'].std():.0f}"],
            ['IO Count', f"{df['io_count'].min()}", f"{df['io_count'].max()}", 
             f"{df['io_count'].mean():.0f}", f"{df['io_count'].std():.0f}"],
            ['Success Rate', f"{(df['return_code']==0).sum()}/{len(df)}", '', 
             f"{(df['return_code']==0).sum()/len(df)*100:.1f}%", ''],
        ]
        
        table = ax7.table(cellText=stats, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.8)
        
        # Color header row
        for i in range(5):
            table[(0, i)].set_facecolor(self.colors[0])
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        filepath = self.output_dir / "smf30_subtype1_analysis.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Saved: {filepath}")
        plt.close()
    
    def create_subtype2_visualization(self):
        """Subtype 2: Job Termination Analysis"""
        df = self.analyze_subtype2()
        if df.empty:
            return
        
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle('SMF Type 30 Subtype 2: Job Termination Analysis', 
                     fontsize=16, fontweight='bold')
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. Total CPU Time
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.bar(range(len(df)), df['cpu_time_ms'].values, color=self.colors[0], alpha=0.7)
        ax1.set_xlabel('Job Index')
        ax1.set_ylabel('Total CPU Time (ms)')
        ax1.set_title('Total CPU Time per Job')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Total Steps vs Failed Steps
        ax2 = fig.add_subplot(gs[0, 1])
        x_pos = np.arange(len(df))
        width = 0.35
        ax2.bar(x_pos - width/2, df['total_steps'], width, label='Total Steps', 
                color=self.colors[1], alpha=0.7)
        ax2.bar(x_pos + width/2, df['failed_steps'], width, label='Failed Steps', 
                color=self.colors[0], alpha=0.7)
        ax2.set_xlabel('Job Index')
        ax2.set_ylabel('Steps')
        ax2.set_title('Total vs Failed Steps')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Memory Allocated vs Used
        ax3 = fig.add_subplot(gs[0, 2])
        x_pos = np.arange(len(df))
        width = 0.35
        ax3.bar(x_pos - width/2, df['memory_allocated_mb'], width, label='Allocated', 
                color=self.colors[2], alpha=0.7)
        ax3.bar(x_pos + width/2, df['memory_max_used_mb'], width, label='Max Used', 
                color=self.colors[3], alpha=0.7)
        ax3.set_xlabel('Job Index')
        ax3.set_ylabel('Memory (MB)')
        ax3.set_title('Memory Allocation vs Usage')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. Total IO Operations
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.bar(range(len(df)), df['total_excp_count'].values, color=self.colors[4], alpha=0.7)
        ax4.set_xlabel('Job Index')
        ax4.set_ylabel('EXCP Count')
        ax4.set_title('Total EXCP Operations')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 5. Total Pages
        ax5 = fig.add_subplot(gs[1, 1])
        x_pos = np.arange(len(df))
        width = 0.35
        ax5.bar(x_pos - width/2, df['total_pages_read'], width, label='Pages Read', 
                color=self.colors[0], alpha=0.7)
        ax5.bar(x_pos + width/2, df['total_pages_written'], width, label='Pages Written', 
                color=self.colors[1], alpha=0.7)
        ax5.set_xlabel('Job Index')
        ax5.set_ylabel('Pages')
        ax5.set_title('Total Pages Read vs Written')
        ax5.legend()
        ax5.grid(True, alpha=0.3, axis='y')
        
        # 6. Job Class Distribution
        ax6 = fig.add_subplot(gs[1, 2])
        class_counts = df['job_class'].value_counts()
        ax6.pie(class_counts.values, labels=class_counts.index, autopct='%1.1f%%',
                colors=self.colors, startangle=90)
        ax6.set_title('Job Class Distribution')
        
        # 7. Statistics table
        ax7 = fig.add_subplot(gs[2, :])
        ax7.axis('tight')
        ax7.axis('off')
        
        stats = [
            ['Metric', 'Min', 'Max', 'Mean', 'Std Dev'],
            ['CPU Time (ms)', f"{df['cpu_time_ms'].min()}", f"{df['cpu_time_ms'].max()}", 
             f"{df['cpu_time_ms'].mean():.0f}", f"{df['cpu_time_ms'].std():.0f}"],
            ['Memory Allocated (MB)', f"{df['memory_allocated_mb'].min()}", 
             f"{df['memory_allocated_mb'].max()}", f"{df['memory_allocated_mb'].mean():.0f}", 
             f"{df['memory_allocated_mb'].std():.0f}"],
            ['Total Steps', f"{df['total_steps'].min()}", f"{df['total_steps'].max()}", 
             f"{df['total_steps'].mean():.1f}", f"{df['total_steps'].std():.1f}"],
            ['Success Rate', f"{(df['failed_steps']==0).sum()}/{len(df)}", '', 
             f"{(df['failed_steps']==0).sum()/len(df)*100:.1f}%", ''],
        ]
        
        table = ax7.table(cellText=stats, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.8)
        
        for i in range(5):
            table[(0, i)].set_facecolor(self.colors[1])
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        filepath = self.output_dir / "smf30_subtype2_analysis.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Saved: {filepath}")
        plt.close()
    
    def create_subtype3_visualization(self):
        """Subtype 3: Step Initiation Analysis"""
        df = self.analyze_subtype3()
        if df.empty:
            return
        
        fig = plt.figure(figsize=(15, 8))
        fig.suptitle('SMF Type 30 Subtype 3: Step Initiation Analysis', 
                     fontsize=16, fontweight='bold')
        gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. Memory Region Size Distribution
        ax1 = fig.add_subplot(gs[0, 0])
        mem_counts = df['memory_region_size_mb'].value_counts().sort_index()
        ax1.bar(mem_counts.index, mem_counts.values, color=self.colors[2], alpha=0.7)
        ax1.set_xlabel('Memory Region Size (MB)')
        ax1.set_ylabel('Count')
        ax1.set_title('Memory Region Size Distribution')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Step Name Distribution
        ax2 = fig.add_subplot(gs[0, 1])
        step_counts = df['step_name'].value_counts()
        ax2.barh(step_counts.index, step_counts.values, color=self.colors[3], alpha=0.7)
        ax2.set_xlabel('Count')
        ax2.set_title('Step Name Distribution')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # 3. Program Name Distribution
        ax3 = fig.add_subplot(gs[0, 2])
        prog_counts = df['program_name'].value_counts()
        colors_prog = plt.cm.Set3(np.linspace(0, 1, len(prog_counts)))
        ax3.pie(prog_counts.values, labels=prog_counts.index, autopct='%1.1f%%',
                colors=colors_prog, startangle=90)
        ax3.set_title('Program Name Distribution')
        
        # 4. Timeline
        ax4 = fig.add_subplot(gs[1, :2])
        ax4.scatter(range(len(df)), df['memory_region_size_mb'], 
                   c=range(len(df)), cmap='viridis', s=100, alpha=0.6)
        ax4.set_xlabel('Step Sequence')
        ax4.set_ylabel('Memory Region Size (MB)')
        ax4.set_title('Step Initiation Timeline - Memory Allocation')
        ax4.grid(True, alpha=0.3)
        
        # 5. Statistics table
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.axis('tight')
        ax5.axis('off')
        
        stats = [
            ['Metric', 'Value'],
            ['Total Steps Initiated', f"{len(df)}"],
            ['Avg Memory Size (MB)', f"{df['memory_region_size_mb'].mean():.0f}"],
            ['Min Memory Size (MB)', f"{df['memory_region_size_mb'].min()}"],
            ['Max Memory Size (MB)', f"{df['memory_region_size_mb'].max()}"],
            ['Unique Procedures', f"{df['procedure_step_name'].nunique()}"],
        ]
        
        table = ax5.table(cellText=stats, loc='center', cellLoc='left')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        for i in range(2):
            table[(0, i)].set_facecolor(self.colors[2])
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        filepath = self.output_dir / "smf30_subtype3_analysis.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Saved: {filepath}")
        plt.close()
    
    def create_subtype4_visualization(self):
        """Subtype 4: Job Initiation Analysis"""
        df = self.analyze_subtype4()
        if df.empty:
            return
        
        fig = plt.figure(figsize=(15, 8))
        fig.suptitle('SMF Type 30 Subtype 4: Job Initiation Analysis', 
                     fontsize=16, fontweight='bold')
        gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. Job Class Distribution
        ax1 = fig.add_subplot(gs[0, 0])
        class_counts = df['job_class'].value_counts()
        ax1.bar(class_counts.index, class_counts.values, color=self.colors[0], alpha=0.7)
        ax1.set_xlabel('Job Class')
        ax1.set_ylabel('Count')
        ax1.set_title('Job Class Distribution')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Job Priority
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.scatter(range(len(df)), df['job_priority'], color=self.colors[1], s=100, alpha=0.6)
        ax2.set_xlabel('Job Index')
        ax2.set_ylabel('Priority')
        ax2.set_title('Job Priority Levels')
        ax2.grid(True, alpha=0.3)
        
        # 3. User ID Distribution
        ax3 = fig.add_subplot(gs[0, 2])
        user_counts = df['owning_userid'].value_counts()
        ax3.barh(user_counts.index, user_counts.values, color=self.colors[2], alpha=0.7)
        ax3.set_xlabel('Count')
        ax3.set_title('User ID Distribution')
        ax3.grid(True, alpha=0.3, axis='x')
        
        # 4. Job Timeline
        ax4 = fig.add_subplot(gs[1, :2])
        ax4.barh(range(len(df)), [1]*len(df), color=self.colors[3], alpha=0.7)
        ax4.set_yticks(range(len(df)))
        ax4.set_yticklabels([f"Job {i+1}" for i in range(len(df))])
        ax4.set_xlabel('Initiation Sequence')
        ax4.set_title('Job Initiation Timeline')
        ax4.set_xlim(0, len(df)+1)
        
        # 5. Statistics table
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.axis('tight')
        ax5.axis('off')
        
        stats = [
            ['Metric', 'Value'],
            ['Total Jobs Initiated', f"{len(df)}"],
            ['Avg Priority', f"{df['job_priority'].mean():.1f}"],
            ['Min Priority', f"{df['job_priority'].min()}"],
            ['Max Priority', f"{df['job_priority'].max()}"],
            ['Unique Users', f"{df['owning_userid'].nunique()}"],
        ]
        
        table = ax5.table(cellText=stats, loc='center', cellLoc='left')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        for i in range(2):
            table[(0, i)].set_facecolor(self.colors[3])
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        filepath = self.output_dir / "smf30_subtype4_analysis.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Saved: {filepath}")
        plt.close()
    
    def create_subtype5_visualization(self):
        """Subtype 5: NetStep Analysis"""
        df = self.analyze_subtype5()
        if df.empty:
            return
        
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle('SMF Type 30 Subtype 5: NetStep Completion Analysis', 
                     fontsize=16, fontweight='bold')
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. Bytes Transmitted vs Received
        ax1 = fig.add_subplot(gs[0, 0])
        x_pos = np.arange(len(df))
        width = 0.35
        ax1.bar(x_pos - width/2, df['bytes_transmitted']/1000, width, 
                label='Transmitted', color=self.colors[0], alpha=0.7)
        ax1.bar(x_pos + width/2, df['bytes_received']/1000, width, 
                label='Received', color=self.colors[1], alpha=0.7)
        ax1.set_xlabel('NetStep Index')
        ax1.set_ylabel('Bytes (KB)')
        ax1.set_title('Network Data Transfer')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Network Response Time
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.bar(range(len(df)), df['network_response_time_ms'], 
                color=self.colors[2], alpha=0.7)
        ax2.set_xlabel('NetStep Index')
        ax2.set_ylabel('Response Time (ms)')
        ax2.set_title('Network Response Time')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Return Codes
        ax3 = fig.add_subplot(gs[0, 2])
        rc_counts = df['return_code'].value_counts()
        colors_rc = [self.colors[0] if x == 0 else self.colors[1] for x in rc_counts.index]
        ax3.bar(rc_counts.index.astype(str), rc_counts.values, color=colors_rc, alpha=0.7)
        ax3.set_xlabel('Return Code')
        ax3.set_ylabel('Count')
        ax3.set_title('Return Code Distribution')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. CPU Time
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.bar(range(len(df)), df['cpu_time_ms'], color=self.colors[3], alpha=0.7)
        ax4.set_xlabel('NetStep Index')
        ax4.set_ylabel('CPU Time (ms)')
        ax4.set_title('CPU Time per NetStep')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # 5. Network Destination Distribution
        ax5 = fig.add_subplot(gs[1, 1])
        dest_counts = df['network_destination'].value_counts()
        ax5.pie(dest_counts.values, labels=dest_counts.index, autopct='%1.1f%%',
                colors=self.colors, startangle=90)
        ax5.set_title('Network Destination Distribution')
        
        # 6. Service Units
        ax6 = fig.add_subplot(gs[1, 2])
        ax6.scatter(df['bytes_transmitted'], df['service_units'], 
                   c=df['network_response_time_ms'], cmap='coolwarm', 
                   s=100, alpha=0.6)
        ax6.set_xlabel('Bytes Transmitted')
        ax6.set_ylabel('Service Units')
        ax6.set_title('Data Size vs Service Units')
        cbar = plt.colorbar(ax6.collections[0], ax=ax6)
        cbar.set_label('Response Time (ms)')
        ax6.grid(True, alpha=0.3)
        
        # 7. Statistics table
        ax7 = fig.add_subplot(gs[2, :])
        ax7.axis('tight')
        ax7.axis('off')
        
        stats = [
            ['Metric', 'Min', 'Max', 'Mean', 'Std Dev'],
            ['Bytes Transmitted', f"{df['bytes_transmitted'].min()}", 
             f"{df['bytes_transmitted'].max()}", f"{df['bytes_transmitted'].mean():.0f}", 
             f"{df['bytes_transmitted'].std():.0f}"],
            ['Bytes Received', f"{df['bytes_received'].min()}", 
             f"{df['bytes_received'].max()}", f"{df['bytes_received'].mean():.0f}", 
             f"{df['bytes_received'].std():.0f}"],
            ['Response Time (ms)', f"{df['network_response_time_ms'].min()}", 
             f"{df['network_response_time_ms'].max()}", f"{df['network_response_time_ms'].mean():.0f}", 
             f"{df['network_response_time_ms'].std():.0f}"],
            ['Success Rate', f"{(df['return_code']==0).sum()}/{len(df)}", '', 
             f"{(df['return_code']==0).sum()/len(df)*100:.1f}%", ''],
        ]
        
        table = ax7.table(cellText=stats, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.8)
        
        for i in range(5):
            table[(0, i)].set_facecolor(self.colors[4])
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        filepath = self.output_dir / "smf30_subtype5_analysis.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Saved: {filepath}")
        plt.close()
    
    def create_summary_dashboard(self):
        """Create overall dashboard with all subtypes"""
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle('SMF Type 30 - Complete Analysis Dashboard', 
                     fontsize=18, fontweight='bold')
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
        
        # Record count by subtype
        ax1 = fig.add_subplot(gs[0, 0])
        subtype_counts = [len(self.records_by_subtype.get(i, [])) for i in range(1, 6)]
        ax1.bar(range(1, 6), subtype_counts, color=self.colors, alpha=0.7)
        ax1.set_xlabel('Subtype')
        ax1.set_ylabel('Record Count')
        ax1.set_title('Records per Subtype')
        ax1.set_xticks(range(1, 6))
        ax1.grid(True, alpha=0.3, axis='y')
        
        # CPU Time by subtype
        ax2 = fig.add_subplot(gs[0, 1])
        cpu_data = []
        for i in [1, 2, 5]:
            if i in self.records_by_subtype:
                df = pd.DataFrame(self.records_by_subtype[i])
                if 'cpu_time_ms' in df.columns:
                    cpu_data.append(df['cpu_time_ms'].mean())
                else:
                    cpu_data.append(0)
            else:
                cpu_data.append(0)
        
        ax2.bar(['ST1', 'ST2', 'ST5'], cpu_data, color=[self.colors[0], self.colors[1], self.colors[4]], alpha=0.7)
        ax2.set_ylabel('Average CPU Time (ms)')
        ax2.set_title('Average CPU Time by Subtype')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Success Rate
        ax3 = fig.add_subplot(gs[0, 2])
        success_rates = []
        for i in [1, 2, 5]:
            if i in self.records_by_subtype:
                df = pd.DataFrame(self.records_by_subtype[i])
                if 'return_code' in df.columns:
                    rate = (df['return_code'] == 0).sum() / len(df) * 100
                    success_rates.append(rate)
                else:
                    success_rates.append(100)
            else:
                success_rates.append(100)
        
        ax3.bar(['ST1', 'ST2', 'ST5'], success_rates, color=[self.colors[0], self.colors[1], self.colors[4]], alpha=0.7)
        ax3.set_ylabel('Success Rate (%)')
        ax3.set_ylim(0, 105)
        ax3.set_title('Job Success Rate')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Subtype details
        ax4 = fig.add_subplot(gs[1:, :])
        ax4.axis('tight')
        ax4.axis('off')
        
        summary_data = [
            ['Subtype', 'Name', 'Records', 'Key Metrics', 'Focus Area'],
            ['1', 'Job Step Termination', f"{len(self.records_by_subtype.get(1, []))}",
             'CPU, IO, Pages, Return Code', 'Step-level performance'],
            ['2', 'Job Termination', f"{len(self.records_by_subtype.get(2, []))}",
             'Total CPU, Memory, Steps, EXCP', 'Overall job resource usage'],
            ['3', 'Step Initiation', f"{len(self.records_by_subtype.get(3, []))}",
             'Memory allocation, Step name', 'Step startup details'],
            ['4', 'Job Initiation', f"{len(self.records_by_subtype.get(4, []))}",
             'Job class, Priority, User', 'Job scheduling details'],
            ['5', 'NetStep Completion', f"{len(self.records_by_subtype.get(5, []))}",
             'Network data, Response time', 'Network performance'],
        ]
        
        table = ax4.table(cellText=summary_data, loc='center', cellLoc='left')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        for i in range(5):
            table[(0, i)].set_facecolor('#34495E')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        for i in range(1, 6):
            table[(i, 0)].set_facecolor(self.colors[i-1])
            table[(i, 0)].set_text_props(weight='bold', color='white')
        
        filepath = self.output_dir / "smf30_summary_dashboard.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Saved: {filepath}")
        plt.close()
    
    def generate_all_visualizations(self):
        """Generate all visualizations"""
        print("\n" + "="*60)
        print("Generating SMF Type 30 Visualizations")
        print("="*60)
        
        self.create_subtype1_visualization()
        self.create_subtype2_visualization()
        self.create_subtype3_visualization()
        self.create_subtype4_visualization()
        self.create_subtype5_visualization()
        self.create_summary_dashboard()
        
        print("\nAll visualizations complete!")

def main():
    """Main execution"""
    analyzer = SMF30Analyzer(output_dir="./reports")
    analyzer.load_sample_data()
    analyzer.generate_all_visualizations()

if __name__ == "__main__":
    main()
