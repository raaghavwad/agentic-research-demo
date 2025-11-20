#!/usr/bin/env python3
"""Test Oracle database connection"""
import oracledb

try:
    conn = oracledb.connect(
        user='SYSTEM',
        password='OraclePassword123',
        dsn='localhost:1521/FREEPDB1'
    )
    print('✅ Oracle connection successful!')
    
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM ai_database_trends')
    count = cursor.fetchone()[0]
    print(f'Found {count} rows in ai_database_trends table')
    
    cursor.execute('SELECT year, trend FROM ai_database_trends ORDER BY year')
    rows = cursor.fetchall()
    print('\nSample data:')
    for year, trend in rows[:3]:
        print(f'  {year}: {trend}')
    
    conn.close()
    print('\n✅ All tests passed!')
except Exception as e:
    print(f'❌ Error: {e}')
