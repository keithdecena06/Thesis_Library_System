let scanInterval = null;
let targetAction = null;

window.startRFIDScan = function(action) {

  if (window.IS_LOGGED_IN === true) {
    if (action === "account") window.location.href = "/kiosk/account/";
    if (action === "record") window.location.href = "/kiosk/record/";
    return;
  }

  targetAction = action;

  const modal = document.getElementById("rfid-modal");
  const title = document.getElementById("rfid-title");
  const sub = document.getElementById("rfid-sub");
  const icon = document.getElementById("rfidIcon");
  const iconSymbol = document.getElementById("rfidIconSymbol");

  // Reset state
  icon.classList.remove("success");
  icon.classList.add("scanning");
  iconSymbol.className = "ph ph-credit-card";

  title.textContent = "Please tap your ID";
  sub.textContent = "Scanning…";

  modal.style.opacity = "1";
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

      // SUCCESS ANIMATION
      icon.classList.remove("scanning");
      icon.classList.add("success");
      iconSymbol.className = "ph ph-check";

      title.textContent = "Verified";
      sub.textContent = "Redirecting…";

      setTimeout(() => {
        modal.style.opacity = "0";

        setTimeout(() => {
          if (targetAction === "account")
            window.location.href = "/kiosk/account/?user=" + data.user_id;

          if (targetAction === "record")
            window.location.href = "/kiosk/record/?user=" + data.user_id;

        }, 300);

      }, 700);

    } catch (err) {
      console.error("RFID error:", err);
    }
  }, 1000);
};

/* SIDEBAR TRIGGERS */
document.addEventListener("click", function (e) {

  const recordBtn = e.target.closest("#recordBookBtn");
  if (recordBtn) {
    e.preventDefault();

    if (window.IS_LOGGED_IN === true) {
      window.location.href = "/kiosk/record/";
    } else {
      startRFIDScan("record");
    }
  }

  const myRecordsBtn = e.target.closest("#myRecordsBtn");
  if (myRecordsBtn) {
    e.preventDefault();

    if (window.IS_LOGGED_IN === true) {
      window.location.href = "/kiosk/account/";
    } else {
      startRFIDScan("account");
    }
  }

});

/* CLOSE MODAL */
function closeRFIDModal() {
  const modal = document.getElementById("rfid-modal");
  modal.classList.add("hidden");
  modal.style.opacity = "1";

  if (scanInterval) {
    clearInterval(scanInterval);
    scanInterval = null;
  }
}

/* Close on outside click */
document.addEventListener("click", function (e) {
  const modal = document.getElementById("rfid-modal");
  if (!modal.classList.contains("hidden") && e.target === modal) {
    closeRFIDModal();
  }
});

/* Close on ESC */
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") closeRFIDModal();
});