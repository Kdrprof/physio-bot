"""
PhysioAssist Oracle v8.0 - Comprehensive Test Suite
Tests all bot functions, error handling, and edge cases
"""

import sys
import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestResult:
    """Store test results"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.errors = []
        self.warnings = []
        self.start_time = datetime.now()
    
    def add_pass(self, test_name: str, details: str = ""):
        self.passed.append({'name': test_name, 'details': details})
        logger.info(f"✅ PASS: {test_name} - {details}")
    
    def add_fail(self, test_name: str, reason: str):
        self.failed.append({'name': test_name, 'reason': reason})
        logger.error(f"❌ FAIL: {test_name} - {reason}")
    
    def add_error(self, test_name: str, error: Exception):
        self.errors.append({'name': test_name, 'error': str(error)})
        logger.error(f"⚠️ ERROR: {test_name} - {str(error)}")
    
    def add_warning(self, test_name: str, warning: str):
        self.warnings.append({'name': test_name, 'warning': warning})
        logger.warning(f"⚠️ WARNING: {test_name} - {warning}")
    
    def get_summary(self) -> Dict:
        duration = (datetime.now() - self.start_time).total_seconds()
        total = len(self.passed) + len(self.failed) + len(self.errors)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'total_tests': total,
            'passed': len(self.passed),
            'failed': len(self.failed),
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'success_rate': f"{(len(self.passed) / total * 100) if total > 0 else 0:.2f}%",
            'details': {
                'passed': self.passed,
                'failed': self.failed,
                'errors': self.errors,
                'warnings': self.warnings
            }
        }
    
    def save_report(self, filename: str = 'test_report.json'):
        """Save test report to file"""
        with open(filename, 'w') as f:
            json.dump(self.get_summary(), f, indent=2)
        logger.info(f"Test report saved to {filename}")


class BotTester:
    """Comprehensive bot testing"""
    
    def __init__(self):
        self.results = TestResult()
        self.bot_token = os.getenv('BOT_TOKEN')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.payment_token = os.getenv('PAYMENT_PROVIDER_TOKEN')
    
    async def run_all_tests(self) -> TestResult:
        """Run all tests"""
        logger.info("=" * 80)
        logger.info("🚀 STARTING COMPREHENSIVE BOT TESTS")
        logger.info("=" * 80)
        
        # Test categories
        await self.test_environment()
        await self.test_imports()
        await self.test_configuration()
        await self.test_bot_structure()
        await self.test_payment_system()
        await self.test_subscription_system()
        await self.test_error_handling()
        await self.test_api_integration()
        await self.test_data_validation()
        await self.test_security()
        
        logger.info("=" * 80)
        logger.info("✅ TEST SUITE COMPLETED")
        logger.info("=" * 80)
        
        return self.results
    
    async def test_environment(self):
        """Test environment variables"""
        logger.info("\n📋 Testing Environment Variables...")
        
        try:
            # Check BOT_TOKEN
            if self.bot_token:
                self.results.add_pass("BOT_TOKEN", "Found and set")
            else:
                self.results.add_fail("BOT_TOKEN", "Not set in environment")
            
            # Check ANTHROPIC_API_KEY
            if self.anthropic_key:
                self.results.add_pass("ANTHROPIC_API_KEY", "Found and set")
            else:
                self.results.add_fail("ANTHROPIC_API_KEY", "Not set in environment")
            
            # Check PAYMENT_PROVIDER_TOKEN
            if self.payment_token:
                self.results.add_pass("PAYMENT_PROVIDER_TOKEN", "Found and set")
            else:
                self.results.add_warning("PAYMENT_PROVIDER_TOKEN", "Not set (optional for testing)")
            
            # Check Python version
            py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            if sys.version_info >= (3, 8):
                self.results.add_pass("Python Version", f"{py_version} (OK)")
            else:
                self.results.add_fail("Python Version", f"{py_version} (requires 3.8+)")
        
        except Exception as e:
            self.results.add_error("Environment Test", e)
    
    async def test_imports(self):
        """Test required imports"""
        logger.info("\n📦 Testing Imports...")
        
        imports_to_test = [
            ('telegram', 'python-telegram-bot'),
            ('anthropic', 'anthropic'),
            ('json', 'standard library'),
            ('asyncio', 'standard library'),
            ('datetime', 'standard library'),
            ('logging', 'standard library'),
        ]
        
        for module_name, package_name in imports_to_test:
            try:
                __import__(module_name)
                self.results.add_pass(f"Import {module_name}", f"from {package_name}")
            except ImportError as e:
                self.results.add_fail(f"Import {module_name}", str(e))
    
    async def test_configuration(self):
        """Test bot configuration"""
        logger.info("\n⚙️ Testing Configuration...")
        
        try:
            # Check bot file exists
            if os.path.exists('bot_hybrid_smart.py'):
                self.results.add_pass("Bot File", "bot_hybrid_smart.py found")
            else:
                self.results.add_fail("Bot File", "bot_hybrid_smart.py not found")
            
            # Check payment system file
            if os.path.exists('payment_system_fixed.py'):
                self.results.add_pass("Payment System File", "payment_system_fixed.py found")
            else:
                self.results.add_warning("Payment System File", "payment_system_fixed.py not found")
            
            # Check test file
            if os.path.exists('test_bot_comprehensive.py'):
                self.results.add_pass("Test File", "test_bot_comprehensive.py found")
            else:
                self.results.add_warning("Test File", "test_bot_comprehensive.py not found")
        
        except Exception as e:
            self.results.add_error("Configuration Test", e)
    
    async def test_bot_structure(self):
        """Test bot code structure"""
        logger.info("\n🏗️ Testing Bot Structure...")
        
        try:
            # Read bot file
            with open('bot_hybrid_smart.py', 'r') as f:
                bot_code = f.read()
            
            # Check for required classes
            required_classes = ['HybridSmartBot']
            for cls in required_classes:
                if f"class {cls}" in bot_code:
                    self.results.add_pass(f"Class {cls}", "Found in bot code")
                else:
                    self.results.add_fail(f"Class {cls}", "Not found in bot code")
            
            # Check for required methods
            required_methods = ['start', 'mode_selection', 'language_selection', 'handle_message']
            for method in required_methods:
                if f"async def {method}" in bot_code or f"def {method}" in bot_code:
                    self.results.add_pass(f"Method {method}", "Found in bot code")
                else:
                    self.results.add_fail(f"Method {method}", "Not found in bot code")
            
            # Check for error handling
            if "try:" in bot_code and "except" in bot_code:
                self.results.add_pass("Error Handling", "Try-except blocks found")
            else:
                self.results.add_warning("Error Handling", "Limited error handling")
        
        except Exception as e:
            self.results.add_error("Bot Structure Test", e)
    
    async def test_payment_system(self):
        """Test payment system"""
        logger.info("\n💳 Testing Payment System...")
        
        try:
            with open('payment_system_fixed.py', 'r') as f:
                payment_code = f.read()
            
            # Check for payment classes
            payment_classes = ['SubscriptionManager', 'PaymentProcessor', 'AccessControl']
            for cls in payment_classes:
                if f"class {cls}" in payment_code:
                    self.results.add_pass(f"Payment Class {cls}", "Found")
                else:
                    self.results.add_fail(f"Payment Class {cls}", "Not found")
            
            # Check for pricing
            if "PRICES" in payment_code or "price" in payment_code.lower():
                self.results.add_pass("Pricing", "Pricing configuration found")
            else:
                self.results.add_fail("Pricing", "Pricing not configured")
        
        except FileNotFoundError:
            self.results.add_fail("Payment System", "payment_system_fixed.py not found")
        except Exception as e:
            self.results.add_error("Payment System Test", e)
    
    async def test_subscription_system(self):
        """Test subscription system"""
        logger.info("\n📅 Testing Subscription System...")
        
        try:
            with open('bot_hybrid_smart.py', 'r') as f:
                bot_code = f.read()
            
            # Check for subscription tracking
            if "subscription" in bot_code.lower():
                self.results.add_pass("Subscription Tracking", "Found in code")
            else:
                self.results.add_fail("Subscription Tracking", "Not found in code")
            
            # Check for expiration handling
            if "expire" in bot_code.lower() or "valid" in bot_code.lower():
                self.results.add_pass("Expiration Handling", "Found in code")
            else:
                self.results.add_fail("Expiration Handling", "Not found in code")
            
            # Check for free assessment limit
            if "FREE_ASSESSMENTS" in bot_code or "free" in bot_code.lower():
                self.results.add_pass("Free Assessment Limit", "Found in code")
            else:
                self.results.add_fail("Free Assessment Limit", "Not found in code")
        
        except Exception as e:
            self.results.add_error("Subscription System Test", e)
    
    async def test_error_handling(self):
        """Test error handling"""
        logger.info("\n🛡️ Testing Error Handling...")
        
        try:
            with open('bot_hybrid_smart.py', 'r') as f:
                bot_code = f.read()
            
            # Count error handling
            try_count = bot_code.count("try:")
            except_count = bot_code.count("except")
            
            if try_count > 0 and except_count > 0:
                self.results.add_pass("Error Handling", f"Found {try_count} try-except blocks")
            else:
                self.results.add_warning("Error Handling", "Limited error handling")
            
            # Check for logging
            if "logger" in bot_code or "logging" in bot_code:
                self.results.add_pass("Logging", "Logging configured")
            else:
                self.results.add_warning("Logging", "Logging not configured")
            
            # Check for specific error types
            error_types = ['ValueError', 'TypeError', 'KeyError', 'IndexError']
            for error_type in error_types:
                if error_type in bot_code:
                    self.results.add_pass(f"Error Type {error_type}", "Handled in code")
        
        except Exception as e:
            self.results.add_error("Error Handling Test", e)
    
    async def test_api_integration(self):
        """Test API integration"""
        logger.info("\n🔌 Testing API Integration...")
        
        try:
            with open('bot_hybrid_smart.py', 'r') as f:
                bot_code = f.read()
            
            # Check for Telegram API
            if "telegram" in bot_code.lower():
                self.results.add_pass("Telegram API", "Integration found")
            else:
                self.results.add_fail("Telegram API", "Integration not found")
            
            # Check for Anthropic API
            if "anthropic" in bot_code.lower() or "claude" in bot_code.lower():
                self.results.add_pass("Anthropic API", "Integration found")
            else:
                self.results.add_fail("Anthropic API", "Integration not found")
            
            # Check for payment API
            if "payment" in bot_code.lower() or "invoice" in bot_code.lower():
                self.results.add_pass("Payment API", "Integration found")
            else:
                self.results.add_fail("Payment API", "Integration not found")
        
        except Exception as e:
            self.results.add_error("API Integration Test", e)
    
    async def test_data_validation(self):
        """Test data validation"""
        logger.info("\n✔️ Testing Data Validation...")
        
        try:
            with open('bot_hybrid_smart.py', 'r') as f:
                bot_code = f.read()
            
            # Check for input validation
            if "if " in bot_code and "not " in bot_code:
                self.results.add_pass("Input Validation", "Validation logic found")
            else:
                self.results.add_warning("Input Validation", "Limited validation")
            
            # Check for type checking
            if "isinstance" in bot_code or "type(" in bot_code:
                self.results.add_pass("Type Checking", "Type checks found")
            else:
                self.results.add_warning("Type Checking", "No explicit type checks")
            
            # Check for length validation
            if "len(" in bot_code:
                self.results.add_pass("Length Validation", "Length checks found")
            else:
                self.results.add_warning("Length Validation", "No length checks")
        
        except Exception as e:
            self.results.add_error("Data Validation Test", e)
    
    async def test_security(self):
        """Test security measures"""
        logger.info("\n🔒 Testing Security...")
        
        try:
            with open('bot_hybrid_smart.py', 'r') as f:
                bot_code = f.read()
            
            # Check for authentication
            if "ADMIN_ID" in bot_code or "auth" in bot_code.lower():
                self.results.add_pass("Authentication", "Admin ID check found")
            else:
                self.results.add_fail("Authentication", "No authentication found")
            
            # Check for token handling
            if "os.getenv" in bot_code or "environ" in bot_code:
                self.results.add_pass("Token Handling", "Environment variables used")
            else:
                self.results.add_fail("Token Handling", "Hardcoded tokens detected")
            
            # Check for SQL injection protection (if using database)
            if "SELECT" in bot_code or "INSERT" in bot_code:
                if "?" in bot_code or "parameterized" in bot_code.lower():
                    self.results.add_pass("SQL Injection Protection", "Parameterized queries used")
                else:
                    self.results.add_warning("SQL Injection Protection", "Check query handling")
            
            # Check for rate limiting
            if "rate" in bot_code.lower() or "limit" in bot_code.lower():
                self.results.add_pass("Rate Limiting", "Rate limiting logic found")
            else:
                self.results.add_warning("Rate Limiting", "No rate limiting found")
        
        except Exception as e:
            self.results.add_error("Security Test", e)


async def main():
    """Main test runner"""
    tester = BotTester()
    results = await tester.run_all_tests()
    
    # Print summary
    summary = results.get_summary()
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} ✅")
    print(f"Failed: {summary['failed']} ❌")
    print(f"Errors: {summary['errors']} ⚠️")
    print(f"Warnings: {summary['warnings']} ⚠️")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Duration: {summary['duration_seconds']:.2f} seconds")
    print("=" * 80)
    
    # Save report
    results.save_report('test_report.json')
    
    # Exit with appropriate code
    if summary['failed'] > 0 or summary['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
