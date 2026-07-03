"""
Data utilities for MSME Financial Health Platform
- Generate sample data for demo
- Load data from CSV uploads (businesses, applications)
- Convert CSV rows into internal dictionary format
"""

import random
import re  # <-- fixed import
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union

# ---------- SAMPLE DATA GENERATORS ----------
def generate_sample_businesses() -> List[Dict[str, Any]]:
    """Generate a list of sample MSME businesses with financial data."""
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
        },
        {
            "name": "Goyal Exports",
            "gstin": "44LMNO1234Z3Z5",
            "industry": "Export/Import",
            "constitution": "Sole Proprietorship",
            "location": "Delhi, NCR",
            "employees": 8,
            "years": 6,
            "revenue": [15, 16, 18, 17, 20, 22, 21, 25, 27, 24, 28, 30],
            "cashflow": [10, 11, 12, 10, 14, 16, 15, 18, 20, 18, 22, 24],
            "gst_score": 82,
            "score": 82,
            "status": "Active",
            "upi_transactions": 6500,
            "upi_collections": 0.92,
            "active_customers": 560
        },
        {
            "name": "Rathi Traders",
            "gstin": "55PQRS1234X9Y1",
            "industry": "Wholesale Trading",
            "constitution": "Partnership",
            "location": "Ahmedabad, Gujarat",
            "employees": 18,
            "years": 10,
            "revenue": [25, 28, 30, 26, 33, 35, 32, 38, 40, 36, 42, 45],
            "cashflow": [16, 18, 20, 17, 22, 24, 21, 26, 28, 25, 30, 32],
            "gst_score": 76,
            "score": 76,
            "status": "Active",
            "upi_transactions": 4200,
            "upi_collections": 0.75,
            "active_customers": 410
        }
    ]

def generate_sample_applications() -> List[Dict[str, Any]]:
    """Generate a list of sample loan applications."""
    return [
        {"id": "APP-2024-045", "business": "Apex Manufacturing Solutions", "gstin": "29AAHC...E1Z8",
         "amount": 42.5, "score": 92, "status": "Pending Review", "date": "2024-06-01"},
        {"id": "APP-2024-044", "business": "Pioneer Engineering Works", "gstin": "19BBJK...F2Z9",
         "amount": 65.0, "score": 78, "status": "Approved", "date": "2024-05-30"},
        {"id": "APP-2024-043", "business": "Sai Industries Pvt Ltd", "gstin": "33CCMN...G3Z2",
         "amount": 18.0, "score": 45, "status": "Rejected", "date": "2024-05-28"},
        {"id": "APP-2024-042", "business": "Goyal Exports", "gstin": "44LMNO...Z3Z5",
         "amount": 35.0, "score": 82, "status": "Under Verification", "date": "2024-05-27"},
        {"id": "APP-2024-041", "business": "Rathi Traders", "gstin": "55PQRS...X9Y1",
         "amount": 28.5, "score": 76, "status": "Approved", "date": "2024-05-25"}
    ]

def generate_sample_alerts() -> List[Dict[str, Any]]:
    """Generate a list of sample alerts/notifications."""
    return [
        {"time": "2 hours ago", "title": "⚠️ High Risk Alert", "desc": "Apex Manufacturing: Cash flow dropped 22% this month", "priority": "high"},
        {"time": "4 hours ago", "title": "✅ Document Verification", "desc": "Sai Industries - All documents verified successfully", "priority": "low"},
        {"time": "Yesterday", "title": "📊 Monthly Report Ready", "desc": "June 2024 portfolio report is available for download", "priority": "medium"},
        {"time": "Yesterday", "title": "🎯 Pre-Approved Offers", "desc": "3 new MSMEs are eligible for pre-approved loans", "priority": "medium"},
        {"time": "2 days ago", "title": "⚠️ Compliance Reminder", "desc": "Goyal Exports - GST filing due in 3 days", "priority": "high"}
    ]

# ---------- CSV LOADERS ----------
def load_businesses_from_csv(file) -> List[Dict[str, Any]]:
    """
    Load business data from a CSV file.
    Expected columns:
        name, gstin, industry, constitution, location, employees, years,
        revenue (comma-separated numbers), cashflow (comma-separated),
        gst_score, score, status, upi_transactions, upi_collections, active_customers
    """
    df = pd.read_csv(file)
    businesses = []
    for _, row in df.iterrows():
        revenue = _parse_list(row.get('revenue', ''))
        cashflow = _parse_list(row.get('cashflow', ''))
        if not revenue:
            revenue = list(np.random.randint(10, 50, 12))
        if not cashflow:
            cashflow = list(np.random.randint(5, 30, 12))

        biz = {
            "name": str(row.get('name', 'Unknown')),
            "gstin": str(row.get('gstin', '')),
            "industry": str(row.get('industry', '')),
            "constitution": str(row.get('constitution', '')),
            "location": str(row.get('location', '')),
            "employees": int(row.get('employees', 0)),
            "years": int(row.get('years', 0)),
            "revenue": revenue,
            "cashflow": cashflow,
            "gst_score": float(row.get('gst_score', 70)),
            "score": float(row.get('score', 70)),
            "status": str(row.get('status', 'Active')),
            "upi_transactions": int(row.get('upi_transactions', 0)),
            "upi_collections": float(row.get('upi_collections', 0.0)),
            "active_customers": int(row.get('active_customers', 0))
        }
        businesses.append(biz)
    return businesses

def load_applications_from_csv(file) -> List[Dict[str, Any]]:
    """Load loan applications from CSV."""
    df = pd.read_csv(file)
    apps = []
    for _, row in df.iterrows():
        app = {
            "id": str(row.get('id', '')),
            "business": str(row.get('business', '')),
            "gstin": str(row.get('gstin', '')),
            "amount": float(row.get('amount', 0)),
            "score": float(row.get('score', 0)),
            "status": str(row.get('status', 'Pending Review')),
            "date": str(row.get('date', datetime.now().strftime('%Y-%m-%d')))
        }
        apps.append(app)
    return apps

def load_alerts_from_csv(file) -> List[Dict[str, Any]]:
    """Load alerts from CSV (optional)."""
    df = pd.read_csv(file)
    alerts = []
    for _, row in df.iterrows():
        alert = {
            "time": str(row.get('time', '')),
            "title": str(row.get('title', '')),
            "desc": str(row.get('desc', '')),
            "priority": str(row.get('priority', 'medium'))
        }
        alerts.append(alert)
    return alerts

# ---------- HELPER: Parse comma-separated list ----------
def _parse_list(value: Union[str, List, None]) -> List[float]:
    """Convert a comma-separated string or list to a list of floats."""
    if value is None:
        return []
    if isinstance(value, list):
        return [float(v) for v in value]
    if isinstance(value, str):
        parts = re.split(r'[;,]\s*', value)
        if len(parts) == 1 and ' ' in parts[0]:
            parts = parts[0].split()
        try:
            return [float(v.strip()) for v in parts if v.strip()]
        except:
            return []
    return []

# ---------- SAVE SAMPLE DATA TO CSV (optional) ----------
def save_sample_data_to_csv(businesses_file="data/sample_businesses.csv",
                            apps_file="data/sample_applications.csv",
                            alerts_file="data/sample_alerts.csv"):
    """Export sample data to CSV files for template use."""
    import csv
    # Businesses
    businesses = generate_sample_businesses()
    with open(businesses_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name','gstin','industry','constitution','location',
                         'employees','years','revenue','cashflow','gst_score',
                         'score','status','upi_transactions','upi_collections',
                         'active_customers'])
        for b in businesses:
            writer.writerow([
                b['name'], b['gstin'], b['industry'], b['constitution'],
                b['location'], b['employees'], b['years'],
                ','.join(map(str, b['revenue'])), ','.join(map(str, b['cashflow'])),
                b['gst_score'], b['score'], b['status'],
                b['upi_transactions'], b['upi_collections'], b['active_customers']
            ])
    # Applications
    apps = generate_sample_applications()
    with open(apps_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id','business','gstin','amount','score','status','date'])
        for a in apps:
            writer.writerow([a['id'], a['business'], a['gstin'], a['amount'],
                             a['score'], a['status'], a['date']])
    # Alerts
    alerts = generate_sample_alerts()
    with open(alerts_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['time','title','desc','priority'])
        for a in alerts:
            writer.writerow([a['time'], a['title'], a['desc'], a['priority']])
