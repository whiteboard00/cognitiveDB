# Database Migration Guide

## Overview

This guide explains how to set up the database schema required for the Cognition Engine SDK. The engine uses several core tables to track learning analytics, mastery probabilities, and performance metrics.

## Required Tables

### 1. `user_skill_mastery`

Tracks individual skill mastery with Bayesian Knowledge Tracing parameters.

```sql
CREATE TABLE user_skill_mastery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    skill_id UUID NOT NULL,
    mastery_probability DECIMAL(4,3) NOT NULL DEFAULT 0.25,
    learning_velocity DECIMAL(5,4) DEFAULT 0.0,
    total_attempts INTEGER DEFAULT 0,
    correct_attempts INTEGER DEFAULT 0,
    plateau_flag BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_user_skill_mastery_user_id ON user_skill_mastery(user_id);
CREATE INDEX idx_user_skill_mastery_skill_id ON user_skill_mastery(skill_id);
CREATE INDEX idx_user_skill_mastery_mastery ON user_skill_mastery(mastery_probability);
```

### 2. `learning_events`

Comprehensive log of all learning activities and state changes.

```sql
CREATE TABLE learning_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    skill_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    mastery_before DECIMAL(4,3),
    mastery_after DECIMAL(4,3),
    event_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_learning_events_user_id ON learning_events(user_id);
CREATE INDEX idx_learning_events_skill_id ON learning_events(skill_id);
CREATE INDEX idx_learning_events_type ON learning_events(event_type);
CREATE INDEX idx_learning_events_created_at ON learning_events(created_at);
```

### 3. `user_performance_snapshots`

Periodic performance captures for trend analysis and predictions.

```sql
CREATE TABLE user_performance_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    snapshot_type VARCHAR(50) NOT NULL,
    related_id UUID,
    estimated_ability_math DECIMAL(4,3),
    estimated_ability_rw DECIMAL(4,3),
    predicted_sat_math INTEGER,
    predicted_sat_rw INTEGER,
    skills_snapshot JSONB,
    avg_time_per_question DECIMAL(6,2),
    avg_confidence_score DECIMAL(3,2),
    cognitive_efficiency_score DECIMAL(4,3),
    questions_answered INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_performance_snapshots_user_id ON user_performance_snapshots(user_id);
CREATE INDEX idx_performance_snapshots_type ON user_performance_snapshots(snapshot_type);
CREATE INDEX idx_performance_snapshots_created_at ON user_performance_snapshots(created_at);
```

### 4. `topics` (if not exists)

Skill/topic definitions with category relationships.

```sql
CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    category_id UUID NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_topics_category_id ON topics(category_id);
CREATE INDEX idx_topics_name ON topics(name);
```

### 5. `categories` (if not exists)

Category definitions for organizing topics.

```sql
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    section VARCHAR(20) NOT NULL, -- 'math' or 'rw' (reading/writing)
    weight DECIMAL(4,3) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_categories_section ON categories(section);
CREATE INDEX idx_categories_name ON categories(name);
```

### 6. `study_plans` (if not exists)

User study plans for goal tracking (enhanced with new columns).

```sql
-- If study_plans table doesn't exist, create it
CREATE TABLE IF NOT EXISTS study_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    target_math_score INTEGER,
    target_rw_score INTEGER,
    test_date DATE,
    start_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add new columns if they don't exist (safe to run multiple times)
ALTER TABLE study_plans
ADD COLUMN IF NOT EXISTS target_math_score INTEGER,
ADD COLUMN IF NOT EXISTS target_rw_score INTEGER,
ADD COLUMN IF NOT EXISTS test_date DATE,
ADD COLUMN IF NOT EXISTS start_date DATE DEFAULT CURRENT_DATE,
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_study_plans_user_id ON study_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_study_plans_active ON study_plans(is_active);
```

## Migration Scripts

### Complete Migration (PostgreSQL/Supabase)

```sql
-- Run this script in your Supabase SQL Editor or PostgreSQL client

-- 1. Create/verify categories table
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    section VARCHAR(20) NOT NULL,
    weight DECIMAL(4,3) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Create/verify topics table
CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    category_id UUID NOT NULL REFERENCES categories(id),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Create/verify study_plans table
CREATE TABLE IF NOT EXISTS study_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    target_math_score INTEGER,
    target_rw_score INTEGER,
    test_date DATE,
    start_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. Create user_skill_mastery table
CREATE TABLE user_skill_mastery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    skill_id UUID NOT NULL REFERENCES topics(id),
    mastery_probability DECIMAL(4,3) NOT NULL DEFAULT 0.25,
    learning_velocity DECIMAL(5,4) DEFAULT 0.0,
    total_attempts INTEGER DEFAULT 0,
    correct_attempts INTEGER DEFAULT 0,
    plateau_flag BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. Create learning_events table
CREATE TABLE learning_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    skill_id UUID NOT NULL REFERENCES topics(id),
    event_type VARCHAR(50) NOT NULL,
    mastery_before DECIMAL(4,3),
    mastery_after DECIMAL(4,3),
    event_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. Create user_performance_snapshots table
CREATE TABLE user_performance_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    snapshot_type VARCHAR(50) NOT NULL,
    related_id UUID,
    estimated_ability_math DECIMAL(4,3),
    estimated_ability_rw DECIMAL(4,3),
    predicted_sat_math INTEGER,
    predicted_sat_rw INTEGER,
    skills_snapshot JSONB,
    avg_time_per_question DECIMAL(6,2),
    avg_confidence_score DECIMAL(3,2),
    cognitive_efficiency_score DECIMAL(4,3),
    questions_answered INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_skill_mastery_user_id ON user_skill_mastery(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skill_mastery_skill_id ON user_skill_mastery(skill_id);
CREATE INDEX IF NOT EXISTS idx_user_skill_mastery_mastery ON user_skill_mastery(mastery_probability);

CREATE INDEX IF NOT EXISTS idx_learning_events_user_id ON learning_events(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_events_skill_id ON learning_events(skill_id);
CREATE INDEX IF NOT EXISTS idx_learning_events_type ON learning_events(event_type);
CREATE INDEX IF NOT EXISTS idx_learning_events_created_at ON learning_events(created_at);

CREATE INDEX IF NOT EXISTS idx_performance_snapshots_user_id ON user_performance_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_performance_snapshots_type ON user_performance_snapshots(snapshot_type);
CREATE INDEX IF NOT EXISTS idx_performance_snapshots_created_at ON user_performance_snapshots(created_at);

CREATE INDEX IF NOT EXISTS idx_study_plans_user_id ON study_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_study_plans_active ON study_plans(is_active);

-- 8. Enable Row Level Security (RLS) if needed
ALTER TABLE user_skill_mastery ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_performance_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_plans ENABLE ROW LEVEL SECURITY;

-- 9. Create RLS policies (adjust based on your auth setup)
-- These policies assume you have user authentication set up

-- Users can only access their own mastery data
CREATE POLICY "Users can view own mastery" ON user_skill_mastery
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own mastery" ON user_skill_mastery
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can only access their own events
CREATE POLICY "Users can view own events" ON learning_events
    FOR SELECT USING (auth.uid() = user_id);

-- Users can only access their own snapshots
CREATE POLICY "Users can view own snapshots" ON user_performance_snapshots
    FOR SELECT USING (auth.uid() = user_id);

-- Users can only access their own study plans
CREATE POLICY "Users can view own study plans" ON study_plans
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own study plans" ON study_plans
    FOR UPDATE USING (auth.uid() = user_id);

-- 10. Insert sample data (optional)
-- Insert sample categories
INSERT INTO categories (name, section, weight) VALUES
    ('Algebra', 'math', 0.35),
    ('Advanced Math', 'math', 0.35),
    ('Problem Solving', 'math', 0.15),
    ('Geometry', 'math', 0.15),
    ('Reading Comprehension', 'rw', 0.25),
    ('Grammar', 'rw', 0.25),
    ('Editing', 'rw', 0.25),
    ('Rhetoric', 'rw', 0.25)
ON CONFLICT (name) DO NOTHING;

-- Insert sample topics
INSERT INTO topics (name, category_id, description)
SELECT
    'Linear Equations',
    id,
    'Solving linear equations and inequalities'
FROM categories WHERE name = 'Algebra'
ON CONFLICT (name) DO NOTHING;

-- 11. Verify installation
SELECT 'Migration completed successfully!' as status;
```

## Verification Queries

After running the migration, verify the setup:

```sql
-- Check table creation
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'user_skill_mastery',
    'learning_events',
    'user_performance_snapshots',
    'study_plans',
    'topics',
    'categories'
);

-- Check indexes
SELECT tablename, indexname FROM pg_indexes
WHERE tablename IN (
    'user_skill_mastery',
    'learning_events',
    'user_performance_snapshots'
);

-- Check RLS policies
SELECT schemaname, tablename, policyname FROM pg_policies
WHERE tablename IN (
    'user_skill_mastery',
    'learning_events',
    'user_performance_snapshots',
    'study_plans'
);
```

## Troubleshooting

### Common Issues

1. **Permission Denied**

   - Ensure you're running as a user with CREATE TABLE permissions
   - Check if tables already exist (use IF NOT EXISTS clauses)

2. **Foreign Key Errors**

   - Create parent tables (categories, topics) before child tables
   - Ensure referenced tables exist

3. **RLS Policy Errors**

   - Verify your authentication setup
   - Check if auth.uid() function is available
   - Adjust policies based on your auth implementation

4. **Index Creation Errors**
   - Indexes are created with IF NOT EXISTS - should be safe to re-run
   - Check for naming conflicts

### Rollback Script

If you need to rollback the migration:

```sql
-- Drop tables (order matters due to foreign keys)
DROP TABLE IF EXISTS user_performance_snapshots;
DROP TABLE IF EXISTS learning_events;
DROP TABLE IF EXISTS user_skill_mastery;
DROP TABLE IF EXISTS study_plans;
DROP TABLE IF EXISTS topics;
DROP TABLE IF EXISTS categories;

-- Drop indexes (if needed)
DROP INDEX IF EXISTS idx_user_skill_mastery_user_id;
DROP INDEX IF EXISTS idx_user_skill_mastery_skill_id;
DROP INDEX IF EXISTS idx_learning_events_user_id;
DROP INDEX IF EXISTS idx_performance_snapshots_user_id;
```

## Performance Optimization

For production environments, consider these additional optimizations:

```sql
-- Additional indexes for common queries
CREATE INDEX idx_mastery_velocity ON user_skill_mastery(learning_velocity);
CREATE INDEX idx_mastery_plateau ON user_skill_mastery(plateau_flag);
CREATE INDEX idx_events_mastery_change ON learning_events(mastery_before, mastery_after);

-- Partitioning for large tables (if expecting high volume)
-- CREATE TABLE learning_events_y2024m01 PARTITION OF learning_events FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Materialized views for common analytics queries
CREATE MATERIALIZED VIEW user_mastery_summary AS
SELECT
    user_id,
    COUNT(*) as total_skills,
    AVG(mastery_probability) as avg_mastery,
    SUM(total_attempts) as total_attempts,
    COUNT(CASE WHEN plateau_flag THEN 1 END) as plateaued_skills
FROM user_skill_mastery
GROUP BY user_id;

-- Create unique index to refresh materialized view
CREATE UNIQUE INDEX idx_user_mastery_summary_user_id ON user_mastery_summary(user_id);
```

## Next Steps

1. **Run the migration script** in your Supabase SQL Editor
2. **Verify table creation** using the verification queries
3. **Test the SDK** with sample data
4. **Set up monitoring** for the new tables
5. **Configure backups** for the analytics data

## Support

If you encounter issues:

1. Check the Supabase logs for detailed error messages
2. Verify your user permissions in Supabase Dashboard
3. Test with a minimal migration script first
4. Contact support with specific error messages and table schemas
