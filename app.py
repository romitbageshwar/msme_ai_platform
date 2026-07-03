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

# --- Helper to display health card (used in Applications) ---
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

# --- Sidebar Navigation (unchanged) ---
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
    # ... (unchanged – same as before) ...
    st.title("📊 Dashboard")
    # (Full dashboard code omitted for brevity – it's identical to previous)

# ======================== SEARCH ========================
elif page == "Search":
    # ... (unchanged) ...
    st.title("🔎 Search")

# ======================== APPLICATIONS (UPDATED) ========================
elif page == "Applications":
    st.title("📋 Loan Applications")
    st.caption("Review, process, and create new applications with CSV data uploads")
    
    # ---- Existing Applications Table (unchanged) ----
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
    
    # ---- Create New Application with CSV Data (UPDATED) ----
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
    # ... (unchanged) ...
    st.title("📇 Health Cards")

# ======================== MONITORING ========================
elif page == "Monitoring":
    # ... (unchanged) ...
    st.title("📈 Monitoring")

# ======================== ALERTS ========================
elif page == "Alerts":
    # ... (unchanged) ...
    st.title("🔔 Alerts")

# ======================== REPORTS ========================
elif page == "Reports":
    # ... (unchanged) ...
    st.title("📑 Reports")

# ======================== SETTINGS ========================
elif page == "Settings":
    # ... (unchanged) ...
    st.title("⚙️ Settings")

# ======================== DOCUMENTS ========================
elif page == "Documents":
    # ... (unchanged) ...
    st.title("📄 Documents")

# ======================== AI CHAT ========================
else:
    # ... (unchanged) ...
    st.title("💬 AI Chat")
