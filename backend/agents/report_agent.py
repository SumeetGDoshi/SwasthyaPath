"""
Report Intelligence Agent - Layer 1
Claude Sonnet integration for medical report analysis and duplicate detection
"""

import os
import json
import re
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import anthropic
from dotenv import load_dotenv

load_dotenv()


# Indian medical test costs (in INR)
INDIAN_TEST_COSTS = {
    # Blood Tests
    "HbA1c": 700,
    "Lipid Profile": 1000,
    "CBC": 500,
    "Complete Blood Count": 500,
    "Hemoglobin": 150,
    "Thyroid Panel": 800,
    "TSH": 350,
    "T3": 300,
    "T4": 300,
    "Liver Function Test": 900,
    "LFT": 900,
    "Kidney Function Test": 850,
    "KFT": 850,
    "Creatinine": 250,
    "Urea": 200,
    "Blood Sugar Fasting": 100,
    "Blood Sugar PP": 100,
    "HBA1C": 700,
    "Fasting Blood Sugar": 100,
    "Random Blood Sugar": 100,
    "Uric Acid": 250,
    "Vitamin D": 1200,
    "Vitamin B12": 800,
    "Iron Studies": 600,
    "Ferritin": 500,
    "ESR": 150,
    "CRP": 400,
    "Electrolytes": 500,
    "Calcium": 200,
    "Phosphorus": 200,
    "Magnesium": 300,
    "Sodium": 150,
    "Potassium": 150,
    "Chloride": 150,
    "LDL Cholesterol": 350,
    "HDL Cholesterol": 350,
    "Triglycerides": 350,
    "Total Cholesterol": 350,
    "VLDL": 250,
    "Prothrombin Time": 400,
    "PT INR": 400,
    "APTT": 400,
    "D-Dimer": 1500,
    "Troponin": 1200,
    "BNP": 2000,
    "PSA": 800,
    "CA-125": 1500,
    "AFP": 800,
    "CEA": 1000,
    
    # Urine Tests
    "Urine Routine": 200,
    "Urine Culture": 600,
    "Microalbumin": 500,
    "24 Hour Urine Protein": 400,
    
    # Imaging
    "X-Ray Chest": 600,
    "X-Ray": 500,
    "Ultrasound Abdomen": 1200,
    "Ultrasound": 1000,
    "ECG": 400,
    "Echo": 2500,
    "Echocardiography": 2500,
    "CT Scan": 5000,
    "MRI": 8000,
    "PET Scan": 25000,
    "Mammography": 2000,
    "Bone Density": 2500,
    "DEXA Scan": 2500,
    
    # Other
    "Stool Test": 300,
    "Stool Culture": 600,
    "Sputum Test": 300,
    "COVID-19 RT-PCR": 500,
    "Dengue NS1": 600,
    "Malaria Test": 400,
    "Typhoid Test": 400,
    "Widal Test": 300,
}

# Test validity periods in days
VALIDITY_PERIODS = {
    # Stable markers - 3-6 months
    "HbA1c": 90,
    "Lipid Profile": 180,
    "LDL Cholesterol": 180,
    "HDL Cholesterol": 180,
    "Total Cholesterol": 180,
    "Triglycerides": 180,
    "Thyroid Panel": 90,
    "TSH": 90,
    "T3": 90,
    "T4": 90,
    "Vitamin D": 90,
    "Vitamin B12": 90,
    
    # Dynamic markers - 1 month
    "CBC": 30,
    "Complete Blood Count": 30,
    "Hemoglobin": 30,
    "Blood Sugar Fasting": 30,
    "Fasting Blood Sugar": 30,
    "Random Blood Sugar": 7,
    "Blood Sugar PP": 30,
    "Liver Function Test": 30,
    "LFT": 30,
    "Kidney Function Test": 30,
    "KFT": 30,
    "Creatinine": 30,
    "Urea": 30,
    "Electrolytes": 30,
    "Uric Acid": 60,
    
    # Imaging - 6-12 months
    "X-Ray Chest": 365,
    "X-Ray": 365,
    "Ultrasound Abdomen": 180,
    "Ultrasound": 180,
    "ECG": 180,
    "Echo": 365,
    "Echocardiography": 365,
    "CT Scan": 365,
    "MRI": 365,
    
    # Tumor markers - 3 months
    "PSA": 90,
    "CA-125": 90,
    "AFP": 90,
    "CEA": 90,
    
    # Urine - 2 weeks
    "Urine Routine": 14,
    "Urine Culture": 14,
    
    # Default
    "default": 30,
}

# Test name normalization mapping
TEST_NAME_ALIASES = {
    "complete blood count": "CBC",
    "cbc": "CBC",
    "blood count": "CBC",
    "hemogram": "CBC",
    "hba1c": "HbA1c",
    "glycated hemoglobin": "HbA1c",
    "glycosylated hemoglobin": "HbA1c",
    "hb a1c": "HbA1c",
    "lipid panel": "Lipid Profile",
    "lipids": "Lipid Profile",
    "cholesterol test": "Lipid Profile",
    "thyroid function test": "Thyroid Panel",
    "tft": "Thyroid Panel",
    "thyroid profile": "Thyroid Panel",
    "liver function test": "Liver Function Test",
    "lft": "Liver Function Test",
    "liver panel": "Liver Function Test",
    "kidney function test": "Kidney Function Test",
    "kft": "Kidney Function Test",
    "renal function test": "Kidney Function Test",
    "rft": "Kidney Function Test",
    "fasting blood sugar": "Fasting Blood Sugar",
    "fbs": "Fasting Blood Sugar",
    "fasting glucose": "Fasting Blood Sugar",
    "random blood sugar": "Random Blood Sugar",
    "rbs": "Random Blood Sugar",
    "pp blood sugar": "Blood Sugar PP",
    "postprandial blood sugar": "Blood Sugar PP",
    "ppbs": "Blood Sugar PP",
    "chest x-ray": "X-Ray Chest",
    "chest xray": "X-Ray Chest",
    "cxr": "X-Ray Chest",
    "electrocardiogram": "ECG",
    "ekg": "ECG",
    "echocardiogram": "Echocardiography",
    "2d echo": "Echocardiography",
}


# System prompt for Claude
REPORT_INTELLIGENCE_SYSTEM_PROMPT = """You are a medical report analysis expert specializing in Indian healthcare documents. Your role is to accurately extract structured data from medical lab reports, prescriptions, imaging reports, and diagnostic documents.

## Your Capabilities:
1. **OCR and Text Extraction**: Read text from images of medical reports, including handwritten notes, printed lab results, and hospital letterheads.
2. **Bilingual Processing**: Handle reports in both Hindi and English, as Indian medical reports often mix both languages.
3. **Test Name Normalization**: Map various test name variations to standardized names (e.g., "Complete Blood Count", "CBC", "Hemogram" → "CBC").
4. **Reference Range Interpretation**: Identify if values are normal, abnormal, or critical based on the reference ranges provided in the report.
5. **Entity Extraction**: Extract hospital name, doctor name, patient details, and report date.

## Output Requirements:
You MUST respond with a valid JSON object containing:

```json
{
  "report_type": "lab_test" | "imaging" | "prescription" | "consultation",
  "hospital_name": "Hospital/Lab name or null",
  "doctor_name": "Doctor name or null",
  "patient_name": "Patient name or null",
  "report_date": "YYYY-MM-DD format or null",
  "tests": [
    {
      "test_name": "Standardized test name",
      "test_value": "Numeric or text value",
      "test_unit": "Unit of measurement",
      "reference_range": "Normal range as shown",
      "status": "normal" | "abnormal" | "critical",
      "category": "blood" | "imaging" | "vitals" | "urine" | "other"
    }
  ],
  "raw_text": "Brief summary of key findings",
  "confidence_score": 0.0 to 1.0
}
```

## Test Categorization Rules:
- **blood**: CBC, HbA1c, Lipid Profile, Thyroid, LFT, KFT, Blood Sugar, Hemoglobin, etc.
- **imaging**: X-Ray, Ultrasound, CT, MRI, ECG, Echo, etc.
- **vitals**: Blood Pressure, Pulse, Temperature, SpO2, etc.
- **urine**: Urine Routine, Urine Culture, Microalbumin, etc.
- **other**: Stool tests, Sputum tests, Biopsies, etc.

## Status Determination:
- **normal**: Value within reference range
- **abnormal**: Value slightly outside reference range
- **critical**: Value significantly outside reference range (e.g., very high blood sugar, very low hemoglobin)

## Important Guidelines:
1. Always extract the EXACT values shown in the report
2. If a date is ambiguous, prefer DD-MM-YYYY format (common in India)
3. If you cannot read a value clearly, set confidence_score lower
4. For imaging reports, describe key findings in raw_text
5. If multiple tests are on one report, extract ALL of them
6. Normalize test names but preserve original values exactly

## Common Indian Lab Report Formats:
- SRL Diagnostics, Dr. Lal PathLabs, Thyrocare, Metropolis
- Hospital labs: Apollo, Fortis, Max, AIIMS, Medanta
- Government hospital reports may have different formats

Always respond with ONLY the JSON object, no additional text or explanation."""


class ReportIntelligenceAgent:
    """AI Agent for medical report analysis using Claude"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"  # Using Sonnet for cost efficiency
    
    def analyze_report(
        self,
        image_base64: str,
        media_type: str = "image/jpeg",
        user_context: Optional[str] = None,
        test_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a medical report image using Claude Vision
        
        Args:
            image_base64: Base64 encoded image
            media_type: MIME type of the image
            user_context: Optional context about the patient/report
            test_history: Previous test results for context
            
        Returns:
            Extracted report data as dictionary
        """
        # Build user message
        user_message = "Please analyze this medical report image and extract all relevant information."
        
        if user_context:
            user_message += f"\n\nAdditional context: {user_context}"
        
        if test_history:
            recent_tests = test_history[:5]  # Last 5 tests
            history_summary = ", ".join([
                f"{t.get('test_name', 'Unknown')} on {t.get('test_date', 'N/A')}"
                for t in recent_tests
            ])
            user_message += f"\n\nRecent test history: {history_summary}"
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=REPORT_INTELLIGENCE_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": user_message,
                            }
                        ],
                    }
                ],
            )
            
            # Parse response
            response_text = response.content[0].text
            return self._parse_claude_response(response_text)
            
        except anthropic.APIError as e:
            print(f"Claude API error: {e}")
            return self._default_response(error=str(e))
        except Exception as e:
            print(f"Error analyzing report: {e}")
            return self._default_response(error=str(e))
    
    def analyze_text_report(
        self,
        text: str,
        user_context: Optional[str] = None,
        test_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a text-based report (from PDF extraction)
        """
        user_message = f"Please analyze this medical report text and extract all relevant information:\n\n{text}"
        
        if user_context:
            user_message += f"\n\nAdditional context: {user_context}"
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=REPORT_INTELLIGENCE_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ],
            )
            
            response_text = response.content[0].text
            return self._parse_claude_response(response_text)
            
        except Exception as e:
            print(f"Error analyzing text report: {e}")
            return self._default_response(error=str(e))
    
    def _parse_claude_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's JSON response"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
                
                # Normalize test names
                if "tests" in result:
                    for test in result["tests"]:
                        test["test_name"] = self._normalize_test_name(test.get("test_name", ""))
                
                return result
            else:
                return self._default_response(error="No JSON found in response")
                
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return self._default_response(error=f"JSON parse error: {e}")
    
    def _default_response(self, error: Optional[str] = None) -> Dict[str, Any]:
        """Return a default response structure"""
        return {
            "report_type": "lab_test",
            "hospital_name": None,
            "doctor_name": None,
            "patient_name": None,
            "report_date": None,
            "tests": [],
            "raw_text": error or "Unable to process report",
            "confidence_score": 0.0,
        }
    
    def _normalize_test_name(self, test_name: str) -> str:
        """Normalize test name to standard format"""
        if not test_name:
            return "Unknown Test"
        
        # Convert to lowercase for lookup
        lower_name = test_name.lower().strip()
        
        # Check aliases
        if lower_name in TEST_NAME_ALIASES:
            return TEST_NAME_ALIASES[lower_name]
        
        # Check if already a standard name (case-insensitive)
        for standard_name in INDIAN_TEST_COSTS.keys():
            if lower_name == standard_name.lower():
                return standard_name
        
        # Return original with title case
        return test_name.strip().title()
    
    def detect_duplicate(
        self,
        test_name: str,
        test_date: date,
        test_history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Check if a test is a potential duplicate based on validity periods
        
        Args:
            test_name: Name of the new test
            test_date: Date of the new test
            test_history: User's previous test results
            
        Returns:
            Dictionary with duplicate detection results
        """
        normalized_name = self._normalize_test_name(test_name)
        
        # Get validity period for this test
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
        
        # No previous test found
        if not latest_test:
            return {
                "is_duplicate": False,
                "test_name": normalized_name,
                "message": "No previous test found",
                "potential_savings": 0,
            }
        
        # Calculate days since last test
        days_since = (test_date - latest_test["date"]).days
        
        # Check if within validity period
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
        return INDIAN_TEST_COSTS.get(normalized_name, 500)  # Default ₹500
    
    def get_test_cost(self, test_name: str) -> float:
        """Get the cost of a specific test"""
        normalized_name = self._normalize_test_name(test_name)
        return INDIAN_TEST_COSTS.get(normalized_name, 500)
    
    def get_validity_period(self, test_name: str) -> int:
        """Get the validity period of a specific test in days"""
        normalized_name = self._normalize_test_name(test_name)
        return VALIDITY_PERIODS.get(normalized_name, VALIDITY_PERIODS["default"])


# Factory function to get the appropriate agent
_agent_instance = None
_using_mock_agent = False


def get_agent():
    """
    Get or create the report agent singleton.
    Auto-detects if Anthropic API key is missing and falls back to mock mode.
    """
    global _agent_instance, _using_mock_agent
    
    if _agent_instance is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        demo_mode = os.getenv("DEMO_MODE", "").lower() in ("true", "1", "yes")
        
        if demo_mode or not api_key or api_key.startswith("your_"):
            # Use mock agent for demo mode
            from agents.mock_agent import MockReportIntelligenceAgent
            _agent_instance = MockReportIntelligenceAgent()
            _using_mock_agent = True
        else:
            _agent_instance = ReportIntelligenceAgent()
            print("✅ Connected to Anthropic API")
    
    return _agent_instance


def is_using_mock_agent() -> bool:
    """Check if running with mock agent"""
    return _using_mock_agent

