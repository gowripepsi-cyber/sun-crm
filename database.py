import sqlite3
import os
from datetime import datetime
from settings_manager import settings_mgr

def get_db_connection():
    db_path = settings_mgr.get("db_location")
    # Ensure directory containing db exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if database is empty
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers';")
    db_exists = cursor.fetchone() is not None
    
    # 1. Customers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        mobile1 TEXT NOT NULL,
        mobile2 TEXT,
        address TEXT,
        created_at TEXT NOT NULL,
        notes TEXT,
        age_group TEXT,
        gender TEXT,
        category TEXT,
        tags TEXT
    );
    """)
    
    # 2. Credentials Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        service_name TEXT NOT NULL,
        username TEXT,
        password TEXT,
        remarks TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
    );
    """)
    
    # 3. Other Info Table (Dynamic custom key-value attributes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS other_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        value TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
    );
    """)
    
    # 4. Documents Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT,
        remarks TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
    );
    """)
    
    # 5. Activity Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        details TEXT,
        timestamp TEXT NOT NULL
    );
    """)
    
    # 6. Backup History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS backup_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        backup_path TEXT NOT NULL,
        backup_type TEXT NOT NULL,
        status TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)
    
    conn.commit()
    
    # Seed default data if database was empty
    if not db_exists:
        seed_sample_data(conn)
        log_activity("Database Initialized", "Created fresh database schemas and seeded initial sample data.")
        
    conn.close()

def log_activity(action, details=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO activity_logs (action, details, timestamp) VALUES (?, ?, ?);",
            (action, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to log activity: {e}")

def seed_sample_data(conn):
    cursor = conn.cursor()
    
    sample_customers = [
        ("SUN-2026-0001", "Aravind Swamy", "9876543210", "9876543211", "12, Gandhi Nagar, Chennai, Tamil Nadu", 
         "2026-01-15 10:30:00", "VIP Client. High priority.", "Adult", "Male", "VIP", "VIP,Tech,Corporate"),
        
        ("SUN-2026-0002", "Priya Sen", "8765432109", None, "56/A, Salt Lake, Sector 2, Kolkata, West Bengal", 
         "2026-02-18 14:22:10", "Enquired about subscription packages.", "Young Adult", "Female", "Regular", "Prospect,Creative"),
        
        ("SUN-2026-0003", "Robert Downey", "9944882211", "9933771100", "404 Malibu Point, California", 
         "2026-04-05 09:00:00", "International customer. Prefers email communication.", "Senior", "Male", "VIP", "Premium,Global"),
         
        ("SUN-2026-0004", "Simran Kaur", "7654321098", None, "Flat 302, Green Avenue, Mohali, Punjab", 
         "2026-06-10 11:15:45", "Retail category shop owner.", "Adult", "Female", "Regular", "Retail,Wholesale"),
         
        ("SUN-2026-0005", "David Beckham", "8887776665", None, "7 Wembley Lane, London", 
         "2026-07-09 18:40:00", "Sports consultant. Contact via WhatsApp primary.", "Adult", "Male", "Prospect", "Sports,International")
    ]
    
    # Insert Customers
    for cust in sample_customers:
        cursor.execute("""
        INSERT INTO customers (customer_code, name, mobile1, mobile2, address, created_at, notes, age_group, gender, category, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, cust)
        
        cust_id = cursor.lastrowid
        
        # Seed matching credentials
        if "VIP" in cust[8] or "Premium" in cust[10]:
            cursor.execute("""
            INSERT INTO credentials (customer_id, service_name, username, password, remarks, created_at)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (cust_id, "Cloud Portal", cust[1].lower().replace(" ", "") + "_admin", "SuperSecurePass123", "Primary admin access key.", cust[5]))
            
        # Seed matching other info
        cursor.execute("""
        INSERT INTO other_info (customer_id, title, value)
        VALUES (?, ?, ?);
        """, (cust_id, "Designation", "Director" if "VIP" in cust[8] else "Manager"))
        
        cursor.execute("""
        INSERT INTO other_info (customer_id, title, value)
        VALUES (?, ?, ?);
        """, (cust_id, "Preferred Contact", "Mobile 1"))
        
    conn.commit()

def generate_customer_code():
    conn = get_db_connection()
    cursor = conn.cursor()
    year = datetime.now().year
    prefix = f"SUN-{year}-"
    
    cursor.execute("SELECT customer_code FROM customers WHERE customer_code LIKE ? ORDER BY customer_code DESC LIMIT 1;", (f"{prefix}%",))
    row = cursor.fetchone()
    
    if row:
        last_code = row['customer_code']
        try:
            seq = int(last_code.split("-")[-1])
            next_seq = seq + 1
        except ValueError:
            next_seq = 1
    else:
        next_seq = 1
        
    conn.close()
    return f"{prefix}{next_seq:04d}"

# CRUD helpers for Customers
def add_customer(data):
    # data is a dict
    conn = get_db_connection()
    cursor = conn.cursor()
    
    code = generate_customer_code()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
    INSERT INTO customers (customer_code, name, mobile1, mobile2, address, created_at, notes, age_group, gender, category, tags)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        code,
        data.get("name"),
        data.get("mobile1"),
        data.get("mobile2"),
        data.get("address"),
        created_at,
        data.get("notes"),
        data.get("age_group"),
        data.get("gender"),
        data.get("category"),
        data.get("tags")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    log_activity("Add Customer", f"Added customer: {data.get('name')} ({code})")
    return new_id, code

def update_customer(customer_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE customers SET 
        name = ?, 
        mobile1 = ?, 
        mobile2 = ?, 
        address = ?, 
        notes = ?, 
        age_group = ?, 
        gender = ?, 
        category = ?, 
        tags = ?
    WHERE id = ?;
    """, (
        data.get("name"),
        data.get("mobile1"),
        data.get("mobile2"),
        data.get("address"),
        data.get("notes"),
        data.get("age_group"),
        data.get("gender"),
        data.get("category"),
        data.get("tags"),
        customer_id
    ))
    conn.commit()
    conn.close()
    log_activity("Update Customer", f"Updated customer ID: {customer_id} (Name: {data.get('name')})")

def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get details first for logs
    cursor.execute("SELECT name, customer_code FROM customers WHERE id = ?;", (customer_id,))
    row = cursor.fetchone()
    name = row['name'] if row else "Unknown"
    code = row['customer_code'] if row else "Unknown"
    
    cursor.execute("DELETE FROM customers WHERE id = ?;", (customer_id,))
    conn.commit()
    conn.close()
    log_activity("Delete Customer", f"Deleted customer: {name} ({code})")

def get_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?;", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY id DESC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# CRUD helpers for Credentials
def add_credential(customer_id, service_name, username, password, remarks=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO credentials (customer_id, service_name, username, password, remarks, created_at)
    VALUES (?, ?, ?, ?, ?, ?);
    """, (customer_id, service_name, username, password, remarks, created_at))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    log_activity("Add Credential", f"Added credential for Customer ID: {customer_id} (Service: {service_name})")
    return new_id

def update_credential(cred_id, service_name, username, password, remarks=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE credentials SET service_name = ?, username = ?, password = ?, remarks = ? WHERE id = ?;
    """, (service_name, username, password, remarks, cred_id))
    conn.commit()
    conn.close()

def delete_credential(cred_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM credentials WHERE id = ?;", (cred_id,))
    conn.commit()
    conn.close()

def get_customer_credentials(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM credentials WHERE customer_id = ? ORDER BY id DESC;", (customer_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# CRUD helpers for Custom Fields (Other Info)
def add_other_info(customer_id, title, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO other_info (customer_id, title, value) VALUES (?, ?, ?);", (customer_id, title, value))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_other_info(info_id, title, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE other_info SET title = ?, value = ? WHERE id = ?;", (title, value, info_id))
    conn.commit()
    conn.close()

def delete_other_info(info_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM other_info WHERE id = ?;", (info_id,))
    conn.commit()
    conn.close()

def get_customer_other_info(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM other_info WHERE customer_id = ? ORDER BY id ASC;", (customer_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# CRUD helpers for Documents
def add_document(customer_id, filename, file_path, file_type, remarks=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO documents (customer_id, filename, file_path, file_type, remarks, created_at)
    VALUES (?, ?, ?, ?, ?, ?);
    """, (customer_id, filename, file_path, file_type, remarks, created_at))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    log_activity("Add Document", f"Attached document: {filename} to Customer ID: {customer_id}")
    return new_id

def update_document_remarks(doc_id, remarks):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE documents SET remarks = ? WHERE id = ?;", (remarks, doc_id))
    conn.commit()
    conn.close()

def delete_document(doc_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get filename for logging
    cursor.execute("SELECT filename FROM documents WHERE id = ?;", (doc_id,))
    row = cursor.fetchone()
    filename = row['filename'] if row else "Unknown File"
    
    cursor.execute("DELETE FROM documents WHERE id = ?;", (doc_id,))
    conn.commit()
    conn.close()
    log_activity("Delete Document", f"Removed document attachment record: {filename}")

def get_customer_documents(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE customer_id = ? ORDER BY id DESC;", (customer_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Stats and Dashboard queries
def get_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Total Customers
    cursor.execute("SELECT COUNT(*) as count FROM customers;")
    stats['total_customers'] = cursor.fetchone()['count']
    
    # Today's Customers
    today_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) as count FROM customers WHERE created_at LIKE ?;", (f"{today_str}%",))
    stats['today_customers'] = cursor.fetchone()['count']
    
    # This Month's Customers
    month_str = datetime.now().strftime("%Y-%m")
    cursor.execute("SELECT COUNT(*) as count FROM customers WHERE created_at LIKE ?;", (f"{month_str}%",))
    stats['month_customers'] = cursor.fetchone()['count']
    
    # Total Documents
    cursor.execute("SELECT COUNT(*) as count FROM documents;")
    stats['total_documents'] = cursor.fetchone()['count']
    
    # Total Credentials
    cursor.execute("SELECT COUNT(*) as count FROM credentials;")
    stats['total_credentials'] = cursor.fetchone()['count']
    
    # Last Backup Status
    cursor.execute("SELECT timestamp, status FROM backup_history ORDER BY id DESC LIMIT 1;")
    row = cursor.fetchone()
    if row:
        stats['backup_status'] = f"Last: {row['timestamp']} ({row['status']})"
    else:
        stats['backup_status'] = "No backups yet"
        
    conn.close()
    return stats

def get_recent_customers(limit=5):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY created_at DESC LIMIT ?;", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recent_activities(limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT ?;", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Backup logs CRUD
def log_backup(backup_path, backup_type, status):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO backup_history (backup_path, backup_type, status, timestamp) VALUES (?, ?, ?, ?);",
            (backup_path, backup_type, status, timestamp)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to log backup: {e}")

def get_backup_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM backup_history ORDER BY timestamp DESC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Advanced Search Query
def search_customers(filters):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT DISTINCT c.* FROM customers c"
    joins = []
    where_clauses = []
    params = []
    
    if filters.get("name"):
        where_clauses.append("c.name LIKE ?")
        params.append(f"%{filters['name']}%")
        
    if filters.get("mobile"):
        where_clauses.append("(c.mobile1 LIKE ? OR c.mobile2 LIKE ?)")
        params.append(f"%{filters['mobile']}%")
        params.append(f"%{filters['mobile']}%")
        
    if filters.get("address"):
        where_clauses.append("c.address LIKE ?")
        params.append(f"%{filters['address']}%")
        
    if filters.get("category"):
        where_clauses.append("c.category = ?")
        params.append(filters['category'])
        
    if filters.get("username"):
        joins.append("JOIN credentials cred ON c.id = cred.customer_id")
        where_clauses.append("cred.username LIKE ?")
        params.append(f"%{filters['username']}%")
        
    if filters.get("document_name"):
        joins.append("JOIN documents doc ON c.id = doc.customer_id")
        where_clauses.append("doc.filename LIKE ?")
        params.append(f"%{filters['document_name']}%")

    if joins:
        query += " " + " ".join(joins)
        
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
        
    query += " ORDER BY c.id DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Report Generator Queries
def get_category_report_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, COUNT(*) as count FROM customers GROUP BY category;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_age_group_report_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT age_group, COUNT(*) as count FROM customers GROUP BY age_group;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_gender_report_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT gender, COUNT(*) as count FROM customers GROUP BY gender;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_document_report_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT d.*, c.name as customer_name, c.customer_code 
    FROM documents d
    JOIN customers c ON d.customer_id = c.id
    ORDER BY d.id DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
