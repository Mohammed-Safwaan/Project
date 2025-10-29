"""
Advanced PDF Report Generator for Skin Lesion Analysis
Creates detailed medical reports with analysis results, recommendations, and images
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import black, white, red, orange, green, blue, grey
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from PIL import Image
import json
import os
from datetime import datetime
import tempfile


class SkinLesionReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.lightgrey,
            borderPadding=5,
            backColor=colors.lightgrey
        ))
        
        # Risk style for different risk levels
        self.styles.add(ParagraphStyle(
            name='HighRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.red,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='MediumRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.orange,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='LowRisk',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.green,
            fontName='Helvetica-Bold'
        ))

    def generate_report(self, prediction_data, output_path=None):
        """Generate comprehensive PDF report"""
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/skin_analysis_report_{timestamp}.pdf"
        
        # Ensure reports directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else "reports", exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            topMargin=1*inch,
            bottomMargin=1*inch,
            leftMargin=1*inch,
            rightMargin=1*inch
        )
        
        # Build report content
        story = []
        
        # Header
        story.extend(self._create_header(prediction_data))
        
        # Image Section (if image path is provided)
        if 'image_path' in prediction_data and prediction_data['image_path']:
            story.extend(self._create_image_section(prediction_data))
        
        # Executive Summary
        story.extend(self._create_executive_summary(prediction_data))
        
        # Analysis Results
        story.extend(self._create_analysis_results(prediction_data))
        
        # Medical Recommendations
        story.extend(self._create_medical_recommendations(prediction_data))
        
        # Technical Details
        story.extend(self._create_technical_details(prediction_data))
        
        # Risk Assessment
        story.extend(self._create_risk_assessment(prediction_data))
        
        # Disclaimer
        story.extend(self._create_disclaimer())
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _create_header(self, data):
        """Create report header with title and basic info"""
        story = []
        
        # Title
        title = Paragraph("Skin Lesion Analysis Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Report info table
        report_info = [
            ['Report Generated:', datetime.now().strftime("%B %d, %Y at %I:%M %p")],
            ['Analysis Date:', datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')).strftime("%B %d, %Y at %I:%M %p")],
            ['Scan ID:', data['prediction_id']],
            ['AI Model:', 'DenseNet121 v1.0 (PyTorch)'],
            ['Image File:', data['filename']]
        ]
        
        info_table = Table(report_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        return story
    
    def _create_image_section(self, data):
        """Create image section with the uploaded lesion image"""
        story = []
        
        # Section header
        header = Paragraph("Analyzed Image", self.styles['CustomHeading'])
        story.append(header)
        story.append(Spacer(1, 10))
        
        try:
            image_path = data['image_path']
            
            # Check if image file exists
            if os.path.exists(image_path):
                # Open image to get dimensions
                with Image.open(image_path) as img:
                    img_width, img_height = img.size
                
                # Calculate display size (max width 4 inches, maintain aspect ratio)
                max_width = 4 * inch
                max_height = 3 * inch
                
                if img_width > img_height:
                    # Landscape orientation
                    display_width = min(max_width, 4 * inch)
                    display_height = (display_width * img_height) / img_width
                else:
                    # Portrait orientation  
                    display_height = min(max_height, 3 * inch)
                    display_width = (display_height * img_width) / img_height
                
                # Create ReportLab Image object
                rl_image = RLImage(image_path, width=display_width, height=display_height)
                story.append(rl_image)
                story.append(Spacer(1, 10))
                
                # Image caption
                caption_text = f"<b>Figure 1:</b> Uploaded skin lesion image ({data['filename']})<br/>"
                caption_text += f"Original size: {img_width} × {img_height} pixels"
                caption = Paragraph(caption_text, self.styles['Normal'])
                story.append(caption)
                story.append(Spacer(1, 20))
                
            else:
                # Image not found message
                error_text = f"<i>Image file not accessible: {data['filename']}</i>"
                error_para = Paragraph(error_text, self.styles['Normal'])
                story.append(error_para)
                story.append(Spacer(1, 20))
                
        except Exception as e:
            # Error handling
            error_text = f"<i>Unable to display image: {str(e)}</i>"
            error_para = Paragraph(error_text, self.styles['Normal'])
            story.append(error_para)
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_executive_summary(self, data):
        """Create executive summary section"""
        story = []
        
        result = data['result']
        
        # Section header
        header = Paragraph("Executive Summary", self.styles['CustomHeading'])
        story.append(header)
        
        # Risk level styling
        risk_level = result['risk_level'].upper()
        if risk_level == 'HIGH':
            risk_style = self.styles['HighRisk']
        elif risk_level == 'MEDIUM':
            risk_style = self.styles['MediumRisk']
        else:
            risk_style = self.styles['LowRisk']
        
        # Primary diagnosis
        diagnosis_text = f"""
        <b>Primary Diagnosis:</b> {result['class_name']}<br/>
        <b>Confidence Level:</b> {result['confidence']*100:.1f}%<br/>
        <b>Risk Classification:</b> {risk_level} RISK<br/>
        <b>Malignancy Status:</b> {'Potentially Malignant' if result['is_malignant'] else 'Benign'}
        """
        
        diagnosis = Paragraph(diagnosis_text, self.styles['Normal'])
        story.append(diagnosis)
        story.append(Spacer(1, 15))
        
        # Description
        desc_text = f"<b>Clinical Description:</b><br/>{result['description']}"
        description = Paragraph(desc_text, self.styles['Normal'])
        story.append(description)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_analysis_results(self, data):
        """Create detailed analysis results section"""
        story = []
        
        # Section header
        header = Paragraph("Detailed Analysis Results", self.styles['CustomHeading'])
        story.append(header)
        
        # All predictions table
        predictions_data = [['Diagnosis', 'Confidence', 'Risk Level', 'Description']]
        
        for pred in data['result']['all_predictions'][:5]:  # Top 5 predictions
            confidence = f"{pred['confidence']*100:.1f}%"
            
            # Determine risk level for each prediction
            class_name = pred['class_name']
            if 'melanoma' in class_name.lower() or 'carcinoma' in class_name.lower():
                risk = 'High'
            elif 'keratoses' in class_name.lower():
                risk = 'Medium' 
            else:
                risk = 'Low'
            
            predictions_data.append([
                pred['class_name'],
                confidence,
                risk,
                pred.get('description', 'N/A')[:50] + '...' if len(pred.get('description', '')) > 50 else pred.get('description', 'N/A')
            ])
        
        predictions_table = Table(predictions_data, colWidths=[2*inch, 1*inch, 1*inch, 2.5*inch])
        predictions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        
        story.append(predictions_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_medical_recommendations(self, data):
        """Create medical recommendations based on analysis"""
        story = []
        
        result = data['result']
        
        # Section header
        header = Paragraph("Medical Recommendations & Next Steps", self.styles['CustomHeading'])
        story.append(header)
        
        # Generate recommendations based on results
        recommendations = self._generate_detailed_recommendations(result)
        
        for i, rec in enumerate(recommendations, 1):
            rec_text = f"""
            <b>{i}. {rec['title']}</b><br/>
            <b>Priority:</b> {rec['priority'].upper()}<br/>
            <b>Timeframe:</b> {rec['timeframe']}<br/>
            <b>Details:</b> {rec['description']}<br/>
            """
            
            rec_para = Paragraph(rec_text, self.styles['Normal'])
            story.append(rec_para)
            story.append(Spacer(1, 12))
        
        return story
    
    def _generate_detailed_recommendations(self, result):
        """Generate detailed medical recommendations based on analysis results"""
        recommendations = []
        
        is_malignant = result['is_malignant']
        confidence = result['confidence']
        risk_level = result['risk_level'].lower()
        class_name = result['class_name'].lower()
        
        # High-priority recommendations for malignant or high-risk lesions
        if is_malignant or confidence > 0.7:
            if 'melanoma' in class_name:
                recommendations.append({
                    'title': 'Urgent Dermatology Consultation',
                    'priority': 'CRITICAL',
                    'timeframe': 'Within 1-2 weeks',
                    'description': 'Melanoma requires immediate evaluation. Contact a dermatologist or dermatologic surgeon for urgent assessment. Early detection and treatment are crucial for optimal outcomes.'
                })
                
                recommendations.append({
                    'title': 'Biopsy Evaluation',
                    'priority': 'CRITICAL', 
                    'timeframe': 'As directed by dermatologist',
                    'description': 'A biopsy will likely be recommended to confirm diagnosis and determine the exact type and stage of melanoma. This is essential for developing an appropriate treatment plan.'
                })
            
            elif 'carcinoma' in class_name:
                recommendations.append({
                    'title': 'Dermatology Consultation',
                    'priority': 'HIGH',
                    'timeframe': 'Within 2-4 weeks', 
                    'description': 'Basal cell carcinoma should be evaluated by a dermatologist. While typically slow-growing, prompt treatment prevents further growth and potential complications.'
                })
            
            elif 'keratoses' in class_name:
                recommendations.append({
                    'title': 'Dermatology Assessment',
                    'priority': 'MEDIUM',
                    'timeframe': 'Within 4-8 weeks',
                    'description': 'Actinic keratoses are pre-cancerous and should be monitored by a dermatologist. Treatment options may be discussed to prevent progression to skin cancer.'
                })
        
        # General monitoring recommendations
        recommendations.append({
            'title': 'Regular Self-Examination',
            'priority': 'ONGOING',
            'timeframe': 'Monthly',
            'description': 'Perform monthly skin self-examinations using the ABCDE method: Asymmetry, Border irregularity, Color variation, Diameter >6mm, Evolution (changes over time). Take photos for comparison.'
        })
        
        recommendations.append({
            'title': 'Sun Protection',
            'priority': 'ONGOING', 
            'timeframe': 'Daily',
            'description': 'Use broad-spectrum SPF 30+ sunscreen daily, seek shade during peak hours (10am-4pm), wear protective clothing, and avoid tanning beds to prevent future skin damage.'
        })
        
        recommendations.append({
            'title': 'Annual Skin Screening',
            'priority': 'ROUTINE',
            'timeframe': 'Annually',
            'description': 'Schedule annual full-body skin examinations with a dermatologist, especially if you have risk factors such as fair skin, history of sun exposure, or family history of skin cancer.'
        })
        
        return recommendations
    
    def _create_technical_details(self, data):
        """Create technical analysis details section"""
        story = []
        
        # Section header
        header = Paragraph("Technical Analysis Details", self.styles['CustomHeading'])
        story.append(header)
        
        # Technical details table
        image_info = data['image_info']
        technical_data = [
            ['Parameter', 'Value', 'Notes'],
            ['Image Dimensions', f"{image_info['width']} × {image_info['height']} pixels", 'Original resolution'],
            ['File Size', f"{image_info['size_bytes'] / 1024:.1f} KB", f"Format: {image_info['format']}"],
            ['Processing Time', f"{data['processing_time']:.3f} seconds", 'AI inference time'],
            ['AI Model', 'DenseNet121', 'Pre-trained on medical datasets'],
            ['Parameters', '6,961,031', 'Neural network complexity'],
            ['Confidence Score', f"{data['result']['confidence']*100:.2f}%", 'AI prediction certainty'],
            ['Analysis Date', datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S"), 'UTC timestamp']
        ]
        
        tech_table = Table(technical_data, colWidths=[2*inch, 2*inch, 2.5*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(tech_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_risk_assessment(self, data):
        """Create comprehensive risk assessment section"""
        story = []
        
        result = data['result']
        
        # Section header
        header = Paragraph("Risk Assessment & Monitoring Guidelines", self.styles['CustomHeading'])
        story.append(header)
        
        # Risk factors analysis
        risk_text = self._generate_risk_assessment_text(result)
        risk_para = Paragraph(risk_text, self.styles['Normal'])
        story.append(risk_para)
        story.append(Spacer(1, 15))
        
        # Monitoring schedule
        monitoring_text = self._generate_monitoring_schedule(result)
        monitoring_para = Paragraph(monitoring_text, self.styles['Normal'])
        story.append(monitoring_para)
        story.append(Spacer(1, 20))
        
        return story
    
    def _generate_risk_assessment_text(self, result):
        """Generate risk assessment text based on analysis"""
        risk_level = result['risk_level'].lower()
        class_name = result['class_name'].lower()
        confidence = result['confidence']
        
        if 'melanoma' in class_name and confidence > 0.5:
            return """
            <b>HIGH RISK ASSESSMENT:</b><br/>
            This lesion shows characteristics consistent with melanoma, the most serious form of skin cancer. 
            Key concerns include potential for rapid growth and metastasis if untreated. 
            <b>IMMEDIATE MEDICAL ATTENTION REQUIRED.</b><br/><br/>
            
            <b>Critical Warning Signs:</b><br/>
            • Asymmetrical shape<br/>
            • Irregular or poorly defined borders<br/>
            • Multiple colors or color changes<br/>
            • Diameter greater than 6mm<br/>
            • Evolving appearance over time<br/><br/>
            
            <b>Recommended Actions:</b><br/>
            • Contact dermatologist within 1-2 weeks<br/>
            • Avoid further sun exposure to the area<br/>
            • Do not attempt to treat or remove lesion yourself<br/>
            • Monitor for any changes and report immediately
            """
            
        elif result['is_malignant']:
            return """
            <b>ELEVATED RISK ASSESSMENT:</b><br/>
            This lesion shows characteristics of a potentially malignant condition requiring professional evaluation.
            While typically slower-growing than melanoma, early treatment improves outcomes.<br/><br/>
            
            <b>Monitoring Points:</b><br/>
            • Changes in size, shape, or color<br/>
            • New symptoms (itching, bleeding, pain)<br/>
            • Lesion growth or elevation<br/>
            • Surrounding tissue changes<br/><br/>
            
            <b>Recommended Timeframe:</b><br/>
            • Professional evaluation within 2-4 weeks<br/>
            • Monthly self-monitoring<br/>
            • Photographic documentation for comparison
            """
        
        else:
            return """
            <b>LOW-MODERATE RISK ASSESSMENT:</b><br/>
            This lesion appears to be benign based on AI analysis. However, regular monitoring 
            remains important as any skin lesion can potentially change over time.<br/><br/>
            
            <b>Routine Monitoring:</b><br/>
            • Monthly self-examination<br/>
            • Annual dermatology screening<br/>
            • Photo documentation for change tracking<br/>
            • Professional evaluation if changes occur<br/><br/>
            
            <b>When to Seek Immediate Care:</b><br/>
            • Rapid size increase<br/>
            • Color or texture changes<br/>
            • Bleeding or ulceration<br/>
            • New associated symptoms
            """
    
    def _generate_monitoring_schedule(self, result):
        """Generate personalized monitoring schedule"""
        if result['is_malignant']:
            return """
            <b>INTENSIVE MONITORING SCHEDULE:</b><br/>
            • <b>Week 1-2:</b> Seek professional dermatology consultation<br/>
            • <b>Monthly:</b> Self-examination with photo documentation<br/>
            • <b>Every 3 months:</b> Dermatology follow-up (first year)<br/>
            • <b>Every 6 months:</b> Full-body skin examination<br/>
            • <b>Ongoing:</b> Daily sun protection measures
            """
        else:
            return """
            <b>ROUTINE MONITORING SCHEDULE:</b><br/>
            • <b>Monthly:</b> Self-examination of lesion and surrounding area<br/>
            • <b>Every 6 months:</b> Progress photos for comparison<br/>
            • <b>Annually:</b> Comprehensive dermatology screening<br/>
            • <b>As needed:</b> Professional evaluation for any changes<br/>
            • <b>Ongoing:</b> Sun protection and skin care routine
            """
    
    def _create_disclaimer(self):
        """Create medical disclaimer section"""
        story = []
        
        # Section header
        header = Paragraph("Important Medical Disclaimer", self.styles['CustomHeading'])
        story.append(header)
        
        disclaimer_text = """
        <b>IMPORTANT:</b> This AI-powered analysis is provided for informational and educational purposes only. 
        It is NOT a substitute for professional medical advice, diagnosis, or treatment.<br/><br/>
        
        <b>Key Limitations:</b><br/>
        • AI analysis may not detect all skin conditions or cancers<br/>
        • False positives and false negatives are possible<br/>
        • Clinical correlation and professional judgment are essential<br/>
        • This tool is not FDA-approved for diagnostic purposes<br/><br/>
        
        <b>Always consult with a qualified dermatologist or healthcare provider for:</b><br/>
        • Definitive diagnosis and treatment planning<br/>
        • Interpretation of results in clinical context<br/>
        • Biopsy recommendations and procedures<br/>
        • Follow-up care and monitoring protocols<br/><br/>
        
        <b>Emergency Warning:</b> If you notice rapid changes in a skin lesion, bleeding, 
        ulceration, or new concerning symptoms, seek immediate medical attention regardless 
        of this AI analysis result.<br/><br/>
        
        <i>Generated by Skin Lesion Detection AI System v1.0 | Report Date: {}</i>
        """.format(datetime.now().strftime("%B %d, %Y"))
        
        disclaimer = Paragraph(disclaimer_text, self.styles['Normal'])
        story.append(disclaimer)
        
        return story


def generate_skin_report(prediction_data, output_path=None):
    """Convenience function to generate skin lesion analysis report"""
    generator = SkinLesionReportGenerator()
    return generator.generate_report(prediction_data, output_path)


if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        'prediction_id': 'test-123-456',
        'filename': 'test_lesion.jpg',
        'timestamp': '2025-10-29T12:00:00Z',
        'processing_time': 1.23,
        'image_info': {
            'width': 600,
            'height': 450,
            'format': 'JPEG',
            'size_bytes': 265932
        },
        'result': {
            'class_name': 'Melanoma',
            'confidence': 0.85,
            'description': 'Serious form of skin cancer developing from pigment cells',
            'is_malignant': True,
            'risk_level': 'High',
            'all_predictions': [
                {'class_name': 'Melanoma', 'confidence': 0.85, 'description': 'Serious skin cancer'},
                {'class_name': 'Melanocytic nevi', 'confidence': 0.10, 'description': 'Common moles'},
                {'class_name': 'Basal cell carcinoma', 'confidence': 0.05, 'description': 'Common skin cancer'}
            ]
        }
    }
    
    output_file = generate_skin_report(sample_data, "test_report.pdf")
    print(f"Test report generated: {output_file}")