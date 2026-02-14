let scanInterval = null;
let targetAction = null;

function startRFIDScan(action) {
  if (window.IS_LOGGED_IN === true) {
    if (action === "account") {
      window.location.href = "/kiosk/account/";
    }
    if (action === "record") {
      window.location.href = "/kiosk/record/";
    }
    return;
  }

  targetAction = action;

  const modal = document.getElementById("rfid-modal");
  const title = document.getElementById("rfid-title");
  const sub = document.getElementById("rfid-sub");

  title.textContent = "Please tap your ID";
  sub.textContent = "Scanning…";
  modal.classList.remove("hidden");

  if (scanInterval) return;

  scanInterval = setInterval(async () => {
    try {
      const res = await fetch("/kiosk/api/last-scan/");
      const data = await res.json();

      if (!data.found) return;

      await fetch("/kiosk/api/consume-scan/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ log_id: data.log_id })
      });

      clearInterval(scanInterval);
      scanInterval = null;

      title.textContent = "Verified";
      sub.textContent = "Redirecting…";

      setTimeout(() => {
        if (targetAction === "account") {
          window.location.href = "/kiosk/account/?user=" + data.user_id;
        }

        if (targetAction === "record") {
          window.location.href = "/kiosk/record/?user=" + data.user_id;
        }
      }, 600);

    } catch (err) {
      console.error("RFID error:", err);
    }
  }, 1000);
}