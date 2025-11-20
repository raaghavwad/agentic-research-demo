-- Oracle Database 23ai Initialization Script
-- Creates sample tables for the agentic research demo

-- Connect as SYSTEM user to FREEPDB1 (the pluggable database)
-- Usage: sqlcl SYSTEM/OraclePassword123@localhost:1521/FREEPDB1 @init_db.sql

-- Create a table to store AI database trends
CREATE TABLE ai_database_trends (
	id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	year NUMBER(4) NOT NULL,
	trend VARCHAR2(200) NOT NULL,
	description CLOB,
	category VARCHAR2(50),
	adoption_level VARCHAR2(20),
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data about AI database trends
INSERT INTO ai_database_trends (year, trend, description, category, adoption_level) VALUES
(2023, 'Vector Databases', 'Specialized databases optimized for storing and querying high-dimensional vector embeddings used in AI/ML applications', 'Storage', 'High');

INSERT INTO ai_database_trends (year, trend, description, category, adoption_level) VALUES
(2024, 'AI-Native Databases', 'Databases designed from the ground up with integrated AI capabilities including vector search, automatic indexing, and ML model serving', 'Architecture', 'Growing');

INSERT INTO ai_database_trends (year, trend, description, category, adoption_level) VALUES
(2024, 'Multi-Modal Search', 'Database systems supporting search across text, images, audio, and video using unified embedding spaces', 'Query', 'Emerging');

INSERT INTO ai_database_trends (year, trend, description, category, adoption_level) VALUES
(2025, 'Autonomous Database Operations', 'Self-managing databases using AI for automatic tuning, patching, backup, and optimization', 'Operations', 'High');

INSERT INTO ai_database_trends (year, trend, description, category, adoption_level) VALUES
(2025, 'Graph + Vector Hybrid', 'Combining graph database capabilities with vector similarity search for complex relationship and semantic queries', 'Storage', 'Emerging');

INSERT INTO ai_database_trends (year, trend, description, category, adoption_level) VALUES
(2025, 'Real-Time AI Inference in Database', 'Direct execution of ML models within the database engine for sub-millisecond inference', 'Performance', 'Growing');

COMMIT;

-- Create an index for faster year-based queries
CREATE INDEX idx_trends_year ON ai_database_trends(year);

-- Create a view for recent trends
CREATE OR REPLACE VIEW recent_ai_trends AS
SELECT year, trend, description, category
FROM ai_database_trends
WHERE year >= 2023
ORDER BY year DESC, trend;

-- Display the created data
SELECT 'Database initialized successfully!' as status FROM dual;
SELECT COUNT(*) as total_trends FROM ai_database_trends;
SELECT year, COUNT(*) as trend_count FROM ai_database_trends GROUP BY year ORDER BY year;
