let mediaRecorder;
let audioChunks = [];

/**
 * Start recording microphone input.
 */
export async function startRecording() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);

  audioChunks = [];
  mediaRecorder.ondataavailable = event => {
    if (event.data.size > 0) audioChunks.push(event.data);
  };

  mediaRecorder.start();
}

/**
 * Stop recording and return audio Blob.
 * @returns {Promise<Blob>} Recorded audio as WAV
 */
export function stopRecording() {
  return new Promise(resolve => {
    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      resolve(audioBlob);
    };
    mediaRecorder.stop();
  });
}

/**
 * Play audio from a given URL.
 * @param {string} url - Backend /download/{filename} URL
 */
export function playAudio(url) {
  const audio = new Audio(url);
  audio.play();
}
