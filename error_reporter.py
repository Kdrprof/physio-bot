"""
Error Reporter and Dashboard Generator
Collects, analyzes, and reports all bot errors
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error_reporter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ErrorCollector:
    """Collect errors from various sources"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info_logs = []
        self.error_dir = Path('error_logs')
        self.error_dir.mkdir(exist_ok=True)
    
    def collect_from_file(self, filepath: str) -> List[Dict]:
        """Collect errors from log file"""
        errors = []
        
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if 'ERROR' in line or 'CRITICAL' in line:
                    errors.append({
                        'type': 'ERROR',
                        'line_number': i + 1,
                        'content': line.strip(),
                        'source': filepath,
                        'timestamp': datetime.now().isoformat()
                    })
                elif 'WARNING' in line:
                    errors.append({
                        'type': 'WARNING',
                        'line_number': i + 1,
                        'content': line.strip(),
                        'source': filepath,
                        'timestamp': datetime.now().isoformat()
                    })
        
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {e}")
        
        return errors
    
    def collect_from_json(self, json_file: str) -> List[Dict]:
        """Collect errors from JSON report"""
        errors = []
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if 'details' in data:
                details = data['details']
                
                # Collect failed tests
                if 'failed' in details:
                    for failed_test in details['failed']:
                        errors.append({
                            'type': 'TEST_FAILURE',
                            'test_name': failed_test.get('name'),
                            'reason': failed_test.get('reason'),
                            'source': json_file,
                            'timestamp': datetime.now().isoformat()
                        })
                
                # Collect errors
                if 'errors' in details:
                    for error in details['errors']:
                        errors.append({
                            'type': 'ERROR',
                            'test_name': error.get('name'),
                            'error': error.get('error'),
                            'source': json_file,
                            'timestamp': datetime.now().isoformat()
                        })
        
        except Exception as e:
            logger.error(f"Error reading JSON {json_file}: {e}")
        
        return errors
    
    def collect_all(self) -> Dict:
        """Collect all errors from all sources"""
        all_errors = []
        
        # Collect from test reports
        for report_file in self.error_dir.glob('*.json'):
            all_errors.extend(self.collect_from_json(str(report_file)))
        
        # Collect from log files
        for log_file in self.error_dir.glob('*.log'):
            all_errors.extend(self.collect_from_file(str(log_file)))
        
        # Collect from main logs
        if os.path.exists('test_results.log'):
            all_errors.extend(self.collect_from_file('test_results.log'))
        
        if os.path.exists('railway_monitor.log'):
            all_errors.extend(self.collect_from_file('railway_monitor.log'))
        
        return {
            'total_errors': len(all_errors),
            'errors': all_errors,
            'collected_at': datetime.now().isoformat()
        }


class ErrorAnalyzer:
    """Analyze collected errors"""
    
    def __init__(self):
        self.collector = ErrorCollector()
    
    def analyze(self) -> Dict:
        """Analyze all errors"""
        collected = self.collector.collect_all()
        errors = collected['errors']
        
        analysis = {
            'total_errors': len(errors),
            'by_type': {},
            'by_source': {},
            'by_severity': {},
            'timeline': {},
            'top_errors': [],
            'recommendations': []
        }
        
        # Group by type
        for error in errors:
            error_type = error.get('type', 'UNKNOWN')
            if error_type not in analysis['by_type']:
                analysis['by_type'][error_type] = 0
            analysis['by_type'][error_type] += 1
        
        # Group by source
        for error in errors:
            source = error.get('source', 'UNKNOWN')
            if source not in analysis['by_source']:
                analysis['by_source'][source] = 0
            analysis['by_source'][source] += 1
        
        # Categorize by severity
        for error in errors:
            severity = self._categorize_severity(error)
            if severity not in analysis['by_severity']:
                analysis['by_severity'][severity] = 0
            analysis['by_severity'][severity] += 1
        
        # Get top errors
        error_counts = {}
        for error in errors:
            key = f"{error.get('type')} - {error.get('test_name', error.get('content', '')[:50])}"
            error_counts[key] = error_counts.get(key, 0) + 1
        
        analysis['top_errors'] = sorted(
            error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _categorize_severity(self, error: Dict) -> str:
        """Categorize error severity"""
        error_type = error.get('type', '')
        content = str(error.get('content', '') or error.get('error', '')).lower()
        
        critical_keywords = ['critical', 'crash', 'fatal', 'memory', 'syntax']
        high_keywords = ['error', 'failed', 'exception', 'timeout']
        medium_keywords = ['warning', 'deprecated', 'retry']
        
        for keyword in critical_keywords:
            if keyword in content or error_type == 'CRITICAL':
                return 'CRITICAL'
        
        for keyword in high_keywords:
            if keyword in content or error_type in ['ERROR', 'TEST_FAILURE']:
                return 'HIGH'
        
        for keyword in medium_keywords:
            if keyword in content:
                return 'MEDIUM'
        
        return 'LOW'
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Check for high error count
        if analysis['total_errors'] > 10:
            recommendations.append("⚠️ High error count detected. Review recent changes.")
        
        # Check for critical errors
        if analysis['by_severity'].get('CRITICAL', 0) > 0:
            recommendations.append("🚨 Critical errors found. Immediate action required!")
        
        # Check for specific error types
        if analysis['by_type'].get('SYNTAX_ERROR', 0) > 0:
            recommendations.append("📝 Syntax errors detected. Check code for typos.")
        
        if analysis['by_type'].get('IMPORT_ERROR', 0) > 0:
            recommendations.append("📦 Import errors found. Check dependencies.")
        
        if analysis['by_type'].get('API_ERROR', 0) > 0:
            recommendations.append("🔌 API errors detected. Check API keys and endpoints.")
        
        if analysis['by_type'].get('PAYMENT_ERROR', 0) > 0:
            recommendations.append("💳 Payment errors found. Check payment configuration.")
        
        if not recommendations:
            recommendations.append("✅ No critical issues detected.")
        
        return recommendations


class ReportGenerator:
    """Generate comprehensive error reports"""
    
    def __init__(self):
        self.analyzer = ErrorAnalyzer()
    
    def generate_text_report(self) -> str:
        """Generate text report"""
        analysis = self.analyzer.analyze()
        
        report = []
        report.append("=" * 80)
        report.append("📊 COMPREHENSIVE ERROR REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        # Summary
        report.append("📈 SUMMARY:")
        report.append(f"Total Errors: {analysis['total_errors']}")
        report.append(f"Critical: {analysis['by_severity'].get('CRITICAL', 0)}")
        report.append(f"High: {analysis['by_severity'].get('HIGH', 0)}")
        report.append(f"Medium: {analysis['by_severity'].get('MEDIUM', 0)}")
        report.append(f"Low: {analysis['by_severity'].get('LOW', 0)}")
        report.append("")
        
        # Errors by type
        report.append("📋 ERRORS BY TYPE:")
        for error_type, count in sorted(analysis['by_type'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {error_type}: {count}")
        report.append("")
        
        # Errors by source
        report.append("📂 ERRORS BY SOURCE:")
        for source, count in sorted(analysis['by_source'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {source}: {count}")
        report.append("")
        
        # Top errors
        report.append("🔝 TOP ERRORS:")
        for error_desc, count in analysis['top_errors']:
            report.append(f"  {error_desc}: {count} occurrences")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        for recommendation in analysis['recommendations']:
            report.append(f"  {recommendation}")
        report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def generate_json_report(self) -> Dict:
        """Generate JSON report"""
        analysis = self.analyzer.analyze()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'recommendations': analysis['recommendations']
        }
    
    def generate_html_report(self) -> str:
        """Generate HTML report"""
        analysis = self.analyzer.analyze()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>PhysioAssist Bot - Error Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary-card.critical {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .summary-card.high {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
        .summary-card.medium {{ background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }}
        .summary-card.low {{ background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333; }}
        .summary-card .number {{ font-size: 32px; font-weight: bold; }}
        .summary-card .label {{ font-size: 12px; opacity: 0.9; margin-top: 5px; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ color: #333; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #667eea; }}
        .error-item {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #f5576c; border-radius: 4px; }}
        .error-item.warning {{ border-left-color: #fee140; }}
        .error-item.info {{ border-left-color: #667eea; }}
        .recommendation {{ background: #e8f5e9; padding: 15px; margin: 10px 0; border-left: 4px solid #4caf50; border-radius: 4px; }}
        .recommendation.warning {{ background: #fff3e0; border-left-color: #ff9800; }}
        .recommendation.critical {{ background: #ffebee; border-left-color: #f44336; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f5f5f5; font-weight: 600; }}
        .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 PhysioAssist Bot - Error Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 Error Summary</h2>
                <div class="summary-grid">
                    <div class="summary-card critical">
                        <div class="number">{analysis['by_severity'].get('CRITICAL', 0)}</div>
                        <div class="label">CRITICAL</div>
                    </div>
                    <div class="summary-card high">
                        <div class="number">{analysis['by_severity'].get('HIGH', 0)}</div>
                        <div class="label">HIGH</div>
                    </div>
                    <div class="summary-card medium">
                        <div class="number">{analysis['by_severity'].get('MEDIUM', 0)}</div>
                        <div class="label">MEDIUM</div>
                    </div>
                    <div class="summary-card low">
                        <div class="number">{analysis['by_severity'].get('LOW', 0)}</div>
                        <div class="label">LOW</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>📈 Errors by Type</h2>
                <table>
                    <tr>
                        <th>Type</th>
                        <th>Count</th>
                    </tr>
                    {''.join([f'<tr><td>{t}</td><td>{c}</td></tr>' for t, c in sorted(analysis['by_type'].items(), key=lambda x: x[1], reverse=True)])}
                </table>
            </div>
            
            <div class="section">
                <h2>🔝 Top Errors</h2>
                {''.join([f'<div class="error-item">{err} <strong>({cnt})</strong></div>' for err, cnt in analysis['top_errors']])}
            </div>
            
            <div class="section">
                <h2>💡 Recommendations</h2>
                {''.join([f'<div class="recommendation">✓ {rec}</div>' for rec in analysis['recommendations']])}
            </div>
        </div>
        
        <div class="footer">
            <p>PhysioAssist Oracle v8.0 - Automated Error Reporting System</p>
        </div>
    </div>
</body>
</html>
        """
        return html
    
    def save_reports(self):
        """Save all reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save text report
        text_report = self.generate_text_report()
        with open(f'reports/error_report_{timestamp}.txt', 'w') as f:
            f.write(text_report)
        logger.info(f"Text report saved: reports/error_report_{timestamp}.txt")
        
        # Save JSON report
        json_report = self.generate_json_report()
        with open(f'reports/error_report_{timestamp}.json', 'w') as f:
            json.dump(json_report, f, indent=2)
        logger.info(f"JSON report saved: reports/error_report_{timestamp}.json")
        
        # Save HTML report
        html_report = self.generate_html_report()
        with open(f'reports/error_report_{timestamp}.html', 'w') as f:
            f.write(html_report)
        logger.info(f"HTML report saved: reports/error_report_{timestamp}.html")
        
        return text_report


if __name__ == '__main__':
    # Create reports directory
    os.makedirs('reports', exist_ok=True)
    
    # Generate reports
    generator = ReportGenerator()
    text_report = generator.save_reports()
    
    # Print text report
    print(text_report)
