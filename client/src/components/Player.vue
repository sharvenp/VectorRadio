<template>
  <div>
    Player
    <audio id="player" controls>
      <source src="" type="audio/mpeg" />
      Your browser does not support the audio element.
    </audio>
  </div>
</template>

<script>
import net from "net";

export default {
  name: "Player",
  data() {
    return {};
  },
  async mounted() {
    const client = new net.Socket();
    const port = 6000;
    const host = "0.0.0.0";

    client.connect(port, host, function () {
      console.log("Connected");
    });

    client.on("data", (data) => {
      // parts = [];
      // stream.on("data", function (chunk) {
      //   parts.push(chunk);
      // });
      // stream.on("end", function () {
      //   audio.src = (window.URL || window.webkitURL).createObjectURL(
      //     new Blob(parts)
      //   );
      //   audio.play();
      // });
      console.log(data);
    });
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
