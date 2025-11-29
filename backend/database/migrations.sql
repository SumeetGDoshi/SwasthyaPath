-- Swasthya Path - Layer 1: Report Intelligence Agent
-- Database Schema for Supabase
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  age INTEGER,
  gender TEXT,
  phone TEXT,
  email TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);

-- =====================================================
-- MEDICAL REPORTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS medical_reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  report_type TEXT DEFAULT 'lab_test', -- 'lab_test', 'imaging', 'prescription', 'consultation'
  report_date DATE NOT NULL,
  hospital_name TEXT,
  doctor_name TEXT,
  raw_image_url TEXT, -- Supabase storage URL
  extracted_data JSONB, -- Structured data from Claude
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_medical_reports_user_id ON medical_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_medical_reports_report_date ON medical_reports(report_date DESC);
CREATE INDEX IF NOT EXISTS idx_medical_reports_report_type ON medical_reports(report_type);

-- =====================================================
-- TEST RESULTS TABLE (Normalized Individual Tests)
-- =====================================================
CREATE TABLE IF NOT EXISTS test_results (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  report_id UUID REFERENCES medical_reports(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  test_name TEXT NOT NULL, -- Normalized test name
  test_category TEXT DEFAULT 'other', -- 'blood', 'imaging', 'vitals', 'urine', 'other'
  test_value TEXT,
  test_unit TEXT,
  reference_range TEXT,
  test_date DATE NOT NULL,
  status TEXT DEFAULT 'normal', -- 'normal', 'abnormal', 'critical'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_test_results_user_id ON test_results(user_id);
CREATE INDEX IF NOT EXISTS idx_test_results_test_name ON test_results(test_name);
CREATE INDEX IF NOT EXISTS idx_test_results_test_date ON test_results(test_date DESC);
CREATE INDEX IF NOT EXISTS idx_test_results_user_test ON test_results(user_id, test_name, test_date DESC);

-- =====================================================
-- DUPLICATE ALERTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS duplicate_alerts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  new_test_name TEXT NOT NULL,
  original_test_date DATE NOT NULL,
  days_since_original INTEGER NOT NULL,
  decision TEXT DEFAULT 'pending', -- 'skip', 'proceed', 'pending'
  savings_amount DECIMAL(10, 2) DEFAULT 0,
  alert_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_duplicate_alerts_user_id ON duplicate_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_duplicate_alerts_decision ON duplicate_alerts(decision);
CREATE INDEX IF NOT EXISTS idx_duplicate_alerts_created_at ON duplicate_alerts(created_at DESC);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE duplicate_alerts ENABLE ROW LEVEL SECURITY;

-- For MVP, allow all operations (adjust for production)
-- Users table policies
CREATE POLICY "Allow all operations on users" ON users
  FOR ALL USING (true) WITH CHECK (true);

-- Medical reports policies
CREATE POLICY "Allow all operations on medical_reports" ON medical_reports
  FOR ALL USING (true) WITH CHECK (true);

-- Test results policies
CREATE POLICY "Allow all operations on test_results" ON test_results
  FOR ALL USING (true) WITH CHECK (true);

-- Duplicate alerts policies
CREATE POLICY "Allow all operations on duplicate_alerts" ON duplicate_alerts
  FOR ALL USING (true) WITH CHECK (true);

-- =====================================================
-- STORAGE BUCKET FOR MEDICAL REPORTS
-- =====================================================
-- Run this separately in Supabase dashboard or via API:
-- 1. Go to Storage in Supabase dashboard
-- 2. Create new bucket named "medical-reports"
-- 3. Set it to "Public" bucket
-- 4. Add policy to allow uploads

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_medical_reports_updated_at ON medical_reports;
CREATE TRIGGER update_medical_reports_updated_at
  BEFORE UPDATE ON medical_reports
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Timeline view with all test details
CREATE OR REPLACE VIEW user_test_timeline AS
SELECT 
  tr.id,
  tr.user_id,
  tr.test_name,
  tr.test_value,
  tr.test_unit,
  tr.reference_range,
  tr.test_date,
  tr.status,
  tr.test_category,
  mr.hospital_name,
  mr.doctor_name,
  mr.report_type
FROM test_results tr
LEFT JOIN medical_reports mr ON tr.report_id = mr.id
ORDER BY tr.test_date DESC, tr.created_at DESC;

-- Savings summary view
CREATE OR REPLACE VIEW user_savings_summary AS
SELECT 
  user_id,
  COUNT(*) FILTER (WHERE decision = 'skip') as tests_skipped,
  COALESCE(SUM(savings_amount) FILTER (WHERE decision = 'skip'), 0) as total_savings,
  COUNT(*) as total_alerts
FROM duplicate_alerts
GROUP BY user_id;

-- =====================================================
-- DEMO DATA (Optional - Comment out if not needed)
-- =====================================================

-- Insert demo user
INSERT INTO users (id, name, age, gender)
VALUES ('demo-user-123', 'Rahul Kumar', 42, 'Male')
ON CONFLICT (id) DO NOTHING;

-- Note: Additional demo data should be created via the API endpoint
-- POST /api/demo/setup

-- =====================================================
-- GRANT PERMISSIONS
-- =====================================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO anon, authenticated;

-- Grant access to tables
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Grant access to views
GRANT SELECT ON user_test_timeline TO anon, authenticated;
GRANT SELECT ON user_savings_summary TO anon, authenticated;


