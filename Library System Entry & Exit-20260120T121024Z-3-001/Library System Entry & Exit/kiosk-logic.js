const rfidInput = document.getElementById('rfid-listener');
const manualId = document.getElementById('manual-id');
const manualPass = document.getElementById('manual-pass');

// SMART FOCUS: Only focus RFID if user isn't clicking a manual input
document.addEventListener('click', (e) => {
    // If the thing the user clicked is NOT the ID box and NOT the password box
    if (e.target !== manualId && e.target !== manualPass) {
        rfidInput.focus();
    }
});

// RFID Listener Logic
rfidInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        const rfidValue = this.value.trim();
        if (rfidValue.length > 0) {
            console.log("Card Detected: " + rfidValue);
            window.location.href = "selection.html"; 
        }
        this.value = ''; 
    }
});

// Manual Logic
function handleManual(action) {
    const id = manualId.value.trim();
    const pass = manualPass.value.trim();

    if (id && pass) {
        if (action === 'login') {
            window.location.href = "selection.html";
        } else {
            window.location.href = "goodbye.html";
        }
    } else {
        alert("Please enter both ID and Password");
    }
}