/**
 * TypeScript types for Swasthya Path Layer 1
 */

// Enums
export type ReportType = "lab_test" | "imaging" | "prescription" | "consultation";
export type TestStatus = "normal" | "abnormal" | "critical";
export type TestCategory = "blood" | "imaging" | "vitals" | "urine" | "other";
export type DuplicateDecision = "skip" | "proceed" | "pending";

// User types
export interface User {
  id: string;
  name: string;
  age?: number;
  gender?: string;
  created_at: string;
}

// Test result types
export interface TestResult {
  id: string;
  report_id: string;
  user_id: string;
  test_name: string;
  test_category: TestCategory;
  test_value?: string;
  test_unit?: string;
  reference_range?: string;
  test_date: string;
  status: TestStatus;
  created_at: string;
}

// Extracted test from Claude
export interface ExtractedTest {
  test_name: string;
  test_value?: string;
  test_unit?: string;
  reference_range?: string;
  status?: string;
  category?: string;
}

// Extracted report data from Claude
export interface ExtractedReportData {
  report_type: string;
  hospital_name?: string;
  doctor_name?: string;
  patient_name?: string;
  report_date?: string;
  tests: ExtractedTest[];
  raw_text?: string;
  confidence_score?: number;
}

// Medical report types
export interface MedicalReport {
  id: string;
  user_id: string;
  report_type: ReportType;
  report_date: string;
  hospital_name?: string;
  doctor_name?: string;
  raw_image_url?: string;
  extracted_data?: ExtractedReportData;
  created_at: string;
}

// Duplicate alert types
export interface DuplicateAlert {
  id: string;
  user_id: string;
  new_test_name: string;
  original_test_date: string;
  days_since_original: number;
  decision: DuplicateDecision;
  savings_amount: number;
  alert_message: string;
  created_at: string;
}

// Timeline entry for display
export interface TimelineEntry {
  id: string;
  test_name: string;
  test_value?: string;
  test_unit?: string;
  test_date: string;
  valid_until?: string;
  status: TestStatus;
  hospital_name?: string;
  is_duplicate: boolean;
  category: TestCategory;
  reference_range?: string;
}

// API Response types
export interface UploadReportResponse {
  success: boolean;
  report_id?: string;
  extracted_data?: ExtractedReportData;
  duplicate_alerts: DuplicateAlert[];
  message: string;
  total_potential_savings: number;
}

export interface TimelineResponse {
  user_id: string;
  entries: TimelineEntry[];
  total_tests: number;
}

export interface SavingsBreakdown {
  test_name: string;
  date_skipped: string;
  amount_saved: number;
}

export interface SavingsResponse {
  user_id: string;
  total_savings: number;
  tests_skipped: number;
  breakdown: SavingsBreakdown[];
}

export interface ReportListResponse {
  user_id: string;
  reports: MedicalReport[];
  total_count: number;
}

export interface DemoSetupResponse {
  success: boolean;
  user_id: string;
  message: string;
  reports_created: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  status_code: number;
}

// Component props types
export interface ReportUploaderProps {
  userId: string;
  onUploadComplete?: (response: UploadReportResponse) => void;
  onError?: (error: string) => void;
}

export interface DuplicateAlertProps {
  alert: DuplicateAlert;
  onDecision: (decision: DuplicateDecision) => void;
  isOpen: boolean;
  onClose: () => void;
}

export interface TimelineViewProps {
  entries: TimelineEntry[];
  isLoading?: boolean;
}

export interface SavingsCounterProps {
  totalSavings: number;
  testsSkipped: number;
  animated?: boolean;
}

export interface TestCardProps {
  test: TimelineEntry;
  showHospital?: boolean;
}

// Utility types
export interface ApiError {
  message: string;
  status: number;
}

export type AsyncState<T> = {
  data: T | null;
  loading: boolean;
  error: string | null;
};


