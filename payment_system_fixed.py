"""
Payment System Module - Fixed Version
Handles subscriptions, payments, and access control
"""

from datetime import datetime, timedelta
from enum import Enum
import json
import os


class SubscriptionLevel(Enum):
    """Subscription levels"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    PRO = "pro"


class PaymentPlan:
    """Payment plan details"""
    
    PLANS = {
        'basic': {
            'name': 'Basic Plan',
            'price_usd': 1.99,
            'price_cents': 199,
            'duration_days': 30,
            'features': [
                'Unlimited assessments',
                'Treatment plans',
                'Exercise programs',
                'Basic support'
            ]
        },
        'premium': {
            'name': 'Premium Plan',
            'price_usd': 4.99,
            'price_cents': 499,
            'duration_days': 90,
            'features': [
                'Everything in Basic',
                'Priority support',
                'Exclusive content',
                'PDF reports'
            ]
        },
        'pro': {
            'name': 'Pro Plan',
            'price_usd': 9.99,
            'price_cents': 999,
            'duration_days': 365,
            'features': [
                'Everything in Premium',
                'Lifetime access',
                'Custom plans',
                'Direct consultation'
            ]
        }
    }


class SubscriptionManager:
    """Manage user subscriptions"""
    
    def __init__(self):
        self.subscriptions = {}  # user_id -> subscription_data
        self.load_subscriptions()
    
    def load_subscriptions(self):
        """Load subscriptions from file"""
        try:
            if os.path.exists('subscriptions.json'):
                with open('subscriptions.json', 'r') as f:
                    self.subscriptions = json.load(f)
        except Exception as e:
            print(f"Error loading subscriptions: {e}")
    
    def save_subscriptions(self):
        """Save subscriptions to file"""
        try:
            with open('subscriptions.json', 'w') as f:
                json.dump(self.subscriptions, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving subscriptions: {e}")
    
    def get_subscription(self, user_id: int) -> dict:
        """Get user subscription"""
        return self.subscriptions.get(str(user_id), {
            'level': 'free',
            'expires': None,
            'created': datetime.now().isoformat(),
            'assessments_used': 0
        })
    
    def create_subscription(self, user_id: int, plan: str) -> dict:
        """Create new subscription"""
        
        if plan not in PaymentPlan.PLANS:
            raise ValueError(f"Invalid plan: {plan}")
        
        plan_data = PaymentPlan.PLANS[plan]
        expires = datetime.now() + timedelta(days=plan_data['duration_days'])
        
        subscription = {
            'level': plan,
            'expires': expires.isoformat(),
            'created': datetime.now().isoformat(),
            'assessments_used': 0,
            'price_paid': plan_data['price_usd'],
            'plan_name': plan_data['name']
        }
        
        self.subscriptions[str(user_id)] = subscription
        self.save_subscriptions()
        
        return subscription
    
    def is_subscription_valid(self, user_id: int) -> bool:
        """Check if subscription is still valid"""
        
        sub = self.get_subscription(user_id)
        
        if sub['level'] == 'free':
            return True  # Free tier always valid
        
        if sub['expires']:
            expires = datetime.fromisoformat(sub['expires'])
            return datetime.now() < expires
        
        return False
    
    def get_remaining_days(self, user_id: int) -> int:
        """Get remaining subscription days"""
        
        sub = self.get_subscription(user_id)
        
        if not sub['expires']:
            return -1  # Unlimited
        
        expires = datetime.fromisoformat(sub['expires'])
        remaining = (expires - datetime.now()).days
        
        return max(0, remaining)
    
    def increment_assessment_count(self, user_id: int):
        """Increment assessment count"""
        
        sub = self.get_subscription(user_id)
        sub['assessments_used'] = sub.get('assessments_used', 0) + 1
        
        self.subscriptions[str(user_id)] = sub
        self.save_subscriptions()
    
    def can_access_assessment(self, user_id: int, free_limit: int = 1) -> tuple:
        """Check if user can access assessment"""
        
        sub = self.get_subscription(user_id)
        level = sub['level']
        
        # Free users have limited assessments
        if level == 'free':
            assessments_used = sub.get('assessments_used', 0)
            if assessments_used >= free_limit:
                return False, f"Free limit reached ({free_limit}). Please upgrade."
            return True, "Free assessment available"
        
        # Paid users - check subscription validity
        if not self.is_subscription_valid(user_id):
            return False, "Subscription expired. Please renew."
        
        return True, "Subscription active"


class PaymentProcessor:
    """Process payments"""
    
    def __init__(self, provider_token: str = None):
        self.provider_token = provider_token or os.getenv('PAYMENT_PROVIDER_TOKEN', 'test')
        self.transactions = {}
        self.load_transactions()
    
    def load_transactions(self):
        """Load transaction history"""
        try:
            if os.path.exists('transactions.json'):
                with open('transactions.json', 'r') as f:
                    self.transactions = json.load(f)
        except Exception as e:
            print(f"Error loading transactions: {e}")
    
    def save_transactions(self):
        """Save transaction history"""
        try:
            with open('transactions.json', 'w') as f:
                json.dump(self.transactions, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving transactions: {e}")
    
    def create_invoice(self, user_id: int, plan: str) -> dict:
        """Create invoice for payment"""
        
        if plan not in PaymentPlan.PLANS:
            raise ValueError(f"Invalid plan: {plan}")
        
        plan_data = PaymentPlan.PLANS[plan]
        
        invoice = {
            'user_id': user_id,
            'plan': plan,
            'amount': plan_data['price_cents'],
            'currency': 'USD',
            'created': datetime.now().isoformat(),
            'status': 'pending',
            'title': plan_data['name'],
            'description': f"PhysioAssist {plan_data['name']} - {plan_data['duration_days']} days"
        }
        
        return invoice
    
    def process_payment(self, user_id: int, plan: str, transaction_id: str) -> dict:
        """Process successful payment"""
        
        invoice = self.create_invoice(user_id, plan)
        
        transaction = {
            'user_id': user_id,
            'plan': plan,
            'transaction_id': transaction_id,
            'amount': invoice['amount'],
            'currency': invoice['currency'],
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        self.transactions[transaction_id] = transaction
        self.save_transactions()
        
        return transaction
    
    def verify_payment(self, transaction_id: str) -> bool:
        """Verify payment transaction"""
        
        transaction = self.transactions.get(transaction_id)
        
        if not transaction:
            return False
        
        return transaction['status'] == 'completed'


class AccessControl:
    """Control access to features"""
    
    FREE_ASSESSMENTS_LIMIT = 1
    
    def __init__(self):
        self.subscription_manager = SubscriptionManager()
    
    def can_perform_assessment(self, user_id: int) -> tuple:
        """Check if user can perform assessment"""
        
        can_access, message = self.subscription_manager.can_access_assessment(
            user_id, 
            self.FREE_ASSESSMENTS_LIMIT
        )
        
        return can_access, message
    
    def can_download_pdf(self, user_id: int) -> tuple:
        """Check if user can download PDF"""
        
        sub = self.subscription_manager.get_subscription(user_id)
        
        if sub['level'] in ['premium', 'pro']:
            return True, "PDF download available"
        
        if sub['level'] == 'basic':
            return True, "PDF download available"
        
        return False, "Upgrade to download PDF"
    
    def can_view_videos(self, user_id: int) -> tuple:
        """Check if user can view diagnostic videos"""
        
        sub = self.subscription_manager.get_subscription(user_id)
        
        if sub['level'] in ['premium', 'pro']:
            return True, "Full video access"
        
        if sub['level'] == 'basic':
            return True, "Basic video access"
        
        return True, "Limited video access"  # Free users can see some videos
    
    def get_user_status(self, user_id: int) -> dict:
        """Get complete user status"""
        
        sub = self.subscription_manager.get_subscription(user_id)
        
        status = {
            'user_id': user_id,
            'subscription_level': sub['level'],
            'subscription_expires': sub.get('expires'),
            'remaining_days': self.subscription_manager.get_remaining_days(user_id),
            'assessments_used': sub.get('assessments_used', 0),
            'assessments_limit': self.FREE_ASSESSMENTS_LIMIT if sub['level'] == 'free' else 'unlimited',
            'can_assess': self.can_perform_assessment(user_id)[0],
            'can_download_pdf': self.can_download_pdf(user_id)[0],
            'can_view_videos': self.can_view_videos(user_id)[0]
        }
        
        return status
    
    def format_status_message(self, user_id: int, language: str = 'English') -> str:
        """Format user status as message"""
        
        status = self.get_user_status(user_id)
        
        if language == 'Arabic':
            return f"""
📊 **حالة حسابك:**

💎 الاشتراك: {status['subscription_level'].upper()}
📅 ينتهي في: {status['subscription_expires'] or 'غير محدود'}
⏳ الأيام المتبقية: {status['remaining_days'] if status['remaining_days'] > 0 else 'غير محدود'}

📋 التقييمات:
• المستخدمة: {status['assessments_used']}
• الحد: {status['assessments_limit']}

✅ الميزات المتاحة:
• تقييم: {'✅' if status['can_assess'] else '❌'}
• تحميل PDF: {'✅' if status['can_download_pdf'] else '❌'}
• مشاهدة الفيديوهات: {'✅' if status['can_view_videos'] else '❌'}
            """
        else:
            return f"""
📊 **Your Account Status:**

💎 Subscription: {status['subscription_level'].upper()}
📅 Expires: {status['subscription_expires'] or 'Unlimited'}
⏳ Days Remaining: {status['remaining_days'] if status['remaining_days'] > 0 else 'Unlimited'}

📋 Assessments:
• Used: {status['assessments_used']}
• Limit: {status['assessments_limit']}

✅ Available Features:
• Assessment: {'✅' if status['can_assess'] else '❌'}
• Download PDF: {'✅' if status['can_download_pdf'] else '❌'}
• Watch Videos: {'✅' if status['can_view_videos'] else '❌'}
            """
