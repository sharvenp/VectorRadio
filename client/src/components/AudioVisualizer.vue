<template>
  <canvas id="visualizer" class="visualizer" @click="toggleVisualizer"></canvas>
</template>

<script>
export default {
  name: "Player",
  props: {
    analyzer: Object,
    visualizerColor: Array,
  },
  data() {
    return {
      enabled: true,
    };
  },
  mounted() {
    requestAnimationFrame(this.visualizeAudio);
  },
  methods: {
    visualizeAudio() {
      requestAnimationFrame(this.visualizeAudio);

      let canvas = document.getElementById("visualizer");
      if (canvas === undefined) return;

      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      let ctx = canvas.getContext("2d");

      if (!this.enabled) {
        return;
      }

      let length = this.analyzer.frequencyBinCount;
      let freqBuffer = new Uint8Array(length);
      this.analyzer.getByteFrequencyData(freqBuffer);

      let baseHeight = 0;
      let maxHeight = window.innerHeight / 2;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      let space = canvas.width / length;
      ctx.fillStyle = `rgba(${this.visualizerColor[0]},${this.visualizerColor[1]}, ${this.visualizerColor[2]}, 0.5)`;
      for (let i = 0; i < length; i++) {
        let val = freqBuffer[i] / 255;
        ctx.fillRect(
          i * space,
          canvas.height - (baseHeight + maxHeight * val),
          space - 1,
          baseHeight + maxHeight * val
        );
      }
    },

    toggleVisualizer() {
      this.enabled = !this.enabled;
    },
  },
};
</script>

<style scoped>
.visualizer {
  top: 0;
  left: 0;
  position: absolute;
  /* pointer-events: none; */
  z-index: 1 !important;
}
</style>
