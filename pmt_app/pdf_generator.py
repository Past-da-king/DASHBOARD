import os
import io
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.units import inch
from datetime import datetime
import calculations

class PDFReportGenerator:
    def __init__(self, project_id):
        self.project_id = project_id
        self.metrics = calculations.get_project_metrics(project_id)
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom paragraph styles for the report"""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            textColor=colors.HexColor('#2c5aa0'),
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#2c5aa0'),
            borderPadding=(0, 0, 5, 0),
            borderWidth=0,
            borderColor=colors.HexColor('#2c5aa0')
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.gray
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['BodyText'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2c5aa0')
        ))

    def _get_status_color(self, status):
        """Return color based on status"""
        if status == 'Green':
            return colors.green
        elif status == 'Yellow':
            return colors.orange
        else:
            return colors.red

    def generate(self):
        """Generate the PDF report and return as bytes"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        story = []
        
        if not self.metrics:
            story.append(Paragraph("Error: Project data not found", self.styles['Normal']))
            doc.build(story)
            buffer.seek(0)
            return buffer

        # --- HEADER ---
        story.append(Paragraph("PROJECT STATUS REPORT", self.styles['ReportTitle']))
        story.append(Paragraph(f"{self.metrics['project_name']} ({self.metrics['project_number']})", self.styles['Heading2']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        story.append(Spacer(1, 20))

        # --- EXECUTIVE SUMMARY ---
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        status_text = "exceeding budget" if self.metrics['forecast'] > self.metrics['total_budget'] else "well within budget"
        summary_text = f"""
        The project <b>{self.metrics['project_name']}</b> is currently in <b>{self.metrics['actual_status']}</b> status. 
        Physical completion is estimated at <b>{self.metrics['pct_complete']:.1f}%</b>. 
        Financial performance shows we are <b>{status_text}</b> with a forecasted completion cost of <b>R {self.metrics['forecast']:,.2f}</b>.
        """
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 20))

        # --- KEY METRICS ---
        story.append(Paragraph("Key Metrics", self.styles['SectionHeader']))
        
        # Prepare data for metrics table
        metrics_data = [
            ['Budget Health', 'Schedule Health', 'Progress'],
            [
                self.metrics['budget_health'],
                self.metrics['schedule_health'],
                f"{self.metrics['pct_complete']:.1f}%"
            ]
        ]
        
        t_metrics = Table(metrics_data, colWidths=[2*inch, 2*inch, 2*inch])
        t_metrics.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('TEXTCOLOR', (0,1), (0,1), self._get_status_color(self.metrics['budget_health'])),
            ('TEXTCOLOR', (1,1), (1,1), self._get_status_color(self.metrics['schedule_health'])),
            ('FONTSIZE', (0,1), (-1,1), 14),
        ]))
        story.append(t_metrics)
        story.append(Spacer(1, 20))

        # --- FINANCIALS ---
        story.append(Paragraph("Financial Overview", self.styles['SectionHeader']))
        
        fin_data = [
            ['Metric', 'Amount', 'Variance'],
            ['Total Budget', f"R {self.metrics['total_budget']:,.2f}", '-'],
            ['Actual Cost', f"R {self.metrics['total_spent']:,.2f}", '-'],
            ['Forecast', f"R {self.metrics['forecast']:,.2f}", f"R {self.metrics['variance_at_completion']:,.2f}"]
        ]
        
        t_fin = Table(fin_data, colWidths=[2.5*inch, 2*inch, 2*inch])
        t_fin.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#333333')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#eeeeee')),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ]))
        story.append(t_fin)
        story.append(Spacer(1, 20))

        # --- RISK REGISTER (Top 5) ---
        # Note: We need to import database to fetch risks
        import database
        risks = database.get_project_risks(self.project_id)
        
        if not risks.empty:
            story.append(Paragraph("Top Risks", self.styles['SectionHeader']))
            
            risk_data = [['Risk Description', 'Impact', 'Status']]
            for _, row in risks.head(5).iterrows():
                risk_data.append([
                    Paragraph(row['description'], self.styles['Normal']),
                    row['impact'],
                    row['status']
                ])
                
            t_risks = Table(risk_data, colWidths=[4*inch, 1*inch, 1.5*inch])
            t_risks.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#eeeeee')),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('padding', (0,0), (-1,-1), 5),
            ]))
            story.append(t_risks)

        # Footer
        story.append(Spacer(1, 40))
        story.append(Paragraph("Generated by Project Management Tool", self.styles['Italic']))

        doc.build(story)
        buffer.seek(0)
        return buffer
