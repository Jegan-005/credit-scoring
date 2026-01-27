#!/usr/bin/env python3
"""
Simple script to view CredX AI database contents
"""

import sqlite3
import pandas as pd

def view_database():
    """View all tables and data in the database"""
    
    print("🗄️  CredX AI Database Viewer")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect('credx.db')
        
        # Get all table names
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"   • {table[0]}")
        
        print("\n" + "=" * 50)
        
        # View each table
        for table_name in [t[0] for t in tables]:
            print(f"\n📋 Table: {table_name}")
            print("-" * 30)
            
            try:
                # Get table data
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                
                if len(df) == 0:
                    print("   (No data)")
                else:
                    print(f"   Rows: {len(df)}")
                    print(f"   Columns: {list(df.columns)}")
                    print("\n   Sample data:")
                    print(df.head().to_string(index=False))
                    
            except Exception as e:
                print(f"   Error reading table: {e}")
        
        # Database stats
        print("\n" + "=" * 50)
        print("📈 Database Statistics:")
        
        # User count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   👥 Total Users: {user_count}")
        
        # Financial profiles
        cursor.execute("SELECT COUNT(*) FROM user_financials")
        financial_count = cursor.fetchone()[0]
        print(f"   💰 Financial Profiles: {financial_count}")
        
        # Credit history records
        cursor.execute("SELECT COUNT(*) FROM credit_history")
        history_count = cursor.fetchone()[0]
        print(f"   📊 Credit History Records: {history_count}")
        
        # Scheduled reviews
        cursor.execute("SELECT COUNT(*) FROM review_schedule")
        review_count = cursor.fetchone()[0]
        print(f"   📅 Scheduled Reviews: {review_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

if __name__ == "__main__":
    view_database()