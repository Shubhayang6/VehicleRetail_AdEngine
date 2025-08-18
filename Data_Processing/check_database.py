import sqlite3

# Connect to database
conn = sqlite3.connect('test_vehicle_data.db')
cursor = conn.cursor()

# Check if tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f'Tables in database: {[t[0] for t in tables]}')

if not tables:
    print('No tables found in database')
    conn.close()
    exit()

# Get total count
cursor.execute('SELECT COUNT(*) FROM processed_vehicle_data')
total_count = cursor.fetchone()[0]
print(f'Total records in database: {total_count}')

# Get sample records
cursor.execute('''
    SELECT vehicle_id, overall_health_score, maintenance_required, anomaly_detected 
    FROM processed_vehicle_data 
    LIMIT 5
''')
records = cursor.fetchall()

print('\nSample records:')
for r in records:
    print(f'  {r[0]}: Health={r[1]:.3f}, Maintenance={r[2]}, Anomaly={r[3]}')

# Get maintenance alerts
cursor.execute('SELECT COUNT(*) FROM health_alerts')
alert_count = cursor.fetchone()[0]
print(f'\nHealth alerts generated: {alert_count}')

if alert_count > 0:
    cursor.execute('SELECT vehicle_id, alert_type, severity, message FROM health_alerts LIMIT 3')
    alerts = cursor.fetchall()
    print('Sample alerts:')
    for alert in alerts:
        print(f'  {alert[0]}: {alert[1]} ({alert[2]}) - {alert[3]}')

conn.close()
