"""
Tests for Report Intelligence Agent
Plan: /Users/sums/mcpDocs/plans/2025-11-27-write-comprehensive-test-cases-for-the-swasthyapat.md
Phase 1: Backend Unit Tests - Report Agent
"""

import pytest
import os
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
import json


class TestReportIntelligenceAgentInit:
    """Tests for ReportIntelligenceAgent initialization"""

    def test_init_without_api_key_raises(self):
        """Should raise error without API key"""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                from agents.report_agent import ReportIntelligenceAgent
                # Force reimport to test with new env
                import importlib
                import agents.report_agent as agent_module
                importlib.reload(agent_module)
                agent_module.ReportIntelligenceAgent()

    def test_init_with_api_key_succeeds(self):
        """Should initialize with valid API key"""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('agents.report_agent.anthropic.Anthropic'):
                from agents.report_agent import ReportIntelligenceAgent
                agent = ReportIntelligenceAgent()
                assert agent is not None
                assert agent.model == "claude-sonnet-4-20250514"


class TestNormalizeTestName:
    """Tests for test name normalization"""

    @pytest.fixture
    def agent(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('agents.report_agent.anthropic.Anthropic'):
                from agents.report_agent import ReportIntelligenceAgent
                return ReportIntelligenceAgent()

    def test_normalize_cbc_aliases(self, agent):
        """CBC aliases should normalize correctly"""
        assert agent._normalize_test_name("complete blood count") == "CBC"
        assert agent._normalize_test_name("cbc") == "CBC"
        assert agent._normalize_test_name("hemogram") == "CBC"
        assert agent._normalize_test_name("blood count") == "CBC"

    def test_normalize_hba1c_aliases(self, agent):
        """HbA1c aliases should normalize correctly"""
        assert agent._normalize_test_name("hba1c") == "HbA1c"
        assert agent._normalize_test_name("glycated hemoglobin") == "HbA1c"
        assert agent._normalize_test_name("glycosylated hemoglobin") == "HbA1c"
        assert agent._normalize_test_name("hb a1c") == "HbA1c"

    def test_normalize_lipid_aliases(self, agent):
        """Lipid profile aliases should normalize correctly"""
        assert agent._normalize_test_name("lipid panel") == "Lipid Profile"
        assert agent._normalize_test_name("lipids") == "Lipid Profile"
        assert agent._normalize_test_name("cholesterol test") == "Lipid Profile"

    def test_normalize_thyroid_aliases(self, agent):
        """Thyroid aliases should normalize correctly"""
        assert agent._normalize_test_name("thyroid function test") == "Thyroid Panel"
        assert agent._normalize_test_name("tft") == "Thyroid Panel"
        assert agent._normalize_test_name("thyroid profile") == "Thyroid Panel"

    def test_normalize_liver_aliases(self, agent):
        """Liver function test aliases should normalize correctly"""
        assert agent._normalize_test_name("liver function test") == "Liver Function Test"
        assert agent._normalize_test_name("lft") == "Liver Function Test"
        assert agent._normalize_test_name("liver panel") == "Liver Function Test"

    def test_normalize_kidney_aliases(self, agent):
        """Kidney function test aliases should normalize correctly"""
        assert agent._normalize_test_name("kidney function test") == "Kidney Function Test"
        assert agent._normalize_test_name("kft") == "Kidney Function Test"
        assert agent._normalize_test_name("renal function test") == "Kidney Function Test"
        assert agent._normalize_test_name("rft") == "Kidney Function Test"

    def test_normalize_blood_sugar_aliases(self, agent):
        """Blood sugar aliases should normalize correctly"""
        assert agent._normalize_test_name("fasting blood sugar") == "Fasting Blood Sugar"
        assert agent._normalize_test_name("fbs") == "Fasting Blood Sugar"
        assert agent._normalize_test_name("fasting glucose") == "Fasting Blood Sugar"

    def test_normalize_ecg_aliases(self, agent):
        """ECG aliases should normalize correctly"""
        assert agent._normalize_test_name("electrocardiogram") == "ECG"
        assert agent._normalize_test_name("ekg") == "ECG"

    def test_normalize_unknown_returns_title_case(self, agent):
        """Unknown tests should return title case"""
        assert agent._normalize_test_name("some random test") == "Some Random Test"
        assert agent._normalize_test_name("NEW FANCY TEST") == "New Fancy Test"

    def test_normalize_empty_returns_unknown(self, agent):
        """Empty string should return Unknown Test"""
        assert agent._normalize_test_name("") == "Unknown Test"
        assert agent._normalize_test_name(None) == "Unknown Test"

    def test_normalize_preserves_standard_names(self, agent):
        """Standard names should be preserved"""
        assert agent._normalize_test_name("HbA1c") == "HbA1c"
        assert agent._normalize_test_name("CBC") == "CBC"
        assert agent._normalize_test_name("TSH") == "TSH"

    def test_normalize_case_insensitive(self, agent):
        """Normalization should be case insensitive"""
        assert agent._normalize_test_name("HBA1C") == "HbA1c"
        assert agent._normalize_test_name("Hba1c") == "HbA1c"
        assert agent._normalize_test_name("COMPLETE BLOOD COUNT") == "CBC"


class TestDetectDuplicate:
    """Tests for duplicate detection"""

    @pytest.fixture
    def agent(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('agents.report_agent.anthropic.Anthropic'):
                from agents.report_agent import ReportIntelligenceAgent
                return ReportIntelligenceAgent()

    def test_no_history_returns_not_duplicate(self, agent):
        """No test history should return not duplicate"""
        result = agent.detect_duplicate("HbA1c", date.today(), [])
        assert result["is_duplicate"] is False
        assert result["potential_savings"] == 0
        assert result["message"] == "No previous test found"

    def test_recent_test_is_duplicate(self, agent, sample_test_history):
        """Test within validity period should be duplicate"""
        # HbA1c has 90 day validity, history has test from 2024-10-15
        test_date = date(2024, 11, 15)  # 31 days later
        result = agent.detect_duplicate("HbA1c", test_date, sample_test_history)
        
        assert result["is_duplicate"] is True
        assert result["potential_savings"] == 700  # HbA1c cost
        assert result["days_since"] == 31
        assert "⚠️ Duplicate Alert" in result["message"]

    def test_old_test_not_duplicate(self, agent, sample_test_history):
        """Test outside validity period should not be duplicate"""
        # Test done 100 days after the history entry (HbA1c validity is 90 days)
        test_date = date(2025, 1, 25)  # More than 90 days from 2024-10-15
        result = agent.detect_duplicate("HbA1c", test_date, sample_test_history)
        assert result["is_duplicate"] is False

    def test_different_test_not_duplicate(self, agent, sample_test_history):
        """Different test type should not be duplicate"""
        result = agent.detect_duplicate("TSH", date.today(), sample_test_history)
        assert result["is_duplicate"] is False
        assert result["message"] == "No previous test found"

    def test_lipid_profile_duplicate_detection(self, agent, sample_test_history):
        """Lipid profile should have 180 day validity"""
        # History has Lipid Profile from 2024-08-20
        # Test 100 days later should be duplicate (within 180 days)
        test_date = date(2024, 11, 28)  # ~100 days later
        result = agent.detect_duplicate("Lipid Profile", test_date, sample_test_history)
        
        assert result["is_duplicate"] is True
        assert result["potential_savings"] == 1000  # Lipid Profile cost

    def test_cbc_short_validity(self, agent, sample_test_history):
        """CBC should have 30 day validity"""
        # History has CBC from 2024-11-01
        # Test 40 days later should NOT be duplicate (beyond 30 days)
        test_date = date(2024, 12, 11)  # 40 days later
        result = agent.detect_duplicate("CBC", test_date, sample_test_history)
        
        assert result["is_duplicate"] is False

    def test_duplicate_info_includes_original_date(self, agent, sample_test_history):
        """Duplicate result should include original test date"""
        test_date = date(2024, 11, 15)
        result = agent.detect_duplicate("HbA1c", test_date, sample_test_history)
        
        assert result["is_duplicate"] is True
        assert result["original_date"] == date(2024, 10, 15)

    def test_duplicate_info_includes_days_remaining(self, agent, sample_test_history):
        """Duplicate result should include days remaining in validity"""
        test_date = date(2024, 11, 15)  # 31 days after HbA1c (90 day validity)
        result = agent.detect_duplicate("HbA1c", test_date, sample_test_history)
        
        assert result["is_duplicate"] is True
        assert result["validity_period"] == 90
        assert result["days_remaining"] == 59  # 90 - 31

    def test_handles_date_as_string(self, agent):
        """Should handle test_date as string in history"""
        history = [
            {"test_name": "HbA1c", "test_date": "2024-10-15", "test_value": "5.8"}
        ]
        test_date = date(2024, 11, 1)
        result = agent.detect_duplicate("HbA1c", test_date, history)
        
        assert result["is_duplicate"] is True

    def test_handles_date_as_date_object(self, agent):
        """Should handle test_date as date object in history"""
        history = [
            {"test_name": "HbA1c", "test_date": date(2024, 10, 15), "test_value": "5.8"}
        ]
        test_date = date(2024, 11, 1)
        result = agent.detect_duplicate("HbA1c", test_date, history)
        
        assert result["is_duplicate"] is True

    def test_uses_most_recent_test(self, agent):
        """Should compare against the most recent test"""
        history = [
            {"test_name": "HbA1c", "test_date": "2024-08-01", "test_value": "5.5"},
            {"test_name": "HbA1c", "test_date": "2024-10-15", "test_value": "5.8"},
            {"test_name": "HbA1c", "test_date": "2024-09-01", "test_value": "5.6"},
        ]
        test_date = date(2024, 11, 15)
        result = agent.detect_duplicate("HbA1c", test_date, history)
        
        # Should compare with 2024-10-15 (most recent), not others
        assert result["is_duplicate"] is True
        assert result["original_date"] == date(2024, 10, 15)
        assert result["days_since"] == 31


class TestCalculateSavings:
    """Tests for savings calculation"""

    @pytest.fixture
    def agent(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('agents.report_agent.anthropic.Anthropic'):
                from agents.report_agent import ReportIntelligenceAgent
                return ReportIntelligenceAgent()

    def test_hba1c_cost(self, agent):
        """HbA1c should return correct cost"""
        assert agent.calculate_savings("HbA1c") == 700

    def test_cbc_cost(self, agent):
        """CBC should return correct cost"""
        assert agent.calculate_savings("CBC") == 500

    def test_lipid_profile_cost(self, agent):
        """Lipid Profile should return correct cost"""
        assert agent.calculate_savings("Lipid Profile") == 1000

    def test_thyroid_panel_cost(self, agent):
        """Thyroid Panel should return correct cost"""
        assert agent.calculate_savings("Thyroid Panel") == 800

    def test_imaging_costs(self, agent):
        """Imaging tests should return correct costs"""
        assert agent.calculate_savings("X-Ray Chest") == 600
        assert agent.calculate_savings("Ultrasound Abdomen") == 1200
        assert agent.calculate_savings("ECG") == 400
        assert agent.calculate_savings("MRI") == 8000

    def test_unknown_test_returns_default(self, agent):
        """Unknown tests should return default cost"""
        result = agent.calculate_savings("Unknown Test XYZ")
        assert result == 500  # Default cost

    def test_normalized_test_name_lookup(self, agent):
        """Should normalize test name before lookup"""
        # These should normalize to standard names
        assert agent.calculate_savings("complete blood count") == 500  # CBC
        assert agent.calculate_savings("glycated hemoglobin") == 700  # HbA1c


class TestGetValidityPeriod:
    """Tests for validity period retrieval"""

    @pytest.fixture
    def agent(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('agents.report_agent.anthropic.Anthropic'):
                from agents.report_agent import ReportIntelligenceAgent
                return ReportIntelligenceAgent()

    def test_hba1c_validity(self, agent):
        """HbA1c should have 90 day validity"""
        assert agent.get_validity_period("HbA1c") == 90

    def test_cbc_validity(self, agent):
        """CBC should have 30 day validity"""
        assert agent.get_validity_period("CBC") == 30

    def test_lipid_profile_validity(self, agent):
        """Lipid Profile should have 180 day validity"""
        assert agent.get_validity_period("Lipid Profile") == 180

    def test_imaging_validity(self, agent):
        """Imaging tests should have longer validity"""
        assert agent.get_validity_period("X-Ray Chest") == 365
        assert agent.get_validity_period("Ultrasound Abdomen") == 180
        assert agent.get_validity_period("ECG") == 180
        assert agent.get_validity_period("MRI") == 365

    def test_urine_test_validity(self, agent):
        """Urine tests should have short validity"""
        assert agent.get_validity_period("Urine Routine") == 14
        assert agent.get_validity_period("Urine Culture") == 14

    def test_unknown_returns_default(self, agent):
        """Unknown tests should return default validity"""
        assert agent.get_validity_period("Unknown Test") == 30


class TestAnalyzeReport:
    """Tests for report analysis"""

    @pytest.fixture
    def agent(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('agents.report_agent.anthropic.Anthropic') as mock_anthropic:
                from agents.report_agent import ReportIntelligenceAgent
                agent = ReportIntelligenceAgent()
                yield agent, mock_anthropic

    def test_analyze_report_calls_claude(self, agent, sample_claude_response):
        """Should call Claude API with image"""
        agent_instance, mock_anthropic = agent
        
        # Mock the Claude response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(sample_claude_response))]
        agent_instance.client.messages.create.return_value = mock_response
        
        result = agent_instance.analyze_report(
            image_base64="base64encodeddata",
            media_type="image/jpeg"
        )
        
        agent_instance.client.messages.create.assert_called_once()
        assert "report_type" in result
        assert result["report_type"] == "lab_test"

    def test_analyze_report_includes_user_context(self, agent, sample_claude_response):
        """Should include user context in request"""
        agent_instance, _ = agent
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(sample_claude_response))]
        agent_instance.client.messages.create.return_value = mock_response
        
        result = agent_instance.analyze_report(
            image_base64="base64data",
            media_type="image/jpeg",
            user_context="Patient has diabetes"
        )
        
        # Verify context was passed to API
        call_args = agent_instance.client.messages.create.call_args
        messages = call_args.kwargs.get('messages', call_args[1].get('messages', []))
        content = str(messages[0]['content'])
        assert "diabetes" in content.lower() or "context" in content.lower()

    def test_analyze_report_handles_api_error(self, agent):
        """Should handle API errors gracefully"""
        agent_instance, _ = agent
        
        import anthropic
        agent_instance.client.messages.create.side_effect = anthropic.APIError(
            message="API Error",
            request=MagicMock(),
            body=None
        )
        
        result = agent_instance.analyze_report("base64data", "image/jpeg")
        
        assert result["confidence_score"] == 0.0
        assert result["tests"] == []

    def test_analyze_report_normalizes_test_names(self, agent):
        """Should normalize test names in response"""
        agent_instance, _ = agent
        
        response_with_unnormalized = {
            "report_type": "lab_test",
            "tests": [
                {"test_name": "complete blood count", "test_value": "Normal"}
            ]
        }
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(response_with_unnormalized))]
        agent_instance.client.messages.create.return_value = mock_response
        
        result = agent_instance.analyze_report("base64data", "image/jpeg")
        
        # Test name should be normalized
        assert result["tests"][0]["test_name"] == "CBC"


class TestAnalyzeTextReport:
    """Tests for text-based report analysis"""

    @pytest.fixture
    def agent(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('agents.report_agent.anthropic.Anthropic'):
                from agents.report_agent import ReportIntelligenceAgent
                agent = ReportIntelligenceAgent()
                yield agent

    def test_analyze_text_report(self, agent, sample_claude_response):
        """Should analyze text reports"""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(sample_claude_response))]
        agent.client.messages.create.return_value = mock_response
        
        result = agent.analyze_text_report(
            text="HbA1c: 6.1%, Fasting Blood Sugar: 126 mg/dL"
        )
        
        assert "report_type" in result
        agent.client.messages.create.assert_called_once()


class TestIndianTestCosts:
    """Tests for Indian test cost data"""

    def test_all_costs_are_positive(self):
        """All test costs should be positive"""
        from agents.report_agent import INDIAN_TEST_COSTS
        for test, cost in INDIAN_TEST_COSTS.items():
            assert cost > 0, f"{test} has invalid cost: {cost}"

    def test_common_tests_exist(self):
        """Common tests should be defined"""
        from agents.report_agent import INDIAN_TEST_COSTS
        common_tests = [
            "HbA1c", "CBC", "Lipid Profile", "TSH", "Creatinine",
            "Liver Function Test", "Kidney Function Test", "Vitamin D"
        ]
        for test in common_tests:
            assert test in INDIAN_TEST_COSTS, f"{test} not found in costs"

    def test_imaging_tests_more_expensive(self):
        """Imaging tests should generally cost more than blood tests"""
        from agents.report_agent import INDIAN_TEST_COSTS
        assert INDIAN_TEST_COSTS["MRI"] > INDIAN_TEST_COSTS["CBC"]
        assert INDIAN_TEST_COSTS["CT Scan"] > INDIAN_TEST_COSTS["HbA1c"]
        assert INDIAN_TEST_COSTS["PET Scan"] > INDIAN_TEST_COSTS["MRI"]


class TestValidityPeriods:
    """Tests for validity period data"""

    def test_all_periods_are_positive(self):
        """All validity periods should be positive"""
        from agents.report_agent import VALIDITY_PERIODS
        for test, days in VALIDITY_PERIODS.items():
            assert days > 0, f"{test} has invalid validity: {days}"

    def test_default_exists(self):
        """Default validity should exist"""
        from agents.report_agent import VALIDITY_PERIODS
        assert "default" in VALIDITY_PERIODS
        assert VALIDITY_PERIODS["default"] == 30

    def test_stable_markers_longer_validity(self):
        """Stable markers should have longer validity"""
        from agents.report_agent import VALIDITY_PERIODS
        assert VALIDITY_PERIODS["HbA1c"] >= 90
        assert VALIDITY_PERIODS["Lipid Profile"] >= 180

    def test_dynamic_markers_shorter_validity(self):
        """Dynamic markers should have shorter validity"""
        from agents.report_agent import VALIDITY_PERIODS
        assert VALIDITY_PERIODS["CBC"] <= 30
        assert VALIDITY_PERIODS["Random Blood Sugar"] <= 7


class TestTestNameAliases:
    """Tests for test name alias data"""

    def test_aliases_map_to_standard_names(self):
        """All aliases should map to names in INDIAN_TEST_COSTS"""
        from agents.report_agent import TEST_NAME_ALIASES, INDIAN_TEST_COSTS
        for alias, standard in TEST_NAME_ALIASES.items():
            assert standard in INDIAN_TEST_COSTS, f"Alias '{alias}' maps to unknown test '{standard}'"

    def test_common_aliases_exist(self):
        """Common aliases should be defined"""
        from agents.report_agent import TEST_NAME_ALIASES
        assert "cbc" in TEST_NAME_ALIASES
        assert "hba1c" in TEST_NAME_ALIASES
        assert "lft" in TEST_NAME_ALIASES
        assert "kft" in TEST_NAME_ALIASES


