"""
Pydantic models for Swasthya Path Layer 1 - Report Intelligence Agent
"""

from datetime import date, datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from enum import Enum


# Enums
class ReportType(str, Enum):
    LAB_TEST = "lab_test"
    IMAGING = "imaging"
    PRESCRIPTION = "prescription"
    CONSULTATION = "consultation"


class TestStatus(str, Enum):
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    CRITICAL = "critical"


class TestCategory(str, Enum):
    BLOOD = "blood"
    IMAGING = "imaging"
    VITALS = "vitals"
    URINE = "urine"
    OTHER = "other"


class DuplicateDecision(str, Enum):
    SKIP = "skip"
    PROCEED = "proceed"
    PENDING = "pending"


# User Models
class UserBase(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Authentication Models
class UserSignup(BaseModel):
    """User signup request"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., description="Full name")
    phone: Optional[str] = Field(None, description="Phone number (optional)")


class UserLogin(BaseModel):
    """User login request"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserResponse(BaseModel):
    """Public user information"""
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Individual Test Result
class TestResultBase(BaseModel):
    test_name: str
    test_category: Optional[TestCategory] = TestCategory.OTHER
    test_value: Optional[str] = None
    test_unit: Optional[str] = None
    reference_range: Optional[str] = None
    test_date: date
    status: Optional[TestStatus] = TestStatus.NORMAL


class TestResultCreate(TestResultBase):
    report_id: str
    user_id: str


class TestResult(TestResultBase):
    id: str
    report_id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Extracted Data from Claude
class ExtractedTest(BaseModel):
    test_name: str
    test_value: Optional[str] = None
    test_unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: Optional[str] = "normal"
    category: Optional[str] = "other"


class ExtractedReportData(BaseModel):
    report_type: str = "lab_test"
    hospital_name: Optional[str] = None
    doctor_name: Optional[str] = None
    patient_name: Optional[str] = None
    report_date: Optional[str] = None
    tests: List[ExtractedTest] = []
    raw_text: Optional[str] = None
    confidence_score: Optional[float] = None


# Medical Report Models
class MedicalReportBase(BaseModel):
    report_type: Optional[ReportType] = ReportType.LAB_TEST
    report_date: date
    hospital_name: Optional[str] = None
    doctor_name: Optional[str] = None


class MedicalReportCreate(MedicalReportBase):
    user_id: str
    raw_image_url: Optional[str] = None
    extracted_data: Optional[dict] = None


class MedicalReport(MedicalReportBase):
    id: str
    user_id: str
    raw_image_url: Optional[str] = None
    extracted_data: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Duplicate Alert Models
class DuplicateAlertBase(BaseModel):
    new_test_name: str
    original_test_date: date
    days_since_original: int
    decision: DuplicateDecision = DuplicateDecision.PENDING
    savings_amount: Optional[float] = None
    alert_message: str


class DuplicateAlertCreate(DuplicateAlertBase):
    user_id: str


class DuplicateAlert(DuplicateAlertBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# API Request/Response Models
class UploadReportRequest(BaseModel):
    user_id: str
    context: Optional[str] = None  # Optional patient context


class UploadReportResponse(BaseModel):
    success: bool
    report_id: Optional[str] = None
    extracted_data: Optional[ExtractedReportData] = None
    duplicate_alerts: List[DuplicateAlert] = []
    message: str
    total_potential_savings: float = 0.0


class TimelineEntry(BaseModel):
    id: str
    test_name: str
    test_value: Optional[str] = None
    test_unit: Optional[str] = None
    test_date: date
    valid_until: Optional[date] = None
    status: TestStatus
    hospital_name: Optional[str] = None
    is_duplicate: bool = False
    category: TestCategory = TestCategory.OTHER
    reference_range: Optional[str] = None


class TimelineResponse(BaseModel):
    user_id: str
    entries: List[TimelineEntry]
    total_tests: int


class SavingsBreakdown(BaseModel):
    test_name: str
    date_skipped: date
    amount_saved: float


class SavingsResponse(BaseModel):
    user_id: str
    total_savings: float
    tests_skipped: int
    breakdown: List[SavingsBreakdown]


class ReportListResponse(BaseModel):
    user_id: str
    reports: List[MedicalReport]
    total_count: int


# Demo Setup
class DemoSetupResponse(BaseModel):
    success: bool
    user_id: str
    message: str
    reports_created: int


# Health Check
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime


# Error Response
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int


