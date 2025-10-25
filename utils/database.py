import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import json

class MedicalDB:
    def __init__(self, db_path="data/medical_assessment.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Patients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                email TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Assessments table - Enhanced for hearing tests
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                assessment_type TEXT NOT NULL,
                results TEXT,
                risk_level TEXT,
                recommendations TEXT,
                critical_flag BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database initialized at: {self.db_path}")
    
    def add_patient(self, name, age, gender, email="", phone=""):
        """Add a new patient to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO patients (name, age, gender, email, phone)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, age, gender, email, phone))
        
        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()
        print(f"Patient added with ID: {patient_id}")
        return patient_id
    
    def add_assessment(self, patient_id, assessment_type, results, risk_level, recommendations, critical_flag=False):
        """Add a new assessment to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert results to JSON string if it's a dict
            if isinstance(results, dict):
                results_str = json.dumps(results)
            else:
                results_str = str(results)
            
            cursor.execute('''
                INSERT INTO assessments (patient_id, assessment_type, results, risk_level, recommendations, critical_flag)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (patient_id, assessment_type, results_str, risk_level, recommendations, critical_flag))
            
            assessment_id = cursor.lastrowid
            conn.commit()
            conn.close()
            print(f"Assessment added with ID: {assessment_id} for patient: {patient_id}")
            return assessment_id
            
        except Exception as e:
            print(f"Error adding assessment: {e}")
            if conn:
                conn.close()
            return None
    
    def get_patient_assessments(self, patient_id):
        """Get all assessments for a specific patient"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = '''
                SELECT id, assessment_type, results, risk_level, recommendations, 
                       critical_flag, created_at
                FROM assessments 
                WHERE patient_id = ?
                ORDER BY created_at DESC
            '''
            df = pd.read_sql_query(query, conn, params=[patient_id])
            conn.close()
            return df
        except Exception as e:
            print(f"Error getting patient assessments: {e}")
            return pd.DataFrame()
    
    def get_all_patients(self):
        """Get all patients"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM patients ORDER BY created_at DESC", conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error getting patients: {e}")
            return pd.DataFrame()
    
    def get_all_assessments(self):
        """Get all assessments with patient info"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = '''
                SELECT a.*, p.name, p.age, p.gender 
                FROM assessments a 
                JOIN patients p ON a.patient_id = p.id 
                ORDER BY a.created_at DESC
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error getting all assessments: {e}")
            return pd.DataFrame()
    
    def get_critical_patients(self):
        """Get patients with critical assessments"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = '''
                SELECT a.*, p.name, p.age, p.gender, p.phone, p.email
                FROM assessments a 
                JOIN patients p ON a.patient_id = p.id 
                WHERE a.critical_flag = TRUE
                ORDER BY a.created_at DESC
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error getting critical patients: {e}")
            return pd.DataFrame()
    
    def get_statistics(self):
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            stats = {}
            
            # Total patients
            stats['total_patients'] = pd.read_sql_query("SELECT COUNT(*) as count FROM patients", conn).iloc[0]['count']
            
            # Total assessments
            stats['total_assessments'] = pd.read_sql_query("SELECT COUNT(*) as count FROM assessments", conn).iloc[0]['count']
            
            # Critical cases
            stats['critical_cases'] = pd.read_sql_query("SELECT COUNT(*) as count FROM assessments WHERE critical_flag = TRUE", conn).iloc[0]['count']
            
            # Assessments by type
            stats['by_type'] = pd.read_sql_query("SELECT assessment_type, COUNT(*) as count FROM assessments GROUP BY assessment_type", conn)
            
            # Daily assessments (last 7 days)
            stats['daily_assessments'] = pd.read_sql_query('''
                SELECT DATE(created_at) as date, COUNT(*) as count 
                FROM assessments 
                WHERE created_at >= date('now', '-7 days')
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            ''', conn)
            
            conn.close()
            return stats
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def test_connection(self):
        """Test database connection and show structure"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Show tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Tables in database: {[table[0] for table in tables]}")
            
            # Show assessments table structure
            cursor.execute("PRAGMA table_info(assessments)")
            columns = cursor.fetchall()
            print(f"Assessments table columns: {[(col[1], col[2]) for col in columns]}")
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM assessments")
            assessment_count = cursor.fetchone()[0]
            print(f"Total assessments in database: {assessment_count}")
            
            conn.close()
            return True
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False
