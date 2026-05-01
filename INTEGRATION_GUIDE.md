# PhysioAssist Oracle v7.0 - Complete Integration Guide

## 🚀 Overview

PhysioAssist Oracle v7.0 is a complete overhaul of the bot with the following new features:

1. **Advanced Diagnostic Engine** - Smart conversation and comprehensive assessment
2. **Professional UX Formatting** - Bilingual (Arabic/English) with beautiful typography
3. **Freemium Subscription System** - Smart paywall strategy for conversion
4. **6-Part Treatment Plans** - Comprehensive, personalized treatment plans
5. **Red Flag Detection** - Automatic detection of emergency conditions
6. **Quick Win Exercises** - Free hook to build trust before paywall

---

## 📦 New Modules

### 1. `diagnostic_engine.py`
Advanced AI-powered diagnostic system with:
- Free Chat Mode (build trust)
- Smart Dynamic Questions
- Comprehensive Assessment Generation
- 6-Part Treatment Plan Generation
- Red Flag Detection
- Quick Win Exercise Generation
- Freemium Strategy Implementation

**Key Classes:**
- `DiagnosticEngine` - Main diagnostic system
- `FreemiumStrategy` - Freemium implementation

**Usage:**
```python
from diagnostic_engine import DiagnosticEngine, FreemiumStrategy

# Initialize
engine = DiagnosticEngine(api_key=ANTHROPIC_API_KEY)
freemium = FreemiumStrategy(language="en")

# Free chat mode
response = engine.free_chat_mode(user_message, conversation_history, language="en")

# Generate assessment
assessment = engine.generate_comprehensive_assessment(patient_data, language="en")

# Generate treatment plan
plan = engine.generate_comprehensive_treatment_plan(patient_data, assessment, language="en")

# Generate quick win exercise
exercise = engine.generate_quick_win_exercise(patient_data, language="en")

# Detect red flags
has_flags, flags = engine.detect_red_flags(patient_data, language="en")
```

---

### 2. `ux_formatter.py`
Professional UX formatting system with:
- Bilingual support (RTL for Arabic, LTR for English)
- Beautiful typography
- Professional emoji system
- Visual hierarchy
- Consistent branding

**Key Classes:**
- `UXFormatter` - Main formatting system

**Usage:**
```python
from ux_formatter import UXFormatter

# Initialize
formatter = UXFormatter(language="ar")  # or "en"

# Format messages
header = formatter.format_header("Clinical Assessment", "🏥", 1)
assessment = formatter.format_assessment_result(diagnosis, confidence, summary, red_flags)
plan = formatter.format_treatment_plan(plan_data)
exercise = formatter.format_exercise_instruction(exercise_name, instructions)
paywall = formatter.format_paywall_message(plan_summary)
```

---

### 3. `subscription_system.py`
Advanced subscription and payment system with:
- 4 subscription tiers (Free, Basic, Premium, Pro)
- Smart paywall strategy
- Feature access control
- Assessment limits
- Conversion optimization
- Retention messages

**Key Classes:**
- `SubscriptionSystem` - Main subscription system
- `SubscriptionTier` - Enum for tiers
- `ConversionOptimizer` - Conversion optimization

**Usage:**
```python
from subscription_system import SubscriptionSystem, SubscriptionTier

# Initialize
subscription = SubscriptionSystem(language="en")

# Check user tier
tier = subscription.get_user_tier(user_data)

# Check feature access
can_access = subscription.can_access_feature(user_data, "full_treatment_plan")

# Get paywall message
paywall = subscription.get_paywall_message(user_data, language="en")

# Record assessment
user_data = subscription.record_assessment(user_data)

# Get upgrade incentive
incentive = subscription.get_upgrade_incentive(user_data, language="en")
```

---

## 🔄 Integration Steps

### Step 1: Update `bot.py`

Add imports at the top:
```python
from diagnostic_engine import DiagnosticEngine, FreemiumStrategy
from ux_formatter import UXFormatter
from subscription_system import SubscriptionSystem, ConversionOptimizer
```

Initialize in `main()`:
```python
# Initialize new systems
diagnostic_engine = DiagnosticEngine(api_key=ANTHROPIC_API_KEY)
ux_formatter_en = UXFormatter(language="en")
ux_formatter_ar = UXFormatter(language="ar")
subscription_system = SubscriptionSystem(language="en")
conversion_optimizer = ConversionOptimizer(language="en")
```

### Step 2: Update Conversation States

Add new states for chat mode:
```python
# New states
CHAT_MODE = 9
ASSESSMENT_PHASE = 10
TREATMENT_PLAN_PHASE = 11
PAYWALL_PHASE = 12
```

### Step 3: Implement Chat Mode Handler

```python
async def chat_mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free chat mode"""
    
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Get user data
    user = get_or_create_user(user_id)
    language = user.get("language", "en")
    
    # Get or initialize conversation history
    if "conversation_history" not in context.user_data:
        context.user_data["conversation_history"] = []
    
    # Get AI response
    response = diagnostic_engine.free_chat_mode(
        user_message,
        context.user_data["conversation_history"],
        language=language
    )
    
    # Format response
    formatter = ux_formatter_ar if language == "ar" else ux_formatter_en
    formatted_response = formatter.format_chat_message("PhysioAssist", response, is_user=False)
    
    # Send response
    await update.message.reply_text(formatted_response, parse_mode=ParseMode.HTML)
```

### Step 4: Implement Assessment Phase

```python
async def assessment_phase_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle assessment generation"""
    
    user_id = update.effective_user.id
    user = get_or_create_user(user_id)
    language = user.get("language", "en")
    
    # Get patient data from conversation
    patient_data = context.user_data.get("patient_data", {})
    
    # Generate assessment
    assessment = diagnostic_engine.generate_comprehensive_assessment(patient_data, language=language)
    
    # Check for red flags
    has_flags, flags = diagnostic_engine.detect_red_flags(patient_data, language=language)
    
    if has_flags:
        # Show emergency message
        formatter = ux_formatter_ar if language == "ar" else ux_formatter_en
        emergency_msg = formatter.format_header("RED FLAGS DETECTED", "🚨", 1)
        await update.message.reply_text(emergency_msg, parse_mode=ParseMode.HTML)
        return
    
    # Generate quick win exercise
    quick_win = diagnostic_engine.generate_quick_win_exercise(patient_data, language=language)
    
    # Format and send
    formatter = ux_formatter_ar if language == "ar" else ux_formatter_en
    formatted_assessment = formatter.format_assessment_result(
        assessment.get("diagnosis", ""),
        80,  # confidence
        assessment.get("summary", ""),
        assessment.get("red_flags", [])
    )
    
    await update.message.reply_text(formatted_assessment, parse_mode=ParseMode.HTML)
    
    # Send quick win exercise
    formatted_exercise = formatter.format_quick_win_exercise(quick_win)
    await update.message.reply_text(formatted_exercise, parse_mode=ParseMode.HTML)
    
    # Store assessment
    context.user_data["assessment"] = assessment
    context.user_data["patient_data"] = patient_data
```

### Step 5: Implement Paywall Phase

```python
async def paywall_phase_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle paywall and subscription"""
    
    user_id = update.effective_user.id
    user = get_or_create_user(user_id)
    language = user.get("language", "en")
    
    # Check subscription status
    tier = subscription_system.get_user_tier(user)
    
    # If free user, show paywall
    if tier.value == "free":
        # Generate full treatment plan (for preview)
        patient_data = context.user_data.get("patient_data", {})
        assessment = context.user_data.get("assessment", {})
        
        plan = diagnostic_engine.generate_comprehensive_treatment_plan(
            patient_data, assessment, language=language
        )
        
        # Get paywall message
        paywall_msg = subscription_system.get_paywall_message(user, language=language)
        
        # Format and send
        formatter = ux_formatter_ar if language == "ar" else ux_formatter_en
        formatted_paywall = formatter.format_paywall_message(paywall_msg)
        
        await update.message.reply_text(formatted_paywall, parse_mode=ParseMode.HTML)
        
        # Show upgrade buttons
        keyboard = [
            [InlineKeyboardButton("💳 Subscribe Now", callback_data="subscribe_basic")],
            [InlineKeyboardButton("📊 See Comparison", callback_data="show_comparison")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
    else:
        # User is paid - show full plan
        patient_data = context.user_data.get("patient_data", {})
        assessment = context.user_data.get("assessment", {})
        
        plan = diagnostic_engine.generate_comprehensive_treatment_plan(
            patient_data, assessment, language=language
        )
        
        formatter = ux_formatter_ar if language == "ar" else ux_formatter_en
        formatted_plan = formatter.format_treatment_plan(plan)
        
        await update.message.reply_text(formatted_plan, parse_mode=ParseMode.HTML)
```

---

## 🔐 Environment Variables

Add to `.env`:
```
BOT_TOKEN=your_telegram_bot_token
ANTHROPIC_API_KEY=your_anthropic_api_key
YOUTUBE_API_KEY=your_youtube_api_key
BOT_USERNAME=PhysioAssistBot
AMAZON_AFFILIATE_ID=your_affiliate_id
DB_PATH=/app/physioassist.db
```

---

## 📊 Database Schema Updates

Add to `database.py`:

```python
# New fields for subscription
user_schema = {
    "user_id": int,
    "language": str,
    "email": str,
    "subscription": {
        "tier": str,  # free, basic, premium, pro
        "active": bool,
        "start_date": str,
        "end_date": str,
        "assessments_this_month": int,
        "last_assessment_date": str,
    },
    "conversation_history": list,
    "patient_data": dict,
    "assessment": dict,
    "treatment_plan": dict,
}
```

---

## 🚀 Deployment

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py
```

### Railway Deployment
```bash
# Push to GitHub
git add .
git commit -m "Add PhysioAssist v7.0 with diagnostic engine"
git push

# Railway will auto-deploy
```

---

## 📈 Key Metrics to Track

1. **Conversion Rate** - Free to Paid users
2. **Retention Rate** - Users staying subscribed
3. **Assessment Completion Rate** - Users finishing assessments
4. **Paywall Hit Rate** - Users hitting paywall
5. **Upgrade Rate** - Users upgrading to higher tiers
6. **Daily Active Users (DAU)**
7. **Monthly Recurring Revenue (MRR)**

---

## 🔄 Workflow

### User Journey:

1. **User Starts** → Language Selection
2. **Chat Mode** → Free conversation to build trust
3. **Assessment** → Comprehensive assessment (free)
4. **Quick Win** → One free exercise for immediate relief
5. **Paywall** → Show full treatment plan (requires subscription)
6. **Subscribe** → User pays for full plan
7. **Treatment** → Full 8-week treatment plan
8. **Follow-up** → Daily follow-up and progress tracking

---

## 💡 Conversion Optimization Tips

1. **Build Trust First** - Free chat + free assessment
2. **Show Value** - Quick win exercise shows results
3. **Low Barrier** - $4.99 first month is low risk
4. **Clear Benefits** - Paywall clearly shows what's included
5. **Social Proof** - Show testimonials and success stories
6. **Scarcity** - Limited time offer ($4.99 first month only)
7. **Easy Upgrade** - One-click upgrade to higher tiers

---

## 🎯 Next Steps

1. ✅ Integrate diagnostic_engine.py
2. ✅ Integrate ux_formatter.py
3. ✅ Integrate subscription_system.py
4. ✅ Update bot.py with new handlers
5. ✅ Update database schema
6. ✅ Test all flows
7. ✅ Deploy to Railway
8. ✅ Monitor metrics
9. ✅ Iterate based on user feedback

---

## 📞 Support

For questions or issues, refer to:
- `diagnostic_engine.py` - Diagnostic logic
- `ux_formatter.py` - Formatting logic
- `subscription_system.py` - Subscription logic
- `PHYSIOASSIST_DOCUMENTATION.md` - Original documentation
