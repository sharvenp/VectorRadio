import { createApp } from "vue";
import App from "./App.vue";
import dotenv from "dotenv";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap";

dotenv.config();

const app = createApp(App);
app.mount("#app");
