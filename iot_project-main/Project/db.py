import sqlite3

class DBManager():
    def __init__(self, db_file):
        self.db_file = db_file

    def _establish_connection_and_get_cursor(self):
        try:
            conn = sqlite3.connect(self.db_file)
            return conn, conn.cursor()
        except Exception as e:
            print(f"Error in db: {e}")


    def _close_connection(self, conn, cursor):
        try:
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error in db: {e}")

    def check_user_exists(self, rfid):
        conn, cursor = self._establish_connection_and_get_cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM User WHERE RFID = ?", (rfid,))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"Error in db: {e}")
        finally:
            self._close_connection(conn, cursor)
    
    def get_user_thresholds(self, rfid):
        conn, cursor = self._establish_connection_and_get_cursor()
        try:
            cursor.execute("SELECT * FROM User WHERE RFID = ?", (rfid,))
            thresholds = cursor.fetchone()
            return thresholds
        except Exception as e:
            print(f"Error in db: {e}")
        finally:
            self._close_connection(conn, cursor)
