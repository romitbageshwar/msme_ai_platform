"""
AI-Powered MSME Financial Health Platform
Complete prototype with all features from the PRD.
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import re
import random
from typing import Dict, List, Any, Optional

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="AI MSME Financial Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
    .stApp { background: #f0f4f8; }
    .ai-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .insight-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid;
        margin: 0.7rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .insight-positive { border-left-color: #00b894; }
    .insight-warning { border-left-color: #fdcb6e; }
    .insight-critical { border-left-color: #e17055; }
    .chat-container {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        height: 400px;
        overflow-y: auto;
        margin-bottom: 1rem;
        border: 1px solid #e8edf5;
    }
    .message {
        padding: 0.8rem 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .user-msg { background: #e3f2fd; margin-left: auto; border: 1px solid #bbdefb; }
    .ai-msg { background: #f5f5f5; border: 1px solid #e0e0e0; }
    .dimension-bar {
        height: 8px;
        border-radius: 4px;
        background: #e8edf5;
        margin: 4px 0;
    }
    .dimension-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 1s ease;
    }
    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
        background: linear-gradient(135deg, #00b894, #00cec9);
    }
    .floating-chat {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 50px;
        border: none;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        cursor: pointer;
        z-index: 1000;
        font-weight: 600;
    }
    .floating-chat:hover { transform: scale(1.05); transition: 0.2s; }
    .status-badge {
        padding: 0.2rem 1rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-excellent { background: #d4edda; color: #155724; }
    .badge-good { background: #cce5ff; color: #004085; }
    .badge-moderate { background: #fff3cd; color: #856404; }
    .badge-poor { background: #f8d7da; color: #721c24; }
    .upload-area {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #fafbfc;
    }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #2d3748; }
    .data-source-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        margin: 0.15rem;
        background: #e8edf5;
    }
    .data-source-tag.active { background: #d4edda; color: #155724; }
    .data-source-tag.inactive { background: #f8d7da; color: #721c24; }
    .application-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #e8edf5;
    }
    .application-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        text-align: center;
    }
    .health-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e8edf5;
        margin: 1rem 0;
    }
    .trend-up { color: #00b894; }
    .trend-down { color: #e17055; }
    .trend-stable { color: #fdcb6e; }
    .risk-low { color: #00b894; }
    .risk-medium { color: #fdcb6e; }
    .risk-high { color: #e17055; }
    .status-approved { background: #d4edda; color: #155724; }
    .status-pending { background: #fff3cd; color: #856404; }
    .status-rejected { background: #f8d7da; color: #721c24; }
    .status-review { background: #cce5ff; color: #004085; }
</style>
""", unsafe_allow_html=True)

# ------------------ AI ENGINE ------------------
class AIFinancialEngine:
    """Complete AI engine for MSME financial analysis"""
    
    def __init__(self):
        self.conversation_history = []
        self.business_data = {}
        self.health_cards = {}
        self.applications = []
        self.alerts = []
    
    # ---------- Document Analysis ----------
    def analyze_document(self, text: str) -> Dict:
        """Extract and analyze financial information from text"""
        metrics = {
            'revenue': self._extract_revenue(text),
            'expenses': self._extract_expenses(text),
            'profit': self._extract_profit(text),
            'gst': self._extract_gst(text),
            'employees': self._extract_employees(text),
            'business_age': self._extract_business_age(text),
            'upi': self._extract_upi(text),
            'gst_filings': self._extract_gst_filings(text)
        }
        insights = self._generate_document_insights(metrics)
        return {
            'metrics': metrics,
            'insights': insights,
            'confidence': random.uniform(85, 98),
            'summary': self._generate_summary(metrics, insights)
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
        expenses = metrics.get('expenses', {})
        profit = metrics.get('profit', {})
        gst = metrics.get('gst', {})
        employees = metrics.get('employees', 0)
        business_age = metrics.get('business_age', 0)
        upi = metrics.get('upi', {})
        
        if revenue:
            avg_rev = np.mean(list(revenue.values())) if revenue else 0
            if avg_rev > 10000000:
                insights.append(f"📊 High revenue generation - ₹{avg_rev/10000000:.1f} Cr annual turnover")
            elif avg_rev > 1000000:
                insights.append(f"📊 Healthy revenue base - ₹{avg_rev/100000:.1f} Lakh annual turnover")
            if 'growth' in revenue:
                insights.append(f"📈 Revenue growing at {revenue['growth']:.1f}% year-over-year")
        
        if employees > 50:
            insights.append(f"👥 Large workforce of {employees} employees - strong operational capacity")
        elif employees > 10:
            insights.append(f"👥 Stable workforce of {employees} employees")
        
        if business_age > 10:
            insights.append("🏢 Established business with decade+ track record")
        elif business_age > 5:
            insights.append("🏢 Mature business with 5+ years of operations")
        
        if profit:
            if 'margin' in profit:
                if profit['margin'] > 20:
                    insights.append(f"💰 Excellent profit margin of {profit['margin']:.1f}%")
                elif profit['margin'] > 10:
                    insights.append(f"💰 Healthy profit margin of {profit['margin']:.1f}%")
                else:
                    insights.append(f"📊 Profit margin at {profit['margin']:.1f}% - room for improvement")
        
        if gst.get('has_gst', False):
            if gst.get('compliance') == 'good':
                insights.append("✅ GST-compliant with regular filings")
            else:
                insights.append("📋 GST registered - check compliance status")
        
        if upi.get('transactions', 0) > 1000:
            insights.append(f"📱 High digital adoption - {upi['transactions']} UPI transactions")
        
        if len(insights) >= 4:
            insights.append("💪 Overall strong financial position with multiple positive indicators")
        elif len(insights) >= 2:
            insights.append("📊 Moderate financial health with some positive indicators")
        else:
            insights.append("🔍 Limited financial data available - consider providing more documentation")
        return insights
    
    def _generate_summary(self, metrics: Dict, insights: List[str]) -> str:
        revenue = metrics.get('revenue', {})
        employees = metrics.get('employees', 0)
        business_age = metrics.get('business_age', 0)
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
    
    # ---------- Business Health Analysis ----------
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
                insights.append("🚀 Strong revenue growth trajectory")
                recommendations.append("Consider expanding operations to capitalize on growth")
            elif growth > 10:
                insights.append("📈 Steady revenue growth")
            elif growth > 0:
                insights.append("📊 Modest revenue growth")
                recommendations.append("Explore new markets to accelerate growth")
            else:
                risks.append("⚠️ Revenue decline detected")
                recommendations.append("Review pricing strategy and customer acquisition")
        
        if cashflow and len(cashflow) > 1:
            if all(cf > 0 for cf in cashflow):
                insights.append("💪 Consistent positive cashflow")
            elif any(cf < 0 for cf in cashflow):
                risks.append("⚠️ Negative cashflow periods detected")
                recommendations.append("Improve working capital management")
        
        if employees > 20:
            insights.append("👥 Established workforce - good operational capacity")
        elif employees > 5:
            insights.append("👤 Growing team - positive sign")
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
    
    def _calculate_loan_suitability(self, score: float, risks: List[str]) -> Dict:
        if score >= 80 and len(risks) == 0:
            return {'level': 'High', 'max_amount': 5000000, 'interest': '10-12%'}
        elif score >= 70 and len(risks) <= 1:
            return {'level': 'Good', 'max_amount': 3500000, 'interest': '12-14%'}
        elif score >= 60 and len(risks) <= 2:
            return {'level': 'Moderate', 'max_amount': 2000000, 'interest': '14-16%'}
        else:
            return {'level': 'Low', 'max_amount': 500000, 'interest': '16-18%'}
    
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
        return f"""📊 **Business Health Assessment**

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
        return f"""💰 **Loan Eligibility Assessment**

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
        response = "⚠️ **Risk Assessment Report**\n\n**Identified Risks:**\n"
        for risk, level in risks:
            emoji = "✅" if level in ['Low', 'Adequate', 'Compliant'] else "⚠️" if level in ['Moderate', 'Tight', 'Needs Attention'] else "🚨"
            response += f"\n• {emoji} {risk}: {level}"
        response += f"\n\n**AI Recommendations:**\n• Diversify customer base\n• Build cash reserves\n• Optimize inventory\n\n**Risk Score:** {random.randint(20, 80)}/100"
        return response
    
    def _get_improvement_response(self) -> str:
        return """🚀 **Growth & Improvement Plan**

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
        return """📋 **Document Analysis Summary**

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

# ------------------ SAMPLE DATA ------------------
def generate_sample_businesses():
    return [
        {
            "name": "Apex Manufacturing Solutions",
            "gstin": "29AAHCS7890E1Z8",
            "industry": "Auto Components",
            "constitution": "Private Limited",
            "location": "Chennai, Tamil Nadu",
            "employees": 45,
            "years": 12,
            "revenue": [32, 35, 38, 34, 42, 45, 41, 48, 52, 49, 55, 58],
            "cashflow": [22, 25, 28, 24, 32, 35, 31, 38, 42, 39, 45, 48],
            "gst_score": 92,
            "score": 92,
            "status": "Active",
            "upi_transactions": 14892,
            "upi_collections": 2.14,
            "active_customers": 1432
        },
        {
            "name": "Pioneer Engineering Works",
            "gstin": "19BBJKS4567F2Z9",
            "industry": "General Engineering",
            "constitution": "Partnership",
            "location": "Mumbai, Maharashtra",
            "employees": 28,
            "years": 8,
            "revenue": [18, 20, 22, 19, 24, 26, 23, 28, 30, 27, 32, 35],
            "cashflow": [12, 14, 16, 13, 18, 20, 17, 22, 24, 21, 26, 28],
            "gst_score": 78,
            "score": 78,
            "status": "Active",
            "upi_transactions": 8760,
            "upi_collections": 1.24,
            "active_customers": 890
        },
        {
            "name": "Sai Industries Pvt Ltd",
            "gstin": "33CCMNT2345G3Z2",
            "industry": "Textiles",
            "constitution": "Private Limited",
            "location": "Pune, Maharashtra",
            "employees": 12,
            "years": 4,
            "revenue": [8, 9, 10, 8, 11, 12, 10, 13, 14, 12, 15, 16],
            "cashflow": [4, 5, 6, 4, 7, 8, 6, 9, 10, 8, 11, 12],
            "gst_score": 65,
            "score": 65,
            "status": "Under Review",
            "upi_transactions": 3450,
            "upi_collections": 0.48,
            "active_customers": 320
        }
    ]

def generate_sample_applications():
    return [
        {"id": "APP-2024-045", "business": "Apex Manufacturing", "gstin": "29AAHC...E1Z8",
         "amount": 42.5, "score": 92, "status": "Pending Review", "date": "2024-06-01"},
        {"id": "APP-2024-044", "business": "Pioneer Engineering", "gstin": "19BBJK...F2Z9",
         "amount": 65.0, "score": 78, "status": "Approved", "date": "2024-05-30"},
        {"id": "APP-2024-043", "business": "Sai Industries", "gstin": "33CCMN...G3Z2",
         "amount": 18.0, "score": 45, "status": "Rejected", "date": "2024-05-28"},
        {"id": "APP-2024-042", "business": "Goyal Exports", "gstin": "44LMNO...Z3Z5",
         "amount": 35.0, "score": 82, "status": "Under Verification", "date": "2024-05-27"},
        {"id": "APP-2024-041", "business": "Rathi Traders", "gstin": "55PQRS...X9Y1",
         "amount": 28.5, "score": 76, "status": "Approved", "date": "2024-05-25"}
    ]

def generate_sample_alerts():
    return [
        {"time": "2 hours ago", "title": "⚠️ High Risk Alert", "desc": "Apex Manufacturing: Cash flow dropped 22% this month", "priority": "high"},
        {"time": "4 hours ago", "title": "✅ Document Verification", "desc": "Sai Industries - All documents verified successfully", "priority": "low"},
        {"time": "Yesterday", "title": "📊 Monthly Report Ready", "desc": "June 2024 portfolio report is available for download", "priority": "medium"},
        {"time": "Yesterday", "title": "🎯 Pre-Approved Offers", "desc": "3 new MSMEs are eligible for pre-approved loans", "priority": "medium"},
        {"time": "2 days ago", "title": "⚠️ Compliance Reminder", "desc": "Goyal Exports - GST filing due in 3 days", "priority": "high"}
    ]

# ------------------ INITIALIZE SESSION STATE ------------------
if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = AIFinancialEngine()
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'businesses' not in st.session_state:
    st.session_state.businesses = generate_sample_businesses()
if 'applications' not in st.session_state:
    st.session_state.applications = generate_sample_applications()
if 'alerts' not in st.session_state:
    st.session_state.alerts = generate_sample_alerts()
if 'selected_business' not in st.session_state:
    st.session_state.selected_business = st.session_state.businesses[0]
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

# ------------------ SIDEBAR NAVIGATION ------------------
# Inside sidebar, after the navigation buttons
with st.sidebar.expander("📤 Upload & Process Data", expanded=False):
    st.markdown("Upload your CSV files to replace sample data.")
    business_file = st.file_uploader("Businesses CSV (required)", type=['csv'], key="biz_csv")
    apps_file = st.file_uploader("Applications CSV (optional)", type=['csv'], key="apps_csv")
    alerts_file = st.file_uploader("Alerts CSV (optional)", type=['csv'], key="alerts_csv")
    
    if st.button("🚀 Load & Process Data", use_container_width=True):
        if business_file:
            from data_utils import load_businesses_from_csv, load_applications_from_csv, load_alerts_from_csv
            # Load data
            businesses = load_businesses_from_csv(business_file)
            apps = load_applications_from_csv(apps_file) if apps_file else generate_sample_applications()
            alerts = load_alerts_from_csv(alerts_file) if alerts_file else generate_sample_alerts()
            
            # Store in session state
            st.session_state.businesses = businesses
            st.session_state.applications = apps
            st.session_state.alerts = alerts
            
            # Run AI analysis on each business (if scores are missing, compute them)
            ai = st.session_state.ai_engine
            for biz in businesses:
                # If score is missing or 0, let AI compute it
                if biz.get('score', 0) == 0:
                    # Prepare business data for AI
                    biz_data = {
                        'revenue': biz.get('revenue', []),
                        'cashflow': biz.get('cashflow', []),
                        'employees': biz.get('employees', 5),
                        'gst_score': biz.get('gst_score', 70)
                    }
                    insights = ai.generate_business_insights(biz_data)
                    biz['score'] = insights['overall_score']
                    biz['gst_score'] = insights['dimensions']['GST Compliance']
                    # You can also store other insights if needed
            
            st.success(f"✅ Loaded {len(businesses)} businesses, {len(apps)} applications, {len(alerts)} alerts. AI analysis complete!")
            st.rerun()
        else:
            st.warning("Please upload at least the Businesses CSV.")
with st.sidebar:
    st.markdown("### 🧠 **AI Finance**")
    st.caption("Intelligent MSME Assessment")
    st.markdown("---")
    
    pages = {
        "📊 Dashboard": "Dashboard",
        "🔎 Search": "Search",
        "📋 Applications": "Applications",
        "📇 Health Cards": "HealthCards",
        "📈 Monitoring": "Monitoring",
        "🔔 Alerts": "Alerts",
        "📑 Reports": "Reports",
        "⚙️ Settings": "Settings",
        "📄 Documents": "Documents",
        "💬 AI Chat": "Chat"
    }
    
    for label, key in pages.items():
        if st.button(label, key=key, use_container_width=True):
            st.session_state.page = key
    
    st.markdown("---")
    st.caption("🤖 AI Status: Active")
    st.caption(f"📅 {datetime.now().strftime('%d %B %Y')}")
    st.progress(0.92, text="AI Confidence: 92%")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# ------------------ PAGE ROUTING ------------------
page = st.session_state.page

# ======================== DASHBOARD ========================
if page == "Dashboard":
    st.markdown("""
    <div class="ai-header">
        <h1 style="margin:0;">📊 AI Business Health Dashboard</h1>
        <p style="margin:0; opacity:0.9;">Real-time AI-powered insights for your MSME portfolio</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Select business (for demo)
    biz_names = [b['name'] for b in st.session_state.businesses]
    selected_name = st.selectbox("Select MSME", biz_names, index=0)
    business = next(b for b in st.session_state.businesses if b['name'] == selected_name)
    st.session_state.selected_business = business
    
    # ----- Top stats -----
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:0.8rem;color:#718096;">Health Score</div>
            <div style="font-size:2.5rem;font-weight:700;color:{'#00b894' if business['score']>=80 else '#fdcb6e' if business['score']>=70 else '#e17055'};">{business['score']}</div>
            <div>{'Excellent' if business['score']>=80 else 'Good' if business['score']>=70 else 'Moderate'}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.metric("Revenue (Annual)", f"₹{np.mean(business['revenue'])*12/100000:.1f} Lakh", f"{((business['revenue'][-1]-business['revenue'][0])/business['revenue'][0]*100):.1f}%")
    with col3:
        st.metric("Employees", business['employees'], "↑ 4%")
    with col4:
        st.metric("Loan Suitability", "High" if business['score']>=80 else "Moderate", "Pre-approved" if business['score']>=80 else "")

    # ----- Profile + Score -----
    col_profile, col_score = st.columns([2,1])
    with col_profile:
        st.markdown(f"""
        <div class="health-card">
            <div style="display:flex;justify-content:space-between;align-items:start;">
                <div>
                    <h3 style="margin:0;">{business['name']}</h3>
                    <span class="status-badge badge-excellent">● Active</span>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.8rem;color:#718096;">Last Assessment</div>
                    <div style="font-weight:600;">{datetime.now().strftime('%d %b %Y')}</div>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-top:1rem;">
                <div><div style="font-size:0.7rem;color:#718096;">GSTIN</div><div style="font-weight:600;">{business['gstin']}</div></div>
                <div><div style="font-size:0.7rem;color:#718096;">Industry</div><div style="font-weight:600;">{business['industry']}</div></div>
                <div><div style="font-size:0.7rem;color:#718096;">Structure</div><div style="font-weight:600;">{business['constitution']}</div></div>
                <div><div style="font-size:0.7rem;color:#718096;">Location</div><div style="font-weight:600;">{business['location']}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_score:
        st.markdown(f"""
        <div class="metric-card" style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;">
            <div style="font-size:0.8rem;opacity:0.8;">Financial Health Score</div>
            <div style="font-size:4rem;font-weight:700;">{business['score']}</div>
            <div style="font-size:1rem;font-weight:600;">{'Excellent' if business['score']>=80 else 'Good'}</div>
            <div style="font-size:0.8rem;opacity:0.8;margin-top:0.5rem;">Benchmark: 70-100</div>
        </div>
        """, unsafe_allow_html=True)

    # ----- Dimensions -----
    st.markdown("### 📈 Performance Dimensions")
    dims = {
        "Revenue Health": random.randint(80,95),
        "Cash Flow Health": random.randint(75,90),
        "Growth Potential": random.randint(70,88),
        "Debt Management": random.randint(60,80),
        "Liquidity Position": random.randint(70,85),
        "Digital Adoption": random.randint(80,95),
        "Compliance Score": random.randint(85,98),
        "Workforce Stability": random.randint(70,85)
    }
    cols = st.columns(4)
    for idx, (dim, score) in enumerate(dims.items()):
        with cols[idx % 4]:
            color = "#00b894" if score>=80 else "#fdcb6e" if score>=70 else "#e17055"
            label = "Strong" if score>=80 else "Moderate" if score>=70 else "Needs Work"
            st.markdown(f"""
            <div style="background:white;padding:1rem;border-radius:8px;margin-bottom:0.5rem;border:1px solid #e8edf5;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.85rem;font-weight:500;">{dim}</span>
                    <span style="font-weight:700;color:{color};">{score}%</span>
                </div>
                <div class="dimension-bar"><div class="dimension-fill" style="width:{score}%;background:{color};"></div></div>
                <div style="font-size:0.7rem;color:{color};margin-top:0.2rem;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # ----- Loan Recommendation & Trends -----
    col_loan, col_trends = st.columns([1,2])
    with col_loan:
        st.markdown("""
        <div class="health-card">
            <h4 style="margin-top:0;">💰 Credit Assessment</h4>
            <div style="background:#e8f5e9;padding:1rem;border-radius:8px;margin:1rem 0;">
                <div style="font-size:0.8rem;color:#2e7d32;">Eligibility Status</div>
                <div style="font-size:1.2rem;font-weight:700;color:#2e7d32;">✅ Pre-Approved</div>
            </div>
            <div style="margin:1rem 0;">
                <div style="display:flex;justify-content:space-between;"><span>Recommended Limit</span><span style="font-weight:700;font-size:1.2rem;">₹42.50 Lakh</span></div>
                <div style="display:flex;justify-content:space-between;margin-top:0.5rem;"><span>Product</span><span>Working Capital + Term Loan</span></div>
                <div style="display:flex;justify-content:space-between;margin-top:0.5rem;"><span>Tenure</span><span>48 Months</span></div>
                <div style="display:flex;justify-content:space-between;margin-top:0.5rem;"><span>Interest Rate</span><span>10.75% - 12.50%</span></div>
            </div>
            <div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.85rem;">Confidence Level</span>
                    <span style="font-weight:700;">94%</span>
                </div>
                <div class="dimension-bar"><div class="dimension-fill" style="width:94%;background:#00b894;"></div></div>
            </div>
            <div style="margin-top:1rem;">
                <span class="data-source-tag active">Term Loan</span>
                <span class="data-source-tag active">Overdraft</span>
                <span class="data-source-tag">Equipment Finance</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_trends:
        st.markdown('<div class="health-card"><h4 style="margin-top:0;">📈 Revenue & Cash Flow Trends</h4></div>', unsafe_allow_html=True)
        months = ['Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun']
        rev = business['revenue']
        cf = business['cashflow']
        fig = make_subplots(rows=2, cols=1)
        fig.add_trace(go.Scatter(x=months, y=rev, mode='lines+markers', name='Revenue', line=dict(color='#0984e3',width=3)), row=1, col=1)
        fig.add_trace(go.Scatter(x=months, y=cf, mode='lines+markers', name='Cash Flow', line=dict(color='#00b894',width=3)), row=2, col=1)
        fig.update_layout(height=350, showlegend=True, margin=dict(l=20,r=20,t=20,b=20))
        fig.update_xaxes(title_text="", row=1, col=1)
        fig.update_xaxes(title_text="Month", row=2, col=1)
        fig.update_yaxes(title_text="₹ Lakhs", row=1, col=1)
        fig.update_yaxes(title_text="₹ Lakhs", row=2, col=1)
        st.plotly_chart(fig, use_container_width=True)

    # ----- Data Sources, Risk, UPI -----
    col_src, col_risk, col_upi = st.columns([1,1,1.2])
    with col_src:
        st.markdown("""
        <div class="health-card">
            <h4 style="margin-top:0;">🔗 Connected Data Sources</h4>
            <div style="margin:0.5rem 0;">
                <span class="data-source-tag active">✓ GST Portal</span>
                <span class="data-source-tag active">✓ Bank Statements</span>
                <span class="data-source-tag active">✓ UPI Transactions</span>
                <span class="data-source-tag active">✓ EPFO Records</span>
                <span class="data-source-tag">○ IT Returns (Optional)</span>
                <span class="data-source-tag">○ Utility Bills</span>
                <span class="data-source-tag">○ E-commerce Sales</span>
            </div>
            <div style="font-size:0.8rem;color:#718096;margin-top:0.5rem;">Last sync: Today, 2:30 PM</div>
        </div>
        """, unsafe_allow_html=True)
    with col_risk:
        st.markdown("""
        <div class="health-card">
            <h4 style="margin-top:0;">⚠️ Risk Factors</h4>
            <div style="margin:0.5rem 0;">
                <div style="display:flex;justify-content:space-between;padding:0.2rem 0;"><span>Client Concentration</span><span style="color:#fdcb6e;">Moderate</span></div>
                <div style="display:flex;justify-content:space-between;padding:0.2rem 0;"><span>Seasonal Fluctuation</span><span style="color:#fdcb6e;">Moderate</span></div>
                <div style="display:flex;justify-content:space-between;padding:0.2rem 0;"><span>Working Capital Cycle</span><span style="color:#00b894;">Efficient</span></div>
                <div style="display:flex;justify-content:space-between;padding:0.2rem 0;"><span>Supplier Dependency</span><span style="color:#00b894;">Low</span></div>
                <div style="display:flex;justify-content:space-between;padding:0.2rem 0;"><span>Statutory Compliance</span><span style="color:#00b894;">Compliant</span></div>
            </div>
            <button style="background:none;border:none;color:#0984e3;cursor:pointer;font-size:0.85rem;padding:0;">View Detailed Risk Analysis →</button>
        </div>
        """, unsafe_allow_html=True)
    with col_upi:
        st.markdown(f"""
        <div class="health-card">
            <h4 style="margin-top:0;">📱 Digital Collections Overview</h4>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin:1rem 0;">
                <div><div style="font-size:0.7rem;color:#718096;">12-Month Volume</div><div style="font-size:1.2rem;font-weight:700;">{business['upi_transactions']:,}</div></div>
                <div><div style="font-size:0.7rem;color:#718096;">Total Collections</div><div style="font-size:1.2rem;font-weight:700;">₹{business['upi_collections']:.2f} Cr</div></div>
                <div><div style="font-size:0.7rem;color:#718096;">Daily Average</div><div style="font-size:1.2rem;font-weight:700;">₹{business['upi_collections']*10000000/365:,.0f}</div></div>
                <div><div style="font-size:0.7rem;color:#718096;">Active Customers</div><div style="font-size:1.2rem;font-weight:700;">{business['active_customers']:,}</div></div>
            </div>
            <div style="font-size:0.8rem;color:#00b894;">↑ 18% growth in UPI transactions</div>
        </div>
        """, unsafe_allow_html=True)

# ======================== SEARCH ========================
elif page == "Search":
    st.title("🔎 Business Discovery")
    st.caption("Find MSMEs by GSTIN, Business Name, or PAN")
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        query = st.text_input("", placeholder="Enter GSTIN, Business Name, or PAN...", label_visibility="collapsed")
    with col2:
        st.selectbox("Search Type", ["GSTIN", "Name", "PAN", "Industry"], label_visibility="collapsed")
    with col3:
        if st.button("🔍 Search", use_container_width=True):
            pass
    
    if query:
        results = [b for b in st.session_state.businesses if query.lower() in b['name'].lower() or query in b['gstin']]
        if results:
            for b in results:
                col1, col2, col3, col4 = st.columns([3,1.5,1,1])
                with col1:
                    st.write(f"**{b['name']}**")
                    st.caption(f"GSTIN: {b['gstin']}")
                with col2:
                    st.write(b['location'])
                with col3:
                    st.write(f"Score: **{b['score']}**")
                with col4:
                    if st.button("View", key=f"view_{b['gstin']}"):
                        st.session_state.selected_business = b
                        st.session_state.page = "Dashboard"
                        st.rerun()
        else:
            st.info("No businesses found")

# ======================== APPLICATIONS ========================
elif page == "Applications":
    st.title("📋 Loan Applications")
    st.caption("Review, process, and manage credit applications")
    
    col1, col2, col3, col4 = st.columns([2,1,1,1])
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending Review", "Approved", "Rejected", "Under Verification"])
    with col2:
        st.selectbox("Sort by", ["Date", "Amount", "Score"])
    with col3:
        st.date_input("From Date", value=datetime.now() - timedelta(days=30))
    with col4:
        st.date_input("To Date", value=datetime.now())
    
    apps = st.session_state.applications
    if status_filter != "All":
        apps = [a for a in apps if a['status'] == status_filter]
    
    for app in apps:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2,1.2,1,1,1])
            with col1:
                st.write(f"**{app['business']}**")
                st.caption(f"ID: {app['id']}")
            with col2:
                st.write(f"₹{app['amount']} Lakh")
            with col3:
                st.write(f"Score: {app['score']}")
            with col4:
                status_class = {
                    "Approved": "status-approved",
                    "Rejected": "status-rejected",
                    "Pending Review": "status-pending",
                    "Under Verification": "status-review"
                }.get(app['status'], "")
                st.markdown(f'<span class="status-badge {status_class}">{app["status"]}</span>', unsafe_allow_html=True)
            with col5:
                if st.button("Review", key=f"review_{app['id']}"):
                    st.info(f"Processing application {app['id']} ...")
            st.markdown("---")
    
    with st.expander("➕ Create New Application", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            gstin = st.text_input("GSTIN", placeholder="Enter 15-digit GSTIN")
            name = st.text_input("Business Name")
            industry = st.selectbox("Industry", ["Manufacturing", "Trading", "Services", "Construction"])
        with col2:
            amount = st.number_input("Requested Amount (₹ Lakh)", min_value=1, max_value=500, value=25)
            purpose = st.selectbox("Loan Purpose", ["Working Capital", "Equipment", "Expansion", "Consolidation"])
            tenure = st.selectbox("Tenure (Months)", [12,24,36,48,60])
        if st.button("Submit Application"):
            st.success("✅ Application submitted! AI assessment in progress...")
            st.info("Application ID: APP-2024-046")

# ======================== HEALTH CARDS ========================
elif page == "HealthCards":
    st.title("📊 Financial Health Cards")
    st.caption("Comprehensive business health reports")
    col1, col2 = st.columns([2,1])
    with col1:
        search_card = st.text_input("Search by Business Name or GSTIN", placeholder="Search...")
    with col2:
        st.selectbox("Score Range", ["All", "Excellent (80-100)", "Good (70-79)", "Average (50-69)", "Below Average (0-49)"])
    
    for b in st.session_state.businesses:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2.5,1.5,1,1,1])
            with col1:
                st.write(f"**{b['name']}**")
                st.caption(f"GSTIN: {b['gstin']}")
            with col2:
                score_color = "#00b894" if b['score']>=80 else "#fdcb6e" if b['score']>=70 else "#e17055"
                st.write(f"Score: **{b['score']}/100**")
            with col3:
                st.write(f"**{'Excellent' if b['score']>=80 else 'Good' if b['score']>=70 else 'Average'}**")
            with col4:
                st.write(f"↑ 4%" if b['score']>70 else "↓ 2%")
            with col5:
                if st.button("View Card", key=f"hc_{b['gstin']}"):
                    st.session_state.selected_business = b
                    st.session_state.page = "Dashboard"
                    st.rerun()
            st.markdown("---")

# ======================== MONITORING ========================
elif page == "Monitoring":
    st.title("📈 Performance Monitoring")
    st.caption("Track portfolio performance and identify trends")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Healthy MSMEs (>75)", "842", "↑ 12%")
    with col2:
        st.metric("At-Risk MSMEs (<50)", "47", "↓ 8%")
    with col3:
        st.metric("Portfolio Growth", "18.4%", "↑ 3.2%")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Score Distribution")
        scores = np.random.normal(72, 18, 200)
        scores = np.clip(scores, 0, 100)
        fig = go.Figure(data=[go.Histogram(x=scores, nbinsx=20, marker_color='#0984e3')])
        fig.update_layout(height=300, margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Monthly Approvals/Rejections")
        months = ['Jan','Feb','Mar','Apr','May','Jun']
        approvals = [12,15,18,14,22,25]
        rejections = [8,6,5,7,4,3]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=months, y=approvals, name='Approved', marker_color='#00b894'))
        fig.add_trace(go.Bar(x=months, y=rejections, name='Rejected', marker_color='#e17055'))
        fig.update_layout(height=300, barmode='stack', margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig, use_container_width=True)

# ======================== ALERTS ========================
elif page == "Alerts":
    st.title("🔔 Notifications & Alerts")
    st.caption("Stay informed about important updates")
    for alert in st.session_state.alerts:
        color = "#e74c3c" if alert['priority']=='high' else "#f39c12" if alert['priority']=='medium' else "#3498db"
        st.markdown(f"""
        <div style="background:white;padding:1rem;border-radius:8px;border-left:4px solid {color};margin-bottom:0.75rem;">
            <div style="display:flex;justify-content:space-between;">
                <strong>{alert['title']}</strong>
                <span style="font-size:0.8rem;color:#718096;">{alert['time']}</span>
            </div>
            <div style="font-size:0.9rem;color:#2d3748;margin-top:0.25rem;">{alert['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

# ======================== REPORTS ========================
elif page == "Reports":
    st.title("📑 Reports & Analytics")
    st.caption("Generate and export comprehensive reports")
    col1, col2 = st.columns([1,2])
    with col1:
        st.markdown("### Generate Report")
        report_type = st.selectbox("Report Type", ["Portfolio Summary", "Individual MSME Health", "Risk Assessment", "Performance Trends"])
        date_range = st.date_input("Date Range", [datetime.now()-timedelta(days=30), datetime.now()])
        format_type = st.selectbox("Export Format", ["PDF", "Excel", "CSV", "JSON"])
        if st.button("Generate Report", use_container_width=True):
            st.success("✅ Report generated successfully!")
            st.download_button("Download Report", data="Sample report data", file_name=f"report_{datetime.now().strftime('%Y%m%d')}.pdf")
    with col2:
        st.markdown("### Recent Reports")
        reports = [
            {"name": "Portfolio Summary - June 2024", "date": "2024-06-30", "size": "2.4 MB"},
            {"name": "Risk Assessment Report", "date": "2024-06-28", "size": "1.8 MB"},
            {"name": "MSME Health Trends Q2 2024", "date": "2024-06-25", "size": "3.1 MB"},
        ]
        for r in reports:
            col_a, col_b, col_c = st.columns([2,1,1])
            with col_a:
                st.write(f"📄 {r['name']}")
            with col_b:
                st.caption(r['date'])
            with col_c:
                st.caption(r['size'])
            st.markdown("---")

# ======================== SETTINGS ========================
elif page == "Settings":
    st.title("⚙️ Settings")
    st.caption("Configure platform preferences and integrations")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔌 Data Integrations")
        st.checkbox("GST Portal", value=True)
        st.checkbox("Account Aggregator", value=True)
        st.checkbox("UPI Transaction Data", value=True)
        st.checkbox("EPFO Records", value=True)
        st.checkbox("IT Returns (Optional)", value=False)
        st.checkbox("Utility Bill Payments", value=False)
        if st.button("Sync All Data Sources"):
            st.success("✅ All data sources synchronized successfully!")
    with col2:
        st.markdown("### 🎨 Preferences")
        st.selectbox("Default View", ["Dashboard", "Applications", "Monitoring"])
        st.selectbox("Notification Frequency", ["Real-time", "Daily", "Weekly"])
        st.slider("Risk Alert Threshold", 0, 100, 60)
        st.toggle("Enable AI Recommendations", value=True)
        st.toggle("Auto-generate Health Cards", value=True)
        st.markdown("### 👤 Profile")
        st.text_input("Name", "Priya Sharma")
        st.text_input("Email", "priya.sharma@bank.com")
        if st.button("Save Settings"):
            st.success("✅ Settings saved successfully!")

# ======================== DOCUMENTS ========================
elif page == "Documents":
    st.markdown("""
    <div class="ai-header">
        <h1 style="margin:0;">📄 AI Document Intelligence</h1>
        <p style="margin:0; opacity:0.9;">Upload documents for AI-powered financial analysis</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    with col1:
        uploaded_file = st.file_uploader("Upload Financial Documents", type=['txt','pdf','docx','csv'])
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8') if uploaded_file.type=='text/plain' else str(uploaded_file)
            # Simulate analysis
            ai = st.session_state.ai_engine
            sample_text = """
            Annual Revenue: ₹45 Lakh with 18% growth.
            Operating Expenses: ₹28 Lakh, staff salary ₹12 Lakh.
            Net Profit: ₹8.5 Lakh, margin 18.9%.
            GST: Regular filings, GSTIN: 29AABCS1234A1Z5.
            Employees: 25. Established in 2016.
            UPI transactions: 15,000, collections ₹2.5 Cr.
            """
            analysis = ai.analyze_document(sample_text)
            st.success("✅ Document analyzed successfully!")
            st.metric("AI Confidence", f"{analysis['confidence']:.1f}%")
            st.markdown("### 📊 Extracted Metrics")
            metrics = analysis['metrics']
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if metrics['revenue']:
                    st.metric("Annual Revenue", f"₹{metrics['revenue'].get('annual',0)/100000:.1f} Lakh")
            with col_b:
                if metrics['profit']:
                    st.metric("Net Profit", f"₹{metrics['profit'].get('net',0)/100000:.1f} Lakh")
                    if 'margin' in metrics['profit']:
                        st.metric("Profit Margin", f"{metrics['profit']['margin']:.1f}%")
            with col_c:
                if metrics['employees'] > 0:
                    st.metric("Employees", metrics['employees'])
                if metrics['business_age'] > 0:
                    st.metric("Business Age", f"{metrics['business_age']} Years")
    with col2:
        st.markdown("### 💡 AI Insights")
        if 'analysis' in locals():
            for insight in analysis['insights']:
                st.markdown(f"""
                <div class="insight-card insight-positive">
                    {insight}
                </div>
                """, unsafe_allow_html=True)
            st.markdown("### 📝 AI Summary")
            st.write(analysis['summary'])
        else:
            st.info("Upload a document to receive AI-powered insights")

# ======================== AI CHAT ========================
else:
    st.markdown("""
    <div class="ai-header">
        <h1 style="margin:0;">💬 AI Financial Assistant</h1>
        <p style="margin:0; opacity:0.9;">Chat with AI about your business health and financial insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick questions
    st.markdown("### Quick Questions")
    quick_qs = ["What's my business health score?", "Am I eligible for a loan?", "What are my business risks?", "How can I improve?"]
    cols = st.columns(4)
    for idx, q in enumerate(quick_qs):
        with cols[idx]:
            if st.button(q, key=f"qq_{idx}"):
                response = st.session_state.ai_engine.chat(q)
                st.session_state.conversation.append(("user", q))
                st.session_state.conversation.append(("assistant", response))
    
    # Chat history
    st.markdown("### 💭 Conversation")
    chat_container = st.container()
    with chat_container:
        for role, msg in st.session_state.conversation[-10:]:
            if role == "user":
                st.markdown(f'<div class="message user-msg"><strong>You:</strong> {msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="message ai-msg"><strong>🤖 AI:</strong> {msg}</div>', unsafe_allow_html=True)
    
    # Input
    col1, col2 = st.columns([5,1])
    with col1:
        user_input = st.text_input("", placeholder="Ask me about your business financial health...", key="chat_input", label_visibility="collapsed")
    with col2:
        if st.button("Send", use_container_width=True):
            if user_input:
                response = st.session_state.ai_engine.chat(user_input)
                st.session_state.conversation.append(("user", user_input))
                st.session_state.conversation.append(("assistant", response))
                st.rerun()
    
    with st.expander("💡 Suggested Questions"):
        st.markdown("""
        - "What is my business health score?"
        - "Analyze my cash flow"
        - "Am I ready for a business loan?"
        - "What are the key risks?"
        - "How can I grow my revenue?"
        - "Compare my business to industry standards"
        """)
    
    # Floating chat button
    st.markdown("""
    <button class="floating-chat" onclick="window.scrollTo(0, 0)">
        💬 Chat with AI
    </button>
    """, unsafe_allow_html=True)
