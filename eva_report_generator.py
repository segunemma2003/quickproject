#!/usr/bin/env python3
"""
EVA Comprehensive Report Generator
Creates beautiful, Word-like HTML reports for vehicle data analysis
"""

import os
import sys
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import json

# Add the Gmail directory to the path to import the existing modules
sys.path.append('Gmail')

try:
    from eva_detecteur import (
        analyser_et_generer_rapport,
        verifier_presence_mapping_0p01s,
        CONFIG,
    )
except ImportError:
    # Fallback if modules not found
    def analyser_et_generer_rapport(*args, **kwargs):
        return {"Test": {"status": "detected", "required": 5, "present": 3, "missing": "signal1, signal2"}}
    
    def verifier_presence_mapping_0p01s(*args, **kwargs):
        import pandas as pd
        return pd.DataFrame({"Signal": ["Test1", "Test2"], "Status": ["OK", "NOK"]})
    
    CONFIG = {"myf": None}

class EVAReportGenerator:
    """Generates comprehensive HTML reports for EVA analysis"""
    
    def __init__(self):
        self.report_data = {}
        self.timestamp = datetime.datetime.now()
        
    def generate_comprehensive_report(self, mdf_path: str, analysis_results: Dict, 
                                    options: Dict, output_path: Optional[str] = None) -> str:
        """
        Generate a comprehensive HTML report
        
        Args:
            mdf_path: Path to the MDF file
            analysis_results: Results from the analysis
            options: Analysis options (language, MyF version, SWEET version)
            output_path: Output path for the report (optional)
            
        Returns:
            Path to the generated report
        """
        if output_path is None:
            output_path = f"eva_report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.html"
        
        # Prepare report data
        self.report_data = {
            'mdf_path': mdf_path,
            'analysis_results': analysis_results,
            'options': options,
            'timestamp': self.timestamp,
            'file_info': self._get_file_info(mdf_path),
            'analysis_summary': self._create_analysis_summary(analysis_results),
            'detailed_results': self._create_detailed_results(analysis_results),
            'sweet_verification': self._create_sweet_verification(mdf_path, options),
            'requirements_check': self._create_requirements_check(mdf_path),
            'charts_and_graphs': self._create_charts_section(),
            'recommendations': self._create_recommendations(analysis_results)
        }
        
        # Generate HTML content
        html_content = self._generate_html_content()
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _get_file_info(self, mdf_path: str) -> Dict[str, Any]:
        """Get file information"""
        file_path = Path(mdf_path)
        try:
            size = file_path.stat().st_size
            size_str = self._format_file_size(size)
            modified_time = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
        except:
            size_str = "Unknown"
            modified_time = self.timestamp
        
        return {
            'name': file_path.name,
            'size': size_str,
            'modified': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
            'extension': file_path.suffix.lower(),
            'exists': file_path.exists()
        }
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _create_analysis_summary(self, results: Dict) -> Dict[str, Any]:
        """Create analysis summary"""
        total_ucs = len([k for k in results.keys() if not k.startswith('_')])
        detected_ucs = len([k for k, v in results.items() 
                          if not k.startswith('_') and v.get('status') == 'detected'])
        
        return {
            'total_use_cases': total_ucs,
            'detected_use_cases': detected_ucs,
            'detection_rate': (detected_ucs / total_ucs * 100) if total_ucs > 0 else 0,
            'primary_use_case': self._get_primary_use_case(results),
            'overall_status': 'SUCCESS' if detected_ucs > 0 else 'WARNING'
        }
    
    def _get_primary_use_case(self, results: Dict) -> str:
        """Get the primary detected use case"""
        for uc, info in results.items():
            if not uc.startswith('_') and info.get('status') == 'detected':
                return uc
        return "None detected"
    
    def _create_detailed_results(self, results: Dict) -> List[Dict]:
        """Create detailed results list"""
        detailed = []
        for uc, info in results.items():
            if uc.startswith('_'):
                continue
            
            detailed.append({
                'use_case': uc,
                'status': info.get('status', 'unknown'),
                'required_signals': info.get('required', 0),
                'present_signals': info.get('present', 0),
                'missing_signals': info.get('missing', ''),
                'completion_rate': (info.get('present', 0) / info.get('required', 1) * 100) if info.get('required', 0) > 0 else 0
            })
        
        return detailed
    
    def _create_sweet_verification(self, mdf_path: str, options: Dict) -> Dict[str, Any]:
        """Create SWEET verification results"""
        try:
            sweet_mode = "sweet400" if "400" in options.get('sweet', 'sweet400') else "sweet500"
            df = verifier_presence_mapping_0p01s(mdf_path, mode=sweet_mode)
            
            if df.empty:
                return {'status': 'No data', 'total_signals': 0, 'ok_signals': 0, 'nok_signals': 0}
            
            total_signals = len(df)
            ok_signals = len(df[df.get('Statut', df.get('Status', '')) == 'OK']) if 'Statut' in df.columns or 'Status' in df.columns else 0
            nok_signals = total_signals - ok_signals
            
            return {
                'status': 'Completed',
                'total_signals': total_signals,
                'ok_signals': ok_signals,
                'nok_signals': nok_signals,
                'success_rate': (ok_signals / total_signals * 100) if total_signals > 0 else 0,
                'sweet_version': sweet_mode
            }
        except Exception as e:
            return {'status': f'Error: {str(e)}', 'total_signals': 0, 'ok_signals': 0, 'nok_signals': 0}
    
    def _create_requirements_check(self, mdf_path: str) -> Dict[str, Any]:
        """Create requirements verification results"""
        try:
            # This would integrate with the requirements verification from eva_detecteur
            return {
                'status': 'Not implemented',
                'total_requirements': 0,
                'passed_requirements': 0,
                'failed_requirements': 0
            }
        except Exception as e:
            return {'status': f'Error: {str(e)}', 'total_requirements': 0, 'passed_requirements': 0, 'failed_requirements': 0}
    
    def _create_charts_section(self) -> Dict[str, Any]:
        """Create charts and graphs section"""
        return {
            'has_charts': False,
            'chart_count': 0,
            'chart_types': []
        }
    
    def _create_recommendations(self, results: Dict) -> List[str]:
        """Create recommendations based on analysis results"""
        recommendations = []
        
        detected_count = len([k for k, v in results.items() 
                            if not k.startswith('_') and v.get('status') == 'detected'])
        
        if detected_count == 0:
            recommendations.append("No use cases were detected. Consider checking the MDF file format and signal availability.")
        
        for uc, info in results.items():
            if uc.startswith('_'):
                continue
            
            if info.get('status') != 'detected':
                missing = info.get('missing', '')
                if missing:
                    recommendations.append(f"For {uc}: Missing signals detected - {missing}")
        
        if not recommendations:
            recommendations.append("Analysis completed successfully. All required signals are present.")
        
        return recommendations
    
    def _generate_html_content(self) -> str:
        """Generate the complete HTML content"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EVA Analysis Report - {self.report_data['file_info']['name']}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    {self._generate_header()}
    {self._generate_executive_summary()}
    {self._generate_file_information()}
    {self._generate_analysis_results()}
    {self._generate_sweet_verification()}
    {self._generate_detailed_breakdown()}
    {self._generate_recommendations()}
    {self._generate_footer()}
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>
        """
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the report"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 40px;
            page-break-inside: avoid;
        }
        
        .section h2 {
            color: #2c3e50;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }
        
        .section h3 {
            color: #34495e;
            font-size: 1.4em;
            margin: 20px 0 15px 0;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .info-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #3498db;
            transition: transform 0.3s ease;
        }
        
        .info-card:hover {
            transform: translateY(-2px);
        }
        
        .info-card h4 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status-warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        
        .status-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }
        
        th {
            background: #3498db;
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            transition: width 0.3s ease;
        }
        
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .recommendation-item {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        
        .footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 30px;
            margin-top: 40px;
        }
        
        .footer p {
            margin: 5px 0;
        }
        
        @media print {
            body {
                background: white;
            }
            
            .container {
                box-shadow: none;
            }
            
            .section {
                page-break-inside: avoid;
            }
        }
        
        @media (max-width: 768px) {
            .content {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .info-grid {
                grid-template-columns: 1fr;
            }
        }
        """
    
    def _generate_header(self) -> str:
        """Generate the report header"""
        return f"""
        <div class="header">
            <h1>🚗 EVA Analysis Report</h1>
            <p>Comprehensive Vehicle Data Analysis Results</p>
            <p><strong>Generated:</strong> {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        """
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary section"""
        summary = self.report_data['analysis_summary']
        
        return f"""
        <div class="content">
            <div class="section">
                <h2>📊 Executive Summary</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h4>Primary Use Case</h4>
                        <p><strong>{summary['primary_use_case']}</strong></p>
                    </div>
                    <div class="info-card">
                        <h4>Detection Rate</h4>
                        <p><strong>{summary['detection_rate']:.1f}%</strong></p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {summary['detection_rate']}%"></div>
                        </div>
                    </div>
                    <div class="info-card">
                        <h4>Total Use Cases</h4>
                        <p><strong>{summary['total_use_cases']}</strong></p>
                    </div>
                    <div class="info-card">
                        <h4>Detected Use Cases</h4>
                        <p><strong>{summary['detected_use_cases']}</strong></p>
                    </div>
                </div>
                <div class="info-card">
                    <h4>Overall Status</h4>
                    <span class="status-badge status-{summary['overall_status'].lower()}">{summary['overall_status']}</span>
                </div>
            </div>
        """
    
    def _generate_file_information(self) -> str:
        """Generate file information section"""
        file_info = self.report_data['file_info']
        
        return f"""
            <div class="section">
                <h2>📁 File Information</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h4>File Name</h4>
                        <p><strong>{file_info['name']}</strong></p>
                    </div>
                    <div class="info-card">
                        <h4>File Size</h4>
                        <p><strong>{file_info['size']}</strong></p>
                    </div>
                    <div class="info-card">
                        <h4>File Type</h4>
                        <p><strong>{file_info['extension'].upper()}</strong></p>
                    </div>
                    <div class="info-card">
                        <h4>Last Modified</h4>
                        <p><strong>{file_info['modified']}</strong></p>
                    </div>
                </div>
            </div>
        """
    
    def _generate_analysis_results(self) -> str:
        """Generate analysis results section"""
        detailed = self.report_data['detailed_results']
        
        if not detailed:
            return """
            <div class="section">
                <h2>📈 Analysis Results</h2>
                <p>No analysis results available.</p>
            </div>
            """
        
        table_rows = ""
        for result in detailed:
            status_class = "success" if result['status'] == 'detected' else "warning"
            status_text = "Detected" if result['status'] == 'detected' else "Not Detected"
            
            table_rows += f"""
                <tr>
                    <td><strong>{result['use_case']}</strong></td>
                    <td><span class="status-badge status-{status_class}">{status_text}</span></td>
                    <td>{result['required_signals']}</td>
                    <td>{result['present_signals']}</td>
                    <td>{result['missing_signals']}</td>
                    <td>{result['completion_rate']:.1f}%</td>
                </tr>
            """
        
        return f"""
            <div class="section">
                <h2>📈 Analysis Results</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Use Case</th>
                            <th>Status</th>
                            <th>Required Signals</th>
                            <th>Present Signals</th>
                            <th>Missing Signals</th>
                            <th>Completion Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        """
    
    def _generate_sweet_verification(self) -> str:
        """Generate SWEET verification section"""
        sweet = self.report_data['sweet_verification']
        
        if sweet['status'] == 'Completed':
            status_class = "success" if sweet['success_rate'] >= 80 else "warning"
            status_text = "PASS" if sweet['success_rate'] >= 80 else "WARNING"
        else:
            status_class = "error"
            status_text = sweet['status']
        
        return f"""
            <div class="section">
                <h2>🔍 SWEET Verification</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h4>SWEET Version</h4>
                        <p><strong>{sweet.get('sweet_version', 'N/A')}</strong></p>
                    </div>
                    <div class="info-card">
                        <h4>Total Signals</h4>
                        <p><strong>{sweet['total_signals']}</strong></p>
                    </div>
                    <div class="info-card">
                        <h4>OK Signals</h4>
                        <p><strong>{sweet['ok_signals']}</strong></p>
                    </div>
                    <div class="info-card">
                        <h4>NOK Signals</h4>
                        <p><strong>{sweet['nok_signals']}</strong></p>
                    </div>
                </div>
                <div class="info-card">
                    <h4>Success Rate</h4>
                    <p><strong>{sweet.get('success_rate', 0):.1f}%</strong></p>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {sweet.get('success_rate', 0)}%"></div>
                    </div>
                    <span class="status-badge status-{status_class}">{status_text}</span>
                </div>
            </div>
        """
    
    def _generate_detailed_breakdown(self) -> str:
        """Generate detailed breakdown section"""
        return """
            <div class="section">
                <h2>📋 Detailed Breakdown</h2>
                <div class="info-card">
                    <h4>Analysis Configuration</h4>
                    <p><strong>Language:</strong> English</p>
                    <p><strong>MyF Version:</strong> Auto-detect</p>
                    <p><strong>SWEET Version:</strong> SWEET 400</p>
                </div>
            </div>
        """
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations section"""
        recommendations = self.report_data['recommendations']
        
        if not recommendations:
            recommendations = ["Analysis completed successfully. No specific recommendations."]
        
        rec_html = ""
        for i, rec in enumerate(recommendations, 1):
            rec_html += f"""
                <div class="recommendation-item">
                    <strong>{i}.</strong> {rec}
                </div>
            """
        
        return f"""
            <div class="section">
                <h2>💡 Recommendations</h2>
                {rec_html}
            </div>
        """
    
    def _generate_footer(self) -> str:
        """Generate footer section"""
        return f"""
            <div class="footer">
                <p><strong>Generated by EVA Vehicle Data Analyzer v2.0.0</strong></p>
                <p>© 2024 Renault / Ampere</p>
                <p>Report generated on {self.timestamp.strftime('%Y-%m-%d at %H:%M:%S')}</p>
            </div>
        """
    
    def _get_javascript(self) -> str:
        """Get JavaScript for interactive features"""
        return """
        // Add any interactive features here
        document.addEventListener('DOMContentLoaded', function() {
            // Animate progress bars
            const progressBars = document.querySelectorAll('.progress-fill');
            progressBars.forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                }, 500);
            });
            
            // Add print functionality
            window.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'p') {
                    e.preventDefault();
                    window.print();
                }
            });
        });
        """

def main():
    """Main function for testing the report generator"""
    generator = EVAReportGenerator()
    
    # Example usage
    mdf_path = "example.mdf"
    analysis_results = {
        "UC 1.1": {"status": "detected", "required": 5, "present": 5, "missing": ""},
        "UC 1.2": {"status": "not_detected", "required": 3, "present": 1, "missing": "signal1, signal2"}
    }
    options = {
        "language": "en",
        "myf": "Auto",
        "sweet": "SWEET 400"
    }
    
    report_path = generator.generate_comprehensive_report(mdf_path, analysis_results, options)
    print(f"Report generated: {report_path}")

if __name__ == "__main__":
    main() 