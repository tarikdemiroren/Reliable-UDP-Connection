import sys
import os
import socket
import struct
import threading
import time

class Sender:
    def __init__(self, file_path, receiver_port, window_size, retransmission_timeout):
        self.file_path = file_path
        self.receiver_port = receiver_port
        self.window_size = window_size
        self.retransmission_timeout = retransmission_timeout / 1000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.base = 1
        self.seq_num = 1
        self.segments = []
        self.read_file()

    def read_file(self):
        with open(self.file_path, 'rb') as file:
            while True:
                data = file.read(1022) 
                if not data:
                    break
                self.segments.append(data)
        

    def start(self):
        self.last_ack_time = time.time()
        main_thread = threading.Thread(target=self.main_loop)
        send_thread = threading.Thread(target=self.send_loop)
        ack_receiver_thread = threading.Thread(target=self.ack_receiver_loop)
        
        main_thread.daemon = True
        send_thread.daemon = True
        ack_receiver_thread.daemon = True

        main_thread.start()
        send_thread.start()
        ack_receiver_thread.start()
        
        try:
            main_thread.join()
        except KeyboardInterrupt:
            print("\nExiting...")

    def send_segment(self, segment, seq_num):
        header = struct.pack('!H', seq_num)
        payload = header + segment
        self.sock.sendto(payload, ('localhost', self.receiver_port))
        # print("Sent: ", seq_num)

    def send_loop(self):
        while True:
            with threading.RLock():
                while self.seq_num <= self.base + (self.window_size - 1) and self.seq_num <= len(self.segments):
                    segment = self.segments[self.seq_num - 1]
                    self.send_segment(segment, self.seq_num)
                    self.seq_num += 1
                if self.seq_num - 1 == len(self.segments):
                    self.send_segment(b'', 0)
                    print("File transfer completed.")
                    break            

    def ack_receiver_loop(self):
        while True:
            ack, _ = self.sock.recvfrom(2)
            ack_seq = struct.unpack('!H', ack[:2])[0]
            # if (ack):
            #     print( "ACK received: ", ack_seq)
            with threading.Lock():
                if ack_seq >= self.base:
                    self.base = ack_seq
                    self.last_ack_time = time.time() 

    def main_loop(self):
        while True:
            with threading.RLock():
                if self.base == len(self.segments):
                    break 
            time_since_last_ack = time.time() - self.last_ack_time
            if time_since_last_ack > self.retransmission_timeout:
                with threading.Lock():
                    self.seq_num = self.base

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 Sender.py <file_path> <receiver_port> <window_size_N> <retransmission_timeout>")
        sys.exit(1)

    file_path = sys.argv[1]
    receiver_port = int(sys.argv[2])
    window_size = int(sys.argv[3])
    retransmission_timeout = int(sys.argv[4])

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    print("Press ctrl + C to exit.")

    sender = Sender(file_path, receiver_port, window_size, retransmission_timeout)
    sender.start()
