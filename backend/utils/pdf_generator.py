"""
PDF Report Generator for Skin Lesion Analysis
Generates detailed medical reports with images, predictions, and recommendations
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

class SkinLesionReportGenerator:
    def __init__(self, output_dir='reports'):
        """Initialize PDF report generator"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_report(self, prediction_data, image_path):
        """
        Generate detailed PDF report for skin lesion analysis
        
        Args:
            prediction_data (dict): Prediction results from ML model
            image_path (str): Path to the analyzed image
            
        Returns:
            str: Path to generated PDF file
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"skin_lesion_report_{timestamp}.pdf"
            pdf_path = os.path.join(self.output_dir, pdf_filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            # Container for PDF elements
            elements = []
            
            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )
            
            subheading_style = ParagraphStyle(
                'CustomSubHeading',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.HexColor('#374151'),
                spaceAfter=6,
                fontName='Helvetica-Bold'
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#1f2937'),
                alignment=TA_JUSTIFY,
                spaceAfter=6
            )
            
            # Title
            elements.append(Paragraph("Skin Lesion Analysis Report", title_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Report Information
            elements.append(Paragraph("Report Information", heading_style))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
            elements.append(Spacer(1, 0.1*inch))
            
            report_info = [
                ['Report Date:', datetime.now().strftime("%B %d, %Y at %I:%M %p")],
                ['Analysis ID:', prediction_data.get('prediction_id', 'N/A')],
                ['Image File:', prediction_data.get('filename', 'N/A')],
                ['Processing Time:', f"{prediction_data.get('processing_time', 0):.2f} seconds"]
            ]
            
            report_table = Table(report_info, colWidths=[2*inch, 4.5*inch])
            report_table.setStyle(TableStyle([
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
                ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(report_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Analyzed Image
            elements.append(Paragraph("Analyzed Image", heading_style))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
            elements.append(Spacer(1, 0.1*inch))
            
            if os.path.exists(image_path):
                img = Image(image_path, width=4*inch, height=3*inch, kind='proportional')
                img.hAlign = 'CENTER'
                elements.append(img)
            else:
                elements.append(Paragraph("Image not available", normal_style))
            
            elements.append(Spacer(1, 0.3*inch))
            
            # Analysis Results
            result = prediction_data.get('result', {})
            elements.append(Paragraph("Analysis Results", heading_style))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
            elements.append(Spacer(1, 0.1*inch))
            
            # Primary Diagnosis
            risk_level = result.get('risk_level', 'Unknown')
            risk_color = colors.HexColor('#dc2626') if result.get('is_malignant') else colors.HexColor('#16a34a')
            
            diagnosis_data = [
                ['Detected Condition:', result.get('class_name', 'Unknown')],
                ['Confidence Level:', f"{result.get('confidence', 0)*100:.2f}%"],
                ['Risk Classification:', risk_level],
                ['Malignancy Status:', 'Malignant' if result.get('is_malignant') else 'Benign']
            ]
            
            diagnosis_table = Table(diagnosis_data, colWidths=[2*inch, 4.5*inch])
            diagnosis_table.setStyle(TableStyle([
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
                ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f2937')),
                ('TEXTCOLOR', (1, 0), (1, 1), colors.HexColor('#1f2937')),
                ('TEXTCOLOR', (1, 2), (1, 2), risk_color),
                ('TEXTCOLOR', (1, 3), (1, 3), risk_color),
                ('FONT', (1, 2), (1, 3), 'Helvetica-Bold', 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(diagnosis_table)
            elements.append(Spacer(1, 0.2*inch))
            
            # Description
            elements.append(Paragraph("Description:", subheading_style))
            elements.append(Paragraph(result.get('description', 'No description available.'), normal_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # All Predictions
            elements.append(Paragraph("Detailed Confidence Scores", heading_style))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
            elements.append(Spacer(1, 0.1*inch))
            
            all_predictions = result.get('all_predictions', [])
            if all_predictions:
                pred_data = [['Condition', 'Confidence', 'Description']]
                for pred in all_predictions:
                    pred_data.append([
                        pred.get('class_name', 'Unknown'),
                        f"{pred.get('confidence', 0)*100:.2f}%",
                        pred.get('description', '')[:50] + '...'
                    ])
                
                pred_table = Table(pred_data, colWidths=[2.2*inch, 1.3*inch, 3*inch])
                pred_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                    ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(pred_table)
            
            elements.append(Spacer(1, 0.3*inch))
            
            # Medical Recommendations
            elements.append(Paragraph("Medical Recommendations", heading_style))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
            elements.append(Spacer(1, 0.1*inch))
            
            recommendations = self._get_recommendations(result.get('is_malignant'), result.get('confidence', 0))
            for i, rec in enumerate(recommendations, 1):
                elements.append(Paragraph(f"<b>{i}. {rec['action']}</b>", subheading_style))
                elements.append(Paragraph(rec['description'], normal_style))
                elements.append(Spacer(1, 0.1*inch))
            
            elements.append(Spacer(1, 0.3*inch))
            
            # Important Notice
            elements.append(Paragraph("Important Medical Notice", heading_style))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
            elements.append(Spacer(1, 0.1*inch))
            
            notice_text = """
            <b>Disclaimer:</b> This analysis is generated by an artificial intelligence system and is intended 
            for informational purposes only. It should NOT be considered as a definitive medical diagnosis. 
            AI predictions can have limitations and may not account for all relevant clinical factors.
            <br/><br/>
            <b>Always consult with a qualified healthcare professional or dermatologist for:</b>
            <br/>• Proper medical diagnosis and interpretation of skin lesions
            <br/>• Treatment recommendations and medical advice
            <br/>• Any concerns about skin changes or abnormalities
            <br/><br/>
            Early detection and professional medical evaluation are crucial for skin health management.
            """
            
            notice_style = ParagraphStyle(
                'Notice',
                parent=normal_style,
                fontSize=9,
                textColor=colors.HexColor('#7f1d1d'),
                leading=12,
                spaceBefore=6,
                spaceAfter=6,
                leftIndent=10,
                rightIndent=10
            )
            
            elements.append(Paragraph(notice_text, notice_style))
            
            # Footer
            elements.append(Spacer(1, 0.3*inch))
            footer_style = ParagraphStyle(
                'Footer',
                parent=normal_style,
                fontSize=8,
                textColor=colors.HexColor('#6b7280'),
                alignment=TA_CENTER
            )
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#d1d5db')))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(
                f"Report generated on {datetime.now().strftime('%B %d, %Y')} by Skin Lesion Detection AI System",
                footer_style
            ))
            elements.append(Paragraph("© 2025 AI Medical Diagnostics. For research and educational purposes.", footer_style))
            
            # Build PDF
            doc.build(elements)
            logger.info(f"PDF report generated: {pdf_path}")
            
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise
    
    def _get_recommendations(self, is_malignant, confidence):
        """Generate medical recommendations based on analysis"""
        recommendations = []
        
        if is_malignant or confidence > 0.7:
            recommendations.append({
                'action': 'Consult a Dermatologist Immediately',
                'description': 'Schedule an appointment with a board-certified dermatologist within 1-2 weeks for professional evaluation. Early detection is crucial for effective treatment.'
            })
            
            if is_malignant:
                recommendations.append({
                    'action': 'Biopsy May Be Recommended',
                    'description': 'Your dermatologist may recommend a skin biopsy to obtain a tissue sample for definitive diagnosis and to determine the best course of treatment.'
                })
        else:
            recommendations.append({
                'action': 'Monitor the Lesion Regularly',
                'description': 'Take clear photographs of the lesion monthly to track any changes in size, shape, color, or texture. Keep a dated record of these images.'
            })
        
        recommendations.extend([
            {
                'action': 'Follow the ABCDE Rule',
                'description': 'Watch for: Asymmetry (one half differs from the other), Border irregularity, Color variation, Diameter greater than 6mm, and Evolution (changes over time).'
            },
            {
                'action': 'Practice Sun Protection',
                'description': 'Use broad-spectrum sunscreen (SPF 30+), wear protective clothing, and avoid peak sun hours (10am-4pm) to prevent further skin damage.'
            },
            {
                'action': 'Schedule Regular Skin Checks',
                'description': 'Perform monthly self-examinations and schedule annual full-body skin exams with a dermatologist, especially if you have multiple moles or skin lesions.'
            }
        ])
        
        return recommendations

def create_report(prediction_data, image_path, output_dir='reports'):
    """Convenience function to generate a PDF report"""
    generator = SkinLesionReportGenerator(output_dir)
    return generator.generate_report(prediction_data, image_path)
