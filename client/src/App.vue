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
@font-face {
  font-family: "Mulish Light";
  src: url("../assets/Mulish-Light.ttf") format("truetype");
}

@font-face {
  font-family: "Mulish";
  src: url("../assets/Mulish-Regular.ttf") format("truetype");
}

#app {
  font-family: "Mulish";
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center; 
}
</style>
