let idleTimer = null;

// 1 minute idle
const IDLE_LIMIT = 60 * 1000;

function goIdle() {
  // clear session on idle
  fetch("/kiosk/api/logout/", { method: "POST" })
    .finally(() => {
      window.location.href = "/kiosk/idle/";
    });
}

function resetIdle() {
  if (idleTimer) clearTimeout(idleTimer);
  idleTimer = setTimeout(goIdle, IDLE_LIMIT);
}

// Any interaction resets idle
["mousemove", "mousedown", "keydown", "touchstart", "click"].forEach(evt => {
  document.addEventListener(evt, resetIdle, true);
});

// Start timer on page load
resetIdle();