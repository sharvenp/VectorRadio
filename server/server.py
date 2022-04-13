
# system
import os
import threading
from datetime import datetime
import time
import random
import base64

# audio & mp3
from pydub import AudioSegment
from pydub.utils import make_chunks
import eyed3

# sockets
import json
from websocket_server import WebsocketServer
from dotenv import load_dotenv

# constants
load_dotenv()
SONG_DIR = os.getenv('SONG_DIR')
SERVER_HOST = os.getenv('SERVER_HOST')
# SERVER_HOST = 'localhost'  # use this for local hosting
SERVER_PORT = int(os.getenv('SERVER_PORT'))
CHUNK_SIZE_MS = 1000

server = WebsocketServer(host=SERVER_HOST, port=SERVER_PORT)
track_metadata = {}


def log(message):
    print(f"[{datetime.now()}] {message}")


def create_message(message, code, extra_info={}):
    data = {'type': message, 'code': code}
    data.update(extra_info)
    return data


def run_radio_server():

    log(f'Radio server started')

    while True:

        log("Loading tracks...")
        tracks = os.listdir(SONG_DIR)
        log(f"Loaded {len(tracks)} track(s)")

        # shuffle all tracks
        random.shuffle(tracks)

        for track in tracks:

            # load track
            # add 3 seconds of trailing silence
            sound = AudioSegment.from_mp3(
                f'{SONG_DIR}/{track}') + AudioSegment.silent(duration=3000)
            channels = sound.channels
            sample_rate = sound.frame_rate
            frame_count = sound.frame_count()
            frame_width = sound.frame_width
            sample_width = sound.sample_width

            # load metadata
            audio_metadata = eyed3.load(f'{SONG_DIR}/{track}')

            encoded_img = ''
            for d in audio_metadata.tag.images:
                encoding = base64.b64encode(d.image_data).decode('ascii')
                encoded_img += f'data:image/png;base64,{encoding}'

            # update the track metadata
            global track_metadata
            track_metadata = {
                "title": audio_metadata.tag.title or "",
                "artist": audio_metadata.tag.artist or "",
                "album": audio_metadata.tag.album or "",
                "publisher": audio_metadata.tag.publisher or "",
                "genre": "" if audio_metadata.tag.genre is None else audio_metadata.tag.genre.name,
                "sample_rate": sample_rate,
                "frame_count": frame_count,
                "channels": channels,
                "frame_width": frame_width,
                "sample_width": sample_width,
                "img": encoded_img
            }

            server.send_message_to_all(json.dumps(create_message(
                "SONG_INFO", 200, extra_info=track_metadata)))

            log(
                f'✨ Playing {audio_metadata.tag.artist} - [{audio_metadata.tag.title}] ✨\n')

            chunks = make_chunks(sound, CHUNK_SIZE_MS)
            for i in range(len(chunks)):

                # split each chunk into individual channels
                channel_datas = chunks[i].split_to_mono()
                data_sum = sum([len(d.raw_data) for d in channel_datas])
                processed_datas = []

                # handle PCM conversion on the server
                for c in range(channels):
                    processed_data = []
                    channel_data = list(channel_datas[c].raw_data)
                    for i in range(len(channel_data) // sample_width):
                        # handles only 2-byte samples for now
                        word = (channel_data[i * sample_width] & 0xff) + \
                            ((channel_data[i * sample_width + 1] & 0xff) << 8)
                        signedWord = ((word + 32768.0) % 65536.0) - 32768.0
                        processed_data.append(signedWord / 32768.0)
                    processed_datas.append(processed_data)

                if (not len(server.clients)):
                    log("No clients connected...")
                else:
                    log(
                        f"Sending chunk {i+1} ({data_sum} bytes) to {len(server.clients)} client(s)")

                    try:
                        server.send_message_to_all(json.dumps(create_message(
                            "SONG_DATA", 200, extra_info={"rawData": processed_datas})))
                    except:
                        pass  # ¯\_(ツ)_/¯

                # broadcast throttle to ensure new clients can be synced
                time.sleep(
                    (((int(i > 0) * CHUNK_SIZE_MS) + CHUNK_SIZE_MS) // 2) / 1000)


# called for every client connecting (after handshake)
def new_client(client, _):
    log(f"Client {client['id']} connected")
    global track_metadata
    server.send_message(client, json.dumps(create_message(
        "SONG_INFO", 200, extra_info=track_metadata)))


# called for every client disconnecting
def client_left(client, _):
    log(f"Client {client['id']} disconnected")


def main():
    print("""
     _    __          __                ____            ___
    | |  / /__  _____/ /_____  _____   / __ \____ _____/ (_)___
    | | / / _ \/ ___/ __/ __ \/ ___/  / /_/ / __ `/ __  / / __ \\
    | |/ /  __/ /__/ /_/ /_/ / /     / _, _/ /_/ / /_/ / / /_/ /
    |___/\___/\___/\__/\____/_/     /_/ |_|\__,_/\__,_/_/\____/

    """)

    log("Starting server...")

    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)

    radio_thread = threading.Thread(target=run_radio_server)
    radio_thread.daemon = True
    radio_thread.start()

    server.run_forever()
    log("Server terminated")


if __name__ == "__main__":
    main()
