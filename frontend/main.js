// frontend/main.js
import { startRecording, stopRecording, playAudio } from "./audio.js";

const BACKEND_URL = "http://127.0.0.1:8000"; // adjust if backend runs elsewhere

// DOM elements
const recordBtn = document.getElementById("record-btn");
const stopBtn = document.getElementById("stop-btn");
const transcriptBox = document.getElementById("transcript");
const responseBox = document.getElementById("response");
const audioPlayer = document.getElementById("audio-player");

let isRecording = false;

// --- Event listeners ---

recordBtn.addEventListener("click", async () => {
  if (isRecording) return;
  isRecording = true;

  recordBtn.disabled = true;
  stopBtn.disabled = false;
  transcriptBox.value = "";
  responseBox.value = "";

  await startRecording();
});

stopBtn.addEventListener("click", async () => {
  if (!isRecording) return;
  isRecording = false;

  recordBtn.disabled = false;
  stopBtn.disabled = true;

  const audioBlob = await stopRecording();

  // Send audio to backend
  const formData = new FormData();
  formData.append("file", audioBlob, "input.wav");


  const res = await fetch(`${BACKEND_URL}/converse`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    alert("❌ Backend error");
    return;
  }

  const data = await res.json();

  // Update UI
  transcriptBox.value = data.transcript || "";
  responseBox.value = data.response || "";

  if (data.audio_file) {
    audioPlayer.src = data.audio_file;
    audioPlayer.style.display = "block";
    audioPlayer.play();
  }
});
