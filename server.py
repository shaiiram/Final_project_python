import socket
import datetime
import threading
import sqlite3

def init (database):
    """ Initializes the database
    (data.sqlite) 
    and creates the 
    station_status table 
    if it does not exist. """
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    create_table = """CREATE TABLE IF NOT EXISTS station_status (
    station_id INT,
    last_date TEXT,
    alarm1 INT,
    alarm2 INT,
    PRIMARY KEY(station_id) );"""
    cursor.execute(create_table)
    conn.commit()
    conn.close()

def handle_client(conn, addr):
    print('New connection from', addr)
    try:
        while True:
            data = conn.recv(1024)
            if len(data) > 1024:  
                print(f"[ERROR] Data too large from {addr}: {len(data)} bytes")
                continue
            if not data:
                break
            decoded_data = data.decode('utf-8').strip()
            print('Received:', decoded_data)
            if decoded_data:
                 # Split the incoming string into three parts: ID, Alarm1, Alarm2
                parts = decoded_data.split()
                if len(parts) == 3:
                    station_id, alarm1, alarm2 = parts
                    if not station_id.isdigit() or alarm1 not in ['0', '1'] or alarm2 not in ['0', '1']:
                        print(f"[ERROR] Invalid data received from {addr}: {decoded_data}")
                        continue 
                    # Get current timestamp in "YYYY-MM-DD HH:mm" format
                    last_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                    # Update or insert the record in the database
                    update_database(station_id, alarm1, alarm2, last_date)
                    print(f"[INFO] Updated station {station_id} at {last_date} \n with alarm 1 status: {alarm1}, \n alarm 2 status: {alarm2}")
                else:
                    print("[ERROR] Received invalid data format:", decoded_data)
    except Exception as e:
        print(f"[EXCEPTION] Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"[INFO] Connection closed for {addr}")
        
def update_database(station_id, alarm1, alarm2, last_date):
    conn = sqlite3.connect('data.sqlite')
    cursor = conn.cursor()
    query = """INSERT OR REPLACE INTO station_status 
    (station_id, last_date, alarm1, alarm2) 
    VALUES (?, ?, ?, ?);"""
    cursor.execute(query, (station_id, last_date, alarm1, alarm2))
    conn.commit()
    conn.close()
    
def main():
    init('data.sqlite')
    host = "127.0.0.1"
    port = 65432
    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        print(f"[INFO] Server started on {host}:{port}... \n Waiting for connections...")
        
        while True:
            conn, addr = s.accept()
            # Spin a new thread for each client
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
if __name__ == "__main__":
    main()

    