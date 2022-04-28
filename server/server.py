
# system
import os
import threading
from datetime import datetime
import time
import random
import base64

# linear regression for timing
import math
from linreg import LinearRegression

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
SERVER_HOST = '0.0.0.0'
# SERVER_HOST = 'localhost'  # use this for local hosting
SERVER_PORT = int(os.getenv('SERVER_PORT'))
CHUNK_SIZE_MS = 1000
ZERO_POINT_TOLERANCE = 0.0005

server = WebsocketServer(host=SERVER_HOST, port=SERVER_PORT)
song_list = []
track_metadata = {}
linreg_estimator = LinearRegression(50)


def log(message):
    print(f"[{datetime.now()}] {message}")


def create_message(message, code, extra_info={}):
    data = {'type': message, 'code': code}
    data.update(extra_info)
    return data


def run_radio_server():

    log(f'Radio server started')

    while True:

        log("Loading tracks ...")
        tracks = os.listdir(SONG_DIR)
        log(f"Loaded {len(tracks)} track(s)")

        # shuffle all tracks
        random.shuffle(tracks)

        # create list of all songs
        global song_list
        song_list.clear()
        for i in range(len(tracks)):
            audio_metadata = eyed3.load(f'{SONG_DIR}/{tracks[i]}')
            song = {
                "n": i + 1,
                "title": audio_metadata.tag.title or "",
                "artist": audio_metadata.tag.artist or "",
            }
            song_list.append(song)

        for i in range(len(tracks)):

            # load track
            track = tracks[i]
            sound = AudioSegment.from_mp3(f'{SONG_DIR}/{track}')
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
                "n": i + 1,
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
                "SONG_INFO", 200, extra_info={"metadata": track_metadata, "queue": song_list})))

            log(
                f'✨ Playing {audio_metadata.tag.artist} - [{audio_metadata.tag.title}] ✨')

            log("Generating PCM chunks ...")

            chunks = make_chunks(sound, CHUNK_SIZE_MS)
            pcm_chunks = []
            print_intervals = [0, 0.25, 0.50, 0.75, 1]
            for i in range(len(chunks)):

                if len(print_intervals) > 0:
                    percentage = (i+1) / len(chunks)
                    if percentage >= print_intervals[0]:
                        log(f'{"{:.0%}".format(percentage)} ({i + 1}/{len(chunks)}) completed')
                        print_intervals.pop(0)

                # split each chunk into individual channels
                channel_datas = chunks[i].split_to_mono()
                pcm_chunk = []
                # handle PCM conversion on the server
                for c in range(channels):
                    raw_channel_data = list(channel_datas[c].raw_data)
                    pcm_channel_data = []
                    for i in range(len(raw_channel_data) // sample_width):
                        # handles only 2-byte samples for now
                        word = (raw_channel_data[i * sample_width] & 0xff) + \
                            ((raw_channel_data[i *
                             sample_width + 1] & 0xff) << 8)
                        signedWord = ((word + 32768.0) % 65536.0) - 32768.0
                        pcm_channel_data.append(signedWord / 32768.0)
                    pcm_chunk.append(pcm_channel_data)
                pcm_chunks.append(pcm_chunk)

            log("Adjusting for zero-point crossings ...")

            for i in range(len(pcm_chunks) - 1):
                curr_pcm_chunk = pcm_chunks[i]
                next_pcm_chunk = pcm_chunks[i+1]
                zero_point_idx = -1
                num_samples = sum([len(b) for b in next_pcm_chunk]) // channels
                for sample_idx in range(num_samples):
                    if all([abs(pcm_val) <= ZERO_POINT_TOLERANCE for pcm_val in [pcm_channel_samples[sample_idx] for pcm_channel_samples in next_pcm_chunk]]):
                        zero_point_idx = sample_idx
                        break
                if zero_point_idx == -1:
                    continue

                # append up until zero-point index to current chunk
                for channel_idx in range(channels):
                    curr_pcm_chunk[channel_idx].extend(
                        next_pcm_chunk[channel_idx][:(zero_point_idx + 1)])

                # delete these samples from the next chunk
                for channel_idx in range(channels):
                    del next_pcm_chunk[channel_idx][:(zero_point_idx + 1)]

            log("Starting broadcast")

            offset = 0

            for i in range(len(pcm_chunks)):

                transmit_time = time.time()

                pcm_chunk = pcm_chunks[i]
                data_sum = sum([len(b) for b in pcm_chunk])
                if data_sum == 0:
                    continue

                if (not len(server.clients)):
                    log("No clients connected ...")
                else:
                    js = json.dumps(create_message(
                        "SONG_DATA", 200, extra_info={"pcm_data": pcm_chunk}))
                    log(
                        f"Sending chunk {i+1}/{len(pcm_chunks)} ({'{0:.2f}'.format(len(str(js)) / 1000000)} MB) to {len(server.clients)} client(s)")
                    try:
                        server.send_message_to_all(js)
                    except:
                        pass  # ¯\_(ツ)_/¯

                # linear regression estimator estimates the transmit time given chunk size
                transmit_time = time.time() - transmit_time
                linreg_estimator.add_point(data_sum, transmit_time)

                # calculate broadcast throttle to ensure new clients can be synced
                # formula: wait = (0.5 * chunk_time) - lin_reg(next_chunk_size) + offset
                # offset = last_chunk_time - last_wait

                # chunk time in seconds
                chunk_time = ((data_sum / channels) / sample_rate)

                # look at next chunk length and subtract a fraction from the wait time
                if i < len(pcm_chunks) - 1:
                    next_chunk_size = sum(
                        [len(b) for b in pcm_chunks[i + 1]])

                    transmit_time_hat = linreg_estimator.estimate(
                        next_chunk_size)
                    if math.isnan(transmit_time_hat) or math.isinf(transmit_time_hat):
                        transmit_time_hat = 0
                        linreg_estimator.clear()

                    # transmit_time_hat = max(transmit_time_hat, 0)
                    transmit_time_hat = 0

                    wait = max((0.5 * chunk_time) -
                               transmit_time_hat + offset, 0)
                    offset = max(chunk_time - wait, 0)

                time.sleep(wait)


# called for every client connecting (after handshake)
def new_client(client, _):
    log(f"Client {client['id']} connected")
    global track_metadata, song_list
    server.send_message(client, json.dumps(create_message(
        "SONG_INFO", 200, extra_info={"metadata": track_metadata, "queue": song_list})))


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

    log("Starting server ...")

    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)

    radio_thread = threading.Thread(target=run_radio_server)
    radio_thread.daemon = True
    radio_thread.start()

    server.run_forever()
    log("Server terminated")


if __name__ == "__main__":
    main()
