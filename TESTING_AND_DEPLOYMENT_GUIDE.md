# PhysioAssist Oracle v8.0 - Testing & Deployment Guide

## 📋 Overview

This guide explains how to test and deploy two versions of the PhysioAssist bot:
1. **Admin Mode** - Full access, no payment restrictions, debug enabled
2. **User Mode** - Regular user experience with working payment system

---

## 🔐 Admin Mode Testing

### What is Admin Mode?

Admin Mode is designed for **administrators and developers** to:
- ✅ Test all features without payment
- ✅ Debug issues with detailed error messages
- ✅ Access unlimited assessments
- ✅ Monitor system performance
- ✅ Identify and fix bugs

### File: `bot_admin_mode.py`

### How to Test Admin Mode

#### Step 1: Get Your Telegram ID

1. Open Telegram
2. Search for: `@userinfobot`
3. Send `/start`
4. Copy your **User ID** (e.g., 123456789)

#### Step 2: Configure Admin Access

Edit `bot_admin_mode.py` and find this line:

```python
ADMIN_IDS = [123456789]  # Replace with your Telegram ID
```

Replace `123456789` with your actual Telegram ID.

#### Step 3: Deploy Admin Bot

**Option A: Local Testing**

```bash
# Install dependencies
pip install python-telegram-bot anthropic

# Set environment variables
export BOT_TOKEN="your_bot_token_here"
export ANTHROPIC_API_KEY="your_anthropic_key_here"

# Run the bot
python bot_admin_mode.py
```

**Option B: Railway Deployment**

1. Create a new Railway project
2. Connect your GitHub repository
3. Set environment variables:
   - `BOT_TOKEN` - Your bot token
   - `ANTHROPIC_API_KEY` - Your Anthropic API key
4. Deploy `bot_admin_mode.py` as the main file

#### Step 4: Test Admin Features

1. Open Telegram
2. Search for your bot: `@YourBotUsername`
3. Send `/start`
4. You'll see: **ADMIN MODE** in the welcome message
5. Select language (English or Arabic)
6. Start a conversation

**What You'll See:**

```
🏥 **Welcome to PhysioAssist Oracle v8.0 - ADMIN MODE**

👤 Admin ID: 123456789
🔐 Mode: ADMIN
💎 Access: PREMIUM (UNLIMITED)
🐛 Debug: ENABLED
```

#### Step 5: Test Assessment Flow

1. Describe your symptoms
2. Continue the conversation (AI will ask questions)
3. After ~6 messages, you'll be asked about pain severity
4. Select severity level (Mild/Moderate/Severe)
5. You'll receive a complete treatment plan with:
   - Prevention tips
   - Home remedies
   - Exercise program
   - Warnings
   - Product recommendations
   - Medication suggestions

**Debug Info:**

Each response will include debug information:
```
🐛 **DEBUG INFO:**
Language: English
Stage: free_chat
Session ID: 123456789
```

#### Step 6: Identify Issues

The admin mode will show:
- ✅ All error messages
- ✅ API response times
- ✅ Token usage
- ✅ Session information
- ✅ Database queries

---

## 👤 User Mode Testing

### What is User Mode?

User Mode simulates the **regular user experience** with:
- 1 free assessment
- Payment system for upgrades
- Subscription management
- Feature restrictions based on plan

### File: `bot_user_mode.py`

### How to Test User Mode

#### Step 1: Deploy User Bot

**Option A: Local Testing**

```bash
# Install dependencies
pip install python-telegram-bot anthropic

# Set environment variables
export BOT_TOKEN="your_bot_token_here"
export ANTHROPIC_API_KEY="your_anthropic_key_here"
export PAYMENT_PROVIDER_TOKEN="test_provider"  # Use test token

# Run the bot
python bot_user_mode.py
```

**Option B: Railway Deployment**

1. Create a new Railway project
2. Connect your GitHub repository
3. Set environment variables:
   - `BOT_TOKEN` - Your bot token
   - `ANTHROPIC_API_KEY` - Your Anthropic API key
   - `PAYMENT_PROVIDER_TOKEN` - Payment provider token
4. Deploy `bot_user_mode.py` as the main file

#### Step 2: Test Free Assessment

1. Open Telegram
2. Search for your bot: `@YourBotUsername`
3. Send `/start`
4. Select language
5. Complete the conversation
6. Select pain severity
7. **Result:** You get a free treatment plan ✅

#### Step 3: Test Payment Flow

1. Send `/start` again
2. Go through the assessment again
3. When you reach severity selection:
   - **First assessment:** ✅ Free (allowed)
   - **Second assessment:** ❌ Payment required

4. You'll see payment options:

```
💳 **Upgrade Your Plan**

You've used your free assessment. Choose a plan to continue:

🔹 **Basic Plan** - $1.99/month
   • Unlimited assessments
   • Treatment plans
   • 1 month access

🔹 **Premium Plan** - $4.99/3 months
   • Everything in Basic
   • Priority support
   • 3 months access

🔹 **Pro Plan** - $9.99/year
   • Everything in Premium
   • Exclusive content
   • 1 year access
```

#### Step 4: Test Payment Processing

**For Testing (Sandbox Mode):**

Use Telegram's test payment system:
- Click on a payment button
- A test invoice will appear
- Click "Pay"
- Use test card: `4242 4242 4242 4242`
- Any future date for expiry
- Any 3-digit CVC

**Result:** Payment successful message ✅

#### Step 5: Verify Subscription

After payment:
```
✅ **Payment Successful!**

Thank you for upgrading to Basic Plan!
Valid until: 2026-06-02

Now you can:
• Get unlimited assessments
• Download full treatment plans
• Access all features
```

#### Step 6: Test Unlimited Access

1. Send `/start` again
2. Complete assessment multiple times
3. **Result:** No payment required ✅

---

## 🔧 Payment System Module

### File: `payment_system_fixed.py`

This module handles:
- Subscription management
- Payment processing
- Access control
- User status tracking

### Key Classes

#### 1. SubscriptionManager

```python
from payment_system_fixed import SubscriptionManager

manager = SubscriptionManager()

# Get user subscription
sub = manager.get_subscription(user_id)

# Create new subscription
manager.create_subscription(user_id, 'basic')

# Check if valid
is_valid = manager.is_subscription_valid(user_id)

# Get remaining days
days = manager.get_remaining_days(user_id)
```

#### 2. PaymentProcessor

```python
from payment_system_fixed import PaymentProcessor

processor = PaymentProcessor(provider_token)

# Create invoice
invoice = processor.create_invoice(user_id, 'basic')

# Process payment
transaction = processor.process_payment(user_id, 'basic', transaction_id)

# Verify payment
is_valid = processor.verify_payment(transaction_id)
```

#### 3. AccessControl

```python
from payment_system_fixed import AccessControl

access = AccessControl()

# Check assessment access
can_assess, message = access.can_perform_assessment(user_id)

# Check PDF download
can_download, message = access.can_download_pdf(user_id)

# Get user status
status = access.get_user_status(user_id)

# Format status message
msg = access.format_status_message(user_id, language='English')
```

---

## 🚀 Deployment Options

### Option 1: Railway.com (Recommended)

#### Step 1: Prepare Repository

```bash
cd /home/ubuntu/physio-bot
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "GitHub Repo"
4. Choose your `physio-bot` repository
5. Click "Deploy"

#### Step 3: Configure Environment

1. Go to "Variables"
2. Add these variables:
   - `BOT_TOKEN` - From BotFather
   - `ANTHROPIC_API_KEY` - From Anthropic
   - `PAYMENT_PROVIDER_TOKEN` - Payment provider token
   - `BOT_USERNAME` - Your bot username

#### Step 4: Set Startup Command

In Railway settings, set the start command:

**For Admin Mode:**
```
python bot_admin_mode.py
```

**For User Mode:**
```
python bot_user_mode.py
```

#### Step 5: Deploy

Click "Deploy" and Railway will automatically:
- Install dependencies
- Start the bot
- Keep it running 24/7

### Option 2: Local Server

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BOT_TOKEN="your_token"
export ANTHROPIC_API_KEY="your_key"

# Run the bot
python bot_admin_mode.py  # or bot_user_mode.py
```

### Option 3: Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot_admin_mode.py"]
```

Build and run:

```bash
docker build -t physio-bot .
docker run -e BOT_TOKEN="..." -e ANTHROPIC_API_KEY="..." physio-bot
```

---

## 📊 Testing Checklist

### Admin Mode Testing

- [ ] Bot starts without errors
- [ ] Welcome message shows "ADMIN MODE"
- [ ] Language selection works (English/Arabic)
- [ ] Free chat works with AI
- [ ] Assessment flow completes
- [ ] Treatment plan generates
- [ ] Debug info is displayed
- [ ] No payment prompts appear
- [ ] Multiple assessments allowed

### User Mode Testing

- [ ] Bot starts without errors
- [ ] Welcome message shows subscription status
- [ ] First assessment is free
- [ ] Second assessment requires payment
- [ ] Payment options display correctly
- [ ] Payment flow works
- [ ] Subscription is saved
- [ ] Unlimited access after payment
- [ ] Subscription expiry is tracked

### Payment System Testing

- [ ] Subscription creation works
- [ ] Payment processing works
- [ ] Access control enforces limits
- [ ] Subscription expiry is checked
- [ ] User status is accurate
- [ ] Transactions are logged

---

## 🐛 Troubleshooting

### Issue: Bot doesn't respond

**Solution:**
1. Check BOT_TOKEN is correct
2. Check internet connection
3. Check logs for errors
4. Restart the bot

### Issue: Payment not working

**Solution:**
1. Check PAYMENT_PROVIDER_TOKEN
2. Use test token for testing
3. Check payment logs
4. Verify payment provider account

### Issue: Assessment stuck

**Solution:**
1. Check AI API key
2. Check message format
3. Restart conversation with `/start`
4. Check logs for API errors

### Issue: Subscription not saved

**Solution:**
1. Check file permissions
2. Check disk space
3. Verify JSON format
4. Check error logs

---

## 📞 Support

For issues or questions:

1. Check logs: `docker logs container_id`
2. Review error messages
3. Check GitHub issues
4. Contact support

---

## 🎯 Next Steps

1. ✅ Test both bot versions
2. ✅ Verify payment system
3. ✅ Check error handling
4. ✅ Deploy to production
5. ✅ Monitor performance
6. ✅ Gather user feedback

---

**Version:** 8.0  
**Last Updated:** May 2, 2026  
**Status:** Ready for Testing
