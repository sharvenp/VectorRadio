<template>
  <div>
    <h1 v-if="connection_status == 0">Loading...</h1>
    <h1 v-else-if="connection_status == 2">Error</h1>
    <div v-else>
      <img :src="song_metadata['img']" width="400" />
      <h1>{{ song_metadata["title"] }}</h1>
      <h2>
        <i>{{ song_metadata["artist"] }}</i>
      </h2>
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
      song_metadata: {},
    };
  },
  mounted() {
    this.websocket = new WebSocket("ws://localhost:8001/");

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
        this.update_song_metadata(data);
      } else {
        // play audio data
      }
    };
  },
  methods: {
    update_song_metadata(song_metadata) {
      this.song_metadata = song_metadata;
    },
  },
};
</script>

<style scoped></style>
