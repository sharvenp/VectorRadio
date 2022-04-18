<template>
  <div class="player" :style="{ 'background-color': backgroundColor }">
    <div
      class="d-flex flex-column vh-100 justify-content-center align-items-center"
    >
      <div
        v-show="isBuffering && connectionStatus === 2"
        class="spinner-grow buffer-spinner"
        :style="{ color: textColor }"
      ></div>
      <div v-if="connectionStatus === 0">
        <div
          class="spinner-border load-spinner"
          :style="{ color: textColor }"
        ></div>
      </div>
      <div v-else-if="connectionStatus === 1">
        <button
          type="button"
          class="btn mt-3 tune-in-button"
          :style="{
            'border-color': textColor,
            color: textColor,
            'background-color': backgroundColor,
          }"
          @click="tuneIn"
        >
          Tune In
        </button>
      </div>
      <div v-else-if="connectionStatus === 2" class="w-100 mt-3">
        <img
          class="album-art shadow"
          id="album-img"
          :src="
            songMetadata['img'] ||
            'https://static.vecteezy.com/system/resources/previews/003/674/909/large_2x/music-note-icon-song-melody-tune-flat-symbol-free-free-vector.jpg'
          "
          @load="adjustColors"
        />
        <h1 class="title mt-4 text-truncate" :style="{ color: textColor }">
          {{ songMetadata["title"] || "[Untitled]" }}
        </h1>
        <h2 class="album mt-3 text-truncate" :style="{ color: textColor }">
          {{ songMetadata["album"] || "[Unknown Album]" }}
        </h2>
        <h3 class="artist mt-3 text-truncate" :style="{ color: textColor }">
          {{ songMetadata["artist"] || "[Unknwon Artist]" }}
        </h3>
        <button
          type="button"
          class="btn mt-3 vol-button"
          :style="{
            'border-color': textColor,
            'background-color': backgroundColor,
          }"
          @click="toggleMute"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            :fill="textColor"
            class="bi bi-volume-mute vol-icon"
            viewBox="0 0 16 16"
            v-if="isMuted"
          >
            <path
              d="M6.717 3.55A.5.5 0 0 1 7 4v8a.5.5 0 0 1-.812.39L3.825 10.5H1.5A.5.5 0 0 1 1 10V6a.5.5 0 0 1 .5-.5h2.325l2.363-1.89a.5.5 0 0 1 .529-.06zM6 5.04 4.312 6.39A.5.5 0 0 1 4 6.5H2v3h2a.5.5 0 0 1 .312.11L6 10.96V5.04zm7.854.606a.5.5 0 0 1 0 .708L12.207 8l1.647 1.646a.5.5 0 0 1-.708.708L11.5 8.707l-1.646 1.647a.5.5 0 0 1-.708-.708L10.793 8 9.146 6.354a.5.5 0 1 1 .708-.708L11.5 7.293l1.646-1.647a.5.5 0 0 1 .708 0z"
            />
          </svg>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            :fill="textColor"
            class="bi bi-volume-up vol-icon"
            viewBox="0 0 16 16"
            v-else
          >
            <path
              d="M11.536 14.01A8.473 8.473 0 0 0 14.026 8a8.473 8.473 0 0 0-2.49-6.01l-.708.707A7.476 7.476 0 0 1 13.025 8c0 2.071-.84 3.946-2.197 5.303l.708.707z"
            />
            <path
              d="M10.121 12.596A6.48 6.48 0 0 0 12.025 8a6.48 6.48 0 0 0-1.904-4.596l-.707.707A5.483 5.483 0 0 1 11.025 8a5.483 5.483 0 0 1-1.61 3.89l.706.706z"
            />
            <path
              d="M10.025 8a4.486 4.486 0 0 1-1.318 3.182L8 10.475A3.489 3.489 0 0 0 9.025 8c0-.966-.392-1.841-1.025-2.475l.707-.707A4.486 4.486 0 0 1 10.025 8zM7 4a.5.5 0 0 0-.812-.39L3.825 5.5H1.5A.5.5 0 0 0 1 6v4a.5.5 0 0 0 .5.5h2.325l2.363 1.89A.5.5 0 0 0 7 12V4zM4.312 6.39 6 5.04v5.92L4.312 9.61A.5.5 0 0 0 4 9.5H2v-3h2a.5.5 0 0 0 .312-.11z"
            />
          </svg>
        </button>
      </div>
      <div v-else-if="connectionStatus === -1">
        <h1>¯\_(ツ)_/¯</h1>
        <h1 class="ps-3 pe-3">
          Could not connect to <b>Vector Radio</b> server
        </h1>
        <p>Refresh the page to try connecting again</p>
      </div>
    </div>
    <canvas v-if="connectionStatus == 2" id="visualizer"></canvas>
  </div>
</template>

<script>
import Vibrant from "node-vibrant";

export default {
  name: "Player",
  data() {
    return {
      connectionStatus: 0,
      websocket: undefined,
      songMetadata: {},
      buffers: [],
      audioContext: undefined,
      gainNode: undefined,
      analyzer: undefined,
      isPlaying: false,
      isBuffering: false,
      isMuted: false,
      minBufferSize: 2,
      backgroundColor: "#000000",
      textColor: "#FFFFFF",
      visualizerColor: "#FFFFFF",
    };
  },
  mounted() {
    this.websocket = new WebSocket(process.env.VUE_APP_SERVER_ADDRESS);
    // this.websocket = new WebSocket("ws://localhost:8001/");

    this.websocket.onopen = () => {
      this.connectionStatus = 1;
    };

    this.websocket.onerror = () => {
      this.connectionStatus = -1;
    };

    this.websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "SONG_INFO") {
        // load metadata
        this.updateSongMetadata(data);
      } else {
        // push data to byteBuffer
        this.createNextAudioBuffer(data.pcm_data);
      }
    };
    requestAnimationFrame(this.visualizeAudio);
  },
  methods: {
    tuneIn() {
      this.connectionStatus = 2;
      this.audioContext = new (window.AudioContext ||
        window.webkitAudioContext)();
      this.analyzer = this.audioContext.createAnalyser();
      this.analyzer.fftSize = 512;
      this.gainNode = this.audioContext.createGain();
      this.gainNode.gain.value = 1;
      this.gainNode.connect(this.analyzer);
      this.analyzer.connect(this.audioContext.destination);

      if (!this.isBuffering && !this.isPlaying) {
        this.play();
      }
    },

    updateSongMetadata(songMetadata) {
      this.songMetadata = songMetadata;
      // console.log({
      //   title: songMetadata.title,
      //   artist: songMetadata.artist,
      //   album: songMetadata.album,
      //   sample_rate: songMetadata.sample_rate,
      //   frame_count: songMetadata.frame_count,
      //   channels: songMetadata.channels,
      //   frame_width: songMetadata.frame_width,
      //   sample_width: songMetadata.sample_width,
      // });
    },

    play() {
      if (!this.songMetadata) {
        return;
      }

      // get the next buffer
      let nextChannelBuffers = this.buffers.shift();
      this.isPlaying = true;
      if (!nextChannelBuffers) {
        this.isPlaying = false;
        return;
      }

      let nextSource = this.audioContext.createBufferSource();
      var nextBuffer = this.audioContext.createBuffer(
        this.songMetadata.channels,
        nextChannelBuffers[0].length,
        this.songMetadata.sample_rate
      );
      for (let channel = 0; channel < this.songMetadata.channels; channel++) {
        nextBuffer.copyToChannel(nextChannelBuffers[channel], channel, 0);
      }
      nextSource.buffer = nextBuffer;
      nextSource.connect(this.gainNode);
      nextSource.onended = this.play;
      nextSource.start();
    },

    createNextAudioBuffer(buffer) {
      let channelBuffers = [];

      // parse the channel buffers
      for (let channel = 0; channel < this.songMetadata.channels; channel++) {
        let floatBuffer = new Float32Array(buffer[channel]);
        channelBuffers.push(floatBuffer);
      }

      this.buffers.push(channelBuffers);

      if (!this.isPlaying) {
        // buffer at least two segments
        if (this.buffers.length > this.minBufferSize) {
          this.isBuffering = false;
          if (this.connectionStatus == 2) {
            this.play();
          } else {
            this.buffers.shift();
          }
        } else {
          this.isBuffering = true;
        }
      }
    },

    toggleMute() {
      this.isMuted = !this.isMuted;
      this.gainNode.gain.setValueAtTime(
        this.isMuted ? 0 : 1,
        this.audioContext.currentTime
      );
    },

    adjustColors() {
      const img = document.getElementById("album-img");
      const vib = new Vibrant(img);
      vib.getPalette().then(
        (palette) => {
          let color = palette.LightMuted;
          this.backgroundColor = color.hex || "#000000";
          let r = color.r;
          let g = color.g;
          let b = color.b;
          if (r * 0.299 + g * 0.587 + b * 0.114 > 186) {
            this.textColor = "#000000";
          } else {
            this.textColor = "#FFFFFF";
          }
          this.visualizerColor = palette.Vibrant.rgb;
        },
        (err) => console.log(err)
      );
    },

    visualizeAudio() {
      requestAnimationFrame(this.visualizeAudio);
      if (this.analyzer === undefined) {
        return;
      }

      let length = this.analyzer.frequencyBinCount;
      let freqBuffer = new Uint8Array(length);
      this.analyzer.getByteFrequencyData(freqBuffer);
      let canvas = document.getElementById("visualizer");

      if (canvas === undefined) return;

      let baseHeight = 0;
      let maxHeight = window.innerHeight / 2;
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      let ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      let space = canvas.width / length;
      ctx.fillStyle = `rgba(${this.visualizerColor[0]},${this.visualizerColor[1]}, ${this.visualizerColor[2]}, 0.5)`;
      for (let i = 0; i < length; i++) {
        let val = freqBuffer[i] / 255;
        ctx.fillRect(
          i * space,
          canvas.height - (baseHeight + maxHeight * val),
          space,
          baseHeight + maxHeight * val
        );
      }
    },
  },
};
</script>

<style scoped>
#visualizer {
  top: 0;
  left: 0;
  position: absolute;
  pointer-events: none;
}

.player {
  position: relative;
  transition: 1s;
}

.tune-in-button {
  font-size: 40px;
  font-weight: bold;
}

.vol-button {
  border-width: 2px;
  border-radius: 10px;
  padding: 5px;
  transition: 1s;
}

.vol-icon {
  width: 2.5rem;
  height: 2.5rem;
  transition: 1s;
}

.load-spinner {
  width: 10vh;
  height: 10vh;
  border-width: 5px;
  transition: 1s;
}

.buffer-spinner {
  position: absolute;
  top: 10vh;
  transition: 1s;
}

.album-art {
  border-radius: 15px;
  width: 70%;
}

.title {
  font-size: 30px;
  font-weight: bold;
  transition: 1s;
}

.album {
  font-size: 20px;
  font-style: bold;
  transition: 1s;
}

.artist {
  font-size: 15px;
  transition: 1s;
}

@media screen and (min-width: 1000px) {
  .album-art {
    width: 15%;
  }
  .title {
    font-size: 65px;
  }
  .album {
    font-size: 35px;
  }
  .artist {
    font-size: 22px;
  }
  .tune-in-button {
    font-size: 30px;
  }
}
</style>
