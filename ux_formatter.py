"""
PhysioAssist Oracle v7.0 - Advanced UX & Formatting Module
Professional bilingual formatting (Arabic RTL / English LTR)
with beautiful typography, emojis, and visual hierarchy.
"""

from typing import List, Dict, Optional

class UXFormatter:
    """Advanced UX formatting for bilingual support"""
    
    # Color-coded emojis for consistent branding
    EMOJIS = {
        "diagnosis": "🏥",
        "warning": "⚠️",
        "success": "✅",
        "info": "ℹ️",
        "exercise": "🏋️",
        "video": "🎥",
        "product": "🛍️",
        "medicine": "💊",
        "timer": "⏱️",
        "heart": "❤️",
        "brain": "🧠",
        "muscle": "💪",
        "check": "✔️",
        "cross": "❌",
        "arrow": "➡️",
        "star": "⭐",
        "fire": "🔥",
        "lock": "🔐",
        "unlock": "🔓",
        "payment": "💳",
        "money": "💰",
        "chart": "📊",
        "document": "📄",
        "phone": "📞",
        "email": "📧",
        "clock": "🕐",
        "calendar": "📅",
        "target": "🎯",
        "light": "💡",
        "shield": "🛡️",
        "danger": "🚨",
        "hand": "👋",
        "thumbs_up": "👍",
        "thinking": "🤔",
    }
    
    def __init__(self, language: str = "en"):
        self.language = language
        self.is_rtl = language == "ar"
    
    def format_header(self, title: str, emoji: str = "🏥", level: int = 1) -> str:
        """Format a header with emoji and proper styling"""
        
        if self.is_rtl:
            # Arabic: emoji on the right
            if level == 1:
                return f"{emoji} <b>{title}</b>\n{'─' * 40}"
            elif level == 2:
                return f"{emoji} <b>{title}</b>"
            else:
                return f"{emoji} {title}"
        else:
            # English: emoji on the left
            if level == 1:
                return f"{emoji} <b>{title}</b>\n{'─' * 40}"
            elif level == 2:
                return f"{emoji} <b>{title}</b>"
            else:
                return f"{emoji} {title}"
    
    def format_section(self, title: str, content: str, emoji: str = "ℹ️") -> str:
        """Format a section with title and content"""
        
        separator = "\n" + "─" * 40 + "\n"
        
        if self.is_rtl:
            return f"{emoji} <b>{title}</b>\n{content}{separator}"
        else:
            return f"{emoji} <b>{title}</b>\n{content}{separator}"
    
    def format_list(self, items: List[str], numbered: bool = False) -> str:
        """Format a list with proper styling"""
        
        if numbered:
            # Numbered list
            if self.is_rtl:
                # Arabic: right-aligned numbers
                return "\n".join([f"{i+1}️⃣ {item}" for i, item in enumerate(items)])
            else:
                # English: left-aligned numbers
                return "\n".join([f"{i+1}️⃣ {item}" for i, item in enumerate(items)])
        else:
            # Bullet list
            if self.is_rtl:
                # Arabic: use ✓ or • bullets
                return "\n".join([f"✓ {item}" for item in items])
            else:
                # English: use • bullets
                return "\n".join([f"• {item}" for item in items])
    
    def format_key_value(self, key: str, value: str, emoji: str = "") -> str:
        """Format a key-value pair"""
        
        if emoji:
            if self.is_rtl:
                return f"{emoji} <b>{key}:</b> {value}"
            else:
                return f"{emoji} <b>{key}:</b> {value}"
        else:
            if self.is_rtl:
                return f"<b>{key}:</b> {value}"
            else:
                return f"<b>{key}:</b> {value}"
    
    def format_assessment_result(self, diagnosis: str, confidence: int, 
                                 summary: str, red_flags: List[str] = None) -> str:
        """Format a clinical assessment result"""
        
        lines = []
        
        # Diagnosis header
        lines.append(self.format_header("Clinical Assessment", "🏥", 1))
        lines.append("")
        
        # Diagnosis
        lines.append(self.format_key_value("Diagnosis" if not self.is_rtl else "التشخيص", 
                                          diagnosis, self.EMOJIS["diagnosis"]))
        lines.append("")
        
        # Confidence level
        confidence_bar = "█" * (confidence // 10) + "░" * (10 - confidence // 10)
        lines.append(self.format_key_value("Confidence" if not self.is_rtl else "الثقة", 
                                          f"{confidence_bar} {confidence}%", self.EMOJIS["chart"]))
        lines.append("")
        
        # Summary
        lines.append(self.format_section("Summary" if not self.is_rtl else "الملخص", 
                                        summary, self.EMOJIS["info"]))
        
        # Red flags if any
        if red_flags and len(red_flags) > 0:
            lines.append(self.format_header("Red Flags" if not self.is_rtl else "علامات الخطر", 
                                           self.EMOJIS["danger"], 2))
            lines.append(self.format_list(red_flags))
            lines.append("")
        
        return "\n".join(lines)
    
    def format_treatment_plan(self, plan_data: Dict) -> str:
        """Format a comprehensive 6-part treatment plan"""
        
        lines = []
        
        # Main header
        lines.append(self.format_header(
            "Your Personalized Treatment Plan" if not self.is_rtl else "خطة العلاج الشخصية",
            "🎯", 1))
        lines.append("")
        
        # Duration
        duration_text = "Duration: 8 weeks" if not self.is_rtl else "المدة: 8 أسابيع"
        lines.append(f"{self.EMOJIS['calendar']} <b>{duration_text}</b>")
        lines.append("")
        
        # Part 1: Prevention
        lines.append(self.format_header(
            "1️⃣ Prevention Instructions" if not self.is_rtl else "1️⃣ تعليمات منع التفاقم",
            self.EMOJIS["shield"], 2))
        lines.append(plan_data.get("prevention", ""))
        lines.append("")
        
        # Part 2: Home Modalities
        lines.append(self.format_header(
            "2️⃣ Home Modalities" if not self.is_rtl else "2️⃣ الوسائل العلاجية المنزلية",
            self.EMOJIS["heart"], 2))
        lines.append(plan_data.get("modalities", ""))
        lines.append("")
        
        # Part 3: Exercise Program
        lines.append(self.format_header(
            "3️⃣ Progressive Exercise Program" if not self.is_rtl else "3️⃣ برنامج التمارين المتدرج",
            self.EMOJIS["exercise"], 2))
        
        # Weeks breakdown
        weeks_data = plan_data.get("exercises", {})
        for week, content in weeks_data.items():
            lines.append(f"\n<b>{week}</b>")
            lines.append(content)
        
        lines.append("")
        
        # Part 4: Contraindications
        lines.append(self.format_header(
            "4️⃣ Contraindications & Warnings" if not self.is_rtl else "4️⃣ الموانع والمحاذير",
            self.EMOJIS["warning"], 2))
        lines.append(plan_data.get("contraindications", ""))
        lines.append("")
        
        # Part 5: Recommended Products
        lines.append(self.format_header(
            "5️⃣ Recommended Products" if not self.is_rtl else "5️⃣ المنتجات الموصى بها",
            self.EMOJIS["product"], 2))
        lines.append(plan_data.get("products", ""))
        lines.append("")
        
        # Part 6: Safe Medications
        lines.append(self.format_header(
            "6️⃣ Safe Medication Suggestions" if not self.is_rtl else "6️⃣ الأدوية الآمنة المقترحة",
            self.EMOJIS["medicine"], 2))
        lines.append(plan_data.get("medications", ""))
        lines.append("")
        
        return "\n".join(lines)
    
    def format_exercise_instruction(self, exercise_name: str, instructions: Dict) -> str:
        """Format a single exercise instruction"""
        
        lines = []
        
        # Exercise name
        lines.append(self.format_header(exercise_name, self.EMOJIS["exercise"], 2))
        lines.append("")
        
        # Starting position
        if "starting_position" in instructions:
            lines.append(self.format_key_value(
                "Starting Position" if not self.is_rtl else "الوضعية الابتدائية",
                instructions["starting_position"], self.EMOJIS["hand"]))
            lines.append("")
        
        # Steps
        if "steps" in instructions:
            lines.append(self.format_header(
                "Steps" if not self.is_rtl else "الخطوات",
                self.EMOJIS["arrow"], 3))
            lines.append(self.format_list(instructions["steps"], numbered=True))
            lines.append("")
        
        # Repetitions
        if "repetitions" in instructions:
            lines.append(self.format_key_value(
                "Repetitions" if not self.is_rtl else "التكرارات",
                instructions["repetitions"], self.EMOJIS["timer"]))
            lines.append("")
        
        # Breathing
        if "breathing" in instructions:
            lines.append(self.format_key_value(
                "Breathing" if not self.is_rtl else "التنفس",
                instructions["breathing"], self.EMOJIS["light"]))
            lines.append("")
        
        # Warnings
        if "warnings" in instructions:
            lines.append(self.format_header(
                "Warnings" if not self.is_rtl else "التحذيرات",
                self.EMOJIS["warning"], 3))
            lines.append(self.format_list(instructions["warnings"]))
            lines.append("")
        
        return "\n".join(lines)
    
    def format_paywall_message(self, plan_summary: str) -> str:
        """Format the paywall message (Freemium strategy)"""
        
        if self.is_rtl:
            return f"""🔐 <b>الخطة الكاملة محمية</b>

{plan_summary}

💳 <b>للوصول للخطة الكاملة:</b>
اشترك الآن بـ <b>$4.99/شهر</b> (الشهر الأول فقط)
ثم <b>$9.99/شهر</b> (بدون التزام - يمكنك الإلغاء في أي وقت)

✅ الخطة تتضمن:
✓ برنامج تمارين متدرج (8 أسابيع)
✓ وسائل علاجية منزلية
✓ منتجات أمازون موصى بها
✓ أدوية آمنة مقترحة
✓ فيديوهات YouTube
✓ متابعة يومية
✓ دعم 24/7"""
        else:
            return f"""🔐 <b>Full Plan Unlocked</b>

{plan_summary}

💳 <b>To access the full plan:</b>
Subscribe now for <b>$4.99/month</b> (first month only)
Then <b>$9.99/month</b> (no commitment - cancel anytime)

✅ Plan includes:
✓ Progressive exercise program (8 weeks)
✓ Home modalities
✓ Recommended Amazon products
✓ Safe medications
✓ YouTube videos
✓ Daily follow-up
✓ 24/7 support"""
    
    def format_quick_win_exercise(self, exercise_data: Dict) -> str:
        """Format the quick win exercise (free hook)"""
        
        lines = []
        
        # Header
        if self.is_rtl:
            lines.append(self.format_header("تمرين سريع لتخفيف الألم الفوري", "🔥", 2))
        else:
            lines.append(self.format_header("Quick Pain Relief Exercise", "🔥", 2))
        
        lines.append("")
        
        # Exercise details
        lines.append(self.format_exercise_instruction(
            exercise_data.get("name", ""),
            exercise_data
        ))
        
        # Duration
        if self.is_rtl:
            lines.append(f"{self.EMOJIS['timer']} <b>المدة:</b> 5-10 دقائق")
        else:
            lines.append(f"{self.EMOJIS['timer']} <b>Duration:</b> 5-10 minutes")
        
        lines.append("")
        
        # Encouragement
        if self.is_rtl:
            lines.append(f"{self.EMOJIS['thumbs_up']} <i>جرب هذا التمرين الآن وشعر بالفرق!</i>")
        else:
            lines.append(f"{self.EMOJIS['thumbs_up']} <i>Try this exercise now and feel the difference!</i>")
        
        return "\n".join(lines)
    
    def format_disclaimer(self) -> str:
        """Format medical disclaimer"""
        
        if self.is_rtl:
            return f"""{self.EMOJIS['warning']} <b>إخلاء مسؤولية طبي مهم</b>

هذا التطبيق لا يستبدل الاستشارة الطبية المتخصصة. 
في حالة الألم الشديد أو الأعراض المقلقة، يرجى التوجه للطبيب فوراً.

{self.EMOJIS['danger']} في حالة الطوارئ: اتصل برقم الطوارئ (911 أو 997)"""
        else:
            return f"""{self.EMOJIS['warning']} <b>Important Medical Disclaimer</b>

This application does not replace professional medical consultation.
In case of severe pain or concerning symptoms, please see a doctor immediately.

{self.EMOJIS['danger']} In case of emergency: Call 911 or your local emergency number"""
    
    def format_success_message(self, message: str) -> str:
        """Format a success message"""
        
        return f"{self.EMOJIS['success']} <b>{message}</b>"
    
    def format_error_message(self, message: str) -> str:
        """Format an error message"""
        
        return f"{self.EMOJIS['cross']} <b>Error:</b> {message}"
    
    def format_info_message(self, message: str) -> str:
        """Format an info message"""
        
        return f"{self.EMOJIS['info']} {message}"
    
    def add_separator(self) -> str:
        """Add a visual separator"""
        return "\n" + "─" * 40 + "\n"
    
    def format_chat_message(self, sender: str, message: str, is_user: bool = False) -> str:
        """Format a chat message"""
        
        if is_user:
            if self.is_rtl:
                return f"👤 <b>أنت:</b>\n{message}"
            else:
                return f"👤 <b>You:</b>\n{message}"
        else:
            if self.is_rtl:
                return f"🤖 <b>PhysioAssist:</b>\n{message}"
            else:
                return f"🤖 <b>PhysioAssist:</b>\n{message}"
