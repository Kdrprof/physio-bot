"""
Railway Monitor - Real-time error detection and reporting
Monitors Railway logs for errors and sends alerts
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('railway_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ErrorDetector:
    """Detect errors in logs"""
    
    # Error patterns to detect
    ERROR_PATTERNS = {
        'syntax_error': [
            'SyntaxError', 'IndentationError', 'TabError'
        ],
        'import_error': [
            'ImportError', 'ModuleNotFoundError', 'cannot import'
        ],
        'runtime_error': [
            'RuntimeError', 'Exception', 'Traceback'
        ],
        'api_error': [
            'APIError', 'ConnectionError', 'TimeoutError', 'HTTPError'
        ],
        'payment_error': [
            'PaymentError', 'TransactionError', 'InvoiceError'
        ],
        'database_error': [
            'DatabaseError', 'OperationalError', 'IntegrityError'
        ],
        'authentication_error': [
            'AuthenticationError', 'PermissionError', 'Unauthorized'
        ],
        'memory_error': [
            'MemoryError', 'OutOfMemory', 'heap space'
        ],
        'timeout_error': [
            'TimeoutError', 'Timeout', 'timed out'
        ]
    }
    
    # Warning patterns
    WARNING_PATTERNS = {
        'deprecation': ['DeprecationWarning', 'deprecated'],
        'performance': ['slow', 'performance', 'latency'],
        'resource': ['resource', 'limit', 'quota'],
        'retry': ['retry', 'retrying', 'attempt']
    }
    
    def __init__(self):
        self.errors_found = []
        self.warnings_found = []
        self.last_check = datetime.now()
    
    def detect_errors(self, log_text: str) -> Dict:
        """Detect errors in log text"""
        errors = []
        warnings = []
        
        lines = log_text.split('\n')
        
        for line in lines:
            # Check for errors
            for error_type, patterns in self.ERROR_PATTERNS.items():
                for pattern in patterns:
                    if pattern.lower() in line.lower():
                        errors.append({
                            'type': error_type,
                            'pattern': pattern,
                            'line': line.strip(),
                            'timestamp': datetime.now().isoformat()
                        })
            
            # Check for warnings
            for warning_type, patterns in self.WARNING_PATTERNS.items():
                for pattern in patterns:
                    if pattern.lower() in line.lower():
                        warnings.append({
                            'type': warning_type,
                            'pattern': pattern,
                            'line': line.strip(),
                            'timestamp': datetime.now().isoformat()
                        })
        
        return {
            'errors': errors,
            'warnings': warnings,
            'total_errors': len(errors),
            'total_warnings': len(warnings)
        }
    
    def categorize_severity(self, error: Dict) -> str:
        """Categorize error severity"""
        error_type = error.get('type', '')
        
        critical = ['syntax_error', 'import_error', 'memory_error']
        high = ['runtime_error', 'api_error', 'database_error']
        medium = ['authentication_error', 'timeout_error', 'payment_error']
        
        if error_type in critical:
            return 'CRITICAL'
        elif error_type in high:
            return 'HIGH'
        elif error_type in medium:
            return 'MEDIUM'
        else:
            return 'LOW'


class RailwayMonitor:
    """Monitor Railway deployment"""
    
    def __init__(self, project_name: str = 'physio-bot'):
        self.project_name = project_name
        self.detector = ErrorDetector()
        self.error_history = []
        self.check_interval = 60  # Check every 60 seconds
    
    def get_railway_logs(self) -> Optional[str]:
        """Get logs from Railway"""
        try:
            # Try using Railway CLI
            result = subprocess.run(
                ['railway', 'logs'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"Railway CLI error: {result.stderr}")
                return None
        
        except FileNotFoundError:
            logger.warning("Railway CLI not installed. Install with: npm install -g @railway/cli")
            return None
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return None
    
    def read_local_logs(self, log_file: str = 'railway_monitor.log') -> str:
        """Read local log file"""
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    return f.read()
            return ""
        except Exception as e:
            logger.error(f"Error reading local logs: {e}")
            return ""
    
    def generate_report(self, detection_result: Dict) -> str:
        """Generate error report"""
        report = []
        report.append("=" * 80)
        report.append("🔍 RAILWAY MONITORING REPORT")
        report.append("=" * 80)
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append(f"Project: {self.project_name}")
        report.append("")
        
        # Summary
        report.append("📊 SUMMARY:")
        report.append(f"Total Errors: {detection_result['total_errors']}")
        report.append(f"Total Warnings: {detection_result['total_warnings']}")
        report.append("")
        
        # Errors by severity
        if detection_result['errors']:
            report.append("❌ ERRORS DETECTED:")
            report.append("-" * 80)
            
            errors_by_severity = {}
            for error in detection_result['errors']:
                severity = self.detector.categorize_severity(error)
                if severity not in errors_by_severity:
                    errors_by_severity[severity] = []
                errors_by_severity[severity].append(error)
            
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                if severity in errors_by_severity:
                    report.append(f"\n🔴 {severity}:")
                    for error in errors_by_severity[severity]:
                        report.append(f"  Type: {error['type']}")
                        report.append(f"  Pattern: {error['pattern']}")
                        report.append(f"  Line: {error['line'][:100]}")
                        report.append("")
        
        # Warnings
        if detection_result['warnings']:
            report.append("\n⚠️ WARNINGS:")
            report.append("-" * 80)
            for warning in detection_result['warnings'][:10]:  # Show first 10
                report.append(f"  Type: {warning['type']}")
                report.append(f"  Pattern: {warning['pattern']}")
                report.append(f"  Line: {warning['line'][:100]}")
                report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    async def monitor_continuous(self, duration_minutes: int = 60):
        """Monitor continuously"""
        logger.info(f"Starting continuous monitoring for {duration_minutes} minutes...")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            try:
                # Get logs
                logs = self.get_railway_logs()
                
                if logs:
                    # Detect errors
                    detection_result = self.detector.detect_errors(logs)
                    
                    # Generate report
                    report = self.generate_report(detection_result)
                    
                    # Log report
                    logger.info(report)
                    
                    # Save report
                    self.save_report(report, detection_result)
                    
                    # Check for critical errors
                    if detection_result['total_errors'] > 0:
                        self.handle_errors(detection_result)
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
            
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
                await asyncio.sleep(self.check_interval)
        
        logger.info("Monitoring completed")
    
    def save_report(self, report: str, detection_result: Dict):
        """Save report to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save text report
            report_file = f"reports/monitor_report_{timestamp}.txt"
            os.makedirs("reports", exist_ok=True)
            
            with open(report_file, 'w') as f:
                f.write(report)
            
            # Save JSON report
            json_file = f"reports/monitor_report_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(detection_result, f, indent=2)
            
            logger.info(f"Reports saved: {report_file}, {json_file}")
        
        except Exception as e:
            logger.error(f"Error saving report: {e}")
    
    def handle_errors(self, detection_result: Dict):
        """Handle detected errors"""
        logger.error("ERRORS DETECTED!")
        
        # Count critical errors
        critical_errors = [e for e in detection_result['errors'] 
                          if self.detector.categorize_severity(e) == 'CRITICAL']
        
        if critical_errors:
            logger.critical(f"🚨 CRITICAL ERRORS FOUND: {len(critical_errors)}")
            for error in critical_errors:
                logger.critical(f"  - {error['type']}: {error['line'][:100]}")
        
        # Store in history
        self.error_history.append({
            'timestamp': datetime.now().isoformat(),
            'detection_result': detection_result
        })


class DashboardGenerator:
    """Generate monitoring dashboard"""
    
    def __init__(self):
        self.monitor = RailwayMonitor()
    
    def generate_html_dashboard(self, detection_result: Dict) -> str:
        """Generate HTML dashboard"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>PhysioAssist Bot - Monitoring Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }}
        .header {{ text-align: center; color: #333; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }}
        .card {{ background-color: #f9f9f9; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; }}
        .card.error {{ border-left-color: #dc3545; }}
        .card.warning {{ border-left-color: #ffc107; }}
        .card.success {{ border-left-color: #28a745; }}
        .number {{ font-size: 24px; font-weight: bold; }}
        .label {{ color: #666; font-size: 12px; }}
        .errors {{ margin-top: 20px; }}
        .error-item {{ background-color: #f8d7da; padding: 10px; margin: 5px 0; border-radius: 4px; border-left: 4px solid #dc3545; }}
        .warning-item {{ background-color: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 4px; border-left: 4px solid #ffc107; }}
        .timestamp {{ color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 PhysioAssist Bot - Monitoring Dashboard</h1>
            <p class="timestamp">Last Updated: {datetime.now().isoformat()}</p>
        </div>
        
        <div class="summary">
            <div class="card error">
                <div class="number">{detection_result['total_errors']}</div>
                <div class="label">ERRORS</div>
            </div>
            <div class="card warning">
                <div class="number">{detection_result['total_warnings']}</div>
                <div class="label">WARNINGS</div>
            </div>
            <div class="card success">
                <div class="number">✅</div>
                <div class="label">STATUS</div>
            </div>
            <div class="card">
                <div class="number">{datetime.now().strftime('%H:%M:%S')}</div>
                <div class="label">CURRENT TIME</div>
            </div>
        </div>
        
        <div class="errors">
            <h2>❌ Errors</h2>
            {''.join([f'<div class="error-item"><strong>{e["type"]}</strong>: {e["line"][:80]}</div>' for e in detection_result['errors'][:10]])}
        </div>
        
        <div class="warnings">
            <h2>⚠️ Warnings</h2>
            {''.join([f'<div class="warning-item"><strong>{w["type"]}</strong>: {w["line"][:80]}</div>' for w in detection_result['warnings'][:10]])}
        </div>
    </div>
</body>
</html>
        """
        return html


async def main():
    """Main monitoring function"""
    logger.info("🚀 Starting Railway Monitor...")
    
    monitor = RailwayMonitor()
    
    # Run continuous monitoring
    await monitor.monitor_continuous(duration_minutes=60)


if __name__ == '__main__':
    asyncio.run(main())
