<template>
  <div class="modal-bg" ref="el">
    <div
      class="queue-modal"
      :style="{
        'background-color': `rgba(${this.backgroundColor[0]},${this.backgroundColor[1]}, ${this.backgroundColor[2]}, 0.55)`,
      }"
    >
      <div class="d-flex flex-row-reverse">
        <button
          type="button"
          class="btn ms-3 me-3 mt-3 close-button"
          :style="{
            'border-color': textColor,
          }"
          @click="closeModal"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            :fill="textColor"
            class="bi bi-x-circle close-icon"
            viewBox="0 0 16 16"
          >
            <path
              fill-rule="evenodd"
              d="M13.854 2.146a.5.5 0 0 1 0 .708l-11 11a.5.5 0 0 1-.708-.708l11-11a.5.5 0 0 1 .708 0Z"
            />
            <path
              fill-rule="evenodd"
              d="M2.146 2.146a.5.5 0 0 0 0 .708l11 11a.5.5 0 0 0 .708-.708l-11-11a.5.5 0 0 0-.708 0Z"
            />
          </svg>
        </button>
      </div>
      <h1 class="display-5 m-4 text no-select" :style="{ color: textColor }">
        <b>Coming Up Next</b>
      </h1>
      <div class="m-3 song-table border mt-5">
        <table class="table table-striped table-bordered">
          <thead :style="{ 'border-color': textColor }">
            <tr>
              <th
                :style="{ color: textColor }"
                class="text no-select"
                scope="col"
              >
                <h4><b>#</b></h4>
              </th>
              <th
                :style="{ color: textColor }"
                class="text no-select"
                scope="col"
              >
                <h4><b>Title</b></h4>
              </th>
              <th
                :style="{ color: textColor }"
                class="text no-select"
                scope="col"
              >
                <h4><b>Artist</b></h4>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="song in queue" :key="song.n">
              <th :style="{ color: textColor }" class="text" scope="row">
                {{ song.n }}
              </th>
              <td :style="{ color: textColor }" class="text user-select-all">
                {{ song.title }}
              </td>
              <td :style="{ color: textColor }" class="text user-select-all">
                {{ song.artist }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import anime from "animejs/lib/anime.es.js";

export default {
  name: "QueueModal",
  props: {
    textColor: String,
    backgroundColor: Array,
    queue: Array,
  },
  mounted() {
    anime({
      targets: this.$refs.el,
      opacity: [0, 1],
      duration: 200,
      easing: "linear",
    });
  },
  methods: {
    closeModal() {
      anime({
        targets: this.$refs.el,
        opacity: [1, 0],
        duration: 200,
        easing: "linear",
        complete: () => this.$emit("closeModal"),
      });
    },
  },
};
</script>

<style scoped>
.song-table {
  height: 60%;
  overflow: auto;
  transition: 1s;
}
.queue-modal {
  outline: 1px solid black;
  background: white;

  width: min(100% - 2rem, 1000px);
  height: min(75% - 2rem, 900px);

  margin: auto;
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  z-index: 4;

  border-radius: 15px;
  transition: 1s;
}

.modal-bg {
  z-index: 3;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
}

.text {
  transition: 1s;
}

.close-icon {
  width: 1.5rem;
  height: 1.5rem;
  transition: 1s;
}
.close-button {
  border-width: 2px;
  border-radius: 10px;
  padding: 5px;
  transition: 1s;
}
</style>
