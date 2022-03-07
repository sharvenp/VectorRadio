<template>
  <Player />
</template>

<script>
import Player from "./components/Player.vue";

export default {
  name: "App",
  components: {
    Player,
  },
};
</script>

<style>
@import url("https://fonts.googleapis.com/css2?family=Shippori+Antique+B1&display=swap");

#app {
  font-family: "Shippori Antique B1", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
