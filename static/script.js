let audio = new Audio();
audio.loop = false;

function playMusic(path, title, artist, cover) {
  audio.src = path;
  audio.play();
  document.getElementById("song-title").innerText = title;
  document.getElementById("artist-name").innerText = artist;
  document.getElementById("cover").src = cover;
  document.getElementById("music-player").style.display = "flex"; // Show the player
  document.getElementById("play-pause").innerText = "⏸️"; // Set play/pause icon to pause
  updateProgress();
}

function togglePlayPause() {
  if (audio.paused) {
    audio.play();
    document.getElementById("play-pause").innerText = "⏸️"; // Show pause icon
  } else {
    audio.pause();
    document.getElementById("play-pause").innerText = "▶️"; // Show play icon
  }
}

function updateProgress() {
  audio.ontimeupdate = function () {
    const progress = (audio.currentTime / audio.duration) * 100;
    document.getElementById("progress-filled").style.width = `${progress}%`;
    document.getElementById("current-time").innerText = formatTime(
      audio.currentTime
    );
    document.getElementById("duration").innerText = formatTime(audio.duration);
  };
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secondsPart = Math.floor(seconds % 60);
  return `${minutes}:${secondsPart < 10 ? "0" : ""}${secondsPart}`;
}

function toggleMute() {
  audio.muted = !audio.muted;
}

function prevSong() {
  // Implement previous song functionality if needed
}

function nextSong() {
  // Implement next song functionality if needed
}
