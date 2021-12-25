import socket
import threading
import pyaudio
import time
import queue
import json

# Constants
SERVER_ADDR = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 3000
BROADCAST_PORT = 6000
BUFF_SIZE = 65536
CHUNK = 10*1024

def buffer():
    time.sleep(3)

def listen_stream():

    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast_socket.bind(('0.0.0.0', BROADCAST_PORT))

    # connect to server
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socket_address = (SERVER_ADDR,SERVER_PORT)
    client_socket.connect(socket_address) 
    info,_ = client_socket.recvfrom(BUFF_SIZE)
    info = json.loads(info)
    print(f'[Playing track: {info}]')

    if not info:
        return

    def get_data():
        while True:
            frame,_= broadcast_socket.recvfrom(BUFF_SIZE)
            q.put(frame)
            print(f'[Queue size {q.qsize()} frames]')

    q = queue.Queue()
    t1 = threading.Thread(target=get_data)
    t1.start()

    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(info['sample_width']),
                    channels=info['channels'],
                    rate=info['sample_rate'],
                    output=True,
                    frames_per_buffer=1)
    while True:
        frame = q.get()
        if (q.qsize() <= 1):
            print("[Buffering...]")
            buffer() # wait for more data
        stream.write(frame)

def run():
    print("********** Vector Music Prototype Client **********")
    t1 = threading.Thread(target=listen_stream, args=())
    t1.start()

if __name__ == '__main__':
    run()

