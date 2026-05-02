"""
PDF Generator - Fixed Version
Generates clean PDF reports without encoding issues
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import os


class FixedPDFGenerator:
    """Generate clean PDF reports"""
    
    def __init__(self, language: str = 'English'):
        self.language = language
        self.is_arabic = language == 'Arabic'
        self.output_dir = '/tmp/physio_reports'
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_detailed_report(self, patient_data: dict, treatment_plan: dict) -> str:
        """Generate detailed treatment report"""
        
        try:
            filename = os.path.join(self.output_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=30,
                alignment=1  # Center
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2e5c8a'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Title
            title = "PhysioAssist Oracle - Treatment Report" if not self.is_arabic else "تقرير العلاج - فيزيو أسيست"
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Patient Information
            patient_info_title = "Patient Information" if not self.is_arabic else "معلومات المريض"
            story.append(Paragraph(patient_info_title, heading_style))
            
            patient_table_data = [
                ["Date", datetime.now().strftime('%Y-%m-%d')] if not self.is_arabic else ["التاريخ", datetime.now().strftime('%Y-%m-%d')],
                ["Condition", patient_data.get('condition', 'General Pain')] if not self.is_arabic else ["الحالة", patient_data.get('condition', 'ألم عام')],
                ["Severity", patient_data.get('severity', 'Moderate')] if not self.is_arabic else ["الشدة", patient_data.get('severity', 'متوسطة')]
            ]
            
            patient_table = Table(patient_table_data, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f7')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            story.append(patient_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Treatment Plan Sections
            plan_sections = [
                ('part1_prevention', 'Prevention Tips' if not self.is_arabic else 'نصائح منع التفاقم'),
                ('part2_home_remedies', 'Home Remedies' if not self.is_arabic else 'العلاجات المنزلية'),
                ('part3_exercises', 'Exercise Program' if not self.is_arabic else 'برنامج التمارين'),
                ('part4_warnings', 'Important Warnings' if not self.is_arabic else 'تحذيرات مهمة'),
                ('part5_products', 'Recommended Products' if not self.is_arabic else 'منتجات موصى بها'),
                ('part6_medications', 'Medications' if not self.is_arabic else 'الأدوية')
            ]
            
            for part_key, section_title in plan_sections:
                story.append(Paragraph(section_title, heading_style))
                content = treatment_plan.get(part_key, '')
                # Clean content
                content = content.replace('\n', '<br/>')
                story.append(Paragraph(content, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Disclaimer
            story.append(Spacer(1, 0.3*inch))
            disclaimer_title = "Important Disclaimer" if not self.is_arabic else "تنبيه مهم"
            story.append(Paragraph(disclaimer_title, heading_style))
            
            disclaimer_text = (
                "This report is for informational purposes only and should not be considered as medical advice. "
                "Always consult with a qualified healthcare professional before starting any treatment plan."
            ) if not self.is_arabic else (
                "هذا التقرير لأغراض إعلامية فقط ولا يجب اعتباره نصيحة طبية. "
                "استشر دائماً متخصصاً صحياً مؤهلاً قبل بدء أي خطة علاجية."
            )
            
            story.append(Paragraph(disclaimer_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            return filename
        
        except Exception as e:
            print(f"Error generating detailed report: {e}")
            return None
    
    def generate_quick_card(self, patient_data: dict, treatment_plan: dict) -> str:
        """Generate quick reference card"""
        
        try:
            filename = os.path.join(self.output_dir, f"card_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CardTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=12,
                alignment=1
            )
            
            # Title
            title = "Quick Reference Card" if not self.is_arabic else "بطاقة مرجعية سريعة"
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Quick Tips
            tips_title = "Quick Tips" if not self.is_arabic else "نصائح سريعة"
            story.append(Paragraph(tips_title, styles['Heading2']))
            
            quick_tips = [
                "✓ Rest regularly" if not self.is_arabic else "✓ خذ فترات راحة منتظمة",
                "✓ Use heat therapy" if not self.is_arabic else "✓ استخدم العلاج الحراري",
                "✓ Maintain good posture" if not self.is_arabic else "✓ حافظ على وضعية جيدة",
                "✓ Do gentle stretches" if not self.is_arabic else "✓ قم بتمارين تمدد خفيفة",
                "✓ Avoid heavy lifting" if not self.is_arabic else "✓ تجنب رفع الأشياء الثقيلة"
            ]
            
            for tip in quick_tips:
                story.append(Paragraph(tip, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.2*inch))
            
            # Emergency Contacts
            emergency_title = "When to Seek Help" if not self.is_arabic else "متى تطلب المساعدة"
            story.append(Paragraph(emergency_title, styles['Heading2']))
            
            emergency_signs = [
                "• Severe pain that doesn't improve" if not self.is_arabic else "• ألم شديد لا يتحسن",
                "• Numbness or tingling" if not self.is_arabic else "• تنميل أو وخز",
                "• Severe swelling" if not self.is_arabic else "• تورم شديد",
                "• Loss of function" if not self.is_arabic else "• فقدان الوظيفة"
            ]
            
            for sign in emergency_signs:
                story.append(Paragraph(sign, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.3*inch))
            
            # Footer
            footer_text = (
                "For more information, consult your healthcare provider or visit PhysioAssist Oracle"
            ) if not self.is_arabic else (
                "للمزيد من المعلومات، استشر مقدم الرعاية الصحية أو قم بزيارة فيزيو أسيست"
            )
            
            story.append(Paragraph(footer_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            return filename
        
        except Exception as e:
            print(f"Error generating quick card: {e}")
            return None
