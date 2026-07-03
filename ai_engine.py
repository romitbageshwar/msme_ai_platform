"""
AI Engine for MSME Financial Health Platform
Handles document analysis, business health scoring, loan eligibility, chat, CSV processing, and PDF generation.
"""

import re
import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from fpdf import FPDF
import io
import base64
from datetime import datetime

class AIFinancialEngine:
    """Complete AI engine for MSME financial analysis"""

    def __init__(self):
        self.conversation_history = []
        self.business_data = {}
        self.health_cards = {}
        self.applications = []
        self.alerts = []

    # ---------- Helper to sanitize text for PDF ----------
    def _sanitize_text(self, text: str) -> str:
        """Remove emojis and non‑latin1 characters for PDF compatibility."""
        # Remove common emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text)
        # Replace common special characters
        replacements = {
            '→': '->',
            '✓': '[OK]',
            '⚠️': '[WARNING]',
            '✅': '[OK]',
            '📊': '[DATA]',
            '📈': '[GROWTH]',
            '💪': '[STRONG]',
            '💰': '[MONEY]',
            '🏢': '[BUSINESS]',
            '👥': '[TEAM]',
            '📱': '[DIGITAL]',
            '🚀': '[GROWTH]',
            '🎯': '[TARGET]',
            '🔍': '[SEARCH]',
            '🔔': '[ALERT]',
            '📑': '[REPORT]',
            '⚙️': '[SETTINGS]',
            '📄': '[DOCUMENT]',
            '💬': '[CHAT]',
            '🧠': '[AI]'
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        # Remove any remaining non‑latin1 characters
        text = text.encode('latin1', errors='ignore').decode('latin1')
        return text

    # ---------- Document Analysis (Text) ----------
    def analyze_documents(self, documents: Dict[str, str]) -> Dict:
        """Analyze multiple uploaded text documents (legacy)"""
        combined_metrics = {}
        all_insights = []
        confidence = 0.0
        num_docs = 0

        for doc_type, text in documents.items():
            if text:
                num_docs += 1
                metrics = self._extract_metrics_from_text(text)
                combined_metrics[doc_type] = metrics
                insights = self._generate_document_insights(metrics)
                all_insights.extend(insights)

        aggregated = self._aggregate_metrics(combined_metrics)
        confidence = min(98, 60 + num_docs * 8)
        summary = self._generate_consolidated_summary(aggregated, all_insights)
        health_card = self._generate_health_card(aggregated, all_insights, confidence)

        return {
            'metrics': aggregated,
            'insights': list(set(all_insights)),
            'confidence': confidence,
            'summary': summary,
            'health_card': health_card,
            'num_documents': num_docs
        }

    def _extract_metrics_from_text(self, text: str) -> Dict:
        return {
            'revenue': self._extract_revenue(text),
            'expenses': self._extract_expenses(text),
            'profit': self._extract_profit(text),
            'gst': self._extract_gst(text),
            'employees': self._extract_employees(text),
            'business_age': self._extract_business_age(text),
            'upi': self._extract_upi(text),
            'gst_filings': self._extract_gst_filings(text)
        }

    def _extract_revenue(self, text: str) -> Dict:
        patterns = {
            'annual': r'(?:annual|yearly).*?(?:revenue|turnover|sales).*?[₹₹]?\s*([\d,]+\.?\d*)\s*(?:lakh|crore|cr)',
            'monthly': r'(?:monthly).*?(?:revenue|turnover).*?[₹₹]?\s*([\d,]+\.?\d*)\s*(?:lakh|crore)',
            'growth': r'(?:growth|increase).*?(\d+\.?\d*)\s*%'
        }
        revenue = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                value = float(match.group(1).replace(',', ''))
                if 'lakh' in text.lower() or 'lac' in text.lower():
                    value = value * 100000
                elif 'crore' in text.lower() or 'cr' in text.lower():
                    value = value * 10000000
                revenue[key] = value
        return revenue

    def _extract_expenses(self, text: str) -> Dict:
        expenses = {}
        patterns = {
            'operational': r'(?:operational|operating).*?(?:expense|cost).*?[₹₹]?\s*([\d,]+\.?\d*)\s*(?:lakh|crore)',
            'staff': r'(?:staff|employee|salary|payroll).*?(?:cost|expense).*?[₹₹]?\s*([\d,]+\.?\d*)\s*(?:lakh|crore)',
            'rent': r'(?:rent|lease).*?[₹₹]?\s*([\d,]+\.?\d*)\s*(?:lakh|crore)'
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                value = float(match.group(1).replace(',', ''))
                if 'lakh' in text.lower() or 'lac' in text.lower():
                    value = value * 100000
                elif 'crore' in text.lower() or 'cr' in text.lower():
                    value = value * 10000000
                expenses[key] = value
        return expenses

    def _extract_profit(self, text: str) -> Dict:
        profit = {}
        patterns = {
            'net': r'(?:net|gross).*?profit.*?[₹₹]?\s*([\d,]+\.?\d*)\s*(?:lakh|crore)',
            'margin': r'(?:profit|margin).*?(\d+\.?\d*)\s*%'
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                if key == 'margin':
                    profit[key] = float(match.group(1))
                else:
                    value = float(match.group(1).replace(',', ''))
                    if 'lakh' in text.lower() or 'lac' in text.lower():
                        value = value * 100000
                    elif 'crore' in text.lower() or 'cr' in text.lower():
                        value = value * 10000000
                    profit[key] = value
        return profit

    def _extract_gst(self, text: str) -> Dict:
        gst = {}
        gst_pattern = r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}'
        gst_numbers = re.findall(gst_pattern, text)
        compliance = re.search(r'(?:regular|timely|on[- ]time).*?gst', text.lower())
        gst['has_gst'] = len(gst_numbers) > 0
        gst['compliance'] = 'good' if compliance else 'unknown'
        if gst_numbers:
            gst['number'] = gst_numbers[0]
        return gst

    def _extract_employees(self, text: str) -> int:
        patterns = [
            r'(\d+)\s*employees',
            r'(\d+)\s*staff',
            r'(\d+)\s*people\s*(?:work|employed)',
            r'workforce\s*(?:of|:)\s*(\d+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        return 0

    def _extract_business_age(self, text: str) -> int:
        patterns = [
            r'(\d+)\s*years?\s*(?:old|in business|established)',
            r'established\s*(?:in|since)\s*(\d{4})',
            r'incorporated\s*(?:in|since)\s*(\d{4})'
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                if len(match.group(1)) == 4:
                    return 2026 - int(match.group(1))
                else:
                    return int(match.group(1))
        return 0

    def _extract_upi(self, text: str) -> Dict:
        upi = {}
        patterns = {
            'transactions': r'(\d+)\s*(?:upi|digital|transaction|payment).*?(?:volume|count)',
            'amount': r'(?:upi|digital).*?(?:collections|receipts).*?[₹₹]?\s*([\d,]+\.?\d*)\s*(?:lakh|crore)'
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                if key == 'transactions':
                    upi[key] = int(match.group(1))
                else:
                    value = float(match.group(1).replace(',', ''))
                    if 'lakh' in text.lower() or 'lac' in text.lower():
                        value = value * 100000
                    elif 'crore' in text.lower() or 'cr' in text.lower():
                        value = value * 10000000
                    upi[key] = value
        return upi

    def _extract_gst_filings(self, text: str) -> Dict:
        filings = {}
        pattern = r'(\d+)\s*(?:gst|tax)\s*(?:returns|filings)'
        match = re.search(pattern, text.lower())
        if match:
            filings['count'] = int(match.group(1))
        return filings

    def _generate_document_insights(self, metrics: Dict) -> List[str]:
        insights = []
        revenue = metrics.get('revenue', {})
        profit = metrics.get('profit', {})
        gst = metrics.get('gst', {})
        employees = metrics.get('employees', 0)
        business_age = metrics.get('business_age', 0)
        upi = metrics.get('upi', {})

        if revenue:
            avg_rev = np.mean(list(revenue.values())) if revenue else 0
            if avg_rev > 10000000:
                insights.append(f"High revenue generation - ₹{avg_rev/10000000:.1f} Cr annual turnover")
            elif avg_rev > 1000000:
                insights.append(f"Healthy revenue base - ₹{avg_rev/100000:.1f} Lakh annual turnover")
            if 'growth' in revenue:
                insights.append(f"Revenue growing at {revenue['growth']:.1f}% year-over-year")

        if employees > 50:
            insights.append(f"Large workforce of {employees} employees - strong operational capacity")
        elif employees > 10:
            insights.append(f"Stable workforce of {employees} employees")

        if business_age > 10:
            insights.append("Established business with decade+ track record")
        elif business_age > 5:
            insights.append("Mature business with 5+ years of operations")

        if profit:
            if 'margin' in profit:
                if profit['margin'] > 20:
                    insights.append(f"Excellent profit margin of {profit['margin']:.1f}%")
                elif profit['margin'] > 10:
                    insights.append(f"Healthy profit margin of {profit['margin']:.1f}%")
                else:
                    insights.append(f"Profit margin at {profit['margin']:.1f}% - room for improvement")

        if gst.get('has_gst', False):
            if gst.get('compliance') == 'good':
                insights.append("GST-compliant with regular filings")
            else:
                insights.append("GST registered - check compliance status")

        if upi.get('transactions', 0) > 1000:
            insights.append(f"High digital adoption - {upi['transactions']} UPI transactions")

        if len(insights) >= 4:
            insights.append("Overall strong financial position with multiple positive indicators")
        elif len(insights) >= 2:
            insights.append("Moderate financial health with some positive indicators")
        else:
            insights.append("Limited financial data available - consider providing more documentation")
        return insights

    def _aggregate_metrics(self, combined_metrics: Dict) -> Dict:
        aggregated = {}
        for doc_type, metrics in combined_metrics.items():
            for key, value in metrics.items():
                if key not in aggregated:
                    aggregated[key] = value
                elif isinstance(value, dict) and not aggregated[key]:
                    aggregated[key] = value
                elif isinstance(value, (int, float)) and aggregated[key] == 0:
                    aggregated[key] = value
        return aggregated

    def _generate_consolidated_summary(self, aggregated: Dict, insights: List[str]) -> str:
        revenue = aggregated.get('revenue', {})
        employees = aggregated.get('employees', 0)
        business_age = aggregated.get('business_age', 0)
        parts = []
        if business_age > 0:
            parts.append(f"This business has been operating for {business_age} years")
        if revenue:
            avg_rev = np.mean(list(revenue.values())) if revenue else 0
            if avg_rev > 0:
                parts.append(f"with annual revenue of approximately ₹{avg_rev/100000:.1f} Lakh")
        if employees > 0:
            parts.append(f"and employs {employees} people")
        base = " ".join(parts) + "." if parts else "Business profile with limited financial data."
        if insights:
            base += f" Key highlights: {'; '.join(insights[:2])}."
        return base

    def _generate_health_card(self, aggregated: Dict, insights: List[str], confidence: float) -> Dict:
        revenue_score = self._calculate_revenue_score_from_metrics(aggregated.get('revenue', {}))
        cashflow_score = random.randint(65, 90)
        compliance_score = 85 if aggregated.get('gst', {}).get('compliance') == 'good' else 60
        stability_score = min(100, (aggregated.get('employees', 0) * 2) + (aggregated.get('business_age', 0) * 2))
        overall = (revenue_score * 0.35 + cashflow_score * 0.25 + compliance_score * 0.20 + stability_score * 0.20)

        risk_level = "Low" if overall >= 80 else "Medium" if overall >= 60 else "High"
        loan_suitability = self._calculate_loan_suitability(overall, [])

        return {
            'business_name': aggregated.get('business_name', 'Unknown MSME'),
            'overall_score': round(overall, 1),
            'dimensions': {
                'Revenue Health': round(revenue_score, 1),
                'Cash Flow Health': round(cashflow_score, 1),
                'Compliance Score': round(compliance_score, 1),
                'Business Stability': round(stability_score, 1)
            },
            'risk_level': risk_level,
            'insights': insights[:5],
            'loan_suitability': loan_suitability,
            'confidence': confidence
        }

    def _calculate_revenue_score_from_metrics(self, revenue_metrics: Dict) -> float:
        if not revenue_metrics:
            return 50.0
        annual = revenue_metrics.get('annual', 0)
        growth = revenue_metrics.get('growth', 0)
        base_score = 50
        if annual > 10000000:
            base_score += 20
        elif annual > 5000000:
            base_score += 10
        elif annual > 1000000:
            base_score += 5
        if growth > 15:
            base_score += 15
        elif growth > 5:
            base_score += 8
        return min(100, base_score)

    def _calculate_loan_suitability(self, score: float, risks: List[str]) -> Dict:
        if score >= 80 and len(risks) == 0:
            return {'level': 'High', 'max_amount': 5000000, 'interest': '10-12%'}
        elif score >= 70 and len(risks) <= 1:
            return {'level': 'Good', 'max_amount': 3500000, 'interest': '12-14%'}
        elif score >= 60 and len(risks) <= 2:
            return {'level': 'Moderate', 'max_amount': 2000000, 'interest': '14-16%'}
        else:
            return {'level': 'Low', 'max_amount': 500000, 'interest': '16-18%'}

    # ---------- CSV Document Processing ----------
    def process_csv_documents(self, csv_data: Dict[str, pd.DataFrame]) -> Dict:
        """Process multiple CSV files (GST, Bank, UPI, EPFO, etc.) and generate health card."""
        metrics = {}
        for source, df in csv_data.items():
            if df is not None and not df.empty:
                extracted = self._extract_metrics_from_csv(source, df)
                metrics[source] = extracted

        aggregated = self._aggregate_csv_metrics(metrics)
        revenue_score = self._calculate_revenue_score_from_csv(aggregated)
        cashflow_score = self._calculate_cashflow_score_from_csv(aggregated)
        compliance_score = self._calculate_compliance_score_from_csv(aggregated)
        stability_score = self._calculate_stability_score_from_csv(aggregated)

        overall = (revenue_score * 0.35 + cashflow_score * 0.25 +
                   compliance_score * 0.20 + stability_score * 0.20)

        risk_level = "Low" if overall >= 80 else "Medium" if overall >= 60 else "High"
        loan_suitability = self._calculate_loan_suitability(overall, [])
        insights = self._generate_csv_insights(aggregated, revenue_score, cashflow_score)

        health_card = {
            'overall_score': round(overall, 1),
            'dimensions': {
                'Revenue Health': round(revenue_score, 1),
                'Cash Flow Health': round(cashflow_score, 1),
                'Compliance Score': round(compliance_score, 1),
                'Business Stability': round(stability_score, 1)
            },
            'risk_level': risk_level,
            'loan_suitability': loan_suitability,
            'insights': insights,
            'confidence': 60 + len(csv_data) * 8
        }
        summary = self._generate_csv_summary(aggregated, insights)

        return {
            'metrics': aggregated,
            'insights': insights,
            'confidence': health_card['confidence'],
            'summary': summary,
            'health_card': health_card,
            'num_documents': len(csv_data)
        }

    def _extract_metrics_from_csv(self, source: str, df: pd.DataFrame) -> Dict:
        metrics = {}
        try:
            if source == 'gst':
                if 'turnover' in df.columns:
                    metrics['revenue_annual'] = df['turnover'].sum() / 12
                if 'filing_date' in df.columns:
                    metrics['gst_compliance'] = len(df)
                if 'tax_paid' in df.columns:
                    metrics['tax_paid'] = df['tax_paid'].sum()
            elif source == 'bank_statement':
                if 'amount' in df.columns and 'type' in df.columns:
                    credits = df[df['type'] == 'credit']['amount'].sum()
                    debits = df[df['type'] == 'debit']['amount'].sum()
                    metrics['total_credits'] = credits
                    metrics['total_debits'] = debits
                    metrics['cash_balance'] = credits - debits
            elif source == 'upi':
                if 'amount' in df.columns:
                    metrics['upi_volume'] = len(df)
                    metrics['upi_total'] = df['amount'].sum()
                if 'customer_id' in df.columns:
                    metrics['upi_customers'] = df['customer_id'].nunique()
            elif source == 'epfo':
                if 'employees' in df.columns:
                    metrics['employee_count'] = df['employees'].max()
                if 'salary_month' in df.columns:
                    metrics['payroll_consistency'] = len(df['salary_month'].unique())
            elif source == 'itr':
                if 'income' in df.columns:
                    metrics['itr_income'] = df['income'].sum()
                if 'expenses' in df.columns:
                    metrics['itr_expenses'] = df['expenses'].sum()
                if 'profit' in df.columns:
                    metrics['itr_profit'] = df['profit'].sum()
            elif source == 'utility':
                if 'bill_amount' in df.columns:
                    metrics['utility_spend'] = df['bill_amount'].sum()
                if 'payment_date' in df.columns and 'due_date' in df.columns:
                    on_time = (df['payment_date'] <= df['due_date']).sum()
                    metrics['utility_compliance'] = on_time / len(df) * 100
        except Exception as e:
            print(f"Error extracting from {source}: {e}")
        return metrics

    def _aggregate_csv_metrics(self, metrics: Dict) -> Dict:
        aggregated = {}
        for source, data in metrics.items():
            for key, value in data.items():
                if key in aggregated:
                    if isinstance(value, (int, float)):
                        if key in ['gst_compliance', 'payroll_consistency', 'utility_compliance']:
                            aggregated[key] = max(aggregated[key], value)
                        else:
                            aggregated[key] += value
                else:
                    aggregated[key] = value
        return aggregated

    def _calculate_revenue_score_from_csv(self, aggregated: Dict) -> float:
        revenue_sources = ['upi_total', 'total_credits', 'itr_income']
        total = sum(aggregated.get(k, 0) for k in revenue_sources)
        if total == 0:
            return 50.0
        score = min(100, (total / 5000000) * 100)
        return max(0, score)

    def _calculate_cashflow_score_from_csv(self, aggregated: Dict) -> float:
        credits = aggregated.get('total_credits', 0)
        debits = aggregated.get('total_debits', 0)
        if credits == 0:
            return 50.0
        ratio = credits / max(debits, 1)
        score = min(100, (ratio / 1.2) * 100)
        return max(0, score)

    def _calculate_compliance_score_from_csv(self, aggregated: Dict) -> float:
        gst_filings = aggregated.get('gst_compliance', 0)
        utility_compliance = aggregated.get('utility_compliance', 0)
        gst_score = min(100, (gst_filings / 12) * 100)
        util_score = utility_compliance
        return (gst_score * 0.7 + util_score * 0.3)

    def _calculate_stability_score_from_csv(self, aggregated: Dict) -> float:
        employees = aggregated.get('employee_count', 0)
        customers = aggregated.get('upi_customers', 0)
        emp_score = min(100, employees * 2)
        cust_score = min(100, customers / 20)
        return (emp_score * 0.5 + cust_score * 0.5)

    def _generate_csv_insights(self, aggregated: Dict, rev_score: float, cf_score: float) -> List[str]:
        insights = []
        if rev_score >= 80:
            insights.append("Strong revenue base from digital transactions")
        elif rev_score >= 60:
            insights.append("Moderate revenue – consider diversifying income sources")
        if cf_score >= 80:
            insights.append("Healthy cash flow with positive net balance")
        elif cf_score >= 60:
            insights.append("Cash flow is adequate but can be improved")
        if aggregated.get('gst_compliance', 0) >= 10:
            insights.append("Good GST compliance – regular filings")
        if aggregated.get('upi_customers', 0) > 100:
            insights.append("High digital customer engagement")
        if aggregated.get('employee_count', 0) > 20:
            insights.append("Substantial workforce – operational capacity")
        if len(insights) == 0:
            insights.append("Insufficient data for detailed insights – upload more CSVs")
        return insights

    def _generate_csv_summary(self, aggregated: Dict, insights: List[str]) -> str:
        total_rev = sum(aggregated.get(k, 0) for k in ['upi_total', 'total_credits', 'itr_income'])
        emp = aggregated.get('employee_count', 0)
        summary = f"Based on {len(aggregated)} data sources, the business has "
        if total_rev > 0:
            summary += f"total revenue of ₹{total_rev/100000:.1f} Lakh "
        if emp > 0:
            summary += f"with {emp} employees. "
        summary += "Financial health is "
        score = self._calculate_revenue_score_from_csv(aggregated)
        if score >= 80:
            summary += "strong with positive indicators."
        elif score >= 60:
            summary += "moderate – scope for improvement."
        else:
            summary += "needs attention – review expenses and revenue."
        return summary

    # ---------- PDF Generation (FIXED) ----------
    def generate_pdf_report(self, health_card: Dict, business_details: Dict) -> bytes:
        pdf = FPDF('P', 'mm', 'A4')
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'MSME Financial Health Report', 0, 1, 'C')
        pdf.ln(10)

        # Sanitize all text before adding to PDF
        name = self._sanitize_text(business_details.get('name', 'N/A'))
        gstin = self._sanitize_text(business_details.get('gstin', 'N/A'))
        industry = self._sanitize_text(business_details.get('industry', 'N/A'))

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, f"Business: {name}", 0, 1)
        pdf.cell(0, 8, f"GSTIN: {gstin}", 0, 1)
        pdf.cell(0, 8, f"Industry: {industry}", 0, 1)
        pdf.ln(5)

        # Health Score
        score = health_card['overall_score']
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f"Health Score: {score}/100", 0, 1)
        pdf.set_font('Arial', '', 12)
        risk = self._sanitize_text(health_card['risk_level'])
        pdf.cell(0, 8, f"Risk Level: {risk}", 0, 1)
        loan = health_card['loan_suitability']
        pdf.cell(0, 8, f"Loan Suitability: {loan['level']} (₹{loan['max_amount']/100000:.1f} Lakh)", 0, 1)
        pdf.ln(5)

        # Dimensions
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, "Performance Dimensions:", 0, 1)
        pdf.set_font('Arial', '', 11)
        for dim, score_val in health_card['dimensions'].items():
            dim_clean = self._sanitize_text(dim)
            pdf.cell(0, 7, f"  {dim_clean}: {score_val}/100", 0, 1)

        pdf.ln(5)

        # Insights
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, "AI Insights:", 0, 1)
        pdf.set_font('Arial', '', 11)
        for insight in health_card['insights']:
            clean_insight = self._sanitize_text(insight)
            pdf.multi_cell(0, 7, f"• {clean_insight}")

        pdf.ln(5)

        # Confidence
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 8, f"AI Confidence: {health_card['confidence']:.0f}%", 0, 1)

        # Generate PDF bytes
        try:
            # Using 'S' returns a string; we then encode to bytes.
            # After sanitization, all text is latin1-compatible.
            pdf_bytes = pdf.output(dest='S').encode('latin1')
        except UnicodeEncodeError:
            # Fallback: remove any remaining non-latin1 chars
            # (shouldn't happen, but just in case)
            pdf_str = pdf.output(dest='S')
            pdf_str = pdf_str.encode('ascii', errors='ignore').decode('ascii')
            pdf_bytes = pdf_str.encode('latin1')
        return pdf_bytes
        def generate_pdf_report(self, health_card: Dict, business_details: Dict) -> bytes:
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'MSME Financial Health Report', 0, 1, 'C')
    pdf.ln(10)

    # Sanitize all text before adding to PDF
    name = self._sanitize_text(business_details.get('name', 'N/A'))
    gstin = self._sanitize_text(business_details.get('gstin', 'N/A'))
    industry = self._sanitize_text(business_details.get('industry', 'N/A'))

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f"Business: {name}", 0, 1)
    pdf.cell(0, 8, f"GSTIN: {gstin}", 0, 1)
    pdf.cell(0, 8, f"Industry: {industry}", 0, 1)
    pdf.ln(5)

    # Health Score
    score = health_card['overall_score']
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f"Health Score: {score}/100", 0, 1)
    pdf.set_font('Arial', '', 12)
    risk = self._sanitize_text(health_card['risk_level'])
    pdf.cell(0, 8, f"Risk Level: {risk}", 0, 1)
    loan = health_card['loan_suitability']
    pdf.cell(0, 8, f"Loan Suitability: {loan['level']} (₹{loan['max_amount']/100000:.1f} Lakh)", 0, 1)
    pdf.ln(5)

    # Dimensions
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "Performance Dimensions:", 0, 1)
    pdf.set_font('Arial', '', 11)
    for dim, score_val in health_card['dimensions'].items():
        dim_clean = self._sanitize_text(dim)
        pdf.cell(0, 7, f"  {dim_clean}: {score_val}/100", 0, 1)

    pdf.ln(5)

    # Insights
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "AI Insights:", 0, 1)
    pdf.set_font('Arial', '', 11)
    for insight in health_card['insights']:
        clean_insight = self._sanitize_text(insight)
        pdf.multi_cell(0, 7, f"• {clean_insight}")

    pdf.ln(5)

    # Confidence
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 8, f"AI Confidence: {health_card['confidence']:.0f}%", 0, 1)

    # Generate PDF bytes safely
    try:
        pdf_bytes = pdf.output(dest='S').encode('latin1')
    except UnicodeEncodeError:
        # Fallback: strip any remaining non‑latin1 characters
        pdf_str = pdf.output(dest='S')
        pdf_str = pdf_str.encode('ascii', errors='ignore').decode('ascii')
        pdf_bytes = pdf_str.encode('latin1')
    return pdf_bytes

    # ---------- Business Health Analysis (for CSV uploads) ----------
    def generate_business_insights(self, business_data: Dict) -> Dict:
        revenue = business_data.get('revenue', [])
        cashflow = business_data.get('cashflow', [])
        gst_score = business_data.get('gst_score', 70)
        employees = business_data.get('employees', 5)

        revenue_score = self._calculate_revenue_score(revenue)
        cashflow_score = self._calculate_cashflow_score(cashflow)
        stability_score = self._calculate_stability_score(employees, len(revenue))
        overall = (revenue_score * 0.35 + cashflow_score * 0.35 +
                  stability_score * 0.20 + gst_score * 0.10)

        insights, risks, recommendations = [], [], []

        if revenue and len(revenue) > 1:
            growth = (revenue[-1] - revenue[0]) / revenue[0] * 100 if revenue[0] > 0 else 0
            if growth > 20:
                insights.append("Strong revenue growth trajectory")
                recommendations.append("Consider expanding operations to capitalize on growth")
            elif growth > 10:
                insights.append("Steady revenue growth")
            elif growth > 0:
                insights.append("Modest revenue growth")
                recommendations.append("Explore new markets to accelerate growth")
            else:
                risks.append("Revenue decline detected")
                recommendations.append("Review pricing strategy and customer acquisition")

        if cashflow and len(cashflow) > 1:
            if all(cf > 0 for cf in cashflow):
                insights.append("Consistent positive cashflow")
            elif any(cf < 0 for cf in cashflow):
                risks.append("Negative cashflow periods detected")
                recommendations.append("Improve working capital management")

        if employees > 20:
            insights.append("Established workforce - good operational capacity")
        elif employees > 5:
            insights.append("Growing team - positive sign")
        else:
            recommendations.append("Consider expanding workforce for growth")

        risk_level = "Low" if len(risks) == 0 else "Medium" if len(risks) <= 2 else "High"

        return {
            'overall_score': round(overall, 1),
            'risk_level': risk_level,
            'dimensions': {
                'Revenue Health': round(revenue_score, 1),
                'Cash Flow Health': round(cashflow_score, 1),
                'Business Stability': round(stability_score, 1),
                'GST Compliance': round(gst_score, 1)
            },
            'insights': insights,
            'risks': risks,
            'recommendations': recommendations,
            'loan_suitability': self._calculate_loan_suitability(overall, risks)
        }

    def _calculate_revenue_score(self, revenue: List[float]) -> float:
        if not revenue:
            return 50.0
        if len(revenue) < 2:
            return 60.0
        growth = [(revenue[i] - revenue[i-1]) / revenue[i-1] * 100
                 for i in range(1, len(revenue)) if revenue[i-1] > 0]
        if not growth:
            return 60.0
        avg_growth = np.mean(growth)
        base_score = 50 + min(avg_growth * 0.5, 40)
        return max(0, min(100, base_score))

    def _calculate_cashflow_score(self, cashflow: List[float]) -> float:
        if not cashflow:
            return 50.0
        positive = sum(1 for cf in cashflow if cf > 0) / len(cashflow)
        return positive * 80 + 20

    def _calculate_stability_score(self, employees: int, data_points: int) -> float:
        emp_score = min(100, employees * 2) if employees > 0 else 30
        data_score = min(100, data_points * 5)
        return (emp_score * 0.6 + data_score * 0.4)

    # ---------- AI Chat ----------
    def chat(self, message: str) -> str:
        self.conversation_history.append({"role": "user", "content": message})
        msg_lower = message.lower()
        if any(w in msg_lower for w in ['health', 'score', 'rating']):
            response = self._get_health_response()
        elif any(w in msg_lower for w in ['loan', 'credit', 'borrow']):
            response = self._get_loan_response()
        elif any(w in msg_lower for w in ['risk', 'danger', 'warning']):
            response = self._get_risk_response()
        elif any(w in msg_lower for w in ['improve', 'better', 'grow']):
            response = self._get_improvement_response()
        elif any(w in msg_lower for w in ['document', 'report', 'analysis']):
            response = self._get_document_response()
        else:
            response = self._get_general_response(message)
        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def _get_health_response(self) -> str:
        scores = {
            'Revenue Health': random.randint(70, 95),
            'Cash Flow': random.randint(65, 90),
            'Stability': random.randint(60, 85),
            'Compliance': random.randint(75, 95)
        }
        overall = np.mean(list(scores.values()))
        status = "Excellent" if overall > 85 else "Good" if overall > 75 else "Moderate"
        return f"""**Business Health Assessment**

Overall Score: **{overall:.0f}/100** - {status}

**Dimension Scores:**
• Revenue Health: {scores['Revenue Health']}/100
• Cash Flow: {scores['Cash Flow']}/100  
• Business Stability: {scores['Stability']}/100
• Compliance: {scores['Compliance']}/100

**AI Analysis:**
The business shows {'strong' if overall > 80 else 'stable' if overall > 70 else 'developing'} financial health with {'excellent' if overall > 85 else 'good' if overall > 75 else 'moderate'} growth indicators. Cash flow remains {'healthy' if scores['Cash Flow'] > 80 else 'stable'} and compliance is {'excellent' if scores['Compliance'] > 90 else 'good'}.

**Recommendation:** {'Consider expansion' if overall > 80 else 'Focus on cash flow optimization' if scores['Cash Flow'] < 75 else 'Maintain current trajectory'}. """

    def _get_loan_response(self) -> str:
        eligibility = random.choice(['High', 'Good', 'Moderate'])
        amount = random.randint(25, 75)
        return f"""**Loan Eligibility Assessment**

**Eligibility Status:** {eligibility}
**Estimated Amount:** ₹{amount} Lakh

**AI Recommendations:**
• Tenure: {random.choice(['24', '36', '48'])} months
• Interest Rate: {random.uniform(9.5, 14.5):.1f}% p.a.
• Best Product: {'Working Capital' if random.random() > 0.5 else 'Term Loan'}

**Confidence Level:** {random.randint(85, 98)}%

**Next Steps:**
1. Complete document verification
2. Review loan terms
3. Submit formal application

Would you like me to explain any specific loan product? """

    def _get_risk_response(self) -> str:
        risks = [
            ("Customer Concentration", random.choice(['Low', 'Moderate', 'High'])),
            ("Market Volatility", random.choice(['Low', 'Moderate', 'High'])),
            ("Working Capital", random.choice(['Adequate', 'Tight', 'Strained'])),
            ("Compliance", random.choice(['Compliant', 'Needs Attention', 'Risk']))
        ]
        response = "**Risk Assessment Report**\n\n**Identified Risks:**\n"
        for risk, level in risks:
            emoji = "[OK]" if level in ['Low', 'Adequate', 'Compliant'] else "[WARNING]" if level in ['Moderate', 'Tight', 'Needs Attention'] else "[CRITICAL]"
            response += f"\n• {emoji} {risk}: {level}"
        response += f"\n\n**AI Recommendations:**\n• Diversify customer base\n• Build cash reserves\n• Optimize inventory\n\n**Risk Score:** {random.randint(20, 80)}/100"
        return response

    def _get_improvement_response(self) -> str:
        return """**Growth & Improvement Plan**

**AI-Generated Recommendations:**

1. **Revenue Growth**
   • Explore new markets
   • Launch digital sales channels
   • Expand product portfolio

2. **Cash Flow Optimization**
   • Reduce payment cycles
   • Offer early payment discounts
   • Renegotiate supplier terms

3. **Risk Management**
   • Diversify customer base
   • Build emergency fund
   • Regular financial reviews

4. **Compliance**
   • Automate GST filings
   • Regular tax audits
   • Maintain digital records

**Estimated Impact:** 20-35% improvement in financial health

**Timeline:** 6-12 months

Shall I create a detailed action plan for any specific area? """

    def _get_document_response(self) -> str:
        return """**Document Analysis Summary**

**Extracted Information:**
• Business Type: Manufacturing
• Revenue: ₹42 Lakh (annual)
• Employees: 15
• Operating Since: 2018
• GST Compliant: Yes

**AI Analysis:**
The documents indicate a mature business with steady revenue growth and good compliance. Cash flow appears stable with positive working capital. Employee base suggests operational capacity for expansion.

**Missing Documents:**
• Last 3 years IT returns
• Detailed expense breakdown
• Future projections

**Recommendation:** Upload additional documents for a complete assessment."""

    def _get_general_response(self, message: str) -> str:
        responses = [
            "I can help you with financial analysis, loan eligibility, risk assessment, or business improvement. What would you like to explore?",
            "Based on the data, I see good potential for growth. Would you like me to analyze specific areas?",
            "I've analyzed your financial profile. The business shows positive indicators. What specific insights do you need?",
            "Let me help you understand your financial health better. Ask me about scores, loans, or risks.",
            "I can provide AI-powered insights on your business. What aspect interests you most?"
        ]
        return random.choice(responses)
