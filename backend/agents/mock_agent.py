"""
Mock Report Intelligence Agent for Demo Mode
Returns realistic sample analysis results without calling Anthropic API
"""

import random
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional

# Import constants from the real agent
from agents.report_agent import (
    INDIAN_TEST_COSTS, 
    VALIDITY_PERIODS, 
    TEST_NAME_ALIASES
)


# Sample report analysis results for demo
SAMPLE_ANALYSES = [
    {
        "report_type": "lab_test",
        "hospital_name": "Apollo Diagnostics",
        "doctor_name": "Dr. Priya Sharma",
        "patient_name": "Patient",
        "report_date": None,  # Will be set dynamically
        "tests": [
            {
                "test_name": "HbA1c",
                "test_value": "6.2",
                "test_unit": "%",
                "reference_range": "4.0-5.6%",
                "status": "abnormal",
                "category": "blood"
            },
            {
                "test_name": "Fasting Blood Sugar",
                "test_value": "118",
                "test_unit": "mg/dL",
                "reference_range": "70-100 mg/dL",
                "status": "abnormal",
                "category": "blood"
            }
        ],
        "raw_text": "Diabetic profile shows pre-diabetic indicators. HbA1c slightly elevated.",
        "confidence_score": 0.92
    },
    {
        "report_type": "lab_test",
        "hospital_name": "Dr. Lal PathLabs",
        "doctor_name": "Dr. Rajesh Kumar",
        "patient_name": "Patient",
        "report_date": None,
        "tests": [
            {
                "test_name": "Lipid Profile",
                "test_value": "Total: 215",
                "test_unit": "mg/dL",
                "reference_range": "<200 mg/dL",
                "status": "abnormal",
                "category": "blood"
            },
            {
                "test_name": "LDL Cholesterol",
                "test_value": "142",
                "test_unit": "mg/dL",
                "reference_range": "<100 mg/dL",
                "status": "abnormal",
                "category": "blood"
            },
            {
                "test_name": "HDL Cholesterol",
                "test_value": "48",
                "test_unit": "mg/dL",
                "reference_range": ">40 mg/dL",
                "status": "normal",
                "category": "blood"
            },
            {
                "test_name": "Triglycerides",
                "test_value": "168",
                "test_unit": "mg/dL",
                "reference_range": "<150 mg/dL",
                "status": "abnormal",
                "category": "blood"
            }
        ],
        "raw_text": "Lipid panel shows elevated total cholesterol and LDL. HDL is borderline normal.",
        "confidence_score": 0.95
    },
    {
        "report_type": "lab_test",
        "hospital_name": "Thyrocare",
        "doctor_name": "Dr. Meena Patel",
        "patient_name": "Patient",
        "report_date": None,
        "tests": [
            {
                "test_name": "TSH",
                "test_value": "3.2",
                "test_unit": "mIU/L",
                "reference_range": "0.4-4.0 mIU/L",
                "status": "normal",
                "category": "blood"
            },
            {
                "test_name": "T3",
                "test_value": "1.1",
                "test_unit": "ng/mL",
                "reference_range": "0.8-2.0 ng/mL",
                "status": "normal",
                "category": "blood"
            },
            {
                "test_name": "T4",
                "test_value": "8.2",
                "test_unit": "µg/dL",
                "reference_range": "5.0-12.0 µg/dL",
                "status": "normal",
                "category": "blood"
            }
        ],
        "raw_text": "Thyroid function tests within normal limits.",
        "confidence_score": 0.97
    },
    {
        "report_type": "lab_test",
        "hospital_name": "SRL Diagnostics",
        "doctor_name": "Dr. Amit Verma",
        "patient_name": "Patient",
        "report_date": None,
        "tests": [
            {
                "test_name": "CBC",
                "test_value": "Complete",
                "test_unit": "",
                "reference_range": "See individual values",
                "status": "normal",
                "category": "blood"
            },
            {
                "test_name": "Hemoglobin",
                "test_value": "13.8",
                "test_unit": "g/dL",
                "reference_range": "13.5-17.5 g/dL",
                "status": "normal",
                "category": "blood"
            },
            {
                "test_name": "ESR",
                "test_value": "12",
                "test_unit": "mm/hr",
                "reference_range": "0-20 mm/hr",
                "status": "normal",
                "category": "blood"
            }
        ],
        "raw_text": "Complete blood count shows normal values. No signs of anemia or infection.",
        "confidence_score": 0.94
    },
    {
        "report_type": "lab_test",
        "hospital_name": "Metropolis Healthcare",
        "doctor_name": "Dr. Sunita Reddy",
        "patient_name": "Patient",
        "report_date": None,
        "tests": [
            {
                "test_name": "Vitamin D",
                "test_value": "22",
                "test_unit": "ng/mL",
                "reference_range": "30-100 ng/mL",
                "status": "abnormal",
                "category": "blood"
            },
            {
                "test_name": "Vitamin B12",
                "test_value": "380",
                "test_unit": "pg/mL",
                "reference_range": "200-900 pg/mL",
                "status": "normal",
                "category": "blood"
            },
            {
                "test_name": "Calcium",
                "test_value": "9.2",
                "test_unit": "mg/dL",
                "reference_range": "8.5-10.5 mg/dL",
                "status": "normal",
                "category": "blood"
            }
        ],
        "raw_text": "Vitamin D deficiency noted. Supplementation recommended. B12 and Calcium normal.",
        "confidence_score": 0.91
    },
    {
        "report_type": "lab_test",
        "hospital_name": "Fortis Hospital",
        "doctor_name": "Dr. Ravi Gupta",
        "patient_name": "Patient",
        "report_date": None,
        "tests": [
            {
                "test_name": "Liver Function Test",
                "test_value": "Panel",
                "test_unit": "",
                "reference_range": "See values",
                "status": "normal",
                "category": "blood"
            },
            {
                "test_name": "Kidney Function Test",
                "test_value": "Panel",
                "test_unit": "",
                "reference_range": "See values",
                "status": "normal",
                "category": "blood"
            },
            {
                "test_name": "Creatinine",
                "test_value": "0.9",
                "test_unit": "mg/dL",
                "reference_range": "0.7-1.3 mg/dL",
                "status": "normal",
                "category": "blood"
            },
            {
                "test_name": "Urea",
                "test_value": "28",
                "test_unit": "mg/dL",
                "reference_range": "15-40 mg/dL",
                "status": "normal",
                "category": "blood"
            }
        ],
        "raw_text": "Liver and kidney function tests within normal limits.",
        "confidence_score": 0.93
    }
]


class MockReportIntelligenceAgent:
    """Mock AI Agent for demo mode - returns sample analysis results"""
    
    def __init__(self):
        self.model = "mock-demo-mode"
        print("🔔 Running in DEMO MODE - AI responses are simulated")
    
    def analyze_report(
        self,
        image_base64: str,
        media_type: str = "image/jpeg",
        user_context: Optional[str] = None,
        test_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Return a sample analysis result for demo purposes
        """
        # Pick a random sample analysis
        analysis = random.choice(SAMPLE_ANALYSES).copy()
        analysis["tests"] = [t.copy() for t in analysis["tests"]]
        
        # Set the report date to today
        analysis["report_date"] = date.today().isoformat()
        
        # Add some context-based customization
        if user_context:
            analysis["raw_text"] += f" User context: {user_context}"
        
        return analysis
    
    def analyze_text_report(
        self,
        text: str,
        user_context: Optional[str] = None,
        test_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Return a sample analysis for text-based reports
        """
        # Pick a random sample analysis
        analysis = random.choice(SAMPLE_ANALYSES).copy()
        analysis["tests"] = [t.copy() for t in analysis["tests"]]
        
        # Set the report date to today
        analysis["report_date"] = date.today().isoformat()
        
        # Try to extract some info from the text
        text_lower = text.lower()
        
        if "diabetes" in text_lower or "hba1c" in text_lower or "blood sugar" in text_lower:
            analysis = SAMPLE_ANALYSES[0].copy()
            analysis["tests"] = [t.copy() for t in SAMPLE_ANALYSES[0]["tests"]]
        elif "lipid" in text_lower or "cholesterol" in text_lower:
            analysis = SAMPLE_ANALYSES[1].copy()
            analysis["tests"] = [t.copy() for t in SAMPLE_ANALYSES[1]["tests"]]
        elif "thyroid" in text_lower or "tsh" in text_lower:
            analysis = SAMPLE_ANALYSES[2].copy()
            analysis["tests"] = [t.copy() for t in SAMPLE_ANALYSES[2]["tests"]]
        elif "cbc" in text_lower or "hemoglobin" in text_lower or "blood count" in text_lower:
            analysis = SAMPLE_ANALYSES[3].copy()
            analysis["tests"] = [t.copy() for t in SAMPLE_ANALYSES[3]["tests"]]
        elif "vitamin" in text_lower:
            analysis = SAMPLE_ANALYSES[4].copy()
            analysis["tests"] = [t.copy() for t in SAMPLE_ANALYSES[4]["tests"]]
        elif "liver" in text_lower or "kidney" in text_lower:
            analysis = SAMPLE_ANALYSES[5].copy()
            analysis["tests"] = [t.copy() for t in SAMPLE_ANALYSES[5]["tests"]]
        
        analysis["report_date"] = date.today().isoformat()
        
        return analysis
    
    def _normalize_test_name(self, test_name: str) -> str:
        """Normalize test name to standard format"""
        if not test_name:
            return "Unknown Test"
        
        lower_name = test_name.lower().strip()
        
        if lower_name in TEST_NAME_ALIASES:
            return TEST_NAME_ALIASES[lower_name]
        
        for standard_name in INDIAN_TEST_COSTS.keys():
            if lower_name == standard_name.lower():
                return standard_name
        
        return test_name.strip().title()
    
    def detect_duplicate(
        self,
        test_name: str,
        test_date: date,
        test_history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Check if a test is a potential duplicate based on validity periods
        """
        normalized_name = self._normalize_test_name(test_name)
        validity_days = VALIDITY_PERIODS.get(normalized_name, VALIDITY_PERIODS["default"])
        
        # Find the most recent instance of this test
        latest_test = None
        for test in test_history:
            hist_name = self._normalize_test_name(test.get("test_name", ""))
            if hist_name == normalized_name:
                hist_date_str = test.get("test_date", "")
                try:
                    if isinstance(hist_date_str, str):
                        hist_date = datetime.strptime(hist_date_str[:10], "%Y-%m-%d").date()
                    elif isinstance(hist_date_str, date):
                        hist_date = hist_date_str
                    else:
                        continue
                    
                    if latest_test is None or hist_date > latest_test["date"]:
                        latest_test = {
                            "date": hist_date,
                            "value": test.get("test_value"),
                            "hospital": test.get("hospital_name"),
                        }
                except (ValueError, TypeError):
                    continue
        
        if not latest_test:
            return {
                "is_duplicate": False,
                "test_name": normalized_name,
                "message": "No previous test found",
                "potential_savings": 0,
            }
        
        days_since = (test_date - latest_test["date"]).days
        
        if days_since <= validity_days:
            savings = self.calculate_savings(normalized_name)
            
            return {
                "is_duplicate": True,
                "test_name": normalized_name,
                "original_date": latest_test["date"],
                "original_value": latest_test["value"],
                "days_since": days_since,
                "validity_period": validity_days,
                "days_remaining": validity_days - days_since,
                "potential_savings": savings,
                "message": f"⚠️ Duplicate Alert: {normalized_name} was done {days_since} days ago. "
                          f"This test is typically valid for {validity_days} days. "
                          f"You could save ₹{savings:,.0f} by using the previous result.",
            }
        
        return {
            "is_duplicate": False,
            "test_name": normalized_name,
            "original_date": latest_test["date"],
            "days_since": days_since,
            "validity_period": validity_days,
            "message": f"Previous {normalized_name} was {days_since} days ago (validity: {validity_days} days). New test recommended.",
            "potential_savings": 0,
        }
    
    def calculate_savings(self, test_name: str) -> float:
        """Calculate potential savings for a test"""
        normalized_name = self._normalize_test_name(test_name)
        return INDIAN_TEST_COSTS.get(normalized_name, 500)
    
    def get_test_cost(self, test_name: str) -> float:
        """Get the cost of a specific test"""
        normalized_name = self._normalize_test_name(test_name)
        return INDIAN_TEST_COSTS.get(normalized_name, 500)
    
    def get_validity_period(self, test_name: str) -> int:
        """Get the validity period of a specific test in days"""
        normalized_name = self._normalize_test_name(test_name)
        return VALIDITY_PERIODS.get(normalized_name, VALIDITY_PERIODS["default"])


