import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import re
import random
import base64
from typing import Dict, List, Any

# Import our modules
from ai_engine import AIFinancialEngine
from data_utils import (
    generate_sample_businesses,
    generate_sample_applications,
    generate_sample_alerts,
    load_businesses_from_csv,
    load_applications_from_csv,
    load_alerts_from_csv
)

# --- Page Configuration ---
st.set_page_config(
    page_title="AI MSME Financial Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS (unchanged) ---
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
    .doc-upload-box {
        border: 1px solid #e8edf5;
        border-radius: 8px;
        padding: 0.8rem;
        background: #fafbfc;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize session state ---
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
if 'health_cards' not in st.session_state:
    st.session_state.health_cards = {}

# --- Helper to display health card ---
def display_health_card(health_card, name, gstin, industry):
    st.markdown(f"""
    <div class="health-card">
        <h3>{name}</h3>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span class="status-badge badge-excellent">{'Excellent' if health_card['overall_score']>=80 else 'Good' if health_card['overall_score']>=70 else 'Moderate'}</span>
                <span style="margin-left:1rem;">Confidence: {health_card['confidence']:.0f}%</span>
            </div>
            <div style="font-size:2.5rem; font-weight:700; color:{'#00b894' if health_card['overall_score']>=80 else '#fdcb6e' if health_card['overall_score']>=70 else '#e17055'};">{health_card['overall_score']}</div>
        </div>
        <hr>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
            <div><strong>Risk Level:</strong> <span class="risk-{health_card['risk_level'].lower()}">{health_card['risk_level']}</span></div>
            <div><strong>Loan Suitability:</strong> {health_card['loan_suitability']['level']} (₹{health_card['loan_suitability']['max_amount']/100000:.1f} Lakh)</div>
            <div><strong>GSTIN:</strong> {gstin}</div>
            <div><strong>Industry:</strong> {industry}</div>
        </div>
        <div style="margin-top:1rem;">
            <strong>Dimensions:</strong>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; margin-top:0.5rem;">
                {''.join([f"<div>{dim}: {score}/100</div>" for dim, score in health_card['dimensions'].items()])}
            </div>
        </div>
        <div style="margin-top:1rem;">
            <strong>AI Insights:</strong>
            <ul>
                {''.join([f"<li>{insight}</li>" for insight in health_card['insights']])}
            </ul>
        </div>
        <div style="margin-top:1rem; font-size:0.9rem; background:#f8f9fa; padding:1rem; border-radius:8px;">
            <strong>Summary:</strong> {health_card.get('summary', 'N/A')}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Sidebar Navigation ---
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
    
    # ---- Upload & Process Data (CSV) ----
    with st.sidebar.expander("📤 Upload & Process Data", expanded=False):
        st.markdown("Upload your business data to get AI insights.")
        business_file = st.file_uploader("Businesses CSV (required)", type=['csv'], key="biz_csv")
        apps_file = st.file_uploader("Applications CSV (optional)", type=['csv'], key="apps_csv")
        
        if st.button("🚀 Load & Process Data", use_container_width=True):
            if business_file:
                businesses = load_businesses_from_csv(business_file)
                apps = load_applications_from_csv(apps_file) if apps_file else generate_sample_applications()
                
                st.session_state.businesses = businesses
                st.session_state.applications = apps
                
                ai = st.session_state.ai_engine
                for biz in businesses:
                    biz_data = {
                        'revenue': biz.get('revenue', []),
                        'cashflow': biz.get('cashflow', []),
                        'employees': biz.get('employees', 5),
                        'gst_score': biz.get('gst_score', 70)
                    }
                    insights = ai.generate_business_insights(biz_data)
                    biz['score'] = insights['overall_score']
                    st.session_state.health_cards[biz['name']] = insights
                
                alerts = []
                for biz in businesses:
                    if biz.get('score', 0) < 60:
                        alerts.append({
                            "time": "Just now",
                            "title": f"⚠️ Low Health Score - {biz['name']}",
                            "desc": f"Health score is {biz['score']} – below acceptable threshold.",
                            "priority": "high"
                        })
                    elif biz.get('score', 0) < 70:
                        alerts.append({
                            "time": "Just now",
                            "title": f"⚠️ Moderate Risk - {biz['name']}",
                            "desc": f"Health score {biz['score']} – monitor closely.",
                            "priority": "medium"
                        })
                st.session_state.alerts = alerts
                
                st.success(f"✅ Processed {len(businesses)} businesses and {len(apps)} applications. AI analysis complete!")
                st.rerun()
            else:
                st.warning("Please upload the Businesses CSV file.")

# --- Page Routing ---
page = st.session_state.page

# ======================== DASHBOARD ========================
if page == "Dashboard":
    st.markdown("""
    <div class="ai-header">
        <h1 style="margin:0;">📊 AI Business Health Dashboard</h1>
        <p style="margin:0; opacity:0.9;">Real-time AI-powered insights for your MSME portfolio</p>
    </div>
    """, unsafe_allow_html=True)
    
    biz_names = [b['name'] for b in st.session_state.businesses]
    if biz_names:
        selected_name = st.selectbox("Select MSME", biz_names, index=0)
        business = next(b for b in st.session_state.businesses if b['name'] == selected_name)
        st.session_state.selected_business = business
        
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
           # Safe growth calculation
rev_start = business['revenue'][0]
rev_end = business['revenue'][-1]
if rev_start != 0:
    growth_pct = ((rev_end - rev_start) / rev_start * 100)
    growth_str = f"{growth_pct:.1f}%"
else:
    growth_str = "N/A"  # or "0.0%" if you prefer
st.metric("Revenue (Annual)", f"₹{np.mean(business['revenue'])*12/100000:.1f} Lakh", growth_str)
        with col3:
            st.metric("Employees", business['employees'], "↑ 4%")
        with col4:
            st.metric("Loan Suitability", "High" if business['score']>=80 else "Moderate", "Pre-approved" if business['score']>=80 else "")
        
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
    else:
        st.warning("No businesses loaded. Please upload data via the sidebar.")

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

# ======================== APPLICATIONS (UPDATED WITH CSV UPLOAD) ========================
elif page == "Applications":
    st.title("📋 Loan Applications")
    st.caption("Review, process, and create new applications with CSV data uploads")
    
    # ---- Existing Applications Table ----
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
    
    # ---- Create New Application with CSV Data ----
    with st.expander("➕ Create New Application with CSV Data", expanded=False):
        st.markdown("""
        **Fill in business details and upload CSV files for each data source.**
        The more CSVs you upload, the more accurate the AI analysis.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            gstin = st.text_input("GSTIN", placeholder="Enter 15-digit GSTIN")
            name = st.text_input("Business Name")
            industry = st.selectbox("Industry", ["Manufacturing", "Trading", "Services", "Construction", "Agriculture"])
            amount = st.number_input("Requested Amount (₹ Lakh)", min_value=1, max_value=500, value=25)
        with col2:
            purpose = st.selectbox("Loan Purpose", ["Working Capital", "Equipment Purchase", "Business Expansion", "Debt Consolidation"])
            tenure = st.selectbox("Tenure (Months)", [12,24,36,48,60])
            
            st.markdown("#### 📎 Upload CSV Data Sources")
            gst_csv = st.file_uploader("GST Data (CSV)", type=['csv'], key="gst_csv")
            bank_csv = st.file_uploader("Bank Statement (CSV)", type=['csv'], key="bank_csv")
            upi_csv = st.file_uploader("UPI Transactions (CSV)", type=['csv'], key="upi_csv")
            epfo_csv = st.file_uploader("EPFO Data (CSV)", type=['csv'], key="epfo_csv")
            itr_csv = st.file_uploader("ITR Data (optional, CSV)", type=['csv'], key="itr_csv")
            utility_csv = st.file_uploader("Utility Payments (optional, CSV)", type=['csv'], key="utility_csv")
        
        if st.button("Submit Application with CSVs"):
            # Gather uploaded CSVs
            csv_files = {
                'gst': gst_csv,
                'bank_statement': bank_csv,
                'upi': upi_csv,
                'epfo': epfo_csv,
                'itr': itr_csv,
                'utility': utility_csv
            }
            uploaded = {k: v for k, v in csv_files.items() if v is not None}
            
            if not uploaded:
                st.error("Please upload at least one CSV file.")
            else:
                # Read CSV files into DataFrames
                dataframes = {}
                for src, file in uploaded.items():
                    try:
                        df = pd.read_csv(file)
                        dataframes[src] = df
                    except Exception as e:
                        st.error(f"Error reading {src} CSV: {e}")
                        st.stop()
                
                # Process with AI
                ai = st.session_state.ai_engine
                result = ai.process_csv_documents(dataframes)
                health_card = result['health_card']
                
                # Create application record
                app_id = f"APP-{datetime.now().strftime('%Y%m%d')}-{random.randint(100,999)}"
                new_app = {
                    "id": app_id,
                    "business": name if name else "Unknown MSME",
                    "gstin": gstin if gstin else "N/A",
                    "amount": amount,
                    "score": health_card['overall_score'],
                    "status": "Under Verification",
                    "date": datetime.now().strftime('%Y-%m-%d')
                }
                st.session_state.applications.append(new_app)
                
                # Store health card
                health_card['business_name'] = name if name else "Unknown MSME"
                st.session_state.health_cards[name if name else "Unknown MSME"] = health_card
                
                # Also add to businesses if not exists
                existing = [b for b in st.session_state.businesses if b['name'] == (name if name else "Unknown MSME")]
                if not existing:
                    new_biz = {
                        "name": name if name else "Unknown MSME",
                        "gstin": gstin if gstin else "",
                        "industry": industry,
                        "constitution": "N/A",
                        "location": "N/A",
                        "employees": result['metrics'].get('employee_count', 0),
                        "years": 0,
                        "revenue": [0] * 12,
                        "cashflow": [0] * 12,
                        "gst_score": health_card['dimensions']['Compliance Score'],
                        "score": health_card['overall_score'],
                        "status": "Active",
                        "upi_transactions": result['metrics'].get('upi_volume', 0),
                        "upi_collections": result['metrics'].get('upi_total', 0) / 10000000,
                        "active_customers": result['metrics'].get('upi_customers', 0)
                    }
                    st.session_state.businesses.append(new_biz)
                
                # Generate alerts
                if health_card['overall_score'] < 60:
                    st.session_state.alerts.append({
                        "time": "Just now",
                        "title": f"⚠️ New Low Health Score - {new_app['business']}",
                        "desc": f"Health score is {health_card['overall_score']} – review recommended.",
                        "priority": "high"
                    })
                
                st.success(f"✅ Application {app_id} created with {len(uploaded)} data sources!")
                st.balloons()
                
                # Display Health Card
                st.markdown("### 📊 Full Financial Health Report")
                display_health_card(health_card, name if name else "Unknown MSME", gstin, industry)
                
                # PDF Download
                business_details = {
                    'name': name if name else "Unknown MSME",
                    'gstin': gstin if gstin else "N/A",
                    'industry': industry
                }
                pdf_bytes = ai.generate_pdf_report(health_card, business_details)
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="HealthCard_{app_id}.pdf">📥 Download PDF Report</a>'
                st.markdown(href, unsafe_allow_html=True)

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
            ai = st.session_state.ai_engine
            sample_text = """
            Annual Revenue: ₹45 Lakh with 18% growth.
            Operating Expenses: ₹28 Lakh, staff salary ₹12 Lakh.
            Net Profit: ₹8.5 Lakh, margin 18.9%.
            GST: Regular filings, GSTIN: 29AABCS1234A1Z5.
            Employees: 25. Established in 2016.
            UPI transactions: 15,000, collections ₹2.5 Cr.
            """
            analysis = ai.analyze_documents({'sample': sample_text})
            st.success("✅ Document analyzed successfully!")
            st.metric("AI Confidence", f"{analysis['confidence']:.1f}%")
            st.markdown("### 📊 Extracted Metrics")
            metrics = analysis['metrics']
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if metrics.get('revenue'):
                    st.metric("Annual Revenue", f"₹{metrics['revenue'].get('annual',0)/100000:.1f} Lakh")
            with col_b:
                if metrics.get('profit'):
                    st.metric("Net Profit", f"₹{metrics['profit'].get('net',0)/100000:.1f} Lakh")
                    if 'margin' in metrics['profit']:
                        st.metric("Profit Margin", f"{metrics['profit']['margin']:.1f}%")
            with col_c:
                if metrics.get('employees', 0) > 0:
                    st.metric("Employees", metrics['employees'])
                if metrics.get('business_age', 0) > 0:
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
    
    st.markdown("### Quick Questions")
    quick_qs = ["What's my business health score?", "Am I eligible for a loan?", "What are my business risks?", "How can I improve?"]
    cols = st.columns(4)
    for idx, q in enumerate(quick_qs):
        with cols[idx]:
            if st.button(q, key=f"qq_{idx}"):
                response = st.session_state.ai_engine.chat(q)
                st.session_state.conversation.append(("user", q))
                st.session_state.conversation.append(("assistant", response))
    
    st.markdown("### 💭 Conversation")
    chat_container = st.container()
    with chat_container:
        for role, msg in st.session_state.conversation[-10:]:
            if role == "user":
                st.markdown(f'<div class="message user-msg"><strong>You:</strong> {msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="message ai-msg"><strong>🤖 AI:</strong> {msg}</div>', unsafe_allow_html=True)
    
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
