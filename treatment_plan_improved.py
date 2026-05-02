"""
Treatment Plan Generator - Improved Version
Generates comprehensive 6-part treatment plans
"""

class SimplifiedTreatmentPlan:
    """Generate simplified treatment plans"""
    
    def __init__(self, language: str = 'English'):
        self.language = language
        self.is_arabic = language == 'Arabic'
    
    def generate_full_plan(self, condition: str, severity: str) -> dict:
        """Generate complete 6-part treatment plan"""
        
        return {
            'part1_prevention': self._get_prevention_tips(condition, severity),
            'part2_home_remedies': self._get_home_remedies(condition),
            'part3_exercises': self._get_exercises(condition, severity),
            'part4_warnings': self._get_warnings(condition),
            'part5_products': self._get_products(condition),
            'part6_medications': self._get_medications(condition)
        }
    
    def _get_prevention_tips(self, condition: str, severity: str) -> str:
        """Part 1: Prevention and care tips"""
        
        if self.is_arabic:
            return """
🛡️ **نصائح منع التفاقم:**

1. **الراحة:** خذ فترات راحة منتظمة كل ساعة
2. **الوضعية:** حافظ على وضعية صحيحة أثناء الجلوس والوقوف
3. **الحركة:** تجنب الحركات المفاجئة والثقيلة
4. **الحرارة:** استخدم كمادات دافئة لمدة 15 دقيقة
5. **التمدد:** قم بتمارين تمدد خفيفة يومياً
6. **النوم:** نم على وسادة مريحة وسرير جيد
            """
        else:
            return """
🛡️ **Prevention Tips:**

1. **Rest:** Take regular breaks every hour
2. **Posture:** Maintain good posture while sitting and standing
3. **Movement:** Avoid sudden and heavy movements
4. **Heat:** Use warm compresses for 15 minutes
5. **Stretching:** Do light stretches daily
6. **Sleep:** Sleep on a comfortable pillow and good bed
            """
    
    def _get_home_remedies(self, condition: str) -> str:
        """Part 2: Home remedies"""
        
        if self.is_arabic:
            return """
🏥 **العلاجات المنزلية:**

1. **الكمادات الدافئة:** ضع كمادة دافئة لمدة 15-20 دقيقة
2. **الكمادات الباردة:** استخدم ثلج في أول 48 ساعة
3. **التدليك:** دلك المنطقة برفق بحركات دائرية
4. **الاسترخاء:** خذ حماماً دافئاً لاسترخاء العضلات
5. **الرفع:** ارفع الطرف المصاب قليلاً أثناء الجلوس
6. **الضغط:** استخدم رباط ضاغط خفيف إذا لزم الأمر
            """
        else:
            return """
🏥 **Home Remedies:**

1. **Warm Compress:** Apply warm compress for 15-20 minutes
2. **Cold Compress:** Use ice in the first 48 hours
3. **Massage:** Gently massage the area with circular motions
4. **Relaxation:** Take a warm bath to relax muscles
5. **Elevation:** Elevate the affected limb while sitting
6. **Compression:** Use a light compression bandage if needed
            """
    
    def _get_exercises(self, condition: str, severity: str) -> str:
        """Part 3: Graduated exercise program"""
        
        if self.is_arabic:
            return """
💪 **برنامج التمارين المتدرج:**

**المرحلة 1 (الأسبوع الأول):**
- تمارين تمدد خفيفة (3 مرات يومياً)
- تحريك المنطقة برفق (5 دقائق)
- تنفس عميق واسترخاء (10 دقائق)

**المرحلة 2 (الأسبوع الثاني):**
- تمارين تقوية خفيفة (يومياً)
- زيادة نطاق الحركة تدريجياً
- تمارين التوازن (5 دقائق)

**المرحلة 3 (الأسبوع الثالث):**
- تمارين تقوية متقدمة
- تمارين وظيفية
- العودة التدريجية للأنشطة العادية

⚠️ توقف إذا شعرت بألم شديد!
            """
        else:
            return """
💪 **Graduated Exercise Program:**

**Phase 1 (Week 1):**
- Light stretching exercises (3 times daily)
- Gentle movement of the area (5 minutes)
- Deep breathing and relaxation (10 minutes)

**Phase 2 (Week 2):**
- Light strengthening exercises (daily)
- Gradually increase range of motion
- Balance exercises (5 minutes)

**Phase 3 (Week 3):**
- Advanced strengthening exercises
- Functional exercises
- Gradual return to normal activities

⚠️ Stop if you feel severe pain!
            """
    
    def _get_warnings(self, condition: str) -> str:
        """Part 4: Warnings and contraindications"""
        
        if self.is_arabic:
            return """
⚠️ **تحذيرات مهمة:**

🚫 **تجنب:**
- الحركات المفاجئة والقوية
- رفع أشياء ثقيلة
- الجلوس لفترات طويلة
- النوم على وضعية خاطئة
- الضغط على المنطقة المصابة

⛔ **اطلب مساعدة طبية فوراً إذا:**
- زاد الألم بشكل كبير
- ظهرت تنميل أو ضعف
- حدث تورم شديد
- لم يتحسن الألم بعد 2-3 أسابيع
- ظهرت أعراض عصبية جديدة

📞 **تذكير:** هذا ليس تشخيصاً طبياً. استشر طبيبك دائماً!
            """
        else:
            return """
⚠️ **Important Warnings:**

🚫 **Avoid:**
- Sudden and forceful movements
- Lifting heavy objects
- Sitting for long periods
- Sleeping in wrong positions
- Pressure on the affected area

⛔ **Seek Medical Help Immediately If:**
- Pain increases significantly
- Numbness or weakness appears
- Severe swelling occurs
- Pain doesn't improve after 2-3 weeks
- New neurological symptoms appear

📞 **Reminder:** This is not a medical diagnosis. Always consult your doctor!
            """
    
    def _get_products(self, condition: str) -> str:
        """Part 5: Recommended products"""
        
        if self.is_arabic:
            return """
🛒 **منتجات موصى بها (من أمازون):**

1. **كمادات حرارية:**
   - Thermacare Heat Wraps
   - Heating Pad Electric

2. **أجهزة تدليك:**
   - Neck Massager
   - Shiatsu Massage Pillow

3. **أدوات دعم:**
   - Cervical Pillow
   - Lumbar Support Pillow

4. **مكملات:**
   - Glucosamine Chondroitin
   - Omega-3 Fish Oil

💡 البحث عن هذه المنتجات على أمازون بحسب احتياجاتك
            """
        else:
            return """
🛒 **Recommended Products (from Amazon):**

1. **Heat Pads:**
   - Thermacare Heat Wraps
   - Heating Pad Electric

2. **Massage Devices:**
   - Neck Massager
   - Shiatsu Massage Pillow

3. **Support Tools:**
   - Cervical Pillow
   - Lumbar Support Pillow

4. **Supplements:**
   - Glucosamine Chondroitin
   - Omega-3 Fish Oil

💡 Search for these products on Amazon based on your needs
            """
    
    def _get_medications(self, condition: str) -> str:
        """Part 6: Safe medications"""
        
        if self.is_arabic:
            return """
💊 **أدوية آمنة مقترحة:**

⚠️ **تحذير:** استشر الصيدلي أو الطبيب قبل تناول أي دواء!

**مسكنات الألم:**
- Paracetamol (تايلينول) - 500-1000 ملغ
- Ibuprofen (بروفين) - 200-400 ملغ
- Naproxen - 250-500 ملغ

**مرخيات العضلات:**
- Muscle Relaxants (بوصفة طبية فقط)

**كريمات موضعية:**
- Diclofenac Gel
- Menthol Cream
- Capsaicin Cream

📋 **التعليمات:**
- اتبع الجرعات الموصى بها
- لا تتجاوز المدة المحددة
- توقف إذا ظهرت آثار جانبية
- أخبر طبيبك عن الأدوية الأخرى التي تتناولها

🚫 **لا تستخدم إذا:**
- كنت حاملاً أو مرضعة
- كان لديك حساسية من الدواء
- كنت تتناول أدوية أخرى قد تتفاعل معها
            """
        else:
            return """
💊 **Safe Suggested Medications:**

⚠️ **Warning:** Consult pharmacist or doctor before taking any medication!

**Pain Relievers:**
- Paracetamol (Tylenol) - 500-1000 mg
- Ibuprofen (Advil) - 200-400 mg
- Naproxen - 250-500 mg

**Muscle Relaxants:**
- Muscle Relaxants (prescription only)

**Topical Creams:**
- Diclofenac Gel
- Menthol Cream
- Capsaicin Cream

📋 **Instructions:**
- Follow recommended dosages
- Don't exceed specified duration
- Stop if side effects appear
- Tell your doctor about other medications

🚫 **Don't Use If:**
- You are pregnant or breastfeeding
- You are allergic to the medication
- You take other medications that may interact
            """
    
    def format_complete_plan(self, plan: dict) -> str:
        """Format complete plan for display"""
        
        message = ""
        if self.is_arabic:
            message += "📋 **خطة العلاج الشاملة الخاصة بك:**\n\n"
        else:
            message += "📋 **Your Comprehensive Treatment Plan:**\n\n"
        
        parts = [
            ('part1_prevention', '1️⃣'),
            ('part2_home_remedies', '2️⃣'),
            ('part3_exercises', '3️⃣'),
            ('part4_warnings', '4️⃣'),
            ('part5_products', '5️⃣'),
            ('part6_medications', '6️⃣')
        ]
        
        for part_key, emoji in parts:
            message += f"{emoji} {plan.get(part_key, '')}\n\n"
        
        return message
