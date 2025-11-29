"""
Swasthya Path - Layer 1: Report Intelligence Agent
FastAPI Backend Application
"""

import os
from datetime import datetime, date
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from models.schemas import (
    UploadReportResponse,
    TimelineResponse,
    SavingsResponse,
    ReportListResponse,
    DemoSetupResponse,
    HealthResponse,
    ErrorResponse,
    DuplicateDecision,
)
from database.supabase_client import get_db, is_demo_mode, reset_db
from agents.report_agent import get_agent
from utils.image_processing import process_upload
import auth_routes  # Authentication routes

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print("🚀 Starting Swasthya Path API...")
    
    # Reset DB singleton on restart to pick up code changes in development
    reset_db()
    
    # Initialize services to show mode info at startup
    db = get_db()
    agent = get_agent()
    
    if is_demo_mode():
        print("=" * 50)
        print("🎮 DEMO MODE ACTIVE")
        print("   - Using in-memory database (no Supabase)")
        print("   - Using simulated AI responses (no Anthropic)")
        print("   - Pre-loaded with sample medical data")
        print("   - Demo user: demo-user-123")
        print("=" * 50)
    
    yield
    # Shutdown
    print("👋 Shutting down Swasthya Path API...")


# Initialize FastAPI app
app = FastAPI(
    title="Swasthya Path API",
    description="Layer 1: Report Intelligence Agent - Medical report analysis and duplicate detection",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",")]
print(f"🌐 CORS enabled for origins: {cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc), "status_code": 500}
    )


# ==================== AUTHENTICATION ROUTES ====================

# Include authentication router
app.include_router(auth_routes.router)


# ==================== HEALTH CHECK ====================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now()
    )


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Swasthya Path API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# ==================== REPORT UPLOAD ====================

@app.post("/api/upload-report", response_model=UploadReportResponse, tags=["Reports"])
async def upload_report(
    file: UploadFile = File(..., description="Medical report image (JPEG, PNG) or PDF"),
    user_id: str = Form(..., description="User ID"),
    context: Optional[str] = Form(None, description="Optional context about the report"),
):
    """
    Upload and analyze a medical report
    
    This endpoint:
    1. Accepts an image or PDF of a medical report
    2. Uploads it to storage
    3. Uses Claude AI to extract structured data
    4. Checks for duplicate tests
    5. Returns analysis results and any duplicate alerts
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read file
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Initialize services
        db = get_db()
        agent = get_agent()
        
        # Ensure user exists
        db.get_or_create_user(user_id)
        
        # Process image
        base64_data, media_type, extracted_text = process_upload(file_bytes, file.content_type)
        
        # Upload to storage (optional, may fail if bucket not configured)
        image_url = None
        try:
            image_url = db.upload_image(file_bytes, file.filename or "report.jpg", user_id)
        except Exception as e:
            print(f"Warning: Could not upload to storage: {e}")
        
        # Get user's test history for duplicate detection
        test_history = db.get_test_results(user_id)
        
        # Analyze report with Claude
        if base64_data:
            analysis = agent.analyze_report(
                image_base64=base64_data,
                media_type=media_type,
                user_context=context,
                test_history=test_history
            )
        elif extracted_text:
            analysis = agent.analyze_text_report(
                text=extracted_text,
                user_context=context,
                test_history=test_history
            )
        else:
            raise HTTPException(status_code=400, detail="Could not process the uploaded file")
        
        # Parse report date
        report_date = date.today()
        if analysis.get("report_date"):
            try:
                report_date = datetime.strptime(analysis["report_date"], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                pass
        
        # Create report in database
        report = db.create_report(
            user_id=user_id,
            report_type=analysis.get("report_type", "lab_test"),
            report_date=report_date,
            hospital_name=analysis.get("hospital_name"),
            doctor_name=analysis.get("doctor_name"),
            raw_image_url=image_url,
            extracted_data=analysis
        )
        
        if not report:
            raise HTTPException(status_code=500, detail="Failed to save report")
        
        # Process tests and check for duplicates
        duplicate_alerts = []
        total_savings = 0.0
        
        for test in analysis.get("tests", []):
            test_name = test.get("test_name", "Unknown Test")
            
            # Check for duplicates
            duplicate_info = agent.detect_duplicate(
                test_name=test_name,
                test_date=report_date,
                test_history=test_history
            )
            
            if duplicate_info["is_duplicate"]:
                # Create duplicate alert
                alert = db.create_duplicate_alert(
                    user_id=user_id,
                    new_test_name=test_name,
                    original_test_date=duplicate_info["original_date"],
                    days_since_original=duplicate_info["days_since"],
                    alert_message=duplicate_info["message"],
                    savings_amount=duplicate_info["potential_savings"],
                    decision="pending"
                )
                if alert:
                    alert["savings_amount"] = duplicate_info["potential_savings"]
                    duplicate_alerts.append(alert)
                    total_savings += duplicate_info["potential_savings"]
            
            # Save test result
            db.create_test_result(
                report_id=report["id"],
                user_id=user_id,
                test_name=test_name,
                test_date=report_date,
                test_category=test.get("category", "other"),
                test_value=test.get("test_value"),
                test_unit=test.get("test_unit"),
                reference_range=test.get("reference_range"),
                status=test.get("status", "normal")
            )
        
        return UploadReportResponse(
            success=True,
            report_id=report["id"],
            extracted_data=analysis,
            duplicate_alerts=duplicate_alerts,
            message=f"Report analyzed successfully. {len(analysis.get('tests', []))} tests extracted.",
            total_potential_savings=total_savings
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing report: {str(e)}")


# ==================== DUPLICATE DECISION ====================

@app.post("/api/duplicate-decision/{alert_id}", tags=["Duplicates"])
async def update_duplicate_decision(
    alert_id: str,
    decision: DuplicateDecision,
):
    """Update the decision for a duplicate alert (skip or proceed)"""
    try:
        db = get_db()
        result = db.update_duplicate_decision(alert_id, decision.value)
        
        if not result:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "success": True,
            "alert_id": alert_id,
            "decision": decision.value,
            "message": f"Decision recorded: {decision.value}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== REPORTS ====================

@app.get("/api/reports/{user_id}", response_model=ReportListResponse, tags=["Reports"])
async def get_user_reports(user_id: str):
    """Get all reports for a user"""
    try:
        db = get_db()
        reports = db.get_reports(user_id)
        
        return ReportListResponse(
            user_id=user_id,
            reports=reports,
            total_count=len(reports)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/report/{report_id}", tags=["Reports"])
async def get_report(report_id: str):
    """Get a specific report by ID"""
    try:
        db = get_db()
        report = db.get_report(report_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== TIMELINE ====================

@app.get("/api/timeline/{user_id}", response_model=TimelineResponse, tags=["Timeline"])
async def get_user_timeline(user_id: str):
    """Get chronological timeline of all tests for a user"""
    try:
        db = get_db()
        timeline = db.get_timeline(user_id)
        
        return TimelineResponse(
            user_id=user_id,
            entries=timeline,
            total_tests=len(timeline)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SAVINGS ====================

@app.get("/api/savings/{user_id}", response_model=SavingsResponse, tags=["Savings"])
async def get_user_savings(user_id: str):
    """Get total savings from avoided duplicate tests"""
    try:
        db = get_db()
        savings = db.get_savings_summary(user_id)
        
        return SavingsResponse(
            user_id=user_id,
            total_savings=savings["total_savings"],
            tests_skipped=savings["tests_skipped"],
            breakdown=savings["breakdown"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DEMO ====================

@app.post("/api/demo/setup", response_model=DemoSetupResponse, tags=["Demo"])
async def setup_demo():
    """Create demo user and sample data for testing"""
    try:
        db = get_db()
        result = db.setup_demo_data()
        
        return DemoSetupResponse(
            success=result["success"],
            user_id=result["user_id"],
            message=result["message"],
            reports_created=result["reports_created"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/demo/user", tags=["Demo"])
async def get_demo_user():
    """Get demo user information"""
    return {
        "user_id": "demo-user-123",
        "name": "Rahul Kumar",
        "age": 42,
        "gender": "Male"
    }


# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

