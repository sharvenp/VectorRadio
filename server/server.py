import os
import socket
import threading
import time
import random
import math
import json
from pydub import AudioSegment
import eyed3


# Constants
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 3000
BROADCAST_PORT = 6000
BUFF_SIZE = 65536
CHUNK = 10*1024

track_metadata = {}

def create_message(message, code, extra_info={}):
    data = {'message': message, 'code': code}
    data.update(extra_info)
    return data

def start_info_server():
    server_socket = socket.socket()
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print(f'[Server listening at {(SERVER_IP, SERVER_PORT)}]')

    while True:
        client_socket,addr = server_socket.accept()
        print(f'[Connection from {addr}]')
        data = json.dumps(create_message("track info", 200, extra_info=track_metadata))
        client_socket.sendall(bytes(data,encoding="utf-8"))
        client_socket.close()

def start_streaming_server():

    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    print(f'[Broadcast server started]')

    while True:

        print("[Loading tracks...]")
        tracks = os.listdir('./../music')
        print(f"[Loaded {len(tracks)} track(s)]")

        # shuffle all tracks
        random.shuffle(tracks)
        
        for track in tracks: 

            # load track
            sound = AudioSegment.from_mp3(f'./../music/{track}') + AudioSegment.silent(duration=5000) # add 5 seconds of trailing silence
            raw_data = sound.raw_data
            sample_rate = sound.frame_rate
            channels = sound.channels
            frame_count = sound.frame_count()
            frame_width = sound.frame_width
            sample_width = sound.sample_width

            # load metadata
            audio_metadata = eyed3.load(f'./../music/{track}')

            # update the track metadata
            global track_metadata
            track_metadata = {
                "title": audio_metadata.tag.title,
                "artist": audio_metadata.tag.artist,
                "album": audio_metadata.tag.album,
                "publisher": audio_metadata.tag.publisher,
                "genre": None if audio_metadata.tag.genre is None else audio_metadata.tag.genre.name,
                "sample_rate": sample_rate,
                "channels": channels,
                "frame_count": frame_count,
                "frame_width": frame_width,
                "sample_width": sample_width,
                "data_size": math.ceil(frame_count/frame_width)
            }

            print(f'✨ [Playing {audio_metadata.tag.artist}-{audio_metadata.tag.title}] ✨')

            # send song info as first chunk
            print(f"[Sending metadata chunk]")
            data = bytes(json.dumps(create_message("track info", 200, extra_info=track_metadata)), encoding="utf-8")
            broadcast_socket.sendto(data, ("255.255.255.255", 6000))

            # create chunks
            chunks = [raw_data[i:i+CHUNK] for i in range(0, len(raw_data), CHUNK)]
            for i in range(len(chunks)):
                # broadcast chunk data
                print(f"[Sending chunk {i+1} (size: {len(chunks[i])} b)]")
                broadcast_socket.sendto(chunks[i], ("255.255.255.255", 6000))
                time.sleep(0.01) # broadcast throttle
                
def run():
    print("********** Vector Music Server **********")
    print("[Starting server...]")
    t1 = threading.Thread(target=start_info_server)
    t1.start()
    t2 = threading.Thread(target=start_streaming_server)
    t2.start()

    t2.join()

if __name__ == '__main__':
    run()