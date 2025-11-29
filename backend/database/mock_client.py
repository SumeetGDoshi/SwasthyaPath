"""
Mock Database Client for Demo Mode
In-memory storage that mimics Supabase operations
"""

import uuid
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from copy import deepcopy

# Test validity periods in days (how long each test result is typically valid)
TEST_VALIDITY_DAYS = {
    "HbA1c": 90,
    "Lipid Profile": 180,
    "LDL Cholesterol": 180,
    "HDL Cholesterol": 180,
    "Triglycerides": 180,
    "CBC": 90,
    "Hemoglobin": 90,
    "Thyroid Panel": 180,
    "TSH": 180,
    "T3": 180,
    "T4": 180,
    "Vitamin D": 90,
    "Vitamin B12": 180,
    "Fasting Blood Sugar": 30,
    "Blood Pressure": 7,
    "Creatinine": 90,
    "Uric Acid": 90,
    "default": 90
}


class MockSupabaseClient:
    """In-memory database client for demo mode"""
    
    def __init__(self):
        self.storage_bucket = "medical-reports"
        
        # Initialize in-memory storage
        self._users: Dict[str, Dict] = {}
        self._reports: Dict[str, Dict] = {}
        self._test_results: Dict[str, Dict] = {}
        self._duplicate_alerts: Dict[str, Dict] = {}
        self._images: Dict[str, bytes] = {}
        self._refresh_tokens: Dict[str, Dict] = {}
        
        # Pre-load demo data
        self._setup_demo_data()
    
    def _generate_id(self) -> str:
        """Generate a unique ID"""
        return str(uuid.uuid4())
    
    def _setup_demo_data(self):
        """Pre-populate with demo data"""
        from utils.auth_utils import hash_password
        
        demo_user_id = "demo-user-123"
        
        # Create demo user with authentication credentials
        self._users[demo_user_id] = {
            "id": demo_user_id,
            "email": "demo@swasthyapath.com",
            "password_hash": hash_password("demo123"),
            "name": "Rahul Kumar",
            "phone": "+91 98765 43210",
            "age": 42,
            "gender": "Male",
            "is_active": True,
            "email_verified": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # Demo reports and tests - using 2025 dates for current validity
        demo_data = [
            {
                "report_type": "lab_test",
                "report_date": "2025-11-29",
                "hospital_name": "Dr. Lal PathLabs",
                "doctor_name": "Dr. Sharma",
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
                ]
            },
            {
                "report_type": "lab_test",
                "report_date": "2025-10-15",
                "hospital_name": "Apollo Hospitals",
                "doctor_name": "Dr. Gupta",
                "tests": [
                    {
                        "test_name": "HbA1c",
                        "test_value": "5.9",
                        "test_unit": "%",
                        "reference_range": "4.0-5.6%",
                        "status": "abnormal",
                        "category": "blood"
                    },
                    {
                        "test_name": "Fasting Blood Sugar",
                        "test_value": "112",
                        "test_unit": "mg/dL",
                        "reference_range": "70-100 mg/dL",
                        "status": "abnormal",
                        "category": "blood"
                    }
                ]
            },
            {
                "report_type": "lab_test",
                "report_date": "2025-09-20",
                "hospital_name": "Fortis Hospital",
                "doctor_name": "Dr. Patel",
                "tests": [
                    {
                        "test_name": "CBC",
                        "test_value": "Normal",
                        "test_unit": "",
                        "reference_range": "Within normal limits",
                        "status": "normal",
                        "category": "blood"
                    },
                    {
                        "test_name": "Hemoglobin",
                        "test_value": "14.2",
                        "test_unit": "g/dL",
                        "reference_range": "13.5-17.5 g/dL",
                        "status": "normal",
                        "category": "blood"
                    }
                ]
            },
            {
                "report_type": "lab_test",
                "report_date": "2025-08-15",
                "hospital_name": "AIIMS",
                "doctor_name": "Dr. Verma",
                "tests": [
                    {
                        "test_name": "Thyroid Panel",
                        "test_value": "TSH: 2.5",
                        "test_unit": "mIU/L",
                        "reference_range": "0.4-4.0 mIU/L",
                        "status": "normal",
                        "category": "blood"
                    },
                    {
                        "test_name": "T3",
                        "test_value": "1.2",
                        "test_unit": "ng/mL",
                        "reference_range": "0.8-2.0 ng/mL",
                        "status": "normal",
                        "category": "blood"
                    },
                    {
                        "test_name": "T4",
                        "test_value": "7.5",
                        "test_unit": "µg/dL",
                        "reference_range": "5.0-12.0 µg/dL",
                        "status": "normal",
                        "category": "blood"
                    }
                ]
            },
            {
                "report_type": "lab_test",
                "report_date": "2024-11-01",
                "hospital_name": "Medanta Hospital",
                "doctor_name": "Dr. Singh",
                "tests": [
                    {
                        "test_name": "Vitamin D",
                        "test_value": "18",
                        "test_unit": "ng/mL",
                        "reference_range": "30-100 ng/mL",
                        "status": "abnormal",
                        "category": "blood"
                    },
                    {
                        "test_name": "Vitamin B12",
                        "test_value": "450",
                        "test_unit": "pg/mL",
                        "reference_range": "200-900 pg/mL",
                        "status": "normal",
                        "category": "blood"
                    }
                ]
            }
        ]
        
        for report_data in demo_data:
            report_id = self._generate_id()
            now = datetime.now().isoformat() + "Z"
            
            self._reports[report_id] = {
                "id": report_id,
                "user_id": demo_user_id,
                "report_type": report_data["report_type"],
                "report_date": report_data["report_date"],
                "hospital_name": report_data["hospital_name"],
                "doctor_name": report_data["doctor_name"],
                "raw_image_url": None,
                "extracted_data": {"tests": report_data["tests"]},
                "created_at": now
            }
            
            for test in report_data["tests"]:
                test_id = self._generate_id()
                self._test_results[test_id] = {
                    "id": test_id,
                    "report_id": report_id,
                    "user_id": demo_user_id,
                    "test_name": test["test_name"],
                    "test_date": report_data["report_date"],
                    "test_category": test.get("category", "blood"),
                    "test_value": test.get("test_value"),
                    "test_unit": test.get("test_unit"),
                    "reference_range": test.get("reference_range"),
                    "status": test.get("status", "normal"),
                    "created_at": now
                }
        
        # Add a sample duplicate alert
        alert_id = self._generate_id()
        self._duplicate_alerts[alert_id] = {
            "id": alert_id,
            "user_id": demo_user_id,
            "new_test_name": "HbA1c",
            "original_test_date": "2025-10-15",
            "days_since_original": 45,
            "alert_message": "⚠️ Duplicate Alert: HbA1c was done 45 days ago. This test is typically valid for 90 days. You could save ₹700 by using the previous result.",
            "savings_amount": 700.0,
            "decision": "skip",
            "created_at": datetime.now().isoformat() + "Z"
        }
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, name: str, age: Optional[int] = None, 
                    gender: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user"""
        uid = user_id or self._generate_id()
        now = datetime.now().isoformat() + "Z"
        
        user = {
            "id": uid,
            "name": name,
            "age": age,
            "gender": gender,
            "created_at": now
        }
        self._users[uid] = user
        return deepcopy(user)
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        user = self._users.get(user_id)
        return deepcopy(user) if user else None
    
    def get_or_create_user(self, user_id: str, name: str = "Demo User", 
                           age: int = 35, gender: str = "Unknown") -> Dict[str, Any]:
        """Get existing user or create new one"""
        user = self.get_user(user_id)
        if not user:
            user = self.create_user(name=name, age=age, gender=gender, user_id=user_id)
        return user
    
    # ==================== AUTHENTICATION OPERATIONS ====================
    
    def create_auth_user(self, email: str, password_hash: str, name: str, 
                        phone: Optional[str] = None) -> Dict[str, Any]:
        """Create a new authenticated user"""
        uid = self._generate_id()
        now = datetime.now().isoformat() + "Z"
        
        user = {
            "id": uid,
            "email": email,
            "password_hash": password_hash,
            "name": name,
            "phone": phone,
            "age": None,
            "gender": None,
            "is_active": True,
            "email_verified": False,
            "created_at": now
        }
        self._users[uid] = user
        return deepcopy(user)
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        for user in self._users.values():
            if user.get("email") == email:
                return deepcopy(user)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID (for auth middleware)"""
        return self.get_user(user_id)
    
    def store_refresh_token(self, user_id: str, token: str, expires_at: datetime) -> Dict[str, Any]:
        """Store a refresh token"""
        token_id = self._generate_id()
        now = datetime.now().isoformat() + "Z"
        
        token_data = {
            "id": token_id,
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at.isoformat() if isinstance(expires_at, datetime) else expires_at,
            "created_at": now,
            "revoked": False
        }
        self._refresh_tokens[token_id] = token_data
        return deepcopy(token_data)
    
    def get_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get refresh token by token string"""
        for token_data in self._refresh_tokens.values():
            if token_data["token"] == token and not token_data["revoked"]:
                return deepcopy(token_data)
        return None
    
    def revoke_refresh_token(self, token: str) -> bool:
        """Revoke a refresh token (logout)"""
        for token_data in self._refresh_tokens.values():
            if token_data["token"] == token:
                token_data["revoked"] = True
                return True
        return False
    
    # ==================== REPORT OPERATIONS ====================
    
    def create_report(self, user_id: str, report_type: str, report_date: date,
                      hospital_name: Optional[str] = None, doctor_name: Optional[str] = None,
                      raw_image_url: Optional[str] = None, 
                      extracted_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new medical report"""
        report_id = self._generate_id()
        now = datetime.now().isoformat() + "Z"
        
        report = {
            "id": report_id,
            "user_id": user_id,
            "report_type": report_type,
            "report_date": report_date.isoformat() if isinstance(report_date, date) else report_date,
            "hospital_name": hospital_name,
            "doctor_name": doctor_name,
            "raw_image_url": raw_image_url,
            "extracted_data": extracted_data,
            "created_at": now
        }
        self._reports[report_id] = report
        return deepcopy(report)
    
    def get_reports(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all reports for a user"""
        reports = [
            deepcopy(r) for r in self._reports.values() 
            if r["user_id"] == user_id
        ]
        return sorted(reports, key=lambda x: x.get("report_date", ""), reverse=True)
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific report"""
        report = self._reports.get(report_id)
        return deepcopy(report) if report else None
    
    # ==================== TEST RESULT OPERATIONS ====================
    
    def create_test_result(self, report_id: str, user_id: str, test_name: str,
                           test_date: date, test_category: str = "other",
                           test_value: Optional[str] = None, test_unit: Optional[str] = None,
                           reference_range: Optional[str] = None, 
                           status: str = "normal") -> Dict[str, Any]:
        """Create a new test result"""
        test_id = self._generate_id()
        now = datetime.now().isoformat() + "Z"
        
        test_result = {
            "id": test_id,
            "report_id": report_id,
            "user_id": user_id,
            "test_name": test_name,
            "test_date": test_date.isoformat() if isinstance(test_date, date) else test_date,
            "test_category": test_category,
            "test_value": test_value,
            "test_unit": test_unit,
            "reference_range": reference_range,
            "status": status,
            "created_at": now
        }
        self._test_results[test_id] = test_result
        return deepcopy(test_result)
    
    def get_test_results(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all test results for a user"""
        results = [
            deepcopy(r) for r in self._test_results.values() 
            if r["user_id"] == user_id
        ]
        return sorted(results, key=lambda x: x.get("test_date", ""), reverse=True)
    
    def get_test_history(self, user_id: str, test_name: str) -> List[Dict[str, Any]]:
        """Get history of a specific test for a user"""
        results = [
            deepcopy(r) for r in self._test_results.values() 
            if r["user_id"] == user_id and r["test_name"] == test_name
        ]
        return sorted(results, key=lambda x: x.get("test_date", ""), reverse=True)
    
    def get_latest_test(self, user_id: str, test_name: str) -> Optional[Dict[str, Any]]:
        """Get the most recent instance of a specific test"""
        history = self.get_test_history(user_id, test_name)
        return history[0] if history else None
    
    # ==================== DUPLICATE ALERT OPERATIONS ====================
    
    def create_duplicate_alert(self, user_id: str, new_test_name: str,
                               original_test_date: date, days_since_original: int,
                               alert_message: str, savings_amount: float = 0.0,
                               decision: str = "pending") -> Dict[str, Any]:
        """Create a duplicate alert"""
        alert_id = self._generate_id()
        now = datetime.now().isoformat() + "Z"
        
        alert = {
            "id": alert_id,
            "user_id": user_id,
            "new_test_name": new_test_name,
            "original_test_date": original_test_date.isoformat() if isinstance(original_test_date, date) else original_test_date,
            "days_since_original": days_since_original,
            "alert_message": alert_message,
            "savings_amount": savings_amount,
            "decision": decision,
            "created_at": now
        }
        self._duplicate_alerts[alert_id] = alert
        return deepcopy(alert)
    
    def update_duplicate_decision(self, alert_id: str, decision: str) -> Dict[str, Any]:
        """Update the decision for a duplicate alert"""
        if alert_id in self._duplicate_alerts:
            self._duplicate_alerts[alert_id]["decision"] = decision
            return deepcopy(self._duplicate_alerts[alert_id])
        return None
    
    def get_duplicate_alerts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all duplicate alerts for a user"""
        alerts = [
            deepcopy(a) for a in self._duplicate_alerts.values() 
            if a["user_id"] == user_id
        ]
        return sorted(alerts, key=lambda x: x.get("created_at", ""), reverse=True)
    
    def get_savings_summary(self, user_id: str) -> Dict[str, Any]:
        """Calculate total savings from skipped duplicates"""
        alerts = [
            a for a in self._duplicate_alerts.values() 
            if a["user_id"] == user_id and a["decision"] == "skip"
        ]
        
        total_savings = sum(alert.get("savings_amount", 0) for alert in alerts)
        
        return {
            "total_savings": total_savings,
            "tests_skipped": len(alerts),
            "breakdown": [
                {
                    "test_name": alert["new_test_name"],
                    "date_skipped": alert["created_at"][:10],
                    "amount_saved": alert["savings_amount"]
                }
                for alert in alerts
            ]
        }
    
    # ==================== STORAGE OPERATIONS ====================
    
    def upload_image(self, file_bytes: bytes, filename: str, user_id: str) -> str:
        """Upload an image to mock storage and return a fake URL"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{user_id}/{timestamp}_{filename}"
        
        self._images[file_path] = file_bytes
        
        # Return a mock URL
        return f"https://demo.swasthyapath.local/storage/{file_path}"
    
    # ==================== TIMELINE OPERATIONS ====================
    
    def get_timeline(self, user_id: str) -> List[Dict[str, Any]]:
        """Get timeline entries for a user with duplicate indicators"""
        test_results = self.get_test_results(user_id)
        reports = {r["id"]: r for r in self.get_reports(user_id)}
        
        duplicate_alerts = self.get_duplicate_alerts(user_id)
        duplicate_tests = {
            (alert["new_test_name"], alert["created_at"][:10])
            for alert in duplicate_alerts
        }
        
        timeline = []
        for test in test_results:
            report = reports.get(test.get("report_id", ""), {})
            
            # Calculate valid_until based on test type
            test_name = test["test_name"]
            validity_days = TEST_VALIDITY_DAYS.get(test_name, TEST_VALIDITY_DAYS["default"])
            test_date = datetime.strptime(test["test_date"], "%Y-%m-%d").date()
            valid_until = (test_date + timedelta(days=validity_days)).isoformat()
            
            entry = {
                "id": test["id"],
                "test_name": test["test_name"],
                "test_value": test.get("test_value"),
                "test_unit": test.get("test_unit"),
                "test_date": test["test_date"],
                "valid_until": valid_until,
                "status": test.get("status", "normal"),
                "hospital_name": report.get("hospital_name"),
                "is_duplicate": (test["test_name"], test["test_date"]) in duplicate_tests,
                "category": test.get("test_category", "other"),
                "reference_range": test.get("reference_range"),
            }
            timeline.append(entry)
        
        return timeline
    
    # ==================== DEMO DATA ====================
    
    def setup_demo_data(self) -> Dict[str, Any]:
        """Return info about existing demo data"""
        demo_user_id = "demo-user-123"
        
        reports = self.get_reports(demo_user_id)
        
        return {
            "success": True,
            "user_id": demo_user_id,
            "message": "Demo data loaded (in-memory mode)",
            "reports_created": len(reports)
        }


