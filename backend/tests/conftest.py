"""
Test fixtures and configuration for SwasthyaPath backend tests
Plan: /Users/sums/mcpDocs/plans/2025-11-27-write-comprehensive-test-cases-for-the-swasthyapat.md
Phase 1: Backend Unit Tests Setup
"""

import pytest
import os
from datetime import date, datetime
from unittest.mock import MagicMock, AsyncMock, patch
import io
from PIL import Image

# Set test environment before importing app modules
os.environ.setdefault("ANTHROPIC_API_KEY", "test-api-key")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client for FastAPI app"""
    # Import inside fixture to ensure env vars are set
    with patch('database.supabase_client.create_client'):
        with patch('agents.report_agent.anthropic.Anthropic'):
            from main import app
            return TestClient(app)


@pytest.fixture
def sample_image_bytes():
    """Create a valid test JPEG image"""
    img = Image.new('RGB', (100, 100), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    return buffer.getvalue()


@pytest.fixture
def sample_png_bytes():
    """Create a valid test PNG image"""
    img = Image.new('RGB', (100, 100), color='blue')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


@pytest.fixture
def sample_large_image_bytes():
    """Create a large test image that needs compression"""
    img = Image.new('RGB', (3000, 3000), color='green')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=100)
    return buffer.getvalue()


@pytest.fixture
def sample_pdf_bytes():
    """Create minimal PDF-like bytes for testing"""
    return b'%PDF-1.4 test content for extraction'


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for database tests"""
    with patch('database.supabase_client.create_client') as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic Claude API for AI tests"""
    with patch('agents.report_agent.anthropic.Anthropic') as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield instance


@pytest.fixture
def sample_test_history():
    """Sample test history data for duplicate detection tests"""
    return [
        {
            "test_name": "HbA1c",
            "test_date": "2024-10-15",
            "test_value": "5.8",
            "hospital_name": "Apollo Hospital"
        },
        {
            "test_name": "Lipid Profile",
            "test_date": "2024-08-20",
            "test_value": "195",
            "hospital_name": "Max Hospital"
        },
        {
            "test_name": "CBC",
            "test_date": "2024-11-01",
            "test_value": "Normal",
            "hospital_name": "Fortis Hospital"
        },
        {
            "test_name": "Thyroid Panel",
            "test_date": "2024-09-15",
            "test_value": "TSH: 2.5",
            "hospital_name": "AIIMS"
        }
    ]


@pytest.fixture
def sample_claude_response():
    """Sample Claude API response for report analysis"""
    return {
        "report_type": "lab_test",
        "hospital_name": "Apollo Diagnostics",
        "doctor_name": "Dr. Sharma",
        "patient_name": "Rahul Kumar",
        "report_date": "2024-11-15",
        "tests": [
            {
                "test_name": "HbA1c",
                "test_value": "6.1",
                "test_unit": "%",
                "reference_range": "4.0-5.6%",
                "status": "abnormal",
                "category": "blood"
            },
            {
                "test_name": "Fasting Blood Sugar",
                "test_value": "126",
                "test_unit": "mg/dL",
                "reference_range": "70-100 mg/dL",
                "status": "abnormal",
                "category": "blood"
            }
        ],
        "raw_text": "Summary of diabetic profile",
        "confidence_score": 0.95
    }


@pytest.fixture
def sample_report_data():
    """Sample medical report data"""
    return {
        "id": "report-123",
        "user_id": "user-456",
        "report_type": "lab_test",
        "report_date": "2024-11-15",
        "hospital_name": "Apollo Hospital",
        "doctor_name": "Dr. Sharma",
        "raw_image_url": "https://storage.example.com/reports/image.jpg",
        "extracted_data": {
            "tests": [
                {"test_name": "HbA1c", "test_value": "5.9", "status": "normal"}
            ]
        },
        "created_at": "2024-11-15T10:30:00Z"
    }


@pytest.fixture
def sample_duplicate_alert():
    """Sample duplicate alert data"""
    return {
        "id": "alert-789",
        "user_id": "user-456",
        "new_test_name": "HbA1c",
        "original_test_date": "2024-10-15",
        "days_since_original": 31,
        "decision": "pending",
        "savings_amount": 700,
        "alert_message": "⚠️ Duplicate Alert: HbA1c was done 31 days ago.",
        "created_at": "2024-11-15T10:30:00Z"
    }


@pytest.fixture
def sample_timeline_entries():
    """Sample timeline entries for display tests"""
    return [
        {
            "id": "1",
            "test_name": "HbA1c",
            "test_value": "5.9",
            "test_unit": "%",
            "test_date": "2024-11-15",
            "status": "normal",
            "hospital_name": "Apollo Hospital",
            "is_duplicate": False,
            "category": "blood",
            "reference_range": "4.0-5.6%"
        },
        {
            "id": "2",
            "test_name": "Lipid Profile",
            "test_value": "210",
            "test_unit": "mg/dL",
            "test_date": "2024-10-15",
            "status": "abnormal",
            "hospital_name": "Max Hospital",
            "is_duplicate": True,
            "category": "blood",
            "reference_range": "<200 mg/dL"
        }
    ]


@pytest.fixture
def sample_savings_summary():
    """Sample savings summary data"""
    return {
        "total_savings": 2100,
        "tests_skipped": 3,
        "breakdown": [
            {"test_name": "HbA1c", "date_skipped": "2024-11-15", "amount_saved": 700},
            {"test_name": "Lipid Profile", "date_skipped": "2024-11-10", "amount_saved": 1000},
            {"test_name": "TSH", "date_skipped": "2024-11-05", "amount_saved": 400}
        ]
    }


