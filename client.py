import socket
import time

HOST = "127.0.0.1"
PORT = 65432
WAIT_SECONDS = 60
FILE_PATH = "./status.txt"

def read_file():
    try: 
        with open(FILE_PATH, 'r') as file:
            lines = file.read().strip().split('\n')
            if len (lines) !=3:
                raise ValueError("Invalid data format in status.txt")
            station_id = lines[0].strip()
            alarm1 = lines[1].strip()
            alarm2 = lines[2].strip()
            if not station_id.isdigit(): 
                print("Invalid station id")
                return None
            if alarm1 not in ['0', '1'] or alarm2 not in ['0', '1']:
                print("Invalid alarm status")
                return None
            return (station_id, alarm1, alarm2)
    except FileNotFoundError:
        print("File not found")
        return None
    
            
def reach_server(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print (f' Connected to server {HOST} on port {PORT}')
            s.sendall(data.encode('utf-8'))
            print ("Sent data to server")
    except ConnectionRefusedError:
        print("Server is not running")
    except Exception as e:
        print(f"Error reaching server: {e}")
        

def main():
    while True:
        status_data = read_file()
        if status_data is not None:
            station_id, alarm1, alarm2 = status_data
            data = f"{station_id} {alarm1} {alarm2}"
            reach_server(data)
        time.sleep(WAIT_SECONDS)
    

if __name__ == "__main__":
    main()