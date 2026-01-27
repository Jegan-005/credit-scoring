import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DATABASE_FILE = 'credx.db'

def get_db():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db_connection():
    conn = get_db()
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        has_age_column = any(col[1] == 'age' for col in columns)
        
        if has_age_column:
            print("🔄 Migrating database schema...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users_backup AS 
                SELECT id, username, password, email, created_at 
                FROM users WHERE 1=0
            ''')
            
            try:
                cursor.execute('''
                    INSERT INTO users_backup (username, password, email, created_at)
                    SELECT username, password, email, created_at FROM users
                ''')
            except:
                pass
            
            cursor.execute('DROP TABLE IF EXISTS users')
            print("✅ Old users table dropped")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        if has_age_column:
            try:
                cursor.execute('''
                    INSERT INTO users (username, password, email, created_at)
                    SELECT username, password, email, created_at FROM users_backup
                ''')
                cursor.execute('DROP TABLE users_backup')
                print("✅ User identity data restored")
            except:
                pass
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_financials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                age INTEGER NOT NULL,
                income INTEGER NOT NULL,
                existing_loans INTEGER NOT NULL,
                total_emi INTEGER NOT NULL,
                credit_utilization REAL NOT NULL,
                defaults INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                credit_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                eligible_amount INTEGER NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS review_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                review_date TEXT NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_username ON users(username)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_email ON users(email)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_financials_username ON user_financials(username)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_credit_history_username ON credit_history(username)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_credit_history_date ON credit_history(date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_review_schedule_username ON review_schedule(username)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_review_schedule_date ON review_schedule(review_date)
        ''')
        
        conn.commit()
        print("✅ Database initialized successfully!")

def create_user(username, password, email):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                return False, "Username already exists", None
            
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return False, "Email already registered", None
            
            created_at = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO users (username, password, email, created_at)
                VALUES (?, ?, ?, ?)
            ''', (username, password, email, created_at))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            return True, "User created successfully", user_id
            
    except sqlite3.IntegrityError as e:
        return False, f"Database integrity error: {str(e)}", None
    except Exception as e:
        return False, f"Database error: {str(e)}", None

def authenticate_user(username, password):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, password, email, created_at
                FROM users 
                WHERE username = ?
            ''', (username,))
            
            user = cursor.fetchone()
            
            if user and user['password'] == password:
                user_data = {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'created_at': user['created_at']
                }
                return True, user_data, "Authentication successful"
            else:
                return False, None, "Invalid username or password"
                
    except Exception as e:
        return False, None, f"Database error: {str(e)}"

def get_user_by_username(username):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, created_at
                FROM users 
                WHERE username = ?
            ''', (username,))
            
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'created_at': user['created_at']
                }
            return None
            
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def get_user_count():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM users')
            result = cursor.fetchone()
            return result['count'] if result else 0
    except Exception as e:
        print(f"Error getting user count: {e}")
        return 0

def database_health_check():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users'
            ''')
            table_exists = cursor.fetchone() is not None
            
            user_count = get_user_count()
            
            db_size = os.path.getsize(DATABASE_FILE) if os.path.exists(DATABASE_FILE) else 0
            
            return {
                'status': 'healthy',
                'database_file': DATABASE_FILE,
                'table_exists': table_exists,
                'user_count': user_count,
                'database_size_bytes': db_size,
                'database_size_kb': round(db_size / 1024, 2)
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

if __name__ == "__main__":
    print("Initializing CredX AI Database...")
    init_db()
    
    health = database_health_check()
    print(f"Database Health Check: {health}")

def save_credit_score_history(username, credit_score, risk_level, eligible_amount):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT id FROM credit_history 
                WHERE username = ? AND date LIKE ?
            ''', (username, f"{today}%"))
            
            existing_record = cursor.fetchone()
            
            if existing_record:
                cursor.execute('''
                    UPDATE credit_history 
                    SET credit_score = ?, risk_level = ?, eligible_amount = ?, date = ?
                    WHERE username = ? AND date LIKE ?
                ''', (credit_score, risk_level, eligible_amount, 
                     datetime.now().isoformat(), username, f"{today}%"))
            else:
                cursor.execute('''
                    INSERT INTO credit_history (username, credit_score, risk_level, eligible_amount, date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, credit_score, risk_level, eligible_amount, datetime.now().isoformat()))
            
            conn.commit()
            return True, "Credit score history saved successfully"
            
    except Exception as e:
        return False, f"Failed to save credit score history: {str(e)}"

def get_credit_score_history(username, limit=30):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT credit_score, risk_level, eligible_amount, date
                FROM credit_history 
                WHERE username = ?
                ORDER BY date DESC
                LIMIT ?
            ''', (username, limit))
            
            records = cursor.fetchall()
            
            return [
                {
                    'credit_score': record['credit_score'],
                    'risk_level': record['risk_level'],
                    'eligible_amount': record['eligible_amount'],
                    'date': record['date']
                }
                for record in records
            ]
            
    except Exception as e:
        print(f"Error fetching credit score history: {e}")
        return []

def get_credit_score_trend_data(username, days=30):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT credit_score, date
                FROM credit_history 
                WHERE username = ?
                AND date >= date('now', '-{} days')
                ORDER BY date ASC
            '''.format(days), (username,))
            
            records = cursor.fetchall()
            
            dates = []
            scores = []
            
            for record in records:
                date_obj = datetime.fromisoformat(record['date'])
                formatted_date = date_obj.strftime('%m/%d')
                dates.append(formatted_date)
                scores.append(record['credit_score'])
            
            return {
                'dates': dates,
                'scores': scores,
                'count': len(records)
            }
            
    except Exception as e:
        print(f"Error fetching trend data: {e}")
        return {'dates': [], 'scores': [], 'count': 0}

def get_score_statistics(username):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    MIN(credit_score) as min_score,
                    MAX(credit_score) as max_score,
                    AVG(credit_score) as avg_score,
                    COUNT(*) as total_records
                FROM credit_history 
                WHERE username = ?
            ''', (username,))
            
            result = cursor.fetchone()
            
            if result and result['total_records'] > 0:
                return {
                    'min_score': result['min_score'],
                    'max_score': result['max_score'],
                    'avg_score': round(result['avg_score'], 1),
                    'total_records': result['total_records']
                }
            else:
                return {
                    'min_score': 0,
                    'max_score': 0,
                    'avg_score': 0,
                    'total_records': 0
                }
                
    except Exception as e:
        print(f"Error fetching score statistics: {e}")
        return {'min_score': 0, 'max_score': 0, 'avg_score': 0, 'total_records': 0}

def save_user_financials(username, age, income, existing_loans, total_emi, credit_utilization, defaults):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM user_financials WHERE username = ?', (username,))
            existing_record = cursor.fetchone()
            
            updated_at = datetime.now().isoformat()
            
            if existing_record:
                cursor.execute('''
                    UPDATE user_financials 
                    SET age = ?, income = ?, existing_loans = ?, total_emi = ?, 
                        credit_utilization = ?, defaults = ?, updated_at = ?
                    WHERE username = ?
                ''', (age, income, existing_loans, total_emi, credit_utilization, defaults, updated_at, username))
            else:
                cursor.execute('''
                    INSERT INTO user_financials (username, age, income, existing_loans, total_emi, credit_utilization, defaults, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, age, income, existing_loans, total_emi, credit_utilization, defaults, updated_at))
            
            conn.commit()
            return True, "Financial data saved successfully"
            
    except Exception as e:
        return False, f"Failed to save financial data: {str(e)}"

def get_user_financials(username):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT age, income, existing_loans, total_emi, credit_utilization, defaults, updated_at
                FROM user_financials 
                WHERE username = ?
            ''', (username,))
            
            financial_data = cursor.fetchone()
            
            if financial_data:
                return {
                    'age': financial_data['age'],
                    'income': financial_data['income'],
                    'existing_loans': financial_data['existing_loans'],
                    'total_emi': financial_data['total_emi'],
                    'credit_utilization': financial_data['credit_utilization'],
                    'defaults': financial_data['defaults'],
                    'updated_at': financial_data['updated_at']
                }
            return None
            
    except Exception as e:
        print(f"Error fetching financial data: {e}")
        return None

def has_financial_data(username):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM user_financials WHERE username = ?', (username,))
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking financial data: {e}")
        return False

def update_user_profile(username, email=None):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if email is not None:
                cursor.execute('UPDATE users SET email = ? WHERE username = ?', (email, username))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    return True, "Profile updated successfully"
                else:
                    return False, "User not found"
            else:
                return False, "No fields to update"
                
    except sqlite3.IntegrityError as e:
        return False, f"Update failed: {str(e)}"
    except Exception as e:
        return False, f"Database error: {str(e)}"

def schedule_review(username, review_date, note=None):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            created_at = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO review_schedule (username, review_date, note, created_at)
                VALUES (?, ?, ?, ?)
            ''', (username, review_date, note, created_at))
            
            conn.commit()
            return True, "Review scheduled successfully"
            
    except Exception as e:
        return False, f"Failed to schedule review: {str(e)}"

def get_scheduled_reviews(username, limit=10):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, review_date, note, created_at
                FROM review_schedule 
                WHERE username = ?
                ORDER BY review_date ASC
                LIMIT ?
            ''', (username, limit))
            
            records = cursor.fetchall()
            
            return [
                {
                    'id': record['id'],
                    'review_date': record['review_date'],
                    'note': record['note'],
                    'created_at': record['created_at']
                }
                for record in records
            ]
            
    except Exception as e:
        print(f"Error fetching scheduled reviews: {e}")
        return []

def get_upcoming_reviews(username, days_ahead=30):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, review_date, note, created_at
                FROM review_schedule 
                WHERE username = ?
                AND date(review_date) >= date('now')
                AND date(review_date) <= date('now', '+{} days')
                ORDER BY review_date ASC
            '''.format(days_ahead), (username,))
            
            records = cursor.fetchall()
            
            return [
                {
                    'id': record['id'],
                    'review_date': record['review_date'],
                    'note': record['note'],
                    'created_at': record['created_at']
                }
                for record in records
            ]
            
    except Exception as e:
        print(f"Error fetching upcoming reviews: {e}")
        return []

def delete_scheduled_review(username, review_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM review_schedule 
                WHERE id = ? AND username = ?
            ''', (review_id, username))
            
            if cursor.rowcount > 0:
                conn.commit()
                return True, "Review deleted successfully"
            else:
                return False, "Review not found or access denied"
                
    except Exception as e:
        return False, f"Failed to delete review: {str(e)}"