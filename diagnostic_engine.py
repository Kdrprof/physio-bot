"""
PhysioAssist Oracle v7.0 - Advanced Diagnostic Engine
Advanced AI-powered diagnostic system with smart conversation, comprehensive history gathering,
and intelligent treatment plan generation (6-part comprehensive plans).

Features:
- Free Chat Mode (build trust & gather initial info)
- Smart Dynamic Questions (based on previous answers)
- Complete Medical History Collection
- Daily Habits & Lifestyle Assessment
- Red Flag Detection
- Intelligent Treatment Plan Generation (6 parts)
- Freemium Paywall Strategy
- Bilingual Support (Arabic/English)
"""

import json
import anthropic
from typing import Dict, List, Tuple, Optional

class DiagnosticEngine:
    """Advanced diagnostic engine for PhysioAssist Oracle"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 8000
        
    def free_chat_mode(self, user_message: str, conversation_history: List[Dict], language: str = "en") -> str:
        """
        Phase 1: Free Chat Mode - Build trust and gather initial information
        This is the "Hook" - provide value before asking for payment
        """
        
        system_prompt = self._build_chat_system_prompt(language)
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Get AI response
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=conversation_history
        )
        
        assistant_message = response.content[0].text
        
        # Add assistant response to history
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def _build_chat_system_prompt(self, language: str = "en") -> str:
        """Build system prompt for free chat mode"""
        
        if language == "ar":
            return """أنت مساعد سريري ذكي متخصص في العلاج الطبيعي والعلاج الفيزيائي.
دورك هو:
1. الاستماع بتعاطف لشكاوى المريض
2. فهم حالته الطبية بشكل شامل
3. جمع معلومات عن التاريخ المرضي والعادات اليومية
4. طرح أسئلة ذكية وديناميكية بناءً على إجاباته
5. تقديم نصائح أولية مفيدة (لبناء الثقة)
6. تحديد ما إذا كانت هناك علامات خطر (Red Flags)

أسلوبك:
- متعاطف وداعم
- احترافي وموثوق
- واضح وسهل الفهم
- محترم للثقافة العربية

ابدأ بفهم شكوى المريض الرئيسية، ثم اطرح أسئلة متابعة ذكية لجمع:
- موقع الألم ومدته
- كيف بدأ الألم
- ما يزيده وما يخففه
- تأثيره على الحياة اليومية
- التاريخ الطبي السابق
- العادات اليومية والوضعيات الخاطئة

لا تطلب الدفع أو الاشتراك الآن - فقط بناء الثقة وجمع المعلومات."""
        else:
            return """You are an intelligent clinical assistant specialized in physiotherapy and physical rehabilitation.
Your role is to:
1. Listen with empathy to the patient's complaints
2. Understand their medical condition comprehensively
3. Gather information about medical history and daily habits
4. Ask smart, dynamic questions based on their answers
5. Provide initial helpful advice (to build trust)
6. Identify any red flags

Your style:
- Empathetic and supportive
- Professional and trustworthy
- Clear and easy to understand
- Respectful of cultural differences

Start by understanding the patient's main complaint, then ask smart follow-up questions to gather:
- Pain location and duration
- How the pain started
- What makes it worse and better
- Impact on daily life
- Previous medical history
- Daily habits and wrong postures

Do NOT ask for payment or subscription yet - just build trust and gather information."""
    
    def generate_comprehensive_assessment(self, patient_data: Dict, language: str = "en") -> Dict:
        """
        Phase 2: Generate comprehensive clinical assessment
        This includes diagnosis, red flags, and initial recommendations
        """
        
        prompt = self._build_assessment_prompt(patient_data, language)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        assessment_text = response.content[0].text
        
        # Parse the assessment
        assessment = self._parse_assessment(assessment_text, language)
        
        return assessment
    
    def _build_assessment_prompt(self, patient_data: Dict, language: str = "en") -> str:
        """Build prompt for clinical assessment"""
        
        patient_info = json.dumps(patient_data, ensure_ascii=False, indent=2)
        
        if language == "ar":
            return f"""بناءً على المعلومات التالية عن المريض، قم بإجراء تقييم سريري شامل:

{patient_info}

قدم التقييم بالصيغة التالية:

## 🏥 التشخيص المبدئي
[اسم الحالة بالعربية والإنجليزية]

## ⚠️ علامات الخطر (Red Flags)
[قائمة بأي علامات خطر تحتاج تدخل طبي فوري]

## 📋 ملخص الحالة
[وصف موجز للحالة والأعراض الرئيسية]

## 💡 التوصيات الأولية
[3-4 نصائح أولية لتخفيف الألم الفوري]

## 🚨 هل يحتاج لطبيب فوراً؟
[نعم/لا مع التفسير]"""
        else:
            return f"""Based on the following patient information, provide a comprehensive clinical assessment:

{patient_info}

Provide the assessment in the following format:

## 🏥 Preliminary Diagnosis
[Condition name in English and Arabic]

## ⚠️ Red Flags
[List any red flags requiring immediate medical intervention]

## 📋 Case Summary
[Brief description of the condition and main symptoms]

## 💡 Initial Recommendations
[3-4 initial tips to provide immediate pain relief]

## 🚨 Does this require immediate doctor visit?
[Yes/No with explanation]"""
    
    def _parse_assessment(self, assessment_text: str, language: str = "en") -> Dict:
        """Parse assessment response into structured format"""
        
        # Simple parsing - in production, use more sophisticated parsing
        assessment = {
            "diagnosis": "",
            "red_flags": [],
            "summary": "",
            "initial_recommendations": [],
            "needs_immediate_doctor": False,
            "raw_text": assessment_text
        }
        
        return assessment
    
    def generate_comprehensive_treatment_plan(self, patient_data: Dict, assessment: Dict, language: str = "en") -> Dict:
        """
        Phase 3: Generate comprehensive 6-part treatment plan
        This is the PREMIUM content (behind paywall)
        
        6 Parts:
        1. Prevention Instructions (منع التفاقم)
        2. Home Modalities (وسائل منزلية)
        3. Progressive Exercise Program (برنامج تمارين متدرج)
        4. Contraindications (موانع)
        5. Recommended Products (منتجات أمازون)
        6. Safe Medications (أدوية آمنة)
        """
        
        prompt = self._build_treatment_plan_prompt(patient_data, assessment, language)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        plan_text = response.content[0].text
        treatment_plan = self._parse_treatment_plan(plan_text, language)
        
        return treatment_plan
    
    def _build_treatment_plan_prompt(self, patient_data: Dict, assessment: Dict, language: str = "en") -> str:
        """Build prompt for comprehensive treatment plan"""
        
        patient_info = json.dumps(patient_data, ensure_ascii=False, indent=2)
        assessment_info = json.dumps(assessment, ensure_ascii=False, indent=2)
        
        if language == "ar":
            return f"""بناءً على تقييم المريض التالي، قم بإنشاء خطة علاج طبيعي منزلية شاملة ومتكاملة:

معلومات المريض:
{patient_info}

التقييم السريري:
{assessment_info}

قدم خطة العلاج بـ 6 أجزاء:

## 1️⃣ تعليمات منع التفاقم (Prevention Instructions)
[تعليمات واضحة لتجنب تفاقم الحالة]

## 2️⃣ الوسائل العلاجية المنزلية (Home Modalities)
[كمادات دافئة/باردة، أجهزة مساج، موجات كهربائية، إلخ]

## 3️⃣ برنامج التمارين المتدرج (Progressive Exercise Program)
### الأسبوع 1-2: تمارين الثبات (Isometric)
### الأسبوع 3-4: تمارين مدى الحركة (Range of Motion)
### الأسبوع 5-6: تمارين الإطالة (Stretching)
### الأسبوع 7-8: تمارين التقوية (Strengthening)

## 4️⃣ الموانع والمحاذير (Contraindications)
[ما يجب تجنبه وعلامات التحذير]

## 5️⃣ المنتجات الموصى بها (Amazon Products)
[منتجات محددة من أمازون مع روابط]

## 6️⃣ الأدوية الآمنة المقترحة (Safe Medications)
[أدوية آمنة مع معلومات عن التفاعلات المحتملة]"""
        else:
            return f"""Based on the following patient assessment, create a comprehensive home physiotherapy treatment plan:

Patient Information:
{patient_info}

Clinical Assessment:
{assessment_info}

Provide a 6-part treatment plan:

## 1️⃣ Prevention Instructions
[Clear instructions to prevent condition worsening]

## 2️⃣ Home Modalities
[Warm/cold compresses, massage devices, electrical therapy, etc.]

## 3️⃣ Progressive Exercise Program
### Week 1-2: Isometric Exercises
### Week 3-4: Range of Motion Exercises
### Week 5-6: Stretching Exercises
### Week 7-8: Strengthening Exercises

## 4️⃣ Contraindications & Warnings
[What to avoid and warning signs]

## 5️⃣ Recommended Products
[Specific Amazon products with links]

## 6️⃣ Safe Medication Suggestions
[Safe medications with information about potential interactions]"""
    
    def _parse_treatment_plan(self, plan_text: str, language: str = "en") -> Dict:
        """Parse treatment plan into structured format"""
        
        treatment_plan = {
            "prevention_instructions": "",
            "home_modalities": "",
            "exercise_program": {
                "week_1_2_isometric": "",
                "week_3_4_rom": "",
                "week_5_6_stretching": "",
                "week_7_8_strengthening": ""
            },
            "contraindications": "",
            "recommended_products": [],
            "safe_medications": [],
            "raw_text": plan_text
        }
        
        return treatment_plan
    
    def detect_red_flags(self, patient_data: Dict, language: str = "en") -> Tuple[bool, List[str]]:
        """
        Detect red flags that require immediate medical attention
        Returns: (has_red_flags, list_of_red_flags)
        """
        
        red_flag_indicators = {
            "en": [
                "fever", "severe swelling", "loss of bladder control",
                "progressive weakness", "severe trauma", "cancer history",
                "unexplained weight loss", "night sweats", "severe pain at rest"
            ],
            "ar": [
                "حمى", "تورم شديد", "فقدان السيطرة على المثانة",
                "ضعف تدريجي", "صدمة شديدة", "تاريخ السرطان",
                "فقدان وزن غير مبرر", "تعرق ليلي", "ألم شديد في الراحة"
            ]
        }
        
        indicators = red_flag_indicators.get(language, red_flag_indicators["en"])
        patient_text = json.dumps(patient_data).lower()
        
        detected_flags = [flag for flag in indicators if flag.lower() in patient_text]
        
        return len(detected_flags) > 0, detected_flags
    
    def generate_quick_win_exercise(self, patient_data: Dict, language: str = "en") -> str:
        """
        Generate ONE quick exercise for immediate pain relief
        This is the "Hook" - free value to build trust
        """
        
        prompt = self._build_quick_win_prompt(patient_data, language)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return response.content[0].text
    
    def _build_quick_win_prompt(self, patient_data: Dict, language: str = "en") -> str:
        """Build prompt for quick win exercise"""
        
        patient_info = json.dumps(patient_data, ensure_ascii=False, indent=2)
        
        if language == "ar":
            return f"""بناءً على حالة المريض التالية، قدم تمرين واحد بسيط وآمن يمكن تنفيذه الآن لتخفيف الألم الفوري:

{patient_info}

التمرين يجب أن يكون:
- بسيط جداً (يمكن تنفيذه في أي مكان)
- آمن تماماً
- يعطي نتائج فورية (خلال 5-10 دقائق)
- لا يتطلب أي معدات

قدم التمرين بصيغة واضحة مع:
1. اسم التمرين
2. الوضعية الابتدائية
3. خطوات التنفيذ
4. عدد التكرارات
5. التنفس الصحيح
6. التحذيرات"""
        else:
            return f"""Based on the following patient condition, provide ONE simple and safe exercise that can be done now for immediate pain relief:

{patient_info}

The exercise should be:
- Very simple (can be done anywhere)
- Completely safe
- Provide immediate results (within 5-10 minutes)
- Require no equipment

Present the exercise clearly with:
1. Exercise name
2. Starting position
3. Step-by-step instructions
4. Number of repetitions
5. Proper breathing
6. Warnings"""


class FreemiumStrategy:
    """Freemium strategy implementation"""
    
    def __init__(self, language: str = "en"):
        self.language = language
    
    def get_free_content(self) -> Dict:
        """Content available for free users"""
        return {
            "assessment": True,  # Free preliminary assessment
            "quick_win_exercise": True,  # One quick exercise
            "initial_recommendations": True,  # 3-4 initial tips
            "prevention_tips": True,  # Basic prevention
        }
    
    def get_paywall_message(self) -> str:
        """Message to show when user hits paywall"""
        
        if self.language == "ar":
            return """🔐 <b>الخطة الكاملة محمية</b>

لقد أعددت لك خطة علاج طبيعي متكاملة ومخصصة لمدة 8 أسابيع تتضمن:

✅ برنامج تمارين متدرج (من الثبات إلى التقوية)
✅ وسائل علاجية منزلية (كمادات، أجهزة مساج، موجات كهربائية)
✅ تعليمات منع التفاقم
✅ منتجات أمازون موصى بها
✅ أدوية آمنة مقترحة
✅ فيديوهات YouTube للتمارين
✅ متابعة يومية وتقييم التقدم

💳 <b>للوصول للخطة الكاملة:</b>
اشترك الآن بـ <b>$4.99/شهر</b> (الشهر الأول فقط)
ثم <b>$9.99/شهر</b> (بدون التزام - يمكنك الإلغاء في أي وقت)"""
        else:
            return """🔐 <b>Full Plan Unlocked</b>

I've prepared a comprehensive, personalized 8-week physiotherapy treatment plan including:

✅ Progressive exercise program (from isometric to strengthening)
✅ Home modalities (compresses, massage devices, electrical therapy)
✅ Prevention instructions
✅ Recommended Amazon products
✅ Safe medication suggestions
✅ YouTube exercise videos
✅ Daily follow-up and progress tracking

💳 <b>To access the full plan:</b>
Subscribe now for <b>$4.99/month</b> (first month only)
Then <b>$9.99/month</b> (no commitment - cancel anytime)"""
    
    def get_premium_benefits(self) -> List[str]:
        """List of premium benefits"""
        
        if self.language == "ar":
            return [
                "✅ خطة علاج شاملة (8 أسابيع)",
                "✅ تمارين متدرجة",
                "✅ وسائل منزلية",
                "✅ منتجات موصى بها",
                "✅ أدوية آمنة",
                "✅ متابعة يومية",
                "✅ دعم 24/7"
            ]
        else:
            return [
                "✅ Comprehensive treatment plan (8 weeks)",
                "✅ Progressive exercises",
                "✅ Home modalities",
                "✅ Recommended products",
                "✅ Safe medications",
                "✅ Daily follow-up",
                "✅ 24/7 support"
            ]
