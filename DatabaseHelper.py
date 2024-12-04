import sqlite3

class DBHelper:
    def __init__(self, db_file):
        self.db_file = db_file
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    rfid_id TEXT PRIMARY KEY,
                    temperature_threshold REAL,
                    light_intensity_threshold REAL
                )
            """)
            conn.commit()

    def insert(self, rfid_id, temperature_threshold, light_intensity_threshold):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (rfid_id, temperature_threshold, light_intensity_threshold)
                    VALUES (?, ?, ?)
                """, (rfid_id, temperature_threshold, light_intensity_threshold))
                conn.commit()
        except sqlite3.IntegrityError:
            print(f"Error: RFID ID '{rfid_id}' already exists.")

    def fetch_by_rfid(self, rfid_id):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users WHERE rfid_id = ?
            """, (rfid_id,))
            row = cursor.fetchone()
            return row

    def update(self, rfid_id, temperature_threshold=None, light_intensity_threshold=None):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            if temperature_threshold is not None:
                cursor.execute("""
                    UPDATE users
                    SET temperature_threshold = ?
                    WHERE rfid_id = ?
                """, (temperature_threshold, rfid_id))
            if light_intensity_threshold is not None:
                cursor.execute("""
                    UPDATE users
                    SET light_intensity_threshold = ?
                    WHERE rfid_id = ?
                """, (light_intensity_threshold, rfid_id))
            conn.commit()


db = DBHelper("users.db")  # Specify the correct database file name
id1 = 'A3:D6:D4:24'
id2 = '03:97:CB:F7'
# # Fetch all records
# all_users = db.fetch_by_rfid(id)

# # Print the results
# if all_users:
#     print("User Records:")
#     for user in all_users:
#         print(user)
# else:
#     print("No records for " + id + " found in the users table.")


#db.insert(id1, 22, 800)
#db.insert(id2, 26, 1000)

user1 = db.fetch_by_rfid(id1)
user2 = db.fetch_by_rfid(id2)

if user1:
    print("User Records:")
    for user in user1:
        print(user)
else:
    print("No records found in the users table.")


if user2:
    print("User Records:")
    for user in user2:
        print(user)
else:
    print("No records for found in the users table.")

        