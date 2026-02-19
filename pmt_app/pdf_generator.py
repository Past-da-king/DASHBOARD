import io
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, NextPageTemplate
)
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import calculations
import database

# Set plotting style
plt.style.use('ggplot')
sns.set_palette("deep")

# --- BRAND COLORS ---
PRIMARY_COLOR = colors.HexColor('#2c5aa0')
SECONDARY_COLOR = colors.HexColor('#5fa2e8')
ACCENT_COLOR = colors.HexColor('#ffc107')
SUCCESS_COLOR = colors.HexColor('#4caf50')
DANGER_COLOR = colors.HexColor('#f44336')
TEXT_COLOR = colors.HexColor('#333333')
LIGHT_BG = colors.HexColor('#f8f9fa')

class PDFReportGenerator:
    def __init__(self, project_id):
        self.project_id = project_id
        self.metrics = calculations.get_project_metrics(project_id)
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom paragraph styles for the report"""
        self.styles.add(ParagraphStyle(
            name='CoverTitle',
            parent=self.styles['Title'],
            fontSize=32,
            leading=40,
            textColor=PRIMARY_COLOR,
            alignment=TA_CENTER,
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='CoverSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceAfter=50
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            leading=20,
            textColor=PRIMARY_COLOR,
            borderPadding=(0, 0, 8, 0),
            spaceBefore=20,
            spaceAfter=15
        ))
        
        self.styles.add(ParagraphStyle(
            name='NormalJustified',
            parent=self.styles['Normal'],
            alignment=TA_JUSTIFY,
            fontSize=10,
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['BodyText'],
            fontSize=9,
            textColor=colors.gray,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['BodyText'],
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=PRIMARY_COLOR,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='StatusTag',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

    def _header_footer(self, canvas, doc):
        """Draw Header and Footer on every page"""
        canvas.saveState()
        
        # Header
        canvas.setFillColor(PRIMARY_COLOR)
        canvas.rect(0, A4[1] - 50, A4[0], 50, fill=1, stroke=0)
        
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 14)
        canvas.drawString(40, A4[1] - 30, f"{self.metrics['project_name']}")
        
        canvas.setFont('Helvetica', 10)
        canvas.drawRightString(A4[0] - 40, A4[1] - 30, f"Status Report | {datetime.now().strftime('%Y-%m-%d')}")
        
        # Footer
        canvas.setStrokeColor(colors.lightgrey)
        canvas.line(40, 50, A4[0] - 40, 50)
        
        canvas.setFillColor(colors.gray)
        canvas.setFont('Helvetica', 9)
        canvas.drawString(40, 30, "Confidential - Internal Use Only")
        canvas.drawRightString(A4[0] - 40, 30, f"Page {doc.page}")
        
        canvas.restoreState()

    def _create_financial_chart(self):
        """Create a Bar chart for Financial Overview"""
        plt.figure(figsize=(6, 3))
        
        categories = ['Budget', 'Forecast', 'Actual']
        values = [
            self.metrics['total_budget'], 
            self.metrics['forecast'], 
            self.metrics['total_spent']
        ]
        colors_list = ['#2c5aa0', '#7c3aed', '#0891b2']
        
        bars = plt.bar(categories, values, color=colors_list, width=0.6)
        
        # Add labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'R {height/1000:.1f}k',
                    ha='center', va='bottom', fontsize=9)
            
        plt.title('Financial Performance', fontsize=12, pad=15)
        plt.ylabel('Amount (ZAR)')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        return buf

    def _create_cost_breakdown_chart(self):
        """Create a Donut chart for Cost Breakdown"""
        exp_df = calculations.get_category_spending(self.project_id)
        
        plt.figure(figsize=(5, 3))
        
        if not exp_df.empty:
            plt.pie(exp_df['total'], labels=exp_df['category'], autopct='%1.1f%%', 
                   startangle=90, pctdistance=0.85, colors=sns.color_palette("pastel"))
            
            # Draw circle for Donut
            centre_circle = plt.Circle((0,0),0.70,fc='white')
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)
            
            plt.title('Cost Distribution', fontsize=12)
        else:
            plt.text(0.5, 0.5, 'No Expenditure Data', ha='center', va='center')
            plt.axis('off')
            
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        return buf

    def _create_progress_chart(self):
        """Create a Horizontal Progress Bar"""
        plt.figure(figsize=(6, 1.5))
        
        progress = self.metrics['pct_complete']
        
        # Background
        plt.barh([0], [100], color='#f0f0f0', height=0.5)
        # Progress
        plt.barh([0], [progress], color='#4caf50', height=0.5)
        
        plt.xlim(0, 100)
        plt.yticks([])
        plt.xticks([0, 25, 50, 75, 100], ['0%', '25%', '50%', '75%', '100%'])
        plt.title(f'Overall Progress: {progress:.1f}%', fontsize=10)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        return buf

    def generate(self):
        buffer = io.BytesIO()
        
        # Layout Setup
        doc = BaseDocTemplate(buffer, pagesize=A4, topMargin=60, bottomMargin=60)
        
        # Frame for content
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        
        # Template
        template = PageTemplate(id='report', frames=frame, onPage=self._header_footer)
        doc.addPageTemplates([template])
        
        story = []
        
        if not self.metrics:
            story.append(Paragraph("Error: Project data not found", self.styles['Normal']))
            doc.build(story)
            buffer.seek(0)
            return buffer

        # --- TITLE PAGE CONTENT (Manually spaced since we are inside the template) ---
        story.append(Spacer(1, 40))
        story.append(Paragraph("PROJECT STATUS REPORT", self.styles['CoverTitle']))
        story.append(Paragraph(f"{self.metrics['project_name']}", self.styles['Heading1']))
        story.append(Paragraph(f"Project #: {self.metrics['project_number']}", self.styles['CoverSubtitle']))
        
        # Title Page Grid of Key Stats
        key_stats_data = [
            ['BUDGET USED', 'SCHEDULE HEALTH', 'RISKS OPEN'],
            [f"{self.metrics['budget_used_pct']:.1f}%", self.metrics['schedule_health'], "Checking..."]
        ]
        
        # Fetch open risk count
        risks_df = database.get_project_risks(self.project_id)
        open_risks = len(risks_df[risks_df['status'] == 'Open']) if not risks_df.empty else 0
        key_stats_data[1][2] = str(open_risks)
        
        t_title_stats = Table(key_stats_data, colWidths=[2*inch, 2*inch, 2*inch])
        t_title_stats.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('TEXTCOLOR', (0,0), (-1,0), colors.gray),
            ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,1), (-1,1), 18),
            ('TEXTCOLOR', (0,1), (-1,1), PRIMARY_COLOR),
            ('TOPPADDING', (0,1), (-1,1), 10),
        ]))
        story.append(t_title_stats)
        story.append(Spacer(1, 50))
        
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        story.append(PageBreak())

        # --- EXECUTIVE SUMMARY ---
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        status_color = "#4caf50" if self.metrics['budget_health'] == 'Green' else "#f44336"
        status_text = "exceeding budget" if self.metrics['forecast'] > self.metrics['total_budget'] else "well within budget"
        
        summary_html = f"""
        <para alignment="justify">
        The project <b>{self.metrics['project_name']}</b> is currently in <b>{self.metrics['actual_status']}</b> status. 
        Physical completion is estimated at <b>{self.metrics['pct_complete']:.1f}%</b>. 
        Financial performance shows we are <font color="{status_color}"><b>{status_text}</b></font> 
        with a forecasted completion cost of <b>R {self.metrics['forecast']:,.2f}</b> against a budget of <b>R {self.metrics['total_budget']:,.2f}</b>.
        <br/><br/>
        Key highlights for this period involve the steady progression of baseline activities and the management of {open_risks} active risks.
        </para>
        """
        story.append(Paragraph(summary_html, self.styles['NormalJustified']))
        story.append(Spacer(1, 20))

        # --- PROGRESS & HEALTH SECTION ---
        story.append(Paragraph("Project Health & Progress", self.styles['SectionHeader']))
        
        # Grid: Chart Left, Health Table Right
        prog_img = Image(self._create_progress_chart(), width=6*inch, height=1.5*inch)
        story.append(prog_img)
        story.append(Spacer(1, 15))
        
        # Health Table
        health_data = [
            ['Metric', 'Status', 'Indicator'],
            ['Budget', self.metrics['budget_health'], ''],
            ['Schedule', self.metrics['schedule_health'], ''],
            ['Scope', 'Green', ''], # Static for now
            ['Resources', 'Green', ''] # Static for now
        ]
        
        t_health = Table(health_data, colWidths=[2*inch, 2*inch, 1*inch])
        
        # Style logic for indicators
        style_cmds = [
            ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#eeeeee')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (2,0), (-1,-1), 'CENTER'),
        ]
        
        for i, row in enumerate(health_data[1:], 1):
            color = SUCCESS_COLOR
            if row[1] == 'Yellow': color = ACCENT_COLOR
            elif row[1] == 'Red': color = DANGER_COLOR
            
            style_cmds.append(('TEXTCOLOR', (1,i), (1,i), color))
            style_cmds.append(('FONTNAME', (1,i), (1,i), 'Helvetica-Bold'))
            style_cmds.append(('BACKGROUND', (2,i), (2,i), color))
        
        t_health.setStyle(TableStyle(style_cmds))
        story.append(t_health)
        story.append(Spacer(1, 20))

        # --- FINANCIALS SECTION ---
        story.append(Paragraph("Financial Overview", self.styles['SectionHeader']))
        
        # Side by Side Charts
        fin_chart = Image(self._create_financial_chart(), width=3.5*inch, height=2.5*inch)
        cost_chart = Image(self._create_cost_breakdown_chart(), width=3.5*inch, height=2.5*inch)
        
        chart_table = Table([[fin_chart, cost_chart]], colWidths=[3.7*inch, 3.7*inch])
        story.append(chart_table)
        
        # Financial Details Table
        fin_data = [
            ['Category', 'Amount (ZAR)', 'Variance'],
            ['Total Budget', f"{self.metrics['total_budget']:,.2f}", '-'],
            ['Actual Cost', f"{self.metrics['total_spent']:,.2f}", '-'],
            ['Forecast', f"{self.metrics['forecast']:,.2f}", f"{self.metrics['variance_at_completion']:,.2f}"],
            ['Remaining', f"{self.metrics['remaining']:,.2f}", '-']
        ]
        
        t_fin = Table(fin_data, colWidths=[2.5*inch, 2.5*inch, 2*inch])
        t_fin.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(Spacer(1, 10))
        story.append(t_fin)
        
        story.append(PageBreak())

        # --- RISKS & ISSUES ---
        story.append(Paragraph("Risk Register (High Priority)", self.styles['SectionHeader']))
        
        if not risks_df.empty:
            risk_data = [['ID', 'Description', 'Impact', 'Status', 'Mitigation']]
            # Top 10 risks
            for idx, row in risks_df.head(10).iterrows():
                risk_data.append([
                    str(row['risk_id']),
                    Paragraph(row['description'], self.styles['Normal']),
                    row['impact'],
                    row['status'],
                    Paragraph(row['mitigation_action'] or '-', self.styles['Normal'])
                ])
                
            t_risks = Table(risk_data, colWidths=[0.5*inch, 2.5*inch, 0.8*inch, 1*inch, 2.5*inch])
            t_risks.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#333333')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                ('SIZE', (0,0), (-1,-1), 9),
            ]))
            story.append(t_risks)
        else:
            story.append(Paragraph("No risks identified.", self.styles['Normal']))

        story.append(Spacer(1, 20))

        # --- MILESTONES ---
        story.append(Paragraph("Key Milestones", self.styles['SectionHeader']))
        
        baseline = database.get_baseline_schedule(self.project_id)
        if not baseline.empty:
            # Filter for milestones (dummy logic: activity name contains Milestone or phase)
            # For now, just show top 10 activities
            ms_data = [['Activity', 'Planned Start', 'Planned Finish', 'Status']]
            for idx, row in baseline.head(10).iterrows():
                status = row['status']
                status_color = colors.black
                if status == 'Complete': status_color = SUCCESS_COLOR
                elif status == 'Active': status_color = PRIMARY_COLOR
                
                ms_data.append([
                    Paragraph(row['activity_name'], self.styles['Normal']),
                    row['planned_start'],
                    row['planned_finish'],
                    status
                ])
                
            t_ms = Table(ms_data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            t_ms.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), SECONDARY_COLOR),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            story.append(t_ms)

        doc.build(story)
        buffer.seek(0)
        return buffer
