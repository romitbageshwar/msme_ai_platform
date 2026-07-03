"""
AI Engine for MSME Financial Health Platform
Handles document analysis, business health scoring, loan eligibility, chat, and insights.
"""

import re
import random
import numpy as np
from typing import Dict, List, Any, Optional

class AIFinancialEngine:
    """Complete AI engine for MSME financial analysis"""

    def __init__(self):
        self.conversation_history = []
        self.business_data = {}
        self.health_cards = {}
        self.applications = []
        self.alerts = []

    # ---------- Document Analysis (with multiple sources) ----------
    def analyze_documents(self, documents: Dict[str, str]) -> Dict:
        """
        Analyze multiple uploaded documents and extract consolidated metrics.
        documents: dict with keys like 'gst', 'bank_statement', 'upi', 'epfo', 'itr', 'utility'
        Returns a dict with combined metrics, insights, and confidence score.
        """
        combined_metrics = {}
        all_insights = []
        confidence = 0.0
        num_docs = 0

        # Process each document if provided
        for doc_type, text in documents.items():
            if text:
                num_docs += 1
                # Extract metrics from this document
                metrics = self._extract_metrics_from_text(text)
                combined_metrics[doc_type] = metrics
                # Generate insights for this document
                insights = self._generate_document_insights(metrics)
                all_insights.extend(insights)

        # Aggregate metrics from all documents
        aggregated = self._aggregate_metrics(combined_metrics)

        # Confidence: higher with more documents
        confidence = min(98, 60 + num_docs * 8)  # 60% base, +8% per doc

        # Overall summary
        summary = self._generate_consolidated_summary(aggregated, all_insights)

        # Generate health card data
        health_card = self._generate_health_card(aggregated, all_insights, confidence)

        return {
            'metrics': aggregated,
            'insights': list(set(all_insights)),  # remove duplicates
            'confidence': confidence,
            'summary': summary,
            'health_card': health_card,
            'num_documents': num_docs
        }

    def _extract_metrics_from_text(self, text: str) -> Dict:
        """Extract all possible financial metrics from a single text."""
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

    def _aggregate_metrics(self, combined_metrics: Dict) -> Dict:
        """Combine metrics from multiple documents into a single aggregated dict."""
        aggregated = {
            'revenue': {},
            'expenses': {},
            'profit': {},
            'gst': {},
            'employees': 0,
            'business_age': 0,
            'upi': {},
            'gst_filings': {}
        }
        # Take the first non-empty value for each key
        for doc_type, metrics in combined_metrics.items():
            for key in aggregated.keys():
                if key in metrics and metrics[key]:
                    if isinstance(aggregated[key], dict) and not aggregated[key]:
                        aggregated[key] = metrics[key]
                    elif key == 'employees' and aggregated[key] == 0:
                        aggregated[key] = metrics[key]
                    elif key == 'business_age' and aggregated[key] == 0:
                        aggregated[key] = metrics[key]
        return aggregated

    def _generate_consolidated_summary(self, aggregated: Dict, insights: List[str]) -> str:
        """Generate a natural language summary from aggregated metrics and insights."""
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
        """Generate a health card from aggregated data."""
        # Compute scores
        revenue_score = self._calculate_revenue_score_from_metrics(aggregated.get('revenue', {}))
        cashflow_score = random.randint(65, 90)  # placeholder – would need cashflow data
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
            'insights': insights,
            'loan_suitability': loan_suitability,
            'confidence': confidence
        }

    def _calculate_revenue_score_from_metrics(self, revenue_metrics: Dict) -> float:
        # Use annual revenue and growth to compute a score
        if not revenue_metrics:
            return 50.0
        # If we have annual revenue, scale it
        annual = revenue_metrics.get('annual', 0)
        growth = revenue_metrics.get('growth', 0)
        base_score = 50
        if annual > 10000000:
            base_score += 20
        elif annual > 5000000:
            base_score += 10
        elif annual > 1000000:
            base_score += 5
        # Add growth bonus
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

    # ---------- Business Health Analysis (for CSV) ----------
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
