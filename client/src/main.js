import { createApp } from "vue";
import App from "./App.vue";
import dotenv from "dotenv";

dotenv.config();

const app = createApp(App);
app.mount("#app");
