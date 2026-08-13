import { invoke } from "@tauri-apps/api/core";

let greetingText = document.querySelector("#greetText");

async function greet() {
  if (greetingText) {
    greetingText.textContent = invoke('greet', { name: "dev"});
  }
}

window.addEventListener("DOMContentLoaded", () => {
  greet();
});
