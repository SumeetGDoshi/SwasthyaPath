"""
Tests for Supabase database client
Plan: /Users/sums/mcpDocs/plans/2025-11-27-write-comprehensive-test-cases-for-the-swasthyapat.md
Phase 5: Database Client Tests
"""

import pytest
import os
from datetime import date
from unittest.mock import MagicMock, patch


class TestSupabaseClientInit:
    """Tests for SupabaseClient initialization"""

    def test_init_without_url_raises(self):
        """Should raise error without SUPABASE_URL"""
        with patch.dict(os.environ, {'SUPABASE_URL': '', 'SUPABASE_KEY': 'test-key'}, clear=True):
            with pytest.raises(ValueError, match="SUPABASE_URL"):
                from database.supabase_client import SupabaseClient
                import importlib
                import database.supabase_client as db_module
                importlib.reload(db_module)
                db_module.SupabaseClient()

    def test_init_without_key_raises(self):
        """Should raise error without SUPABASE_KEY"""
        with patch.dict(os.environ, {'SUPABASE_URL': 'https://test.supabase.co', 'SUPABASE_KEY': ''}, clear=True):
            with pytest.raises(ValueError):
                from database.supabase_client import SupabaseClient
                import importlib
                import database.supabase_client as db_module
                importlib.reload(db_module)
                db_module.SupabaseClient()


class TestUserOperations:
    """Tests for user CRUD operations"""

    @pytest.fixture
    def mock_client(self):
        with patch('database.supabase_client.create_client') as mock:
            mock_supabase = MagicMock()
            mock.return_value = mock_supabase
            
            with patch.dict(os.environ, {
                'SUPABASE_URL': 'https://test.supabase.co',
                'SUPABASE_KEY': 'test-key'
            }):
                from database.supabase_client import SupabaseClient
                client = SupabaseClient()
                yield client, mock_supabase

    def test_create_user_basic(self, mock_client):
        """Should create user with name only"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "user-123", "name": "Test User"}
        ]
        
        result = client.create_user("Test User")
        
        assert result["name"] == "Test User"
        mock_supabase.table.assert_called_with("users")

    def test_create_user_with_all_fields(self, mock_client):
        """Should create user with all optional fields"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "user-123", "name": "Test User", "age": 30, "gender": "Male"}
        ]
        
        result = client.create_user("Test User", age=30, gender="Male", user_id="user-123")
        
        assert result["name"] == "Test User"
        assert result["age"] == 30
        assert result["gender"] == "Male"

    def test_create_user_returns_none_on_empty_response(self, mock_client):
        """Should return None if insert returns empty data"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = []
        
        result = client.create_user("Test User")
        
        assert result is None

    def test_get_user_found(self, mock_client):
        """Should return user when found"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "user-123", "name": "Test User"}
        ]
        
        result = client.get_user("user-123")
        
        assert result["id"] == "user-123"
        assert result["name"] == "Test User"

    def test_get_user_not_found(self, mock_client):
        """Should return None when user not found"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        result = client.get_user("nonexistent")
        
        assert result is None

    def test_get_or_create_user_existing(self, mock_client):
        """Should return existing user"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "user-123", "name": "Existing User"}
        ]
        
        result = client.get_or_create_user("user-123")
        
        assert result["name"] == "Existing User"

    def test_get_or_create_user_creates_new(self, mock_client):
        """Should create new user when not found"""
        client, mock_supabase = mock_client
        # First call returns empty (user not found)
        # Second call returns created user
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "user-123", "name": "Demo User"}
        ]
        
        result = client.get_or_create_user("user-123")
        
        assert result["name"] == "Demo User"


class TestReportOperations:
    """Tests for medical report operations"""

    @pytest.fixture
    def mock_client(self):
        with patch('database.supabase_client.create_client') as mock:
            mock_supabase = MagicMock()
            mock.return_value = mock_supabase
            
            with patch.dict(os.environ, {
                'SUPABASE_URL': 'https://test.supabase.co',
                'SUPABASE_KEY': 'test-key'
            }):
                from database.supabase_client import SupabaseClient
                client = SupabaseClient()
                yield client, mock_supabase

    def test_create_report_basic(self, mock_client):
        """Should create report with required fields"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "report-123", "report_type": "lab_test", "report_date": "2024-11-15"}
        ]
        
        result = client.create_report(
            user_id="user-123",
            report_type="lab_test",
            report_date=date(2024, 11, 15)
        )
        
        assert result["id"] == "report-123"
        assert result["report_type"] == "lab_test"

    def test_create_report_with_all_fields(self, mock_client):
        """Should create report with all optional fields"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {
                "id": "report-123",
                "report_type": "lab_test",
                "hospital_name": "Apollo Hospital",
                "doctor_name": "Dr. Sharma"
            }
        ]
        
        result = client.create_report(
            user_id="user-123",
            report_type="lab_test",
            report_date=date(2024, 11, 15),
            hospital_name="Apollo Hospital",
            doctor_name="Dr. Sharma",
            raw_image_url="https://example.com/image.jpg",
            extracted_data={"tests": []}
        )
        
        assert result["hospital_name"] == "Apollo Hospital"

    def test_create_report_with_string_date(self, mock_client):
        """Should handle string date format"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "report-123"}
        ]
        
        result = client.create_report(
            user_id="user-123",
            report_type="lab_test",
            report_date="2024-11-15"
        )
        
        assert result is not None

    def test_get_reports(self, mock_client):
        """Should return all user reports"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [
            {"id": "1", "report_type": "lab_test"},
            {"id": "2", "report_type": "imaging"}
        ]
        
        result = client.get_reports("user-123")
        
        assert len(result) == 2

    def test_get_reports_empty(self, mock_client):
        """Should return empty list when no reports"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = None
        
        result = client.get_reports("user-123")
        
        assert result == []

    def test_get_report_found(self, mock_client):
        """Should return specific report"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "report-123", "report_type": "lab_test"}
        ]
        
        result = client.get_report("report-123")
        
        assert result["id"] == "report-123"

    def test_get_report_not_found(self, mock_client):
        """Should return None when report not found"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        result = client.get_report("nonexistent")
        
        assert result is None


class TestTestResultOperations:
    """Tests for test result operations"""

    @pytest.fixture
    def mock_client(self):
        with patch('database.supabase_client.create_client') as mock:
            mock_supabase = MagicMock()
            mock.return_value = mock_supabase
            
            with patch.dict(os.environ, {
                'SUPABASE_URL': 'https://test.supabase.co',
                'SUPABASE_KEY': 'test-key'
            }):
                from database.supabase_client import SupabaseClient
                client = SupabaseClient()
                yield client, mock_supabase

    def test_create_test_result(self, mock_client):
        """Should create test result"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "test-123", "test_name": "HbA1c"}
        ]
        
        result = client.create_test_result(
            report_id="report-123",
            user_id="user-123",
            test_name="HbA1c",
            test_date=date(2024, 11, 15)
        )
        
        assert result["test_name"] == "HbA1c"

    def test_create_test_result_with_all_fields(self, mock_client):
        """Should create test result with all fields"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {
                "id": "test-123",
                "test_name": "HbA1c",
                "test_value": "5.8",
                "test_unit": "%",
                "reference_range": "4.0-5.6%",
                "status": "abnormal"
            }
        ]
        
        result = client.create_test_result(
            report_id="report-123",
            user_id="user-123",
            test_name="HbA1c",
            test_date=date(2024, 11, 15),
            test_category="blood",
            test_value="5.8",
            test_unit="%",
            reference_range="4.0-5.6%",
            status="abnormal"
        )
        
        assert result["test_value"] == "5.8"

    def test_get_test_results(self, mock_client):
        """Should get all test results for user"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [
            {"test_name": "HbA1c"},
            {"test_name": "CBC"}
        ]
        
        result = client.get_test_results("user-123")
        
        assert len(result) == 2

    def test_get_test_history(self, mock_client):
        """Should get history of specific test"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
            {"test_name": "HbA1c", "test_date": "2024-11-15"},
            {"test_name": "HbA1c", "test_date": "2024-08-15"}
        ]
        
        result = client.get_test_history("user-123", "HbA1c")
        
        assert len(result) == 2

    def test_get_latest_test(self, mock_client):
        """Should get most recent test result"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
            {"test_name": "HbA1c", "test_date": "2024-11-15"}
        ]
        
        result = client.get_latest_test("user-123", "HbA1c")
        
        assert result["test_date"] == "2024-11-15"

    def test_get_latest_test_not_found(self, mock_client):
        """Should return None when no test found"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
        
        result = client.get_latest_test("user-123", "NonexistentTest")
        
        assert result is None


class TestDuplicateAlertOperations:
    """Tests for duplicate alert operations"""

    @pytest.fixture
    def mock_client(self):
        with patch('database.supabase_client.create_client') as mock:
            mock_supabase = MagicMock()
            mock.return_value = mock_supabase
            
            with patch.dict(os.environ, {
                'SUPABASE_URL': 'https://test.supabase.co',
                'SUPABASE_KEY': 'test-key'
            }):
                from database.supabase_client import SupabaseClient
                client = SupabaseClient()
                yield client, mock_supabase

    def test_create_duplicate_alert(self, mock_client):
        """Should create duplicate alert"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "alert-123", "new_test_name": "HbA1c"}
        ]
        
        result = client.create_duplicate_alert(
            user_id="user-123",
            new_test_name="HbA1c",
            original_test_date=date(2024, 10, 15),
            days_since_original=30,
            alert_message="Duplicate detected",
            savings_amount=700
        )
        
        assert result["new_test_name"] == "HbA1c"

    def test_update_duplicate_decision_skip(self, mock_client):
        """Should update decision to skip"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": "alert-123", "decision": "skip"}
        ]
        
        result = client.update_duplicate_decision("alert-123", "skip")
        
        assert result["decision"] == "skip"

    def test_update_duplicate_decision_proceed(self, mock_client):
        """Should update decision to proceed"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": "alert-123", "decision": "proceed"}
        ]
        
        result = client.update_duplicate_decision("alert-123", "proceed")
        
        assert result["decision"] == "proceed"

    def test_update_duplicate_decision_not_found(self, mock_client):
        """Should return None for non-existent alert"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = []
        
        result = client.update_duplicate_decision("nonexistent", "skip")
        
        assert result is None

    def test_get_duplicate_alerts(self, mock_client):
        """Should get all duplicate alerts for user"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [
            {"id": "1", "new_test_name": "HbA1c"},
            {"id": "2", "new_test_name": "Lipid Profile"}
        ]
        
        result = client.get_duplicate_alerts("user-123")
        
        assert len(result) == 2

    def test_get_savings_summary(self, mock_client):
        """Should calculate total savings from skipped tests"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"savings_amount": 700, "new_test_name": "HbA1c", "created_at": "2024-11-15T00:00:00"},
            {"savings_amount": 1000, "new_test_name": "Lipid Profile", "created_at": "2024-11-14T00:00:00"}
        ]
        
        result = client.get_savings_summary("user-123")
        
        assert result["total_savings"] == 1700
        assert result["tests_skipped"] == 2
        assert len(result["breakdown"]) == 2

    def test_get_savings_summary_empty(self, mock_client):
        """Should return zero savings when no skipped tests"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        
        result = client.get_savings_summary("user-123")
        
        assert result["total_savings"] == 0
        assert result["tests_skipped"] == 0


class TestStorageOperations:
    """Tests for storage operations"""

    @pytest.fixture
    def mock_client(self):
        with patch('database.supabase_client.create_client') as mock:
            mock_supabase = MagicMock()
            mock.return_value = mock_supabase
            
            with patch.dict(os.environ, {
                'SUPABASE_URL': 'https://test.supabase.co',
                'SUPABASE_KEY': 'test-key'
            }):
                from database.supabase_client import SupabaseClient
                client = SupabaseClient()
                yield client, mock_supabase

    def test_upload_image(self, mock_client):
        """Should upload image and return URL"""
        client, mock_supabase = mock_client
        mock_supabase.storage.from_.return_value.upload.return_value = None
        mock_supabase.storage.from_.return_value.get_public_url.return_value = "https://storage.example.com/image.jpg"
        
        result = client.upload_image(b"image_bytes", "test.jpg", "user-123")
        
        assert result == "https://storage.example.com/image.jpg"
        mock_supabase.storage.from_.assert_called_with("medical-reports")


class TestTimelineOperations:
    """Tests for timeline operations"""

    @pytest.fixture
    def mock_client(self):
        with patch('database.supabase_client.create_client') as mock:
            mock_supabase = MagicMock()
            mock.return_value = mock_supabase
            
            with patch.dict(os.environ, {
                'SUPABASE_URL': 'https://test.supabase.co',
                'SUPABASE_KEY': 'test-key'
            }):
                from database.supabase_client import SupabaseClient
                client = SupabaseClient()
                yield client, mock_supabase

    def test_get_timeline(self, mock_client):
        """Should return timeline with duplicate indicators"""
        client, mock_supabase = mock_client
        
        # Mock test results
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [
            {"id": "1", "test_name": "HbA1c", "report_id": "report-1", "test_date": "2024-11-15", "status": "normal"}
        ]
        
        # Mock reports
        mock_reports = MagicMock()
        mock_reports.data = [{"id": "report-1", "hospital_name": "Apollo"}]
        
        # Mock duplicate alerts
        mock_alerts = MagicMock()
        mock_alerts.data = []
        
        result = client.get_timeline("user-123")
        
        assert isinstance(result, list)


class TestDemoData:
    """Tests for demo data setup"""

    @pytest.fixture
    def mock_client(self):
        with patch('database.supabase_client.create_client') as mock:
            mock_supabase = MagicMock()
            mock.return_value = mock_supabase
            
            with patch.dict(os.environ, {
                'SUPABASE_URL': 'https://test.supabase.co',
                'SUPABASE_KEY': 'test-key'
            }):
                from database.supabase_client import SupabaseClient
                client = SupabaseClient()
                yield client, mock_supabase

    def test_setup_demo_data_existing_user(self, mock_client):
        """Should return early if demo user exists"""
        client, mock_supabase = mock_client
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "demo-user-123", "name": "Rahul Kumar"}
        ]
        
        result = client.setup_demo_data()
        
        assert result["success"] is True
        assert result["user_id"] == "demo-user-123"
        assert result["reports_created"] == 0


class TestGetDbSingleton:
    """Tests for database singleton"""

    def test_get_db_returns_instance(self):
        """get_db should return SupabaseClient instance"""
        with patch('database.supabase_client.create_client'):
            with patch.dict(os.environ, {
                'SUPABASE_URL': 'https://test.supabase.co',
                'SUPABASE_KEY': 'test-key'
            }):
                # Reset singleton
                import database.supabase_client as db_module
                db_module._db_client = None
                
                from database.supabase_client import get_db
                db = get_db()
                
                assert db is not None

    def test_get_db_returns_same_instance(self):
        """get_db should return same instance on multiple calls"""
        with patch('database.supabase_client.create_client'):
            with patch.dict(os.environ, {
                'SUPABASE_URL': 'https://test.supabase.co',
                'SUPABASE_KEY': 'test-key'
            }):
                # Reset singleton
                import database.supabase_client as db_module
                db_module._db_client = None
                
                from database.supabase_client import get_db
                db1 = get_db()
                db2 = get_db()
                
                assert db1 is db2


