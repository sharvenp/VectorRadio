<template>
  <div>
    <div
      class="d-flex flex-column vh-100 justify-content-center align-items-center"
    >
      <div
        v-show="isBuffering"
        class="spinner-grow text-primary buffer-spinner"
      ></div>
      <div v-if="connectionStatus === 0">
        <div class="spinner-border text-primary load-spinner"></div>
      </div>
      <div v-else-if="connectionStatus === 1" class="w-100">
        <img class="album-art shadow" :src="songMetadata['img']" />
        <h1 class="title mt-5 text-truncate">{{ songMetadata["title"] }}</h1>
        <h3 class="artist text-truncate">
          {{ songMetadata["artist"] }}
        </h3>
        <button type="button" class="btn btn-dark mt-3" @click="toggleMute">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="currentColor"
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
            fill="currentColor"
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
        <h1>Could not connect to <b>VectorRadio</b> server</h1>
        <p>
          Please make sure the server is set up properly and refresh the page to
          try connecting again.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Player",
  data() {
    return {
      connectionStatus: 0,
      websocket: undefined,
      songMetadata: {},
      audioBufferSources: [],
      audioContext: undefined,
      gainNode: undefined,
      nextAudioBufferSource: undefined,
      isPlaying: false,
      isBuffering: false,
      isMuted: false,
    };
  },
  mounted() {
    this.audioContext = new (window.AudioContext ||
      window.webkitAudioContext)();
    this.gainNode = this.audioContext.createGain();
    this.gainNode.gain.value = 1;
    this.gainNode.connect(this.audioContext.destination);

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
        this.createNextAudioBuffer(data.rawData);
      }
    };
  },
  methods: {
    tuneIn() {
      this.connectionStatus = 2;
    },

    updateSongMetadata(songMetadata) {
      this.songMetadata = songMetadata;
      console.log({
        title: songMetadata.title,
        artist: songMetadata.artist,
        album: songMetadata.album,
        sample_rate: songMetadata.sample_rate,
        frame_count: songMetadata.frame_count,
        channels: songMetadata.channels,
        frame_width: songMetadata.frame_width,
        sample_width: songMetadata.sample_width,
      });
    },

    play() {
      if (!this.songMetadata) {
        return;
      }

      // start playing the next audio buffer
      if (this.nextAudioBufferSource) {
        this.nextAudioBufferSource.start();
      }

      // get the next buffer
      this.nextAudioBufferSource = this.audioBufferSources.shift();
      this.isPlaying = true;
      if (!this.nextAudioBufferSource) {
        this.isPlaying = false;
        return;
      }
    },

    createNextAudioBuffer(buffer) {
      const audioBuffer = this.audioContext.createBuffer(
        this.songMetadata.channels,
        buffer[0].length / this.songMetadata.sample_width,
        this.songMetadata.sample_rate
      );

      // parse the channel buffers
      for (let channel = 0; channel < this.songMetadata.channels; channel++) {
        let nowBuffering = audioBuffer.getChannelData(channel);
        for (
          let i = 0;
          i < buffer[channel].length / this.songMetadata.sample_width;
          i++
        ) {
          // hard-coded for 2-byte samples for now
          var word =
            (buffer[channel][i * this.songMetadata.sample_width] & 0xff) +
            ((buffer[channel][i * this.songMetadata.sample_width + 1] & 0xff) <<
              8);
          let signedWord = ((word + 32768.0) % 65536.0) - 32768.0;
          nowBuffering[i] = signedWord / 32768.0;
        }
      }

      let nextSource = this.audioContext.createBufferSource();
      nextSource.buffer = audioBuffer;
      nextSource.loop = false;
      nextSource.connect(this.gainNode);
      nextSource.onended = this.play;

      if (!this.nextAudioBufferSource) {
        this.nextAudioBufferSource = nextSource;
      } else {
        this.audioBufferSources.push(nextSource);
      }

      if (!this.isPlaying) {
        // buffer at least two segments
        if (this.audioBufferSources.length > 2) {
          this.isBuffering = false;
          this.play();
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
  },
};
</script>

<style scoped>
.vol-icon {
  width: 2rem;
  height: 2rem;
}

.load-spinner {
  width: 10vh;
  height: 10vh;
  border-width: 5px;
}

.buffer-spinner {
  position: absolute;
  top: 10vh;
}

.tune-in {
  width: 20vh;
  height: 10vh;
  font-size: 1.5rem;
  border-radius: 25px !important;
}

.album-art {
  border-radius: 15px;
  border: 2px black solid;
  width: 70%;
}

.title {
  font-size: 30px;
  font-weight: bold;
}

.artist {
  font-size: 15px;
  font-style: italic;
}

.volume-slider {
  width: 50%;
}

@media screen and (min-width: 1000px) {
  .album-art {
    width: 20%;
  }
  .title {
    font-size: 50px;
  }
  .artist {
    font-size: 20px !important;
  }
  .tune-in {
    font-size: 3rem;
  }
  .volume-slider {
    width: 10%;
  }
}
</style>
