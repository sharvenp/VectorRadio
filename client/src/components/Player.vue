<template>
  <div>
    <h1 v-if="connection_status == 0">Loading...</h1>
    <h1 v-else-if="connection_status == 2">Error</h1>
    <div v-else>
      <img :src="songMetadata['img']" width="300" />
      <h1>{{ songMetadata["title"] }}</h1>
      <h2>
        <i>{{ songMetadata["artist"] }}</i>
      </h2>
      <button>Tune In!</button>
    </div>
  </div>
</template>

<script>
export default {
  name: "Player",
  data() {
    return {
      connection_status: 0,
      websocket: undefined,
      songMetadata: {},
      audioBuffers: [],
      audioContext: undefined,
      isPlaying: false,
    };
  },
  mounted() {
    this.audioContext = new (window.AudioContext ||
      window.webkitAudioContext)();

    this.websocket = new WebSocket(process.env.VUE_APP_SERVER_ADDRESS);

    this.websocket.onopen = () => {
      this.connection_status = 1;
    };

    this.websocket.onerror = () => {
      this.connection_status = 2;
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
      source.connect(this.audioContext.destination);
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
  },
};
</script>

<style scoped></style>
