# PhysioAssist Oracle v7.0 - Deployment Guide

## 🚀 Quick Start

### Step 1: Prepare Your Code

```bash
# Navigate to project directory
cd physio-bot

# Replace old bot.py with new version
mv bot.py bot_v6_backup.py
mv bot_v7_updated.py bot.py

# Update requirements.txt
mv requirements.txt requirements_v6_backup.txt
mv requirements_v7.txt requirements.txt

# Verify all files are present
ls -la *.py
```

**Files that should exist:**
```
bot.py                          ← Main bot (updated)
diagnostic_engine.py            ← New: Diagnostic system
ux_formatter.py                 ← New: UX formatting
subscription_system.py          ← New: Subscription system
database.py                     ← Existing: Database
pdf_gen.py                      ← Existing: PDF generation
youtube_api.py                  ← Existing: YouTube integration
clinical_tests.py               ← Existing: Clinical tests
prompts.py                      ← Existing: AI prompts
requirements.txt                ← Updated dependencies
```

### Step 2: Update GitHub

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "feat: PhysioAssist v7.0 - Diagnostic engine, UX formatter, subscription system

- Add diagnostic_engine.py with smart conversation & assessment
- Add ux_formatter.py with bilingual professional formatting
- Add subscription_system.py with Freemium strategy
- Update bot.py to integrate all new modules
- Implement 6-part treatment plan generation
- Add red flag detection
- Implement paywall strategy"

# Push to GitHub
git push origin main
```

### Step 3: Configure Railway

1. **Go to Railway.com**
2. **Connect your GitHub repository**
3. **Set Environment Variables**

```
BOT_TOKEN=your_telegram_bot_token
ANTHROPIC_API_KEY=your_anthropic_api_key
YOUTUBE_API_KEY=your_youtube_api_key
BOT_USERNAME=PhysioAssistBot
AMAZON_AFFILIATE_ID=your_affiliate_id
DB_PATH=/app/physioassist.db
```

4. **Railway will automatically:**
   - Install dependencies from requirements.txt
   - Run bot.py
   - Restart on crashes
   - Scale as needed

---

## 🔧 Environment Setup

### Get Required API Keys

#### 1. Telegram Bot Token
```
1. Open Telegram
2. Search for @BotFather
3. Send /newbot
4. Follow instructions
5. Copy the token
```

#### 2. Anthropic API Key
```
1. Go to console.anthropic.com
2. Sign up / Log in
3. Create new API key
4. Copy the key (starts with sk-ant-api03-)
```

#### 3. YouTube API Key
```
1. Go to Google Cloud Console
2. Create new project
3. Enable YouTube Data API v3
4. Create API key
5. Copy the key (starts with AIza)
```

#### 4. Amazon Affiliate ID
```
1. Join Amazon Associates
2. Get your Affiliate ID
3. Add to environment variables
```

---

## 📋 Pre-Deployment Checklist

- [ ] All new Python files copied to project
- [ ] requirements.txt updated
- [ ] bot.py replaced with bot_v7_updated.py
- [ ] All imports in bot.py are correct
- [ ] .env file has all required variables
- [ ] GitHub repository updated
- [ ] Railway environment variables set
- [ ] Bot token is valid
- [ ] API keys are valid
- [ ] Database path is correct

---

## 🧪 Testing Before Deployment

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BOT_TOKEN="your_token"
export ANTHROPIC_API_KEY="your_key"
export YOUTUBE_API_KEY="your_key"
export BOT_USERNAME="PhysioAssistBot"

# Run bot
python bot.py
```

### Test Flows

1. **Start Command**
   - `/start` → Language selection

2. **Language Selection**
   - Click English or Arabic
   - Should enter chat mode

3. **Chat Mode**
   - Send a message about pain
   - Bot should respond conversationally

4. **Assessment**
   - Click "Let's Go" button
   - Bot should ask questions

5. **Treatment Plan**
   - Complete assessment
   - Should see quick win exercise
   - Should see paywall for full plan

6. **Paywall**
   - Click "Subscribe"
   - Should show subscription options

---

## 🚨 Troubleshooting

### Bot Not Responding

**Problem:** Bot doesn't respond to messages

**Solution:**
```bash
# Check logs in Railway
# Verify BOT_TOKEN is correct
# Check if bot is running: /start command

# Restart bot in Railway dashboard
```

### API Key Errors

**Problem:** "Invalid API key" error

**Solution:**
```
1. Verify API key format
2. Check expiration date
3. Regenerate key if needed
4. Update in Railway environment
```

### Database Errors

**Problem:** "Database locked" or "No such table"

**Solution:**
```bash
# Delete old database
rm physioassist.db

# Bot will recreate on startup
# Check logs for initialization
```

### Memory Issues

**Problem:** Bot crashes with memory error

**Solution:**
```
1. Upgrade Railway plan
2. Optimize database queries
3. Clear old data
4. Monitor memory usage
```

---

## 📊 Monitoring

### Key Metrics to Monitor

```
1. Bot Response Time
   - Target: < 2 seconds

2. Error Rate
   - Target: < 0.1%

3. User Growth
   - Target: 20% monthly

4. Conversion Rate
   - Target: 5-10%

5. API Usage
   - Monitor Anthropic costs
   - Monitor YouTube API quota
```

### Logs

Check Railway logs for:
```
- Bot startup messages
- User interactions
- API errors
- Database operations
- Payment processing
```

---

## 🔄 Updates & Maintenance

### Regular Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Test locally
python bot.py

# Push to GitHub
git push origin main

# Railway auto-deploys
```

### Database Backups

```bash
# Download database from Railway
# Store in safe location
# Create weekly backups
```

### Version Control

```
v7.0 - Initial release with diagnostic engine
v7.1 - Bug fixes and improvements
v7.2 - Payment integration
v8.0 - Mobile app launch
```

---

## 💰 Cost Estimation

### Monthly Costs

| Service | Cost | Notes |
|---------|------|-------|
| Railway | $5-50 | Depends on usage |
| Anthropic API | $0.003-0.03/1K tokens | ~$50-200/month |
| YouTube API | Free | 10K quota/day |
| Telegram | Free | - |
| Domain | $10-15 | Optional |
| **Total** | **$65-265** | - |

### Revenue Projection

| Metric | Value | Revenue |
|--------|-------|---------|
| Users | 1,000 | - |
| Conversion Rate | 7.5% | - |
| Paid Users | 75 | - |
| Avg Subscription | $12/month | $900 |
| Affiliate Revenue | 20% of subs | $180 |
| **Total Monthly** | - | **$1,080** |

---

## 🎯 Success Metrics

### First Month Goals
- 100+ users
- 5-10 paid subscriptions
- 0 critical errors
- 4.5+ star rating

### First Quarter Goals
- 1,000+ users
- 100+ paid subscriptions
- $1,000+ MRR
- 4.7+ star rating

### First Year Goals
- 10,000+ users
- 1,000+ paid subscriptions
- $10,000+ MRR
- 4.8+ star rating

---

## 📞 Support

For deployment issues:
1. Check Railway logs
2. Review this guide
3. Check GitHub issues
4. Contact support team

---

## ✅ Post-Deployment

After successful deployment:

1. **Announce Launch**
   - Social media
   - Telegram channels
   - Health forums

2. **Monitor Metrics**
   - User growth
   - Conversion rate
   - Error rate

3. **Gather Feedback**
   - User reviews
   - Error reports
   - Feature requests

4. **Iterate**
   - Fix bugs
   - Add features
   - Optimize conversion

---

**Deployment Complete! 🎉**

Your PhysioAssist Oracle v7.0 is now live!
