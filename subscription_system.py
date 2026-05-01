"""
PhysioAssist Oracle v7.0 - Advanced Subscription & Payment System
Freemium strategy with smart paywall, multiple subscription tiers,
and conversion optimization.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

class SubscriptionTier(Enum):
    """Subscription tiers"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    PRO = "pro"

class SubscriptionSystem:
    """Advanced subscription and payment system"""
    
    # Pricing configuration
    PRICING = {
        "free": {
            "price": 0,
            "currency": "USD",
            "billing_cycle": None,
            "features": {
                "assessments_per_month": 1,
                "quick_exercises": True,
                "initial_recommendations": True,
                "full_treatment_plan": False,
                "video_access": False,
                "product_recommendations": False,
                "medication_suggestions": False,
                "daily_followup": False,
                "priority_support": False,
            }
        },
        "basic": {
            "price": 4.99,
            "currency": "USD",
            "billing_cycle": "monthly",
            "first_month_price": 4.99,
            "regular_price": 9.99,
            "features": {
                "assessments_per_month": 5,
                "quick_exercises": True,
                "initial_recommendations": True,
                "full_treatment_plan": True,
                "video_access": True,
                "product_recommendations": True,
                "medication_suggestions": True,
                "daily_followup": True,
                "priority_support": False,
            }
        },
        "premium": {
            "price": 19.99,
            "currency": "USD",
            "billing_cycle": "monthly",
            "features": {
                "assessments_per_month": 20,
                "quick_exercises": True,
                "initial_recommendations": True,
                "full_treatment_plan": True,
                "video_access": True,
                "product_recommendations": True,
                "medication_suggestions": True,
                "daily_followup": True,
                "priority_support": True,
                "consultation_minutes": 60,
            }
        },
        "pro": {
            "price": 49.99,
            "currency": "USD",
            "billing_cycle": "monthly",
            "features": {
                "assessments_per_month": 100,
                "quick_exercises": True,
                "initial_recommendations": True,
                "full_treatment_plan": True,
                "video_access": True,
                "product_recommendations": True,
                "medication_suggestions": True,
                "daily_followup": True,
                "priority_support": True,
                "consultation_minutes": 300,
                "personal_coach": True,
            }
        }
    }
    
    def __init__(self, language: str = "en"):
        self.language = language
    
    def get_user_tier(self, user_data: Dict) -> SubscriptionTier:
        """Get user's current subscription tier"""
        
        if "subscription" not in user_data:
            return SubscriptionTier.FREE
        
        tier_str = user_data["subscription"].get("tier", "free").lower()
        
        try:
            return SubscriptionTier(tier_str)
        except ValueError:
            return SubscriptionTier.FREE
    
    def can_access_feature(self, user_data: Dict, feature: str) -> bool:
        """Check if user can access a specific feature"""
        
        tier = self.get_user_tier(user_data)
        features = self.PRICING[tier.value]["features"]
        
        return features.get(feature, False)
    
    def get_remaining_assessments(self, user_data: Dict) -> int:
        """Get remaining assessments for the month"""
        
        tier = self.get_user_tier(user_data)
        max_assessments = self.PRICING[tier.value]["features"]["assessments_per_month"]
        
        if "subscription" not in user_data:
            return 0
        
        assessments_this_month = user_data["subscription"].get("assessments_this_month", 0)
        
        return max(0, max_assessments - assessments_this_month)
    
    def has_hit_limit(self, user_data: Dict) -> bool:
        """Check if user has hit their assessment limit"""
        
        return self.get_remaining_assessments(user_data) <= 0
    
    def get_paywall_message(self, user_data: Dict, language: str = "en") -> str:
        """Get paywall message based on user's current tier"""
        
        tier = self.get_user_tier(user_data)
        
        if language == "ar":
            if tier == SubscriptionTier.FREE:
                return self._get_free_to_basic_paywall_ar()
            elif tier == SubscriptionTier.BASIC:
                return self._get_basic_to_premium_paywall_ar()
            elif tier == SubscriptionTier.PREMIUM:
                return self._get_premium_to_pro_paywall_ar()
        else:
            if tier == SubscriptionTier.FREE:
                return self._get_free_to_basic_paywall_en()
            elif tier == SubscriptionTier.BASIC:
                return self._get_basic_to_premium_paywall_en()
            elif tier == SubscriptionTier.PREMIUM:
                return self._get_premium_to_pro_paywall_en()
        
        return ""
    
    def _get_free_to_basic_paywall_ar(self) -> str:
        """Paywall message for Free → Basic upgrade"""
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
ثم <b>$9.99/شهر</b> (بدون التزام - يمكنك الإلغاء في أي وقت)

✨ <b>الفوائد الإضافية:</b>
• 5 تقييمات شهرية
• دعم 24/7
• تحديثات يومية
• تقارير PDF"""
    
    def _get_free_to_basic_paywall_en(self) -> str:
        """Paywall message for Free → Basic upgrade"""
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
Then <b>$9.99/month</b> (no commitment - cancel anytime)

✨ <b>Additional Benefits:</b>
• 5 assessments per month
• 24/7 support
• Daily updates
• PDF reports"""
    
    def _get_basic_to_premium_paywall_ar(self) -> str:
        """Paywall message for Basic → Premium upgrade"""
        return """⭐ <b>ترقية إلى Premium</b>

احصل على المزيد من المميزات:

✅ تقييمات غير محدودة (بدلاً من 5)
✅ استشارات مع أخصائي حقيقي (60 دقيقة/شهر)
✅ دعم أولوي 24/7
✅ برامج تمارين متقدمة
✅ تحليلات تقدم مفصلة

💳 <b>فقط $19.99/شهر</b>
(بدون التزام - يمكنك الإلغاء في أي وقت)"""
    
    def _get_basic_to_premium_paywall_en(self) -> str:
        """Paywall message for Basic → Premium upgrade"""
        return """⭐ <b>Upgrade to Premium</b>

Get more features:

✅ Unlimited assessments (instead of 5)
✅ Consultations with a real specialist (60 min/month)
✅ Priority 24/7 support
✅ Advanced exercise programs
✅ Detailed progress analytics

💳 <b>Only $19.99/month</b>
(no commitment - cancel anytime)"""
    
    def _get_premium_to_pro_paywall_ar(self) -> str:
        """Paywall message for Premium → Pro upgrade"""
        return """🏆 <b>ترقية إلى Pro</b>

احصل على أفضل ما لدينا:

✅ مدرب شخصي مخصص
✅ استشارات غير محدودة (300 دقيقة/شهر)
✅ برامج تمارين مخصصة 100%
✅ تحليلات متقدمة وتقارير أسبوعية
✅ أولوية عالية جداً في الدعم

💳 <b>فقط $49.99/شهر</b>
(بدون التزام - يمكنك الإلغاء في أي وقت)"""
    
    def _get_premium_to_pro_paywall_en(self) -> str:
        """Paywall message for Premium → Pro upgrade"""
        return """🏆 <b>Upgrade to Pro</b>

Get the best we have to offer:

✅ Dedicated personal coach
✅ Unlimited consultations (300 min/month)
✅ 100% customized exercise programs
✅ Advanced analytics and weekly reports
✅ VIP support priority

💳 <b>Only $49.99/month</b>
(no commitment - cancel anytime)"""
    
    def get_subscription_comparison(self, language: str = "en") -> str:
        """Get subscription comparison table"""
        
        if language == "ar":
            return """
<b>مقارنة الخطط</b>

<b>مجاني</b>
• تقييم واحد/شهر
• تمارين سريعة
• نصائح أولية

<b>Basic - $4.99 (الشهر الأول)</b>
• 5 تقييمات/شهر
• خطة علاج كاملة
• فيديوهات YouTube
• منتجات موصى بها
• أدوية آمنة

<b>Premium - $19.99/شهر</b>
• تقييمات غير محدودة
• استشارات (60 دقيقة)
• دعم أولوي
• برامج متقدمة

<b>Pro - $49.99/شهر</b>
• مدرب شخصي
• استشارات غير محدودة
• برامج مخصصة 100%
• تحليلات متقدمة"""
        else:
            return """
<b>Plan Comparison</b>

<b>Free</b>
• 1 assessment/month
• Quick exercises
• Initial tips

<b>Basic - $4.99 (First Month)</b>
• 5 assessments/month
• Full treatment plan
• YouTube videos
• Recommended products
• Safe medications

<b>Premium - $19.99/month</b>
• Unlimited assessments
• Consultations (60 min)
• Priority support
• Advanced programs

<b>Pro - $49.99/month</b>
• Personal coach
• Unlimited consultations
• 100% customized programs
• Advanced analytics"""
    
    def record_assessment(self, user_data: Dict) -> Dict:
        """Record that user completed an assessment"""
        
        if "subscription" not in user_data:
            user_data["subscription"] = {}
        
        # Check if it's a new month
        last_assessment_date = user_data["subscription"].get("last_assessment_date")
        
        if last_assessment_date:
            last_date = datetime.fromisoformat(last_assessment_date)
            if last_date.month != datetime.now().month:
                # New month - reset counter
                user_data["subscription"]["assessments_this_month"] = 0
        
        # Increment counter
        current_count = user_data["subscription"].get("assessments_this_month", 0)
        user_data["subscription"]["assessments_this_month"] = current_count + 1
        user_data["subscription"]["last_assessment_date"] = datetime.now().isoformat()
        
        return user_data
    
    def get_upgrade_incentive(self, user_data: Dict, language: str = "en") -> str:
        """Get upgrade incentive message"""
        
        tier = self.get_user_tier(user_data)
        
        if tier == SubscriptionTier.FREE:
            if language == "ar":
                return """🎁 <b>عرض خاص للمشتركين الجدد!</b>

احصل على الشهر الأول بـ $4.99 فقط (بدلاً من $9.99)
ثم $9.99/شهر بدون التزام

✅ خطط علاج كاملة
✅ فيديوهات YouTube
✅ منتجات موصى بها
✅ أدوية آمنة
✅ متابعة يومية"""
            else:
                return """🎁 <b>Special Offer for New Subscribers!</b>

Get the first month for just $4.99 (instead of $9.99)
Then $9.99/month with no commitment

✅ Full treatment plans
✅ YouTube videos
✅ Recommended products
✅ Safe medications
✅ Daily follow-up"""
        
        return ""
    
    def calculate_subscription_value(self, tier: str) -> Dict:
        """Calculate the value proposition of a subscription tier"""
        
        pricing = self.PRICING.get(tier, {})
        features = pricing.get("features", {})
        
        value_points = []
        
        if features.get("full_treatment_plan"):
            value_points.append("Full treatment plans")
        if features.get("video_access"):
            value_points.append("YouTube video access")
        if features.get("product_recommendations"):
            value_points.append("Product recommendations")
        if features.get("medication_suggestions"):
            value_points.append("Medication suggestions")
        if features.get("daily_followup"):
            value_points.append("Daily follow-up")
        if features.get("priority_support"):
            value_points.append("Priority support")
        if features.get("personal_coach"):
            value_points.append("Personal coach")
        
        return {
            "tier": tier,
            "price": pricing.get("price", 0),
            "features": value_points,
            "assessments_per_month": features.get("assessments_per_month", 0)
        }


class ConversionOptimizer:
    """Optimize conversion rates with smart strategies"""
    
    def __init__(self, language: str = "en"):
        self.language = language
    
    def get_conversion_hook(self, user_data: Dict) -> str:
        """Get the hook message to convert free users"""
        
        if self.language == "ar":
            return """🎯 <b>لاحظ الفرق!</b>

لقد أعددت لك خطة علاج شاملة تتضمن:
✅ 8 أسابيع من التمارين المتدرجة
✅ وسائل علاجية منزلية
✅ منتجات موصى بها
✅ أدوية آمنة

فقط $4.99 للشهر الأول!"""
        else:
            return """🎯 <b>See the Difference!</b>

I've prepared a comprehensive treatment plan including:
✅ 8 weeks of progressive exercises
✅ Home modalities
✅ Recommended products
✅ Safe medications

Only $4.99 for the first month!"""
    
    def get_retention_message(self, user_data: Dict, days_subscribed: int) -> str:
        """Get retention message based on subscription duration"""
        
        if days_subscribed < 7:
            if self.language == "ar":
                return "شكراً لاختيارك PhysioAssist! نتمنى أن تستفيد من الخطة."
            else:
                return "Thank you for choosing PhysioAssist! We hope you're enjoying the plan."
        elif days_subscribed < 30:
            if self.language == "ar":
                return "كيف تشعر بالتقدم؟ نحن هنا لدعمك!"
            else:
                return "How's your progress? We're here to support you!"
        else:
            if self.language == "ar":
                return "أنت عضو مخلص! شكراً لثقتك بنا."
            else:
                return "You're a loyal member! Thank you for your trust."
