<template>
  <div></div>
</template>

<script>
export default {
  name: "QueueModal",
  props: {
    textColor: String,
  },
  data() {
    return {
      isOpen: false,
    };
  },
  mounted() {},
  methods: {
    toggleOpen() {
      this.isOpen = !this.isOpen;
    },
  },
};
</script>

<style scoped>
@media screen and (min-width: 1000px) {
}
</style>
