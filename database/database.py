"""
Database Module for Livestock Health Monitoring Assistant
=========================================================
This module handles all database operations using SQLite.

WHAT IS SQLITE?
SQLite is a simple database that stores data in a single file.
Unlike big databases (MySQL, PostgreSQL), SQLite doesn't need
a separate server - it works directly from a file.

WHY WE USE IT:
- It's built into Python (no extra installation needed)
- Perfect for small to medium projects
- Data persists even after the application restarts
- Easy to understand for beginners

HOW IT WORKS IN THIS PROJECT:
1. When the app starts, it creates/connects to livestock.db
2. It creates tables if they don't exist
3. Agents use this module to save and retrieve animal data
4. This is the "memory" of our AI agents
"""

import sqlite3
import os
from datetime import datetime


class LivestockDatabase:
    """
    Database manager for livestock health records.
    
    This class handles creating, reading, updating, and deleting
    animal health records in the SQLite database.
    
    AGENT MEMORY CONCEPT:
    This database serves as the "long-term memory" for our AI agents.
    When an agent saves health data, it can be retrieved later by
    any other agent. This is how agents "remember" previous interactions.
    """
    
    def __init__(self, db_path=None):
        """
        Initialize the database connection.
        
        Args:
            db_path (str): Path to the SQLite database file.
                          If None, uses the default path.
        """
        if db_path is None:
            # Default path: database/livestock.db in the project folder
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "database", "livestock.db"
            )
        
        self.db_path = db_path
        
        # Make sure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Create the tables when the database is first initialized
        self._create_tables()
    
    def _get_connection(self):
        """
        Create a new database connection.
        
        WHY WE CREATE NEW CONNECTIONS:
        SQLite works best when we create a connection, do our work,
        and then close it. This prevents issues with multiple parts
        of the program trying to use the same connection.
        
        Returns:
            sqlite3.Connection: A database connection
        """
        conn = sqlite3.connect(self.db_path)
        # This makes results come back as dictionaries instead of tuples
        # So we can access data like row["animal_type"] instead of row[1]
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self):
        """
        Create the database tables if they don't already exist.
        
        We have two main tables:
        1. animals - Stores basic animal information
        2. health_records - Stores health check records over time
        
        The relationship: One animal can have MANY health records.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # -----------------------------------------------------------
            # Table 1: ANIMALS
            # Stores basic information about each animal
            # -----------------------------------------------------------
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS animals (
                    animal_id TEXT PRIMARY KEY,
                    animal_type TEXT NOT NULL,
                    breed TEXT DEFAULT 'Unknown',
                    age TEXT DEFAULT 'Unknown',
                    gender TEXT DEFAULT 'Unknown',
                    owner_name TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # -----------------------------------------------------------
            # Table 2: HEALTH_RECORDS
            # Stores health check-up data for animals over time
            # Each time we check an animal, a new record is added
            # -----------------------------------------------------------
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_records (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id TEXT NOT NULL,
                    animal_type TEXT NOT NULL,
                    breed TEXT DEFAULT 'Unknown',
                    age TEXT DEFAULT 'Unknown',
                    gender TEXT DEFAULT 'Unknown',
                    weight REAL DEFAULT 0,
                    temperature REAL DEFAULT 0,
                    symptoms TEXT DEFAULT '',
                    food_intake TEXT DEFAULT 'Normal',
                    water_intake TEXT DEFAULT 'Normal',
                    activity_level TEXT DEFAULT 'Normal',
                    additional_notes TEXT DEFAULT '',
                    health_status TEXT DEFAULT 'Unknown',
                    health_analysis TEXT DEFAULT '',
                    nutrition_advice TEXT DEFAULT '',
                    monitoring_notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"❌ Database error while creating tables: {e}")
        finally:
            conn.close()
    
    # ===================================================================
    # ANIMAL OPERATIONS
    # ===================================================================
    
    def add_animal(self, animal_id, animal_type, breed="Unknown", 
                   age="Unknown", gender="Unknown"):
        """
        Add a new animal to the database.
        
        Args:
            animal_id (str): Unique identifier for the animal
            animal_type (str): Type of animal (Cow, Goat, etc.)
            breed (str): Breed of the animal
            age (str): Age of the animal
            gender (str): Gender of the animal
        
        Returns:
            tuple: (success: bool, message: str)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO animals 
                (animal_id, animal_type, breed, age, gender, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (animal_id, animal_type, breed, age, gender, 
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            return True, f"✅ Animal {animal_id} added/updated successfully."
        except sqlite3.Error as e:
            return False, f"❌ Error adding animal: {e}"
        finally:
            conn.close()
    
    def get_animal(self, animal_id):
        """
        Get basic information about a specific animal.
        
        Args:
            animal_id (str): The animal's unique ID
        
        Returns:
            dict or None: Animal information, or None if not found
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM animals WHERE animal_id = ?', 
                         (animal_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_animals(self):
        """
        Get a list of all animals in the database.
        
        Returns:
            list: List of animal dictionaries
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM animals ORDER BY updated_at DESC')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            conn.close()
    
    # ===================================================================
    # HEALTH RECORD OPERATIONS
    # ===================================================================
    
    def save_health_record(self, record_data):
        """
        Save a new health check-up record.
        
        THIS IS A KEY TOOL USED BY AI AGENTS:
        When the Health Analysis Agent finishes analyzing an animal,
        it calls this function to save the results to the database.
        
        Args:
            record_data (dict): Dictionary containing health record fields
        
        Returns:
            tuple: (success: bool, message: str, record_id: int or None)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Also add/update the animal in the animals table
            self.add_animal(
                animal_id=record_data.get("animal_id", "UNKNOWN"),
                animal_type=record_data.get("animal_type", "Unknown"),
                breed=record_data.get("breed", "Unknown"),
                age=record_data.get("age", "Unknown"),
                gender=record_data.get("gender", "Unknown")
            )
            
            cursor.execute('''
                INSERT INTO health_records 
                (animal_id, animal_type, breed, age, gender, weight,
                 temperature, symptoms, food_intake, water_intake,
                 activity_level, additional_notes, health_status,
                 health_analysis, nutrition_advice, monitoring_notes,
                 created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record_data.get("animal_id", "UNKNOWN"),
                record_data.get("animal_type", "Unknown"),
                record_data.get("breed", "Unknown"),
                record_data.get("age", "Unknown"),
                record_data.get("gender", "Unknown"),
                float(record_data.get("weight", 0)),
                float(record_data.get("temperature", 0)),
                record_data.get("symptoms", ""),
                record_data.get("food_intake", "Normal"),
                record_data.get("water_intake", "Normal"),
                record_data.get("activity_level", "Normal"),
                record_data.get("additional_notes", ""),
                record_data.get("health_status", "Unknown"),
                record_data.get("health_analysis", ""),
                record_data.get("nutrition_advice", ""),
                record_data.get("monitoring_notes", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            record_id = cursor.lastrowid
            return True, f"✅ Health record #{record_id} saved successfully.", record_id
        except sqlite3.Error as e:
            return False, f"❌ Error saving health record: {e}", None
        except (ValueError, TypeError) as e:
            return False, f"❌ Invalid data format: {e}", None
        finally:
            conn.close()
    
    def get_animal_history(self, animal_id, limit=20):
        """
        Get the health history for a specific animal.
        
        MONITORING AGENT USES THIS:
        The monitoring agent retrieves past records to compare
        with current health data and identify trends or changes.
        
        Args:
            animal_id (str): The animal's unique ID
            limit (int): Maximum number of records to return
        
        Returns:
            list: List of health record dictionaries, newest first
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM health_records 
                WHERE animal_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (animal_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            conn.close()
    
    def get_latest_record(self, animal_id):
        """
        Get the most recent health record for an animal.
        
        Args:
            animal_id (str): The animal's unique ID
        
        Returns:
            dict or None: Latest health record, or None if not found
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM health_records 
                WHERE animal_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (animal_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_records(self, limit=50):
        """
        Get all health records (most recent first).
        
        Args:
            limit (int): Maximum number of records to return
        
        Returns:
            list: List of health record dictionaries
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM health_records 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            conn.close()
    
    def get_dashboard_stats(self):
        """
        Get statistics for the dashboard display.
        
        Returns:
            dict: Dashboard statistics including counts and status breakdowns
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Total animals
            cursor.execute('SELECT COUNT(*) as count FROM animals')
            total_animals = cursor.fetchone()["count"]
            
            # Total health records
            cursor.execute('SELECT COUNT(*) as count FROM health_records')
            total_records = cursor.fetchone()["count"]
            
            # Get latest status for each animal
            cursor.execute('''
                SELECT health_status, COUNT(*) as count 
                FROM (
                    SELECT animal_id, health_status,
                           ROW_NUMBER() OVER (PARTITION BY animal_id 
                                              ORDER BY created_at DESC) as rn
                    FROM health_records
                )
                WHERE rn = 1
                GROUP BY health_status
            ''')
            
            status_counts = {"Healthy": 0, "Needs Monitoring": 0, 
                           "Warning": 0, "Critical": 0, "Unknown": 0}
            for row in cursor.fetchall():
                status = row["health_status"]
                count = row["count"]
                if status.lower() in ("healthy", "normal"):
                    status_counts["Healthy"] += count
                elif "monitor" in status.lower():
                    status_counts["Needs Monitoring"] += count
                elif status.lower() == "warning":
                    status_counts["Warning"] += count
                elif status.lower() == "critical":
                    status_counts["Critical"] += count
                else:
                    status_counts["Unknown"] += count
            
            # Recent records
            cursor.execute('''
                SELECT animal_id, animal_type, health_status, created_at 
                FROM health_records 
                ORDER BY created_at DESC 
                LIMIT 10
            ''')
            recent_records = [dict(row) for row in cursor.fetchall()]
            
            # Get all unique animal IDs
            cursor.execute('SELECT animal_id FROM animals ORDER BY animal_id')
            animal_ids = [row["animal_id"] for row in cursor.fetchall()]
            
            return {
                "total_animals": total_animals,
                "total_records": total_records,
                "status_counts": status_counts,
                "recent_records": recent_records,
                "animal_ids": animal_ids,
            }
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return {
                "total_animals": 0,
                "total_records": 0,
                "status_counts": {"Healthy": 0, "Needs Monitoring": 0, 
                                "Warning": 0, "Critical": 0, "Unknown": 0},
                "recent_records": [],
                "animal_ids": [],
            }
        finally:
            conn.close()
    
    def search_animals(self, search_term):
        """
        Search for animals by ID or type.
        
        Args:
            search_term (str): Search text
        
        Returns:
            list: Matching animal records
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            search_pattern = f"%{search_term}%"
            cursor.execute('''
                SELECT * FROM animals 
                WHERE animal_id LIKE ? OR animal_type LIKE ? OR breed LIKE ?
                ORDER BY updated_at DESC
            ''', (search_pattern, search_pattern, search_pattern))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return []
        finally:
            conn.close()
    
    def seed_sample_data(self, csv_path=None):
        """
        Seed database with sample records if empty.
        """
        if csv_path is None:
            csv_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data", "sample_livestock.csv"
            )
        
        if not os.path.exists(csv_path):
            return False, "CSV file not found"
            
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM animals")
            if cursor.fetchone()["count"] > 0:
                conn.close()
                return True, "Database already contains records."
                
            import csv
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Insert animal
                    cursor.execute('''
                        INSERT OR REPLACE INTO animals 
                        (animal_id, animal_type, breed, age, gender, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (row['animal_id'], row['animal_type'], row['breed'], 
                          row['age'], row['gender'], row['created_at']))
                          
                    # Insert health record
                    cursor.execute('''
                        INSERT INTO health_records 
                        (animal_id, animal_type, breed, age, gender, weight,
                         temperature, symptoms, food_intake, water_intake,
                         activity_level, additional_notes, health_status,
                         health_analysis, nutrition_advice, monitoring_notes,
                         created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['animal_id'],
                        row['animal_type'],
                        row['breed'],
                        row['age'],
                        row['gender'],
                        float(row.get('weight', 0)),
                        float(row.get('temperature', 0)),
                        row.get('symptoms', ''),
                        row.get('food_intake', 'Normal'),
                        row.get('water_intake', 'Normal'),
                        row.get('activity_level', 'Normal'),
                        row.get('additional_notes', ''),
                        row.get('health_status', 'Healthy'),
                        f"Automated health record imported for {row['animal_id']}.",
                        "Standard balanced dietary regimen.",
                        "Initial baseline parameters recorded.",
                        row['created_at']
                    ))
            conn.commit()
            return True, "Sample data seeded successfully."
        except Exception as e:
            return False, f"Failed seeding data: {e}"
        finally:
            conn.close()
