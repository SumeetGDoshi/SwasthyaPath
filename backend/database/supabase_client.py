"""
Supabase client for Swasthya Path - Database operations
"""

import os
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SupabaseClient:
    """Wrapper class for Supabase operations"""
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        self.client: Client = create_client(url, key)
        self.storage_bucket = "medical-reports"
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, name: str, age: Optional[int] = None, 
                    gender: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user"""
        data = {"name": name}
        if age:
            data["age"] = age
        if gender:
            data["gender"] = gender
        if user_id:
            data["id"] = user_id
            
        result = self.client.table("users").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        result = self.client.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    
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
        data = {
            "email": email,
            "password_hash": password_hash,
            "name": name,
            "is_active": True,
            "email_verified": False
        }
        if phone:
            data["phone"] = phone
            
        result = self.client.table("users").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        result = self.client.table("users").select("*").eq("email", email).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None

    def verify_refresh_token(self, token: str) -> bool:
        """Verify if a refresh token exists and is valid"""
        result = self.client.table("refresh_tokens").select("*").eq("token", token).execute()
        if result.data and len(result.data) > 0:
            # Check if revoked
            if result.data[0].get("revoked", False):
                return False
            # Check expiry
            expires_at = datetime.fromisoformat(result.data[0]["expires_at"].replace("Z", "+00:00"))
            if expires_at < datetime.now(expires_at.tzinfo):
                return False
            return True
        return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID (for auth middleware)"""
        return self.get_user(user_id)
    
    def store_refresh_token(self, user_id: str, token: str, expires_at: datetime) -> Dict[str, Any]:
        """Store a refresh token"""
        data = {
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at.isoformat(),
            "revoked": False
        }
        result = self.client.table("refresh_tokens").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get refresh token by token string"""
        result = self.client.table("refresh_tokens")\
            .select("*")\
            .eq("token", token)\
            .eq("revoked", False)\
            .execute()
        return result.data[0] if result.data else None
    
    def revoke_refresh_token(self, token: str) -> bool:
        """Revoke a refresh token (logout)"""
        result = self.client.table("refresh_tokens")\
            .update({"revoked": True})\
            .eq("token", token)\
            .execute()
        return bool(result.data)
    
    # ==================== REPORT OPERATIONS ====================
    
    def create_report(self, user_id: str, report_type: str, report_date: date,
                      hospital_name: Optional[str] = None, doctor_name: Optional[str] = None,
                      raw_image_url: Optional[str] = None, 
                      extracted_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new medical report"""
        data = {
            "user_id": user_id,
            "report_type": report_type,
            "report_date": report_date.isoformat() if isinstance(report_date, date) else report_date,
        }
        if hospital_name:
            data["hospital_name"] = hospital_name
        if doctor_name:
            data["doctor_name"] = doctor_name
        if raw_image_url:
            data["raw_image_url"] = raw_image_url
        if extracted_data:
            data["extracted_data"] = extracted_data
            
        result = self.client.table("medical_reports").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_reports(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all reports for a user"""
        result = self.client.table("medical_reports")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("report_date", desc=True)\
            .execute()
        return result.data or []
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific report"""
        result = self.client.table("medical_reports").select("*").eq("id", report_id).execute()
        return result.data[0] if result.data else None
    
    # ==================== TEST RESULT OPERATIONS ====================
    
    def create_test_result(self, report_id: str, user_id: str, test_name: str,
                           test_date: date, test_category: str = "other",
                           test_value: Optional[str] = None, test_unit: Optional[str] = None,
                           reference_range: Optional[str] = None, 
                           status: str = "normal") -> Dict[str, Any]:
        """Create a new test result"""
        data = {
            "report_id": report_id,
            "user_id": user_id,
            "test_name": test_name,
            "test_date": test_date.isoformat() if isinstance(test_date, date) else test_date,
            "test_category": test_category,
            "status": status,
        }
        if test_value:
            data["test_value"] = test_value
        if test_unit:
            data["test_unit"] = test_unit
        if reference_range:
            data["reference_range"] = reference_range
            
        result = self.client.table("test_results").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_test_results(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all test results for a user"""
        result = self.client.table("test_results")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("test_date", desc=True)\
            .execute()
        return result.data or []
    
    def get_test_history(self, user_id: str, test_name: str) -> List[Dict[str, Any]]:
        """Get history of a specific test for a user"""
        result = self.client.table("test_results")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("test_name", test_name)\
            .order("test_date", desc=True)\
            .execute()
        return result.data or []
    
    def get_latest_test(self, user_id: str, test_name: str) -> Optional[Dict[str, Any]]:
        """Get the most recent instance of a specific test"""
        result = self.client.table("test_results")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("test_name", test_name)\
            .order("test_date", desc=True)\
            .limit(1)\
            .execute()
        return result.data[0] if result.data else None
    
    # ==================== DUPLICATE ALERT OPERATIONS ====================
    
    def create_duplicate_alert(self, user_id: str, new_test_name: str,
                               original_test_date: date, days_since_original: int,
                               alert_message: str, savings_amount: float = 0.0,
                               decision: str = "pending") -> Dict[str, Any]:
        """Create a duplicate alert"""
        data = {
            "user_id": user_id,
            "new_test_name": new_test_name,
            "original_test_date": original_test_date.isoformat() if isinstance(original_test_date, date) else original_test_date,
            "days_since_original": days_since_original,
            "alert_message": alert_message,
            "savings_amount": savings_amount,
            "decision": decision,
        }
        result = self.client.table("duplicate_alerts").insert(data).execute()
        return result.data[0] if result.data else None
    
    def update_duplicate_decision(self, alert_id: str, decision: str) -> Dict[str, Any]:
        """Update the decision for a duplicate alert"""
        result = self.client.table("duplicate_alerts")\
            .update({"decision": decision})\
            .eq("id", alert_id)\
            .execute()
        return result.data[0] if result.data else None
    
    def get_duplicate_alerts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all duplicate alerts for a user"""
        result = self.client.table("duplicate_alerts")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        return result.data or []
    
    def get_savings_summary(self, user_id: str) -> Dict[str, Any]:
        """Calculate total savings from skipped duplicates"""
        result = self.client.table("duplicate_alerts")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("decision", "skip")\
            .execute()
        
        alerts = result.data or []
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
        """Upload an image to Supabase storage and return the public URL"""
        # Create a unique path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{user_id}/{timestamp}_{filename}"
        
        # Upload to storage
        self.client.storage.from_(self.storage_bucket).upload(
            file_path,
            file_bytes,
            {"content-type": "image/jpeg"}  # Adjust based on actual type
        )
        
        # Get public URL
        public_url = self.client.storage.from_(self.storage_bucket).get_public_url(file_path)
        return public_url
    
    # ==================== TIMELINE OPERATIONS ====================
    
    def get_timeline(self, user_id: str) -> List[Dict[str, Any]]:
        """Get timeline entries for a user with duplicate indicators"""
        # Get all test results
        test_results = self.get_test_results(user_id)
        
        # Get all reports for hospital info
        reports = {r["id"]: r for r in self.get_reports(user_id)}
        
        # Get duplicate alerts
        duplicate_alerts = self.get_duplicate_alerts(user_id)
        duplicate_tests = {
            (alert["new_test_name"], alert["created_at"][:10])
            for alert in duplicate_alerts
        }
        
        timeline = []
        for test in test_results:
            report = reports.get(test.get("report_id", ""), {})
            entry = {
                "id": test["id"],
                "test_name": test["test_name"],
                "test_value": test.get("test_value"),
                "test_unit": test.get("test_unit"),
                "test_date": test["test_date"],
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
        """Create demo user and sample data"""
        demo_user_id = "demo-user-123"
        
        # Check if demo user exists
        existing = self.get_user(demo_user_id)
        if existing:
            return {
                "success": True,
                "user_id": demo_user_id,
                "message": "Demo user already exists",
                "reports_created": 0
            }
        
        # Create demo user
        user = self.create_user(
            name="Rahul Kumar",
            age=42,
            gender="Male",
            user_id=demo_user_id
        )
        
        # Demo reports data
        demo_reports = [
            {
                "report_type": "lab_test",
                "report_date": "2024-10-13",
                "hospital_name": "Apollo Hospitals",
                "doctor_name": "Dr. Sharma",
                "tests": [
                    {
                        "test_name": "HbA1c",
                        "test_value": "5.9",
                        "test_unit": "%",
                        "reference_range": "4.0-5.6%",
                        "status": "abnormal",
                        "category": "blood"
                    }
                ]
            },
            {
                "report_type": "lab_test",
                "report_date": "2024-05-11",
                "hospital_name": "Max Hospital",
                "doctor_name": "Dr. Gupta",
                "tests": [
                    {
                        "test_name": "Lipid Profile",
                        "test_value": "210",
                        "test_unit": "mg/dL",
                        "reference_range": "<200 mg/dL",
                        "status": "abnormal",
                        "category": "blood"
                    },
                    {
                        "test_name": "LDL Cholesterol",
                        "test_value": "130",
                        "test_unit": "mg/dL",
                        "reference_range": "<100 mg/dL",
                        "status": "abnormal",
                        "category": "blood"
                    },
                    {
                        "test_name": "HDL Cholesterol",
                        "test_value": "45",
                        "test_unit": "mg/dL",
                        "reference_range": ">40 mg/dL",
                        "status": "normal",
                        "category": "blood"
                    }
                ]
            },
            {
                "report_type": "lab_test",
                "report_date": "2024-09-20",
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
                "report_date": "2024-08-15",
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
            }
        ]
        
        reports_created = 0
        for report_data in demo_reports:
            # Create report
            report = self.create_report(
                user_id=demo_user_id,
                report_type=report_data["report_type"],
                report_date=report_data["report_date"],
                hospital_name=report_data["hospital_name"],
                doctor_name=report_data["doctor_name"],
                extracted_data={"tests": report_data["tests"]}
            )
            
            if report:
                reports_created += 1
                # Create test results
                for test in report_data["tests"]:
                    self.create_test_result(
                        report_id=report["id"],
                        user_id=demo_user_id,
                        test_name=test["test_name"],
                        test_date=report_data["report_date"],
                        test_category=test.get("category", "blood"),
                        test_value=test.get("test_value"),
                        test_unit=test.get("test_unit"),
                        reference_range=test.get("reference_range"),
                        status=test.get("status", "normal")
                    )
        
        return {
            "success": True,
            "user_id": demo_user_id,
            "message": "Demo data created successfully",
            "reports_created": reports_created
        }


# Singleton instance - reset on module reload for development
_db_client = None
_using_mock = False


def reset_db():
    """Reset the database client singleton (useful for hot-reloading in development)"""
    global _db_client, _using_mock
    _db_client = None
    _using_mock = False


def get_db():
    """
    Get or create the database client singleton.
    Auto-detects if Supabase credentials are missing and falls back to mock mode.
    """
    global _db_client, _using_mock
    
    if _db_client is None:
        # Check if we should use mock mode
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        demo_mode = os.getenv("DEMO_MODE", "").lower() in ("true", "1", "yes")
        
        if demo_mode or not url or not key or url.startswith("https://your-"):
            # Use mock client for demo mode
            from database.mock_client import MockSupabaseClient
            _db_client = MockSupabaseClient()
            _using_mock = True
            print("🔔 Running in DEMO MODE - Using in-memory database")
        else:
            _db_client = SupabaseClient()
            print("✅ Connected to Supabase database")
    
    return _db_client


def is_demo_mode() -> bool:
    """Check if running in demo mode"""
    return _using_mock

