-- Migration: Add API Keys and Usage Tracking
-- Description: Creates tables for API key management and usage analytics
-- Version: 1.0.0
-- Date: 2024-10-17

-- Create API keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    api_key_hash VARCHAR(64) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit_per_hour INTEGER DEFAULT 1000,
    requests_this_hour INTEGER DEFAULT 0,
    last_request_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create API usage logs table
CREATE TABLE IF NOT EXISTS api_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key_hash VARCHAR(64) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    timestamp TIMESTAMP DEFAULT NOW(),
    request_count INTEGER,
    response_time_ms INTEGER,
    status_code INTEGER,
    error_message TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(api_key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active);
CREATE INDEX IF NOT EXISTS idx_api_keys_company ON api_keys(company_name);

CREATE INDEX IF NOT EXISTS idx_usage_logs_timestamp ON api_usage_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_usage_logs_key ON api_usage_logs(api_key_hash);
CREATE INDEX IF NOT EXISTS idx_usage_logs_endpoint ON api_usage_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_usage_logs_user ON api_usage_logs(user_id);

-- Create updated_at trigger for api_keys
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_api_keys_updated_at
    BEFORE UPDATE ON api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) for multi-tenant isolation
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (adjust based on your auth setup)
-- Note: These policies assume you have a way to identify API key owners
-- You may need to modify these based on your specific auth implementation

-- For now, allow all operations (you can restrict later based on your needs)
-- In production, you'd want more restrictive policies

-- Example policies (uncomment and modify as needed):
/*
-- Users can only access their own API keys
CREATE POLICY "Users can view own api keys" ON api_keys
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can update own api keys" ON api_keys
    FOR UPDATE USING (auth.uid()::text = user_id);

-- Users can only access their own usage logs
CREATE POLICY "Users can view own usage logs" ON api_usage_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM api_keys
            WHERE api_key_hash = api_usage_logs.api_key_hash
            AND user_id = auth.uid()::text
        )
    );
*/

-- Insert sample data for testing (optional)
-- This creates a test API key you can use for development
/*
INSERT INTO api_keys (company_name, contact_email, api_key_hash, is_active, rate_limit_per_hour)
VALUES (
    'Cognition Engine Test',
    'test@cognition-engine.com',
    '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08', -- test-key-123
    true,
    10000
) ON CONFLICT (api_key_hash) DO NOTHING;
*/

-- Verification query
SELECT 'API keys migration completed successfully!' as status;
