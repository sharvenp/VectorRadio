<template>
  <div>
    <div
      class="d-flex flex-column vh-100 justify-content-center align-items-center"
    >
      <div v-if="connectionStatus === 0">
        <div
          class="spinner-border text-primary load-spinner"
          role="status"
        ></div>
      </div>
      <div v-else-if="connectionStatus === 1">
        <button type="button" class="btn btn-primary tune-in" @click="tuneIn">
          Tune In
        </button>
      </div>
      <div v-else-if="connectionStatus === 2" class="w-100">
        <img class="album-art" :src="songMetadata['img']" width="300" />
        <h1 class="title mt-5 text-truncate">{{ songMetadata["title"] }}</h1>
        <h3 class="artist text-truncate">
          {{ songMetadata["artist"] }}
        </h3>
        <input
          type="range"
          class="form-range volume-slider mt-3"
          v-model="volume"
          min="1"
          max="1000"
          step="1"
          @change="onVolumeChange"
        />
      </div>
      <div v-else-if="connectionStatus === -1">
        <h1>Could not connect to <b>VectorRadio</b> server</h1>
        <p>
          Please make sure the server is set up properly and refresh the page to
          try again.
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
      audioBuffers: [],
      audioContext: undefined,
      gainNode: undefined,
      isPlaying: false,
      isTunedIn: false,
      volume: 1000,
    };
  },
  mounted() {
    this.audioContext = new (window.AudioContext ||
      window.webkitAudioContext)();
    this.gainNode = this.audioContext.createGain();
    this.gainNode.gain.value = this.volume / 1000;
    this.gainNode.connect(this.audioContext.destination);

    this.websocket = new WebSocket(process.env.VUE_APP_SERVER_ADDRESS);

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
        this.createNextAudioBuffer(data.bytes);
      }
    };
  },
  methods: {
    tuneIn() {
      this.connectionStatus = 2;
    },
    updateSongMetadata(songMetadata) {
      this.songMetadata = songMetadata;
    },
    play() {
      if (!this.songMetadata) {
        return;
      }

      const nextBuffer = this.audioBuffers.shift();
      this.isPlaying = true;

      if (!nextBuffer) {
        this.isPlaying = false;
        return;
      }

      let source = this.audioContext.createBufferSource();
      source.buffer = nextBuffer;
      source.connect(this.gainNode);
      source.onended = this.play;
      source.start();
    },
    createNextAudioBuffer(buffer) {
      // 16-bit, so it is twice the length
      const frameCount = buffer.length / 2;
      let audioBuffer = this.audioContext.createBuffer(
        this.songMetadata.channels,
        frameCount,
        this.songMetadata.sample_rate * 2
      );

      for (let channel = 0; channel < this.songMetadata.channels; channel++) {
        let nowBuffering = audioBuffer.getChannelData(channel);
        for (let i = 0; i < frameCount; i++) {
          var word = (buffer[i * 2] & 0xff) + ((buffer[i * 2 + 1] & 0xff) << 8);
          let signedWord = ((word + 32768.0) % 65536.0) - 32768.0;
          nowBuffering[i] = signedWord / 32768.0;
        }
      }

      this.audioBuffers.push(audioBuffer);
      if (!this.isPlaying) {
        this.play();
      }
    },
    onVolumeChange() {
      this.gainNode.gain.setValueAtTime(
        this.volume / 1000,
        this.audioContext.currentTime
      );
    },
  },
};
</script>

<style scoped>
.load-spinner {
  width: 25vh;
  height: 25vh;
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
