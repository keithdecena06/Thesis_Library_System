document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("record-search");
  const results = document.getElementById("record-results");

  let debounceTimer = null;

  input.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    const query = input.value.trim();

    if (query.length < 2) {
      results.innerHTML = "";
      return;
    }

    debounceTimer = setTimeout(() => fetchResults(query), 300);
  });

  async function fetchResults(query) {
    try {
      const res = await fetch(`/kiosk/api/search/?q=${encodeURIComponent(query)}`);
      const data = await res.json();

      results.innerHTML = "";

      if (!data.results || data.results.length === 0) {
        results.innerHTML = `<p class="empty">No results found</p>`;
        return;
      }

      data.results.forEach(item => {
        const card = document.createElement("div");
        card.className = "record-card";

        card.innerHTML = `
          <span class="record-type">${item.type}</span>
          <h3 class="record-title">${item.title}</h3>
          <p class="record-meta">${item.meta || ""}</p>

          <div class="record-actions">
            <button class="record-btn">Record</button>
            <button class="save-btn">Save</button>
          </div>
        `;

        card.querySelector(".record-btn").onclick = () =>
          submitAction(item.type.toLowerCase(), item.id, "recorded");

        card.querySelector(".save-btn").onclick = () =>
          submitAction(item.type.toLowerCase(), item.id, "saved");

        results.appendChild(card);
      });

    } catch (err) {
      console.error("Search error:", err);
    }
  }

  async function submitAction(type, id, action) {
    await fetch("/kiosk/api/library-action/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content_type: type,
        content_id: id,
        action: action
      })
    });

    window.location.href = "/kiosk/account/";
  }
});