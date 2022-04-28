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
        <h1
          class="display-1"
          :style="{
            color: textColor,
          }"
        >
          <b>Vector Radio</b>
        </h1>
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

      <div
        class="d-flex flex-column min-vh-100 justify-content-center align-items-center"
        v-else-if="connectionStatus === 2"
      >
        <div class="metadata">
          <img
            class="album-art shadow no-select"
            id="album-img"
            :src="
              songMetadata['img'] ||
              require('../../public/default_album_art.webp')
            "
            @load="adjustColors"
          />
          <h1
            class="ps-5 pe-5 title mt-4 no-select"
            :style="{ color: textColor }"
            @click="() => (showQueueModal = !showQueueModal)"
          >
            {{ songMetadata["title"] || "[Untitled]" }}
          </h1>
          <h2
            class="ps-5 pe-5 album mt-3 text-truncate no-select"
            :style="{ color: textColor }"
          >
            {{ songMetadata["album"] || "[Unknown Album]" }}
          </h2>
          <h3
            class="ps-5 pe-5 artist mt-3 text-truncate no-select"
            :style="{ color: textColor }"
          >
            {{ songMetadata["artist"] || "[Unknown Artist]" }}
          </h3>
          <button
            type="button"
            class="btn mt-3 vol-button"
            :style="{
              'border-color': textColor,
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
      </div>
      <div v-else-if="connectionStatus === -1">
        <h1 :style="{ color: textColor }">¯\_(ツ)_/¯</h1>
        <h1 class="ps-3 pe-3" :style="{ color: textColor }">
          Could not connect to <b>Vector Radio</b>
        </h1>
        <p :style="{ color: textColor }">
          Refresh the page to try connecting again
        </p>
      </div>
    </div>
    <AudioVisualizer
      v-if="connectionStatus == 2"
      :analyzer="analyzer"
      :visualizerColor="visualizerColor"
    />
    <QueueModal
      v-if="connectionStatus == 2 && showQueueModal"
      :textColor="textColor"
      :backgroundColor="visualizerColor"
      :queue="queue"
      @closeModal="() => (showQueueModal = !showQueueModal)"
    />
  </div>
</template>

<script>
import Vibrant from "node-vibrant";
import QueueModal from "./QueueModal.vue";
import AudioVisualizer from "./AudioVisualizer.vue";

export default {
  name: "Player",
  data() {
    return {
      connectionStatus: 0,
      websocket: undefined,
      songMetadata: {},
      queue: [],
      buffers: [],
      audioContext: undefined,
      gainNode: undefined,
      analyzer: undefined,
      isPlaying: false,
      isBuffering: false,
      isMuted: false,
      showQueueModal: false,
      backgroundColor: "#000000",
      textColor: "#FFFFFF",
      visualizerColor: [100, 100, 100],
    };
  },
  components: {
    QueueModal,
    AudioVisualizer,
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

      const calculateFFTSize = () => {
        if (!this.analyzer) {
          return;
        }
        this.analyzer.fftSize = Math.min(
          Math.max(
            1 << (31 - Math.clz32(Math.round(window.innerWidth * 0.2))),
            32
          ),
          32768
        );
      };
      window.addEventListener("resize", calculateFFTSize);
      calculateFFTSize();

      if (!this.isBuffering && !this.isPlaying) {
        this.play();
      }
    },

    updateSongMetadata(data) {
      this.songMetadata = data.metadata;
      this.queue = data.queue.slice(data.metadata.n, data.queue.length);
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

      console.log(this.buffers.length);

      if (!this.isPlaying) {
        // buffer at least two segments
        if (this.buffers.length > 1) {
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
      if (!this.songMetadata || !this.songMetadata.img) {
        return;
      }

      const img = document.getElementById("album-img");
      const vib = new Vibrant(img);
      vib.getPalette().then(
        (palette) => {
          let color = palette.Muted;
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
  },
};
</script>

<style scoped>
.player {
  position: relative;
  transition: 1s;
}

.tune-in-button {
  font-size: 20px;
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
  width: 20vh;
  height: 20vh;
  border-width: 5px;
  transition: 1s;
}

.buffer-spinner {
  position: absolute;
  top: 5vh;
  transition: 1s;
}

.metadata {
  z-index: 2 !important;
  width: 100%;
  height: min(75% - 2rem, 700px);
}

.album-art {
  border-radius: 15px;
  width: 80%;
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
    width: 400px;
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
    font-size: 40px;
  }
  .buffer-spinner {
    top: 10vh;
  }
}

img {
  pointer-events: none;
}
</style>
