-- Authentication System Migration
-- Add authentication fields to users table and create refresh_tokens table
-- Run this AFTER the initial migrations.sql

-- =====================================================
-- ADD AUTHENTICATION FIELDS TO USERS TABLE
-- =====================================================

-- Add email column (unique)
ALTER TABLE users ADD COLUMN IF NOT EXISTS email TEXT UNIQUE;

-- Add password hash column
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- Add account status columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false;

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- =====================================================
-- REFRESH TOKENS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS refresh_tokens (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token TEXT UNIQUE NOT NULL,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  revoked BOOLEAN DEFAULT false
);

-- Indexes for refresh tokens
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- =====================================================
-- ROW LEVEL SECURITY FOR REFRESH TOKENS
-- =====================================================

ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;

-- Allow all operations for MVP (adjust for production)
CREATE POLICY "Allow all operations on refresh_tokens" ON refresh_tokens
  FOR ALL USING (true) WITH CHECK (true);

-- =====================================================
-- CLEANUP EXPIRED TOKENS FUNCTION (Optional)
-- =====================================================

CREATE OR REPLACE FUNCTION cleanup_expired_refresh_tokens()
RETURNS void AS $$
BEGIN
  DELETE FROM refresh_tokens 
  WHERE expires_at < NOW() OR revoked = true;
END;
$$ LANGUAGE plpgsql;

-- Optional: Schedule this to run periodically
-- You can set up a cron job or pg_cron extension to run this daily
