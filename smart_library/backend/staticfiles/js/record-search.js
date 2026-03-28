console.log("record-search.js loaded");

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("record-search");
  const results = document.getElementById("record-results");
  const emptyState = document.getElementById("record-empty");
  const recordCount = document.getElementById("record-count");

  if (!input || !results) {
    console.error("record-search or record-results not found");
    return;
  }

  let debounceTimer = null;
  let activeController = null;
  let latestQuery = "";

  // =========================
  // INITIAL UI
  // =========================
  setCountText("Start typing to search for a book or thesis.");
  showEmptyState(false);

  // =========================
  // SEARCH INPUT
  // =========================
  input.addEventListener("input", () => {
    clearTimeout(debounceTimer);

    const query = input.value.trim();
    latestQuery = query;

    if (query.length === 0) {
      clearResults();
      showEmptyState(false);
      setCountText("Start typing to search for a book or thesis.");
      abortActiveRequest();
      return;
    }

    if (query.length < 2) {
      clearResults();
      showEmptyState(false);
      setCountText("Type at least 2 characters to search.");
      abortActiveRequest();
      return;
    }

    debounceTimer = setTimeout(() => {
      fetchResults(query);
    }, 280);
  });

  // Optional: Enter key = search immediately
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      clearTimeout(debounceTimer);

      const query = input.value.trim();
      latestQuery = query;

      if (query.length >= 2) {
        fetchResults(query);
      }
    }
  });

  // =========================
  // FETCH RESULTS
  // =========================
  async function fetchResults(query) {
    abortActiveRequest();

    activeController = new AbortController();
    const signal = activeController.signal;

    try {
      renderSkeletonCards(4);
      setCountText(`Searching for "${query}"...`);
      showEmptyState(false);

      const res = await fetch(`/kiosk/api/search/?q=${encodeURIComponent(query)}`, {
        method: "GET",
        headers: {
          "X-Requested-With": "XMLHttpRequest"
        },
        signal
      });

      if (!res.ok) {
        throw new Error(`Search failed with status ${res.status}`);
      }

      const data = await res.json();

      // Ignore stale response
      if (query !== latestQuery) return;

      clearResults();

      if (!data.results || data.results.length === 0) {
        setCountText(`No matches found for "${query}".`);
        showEmptyState(true);
        return;
      }

      const fragment = document.createDocumentFragment();

      data.results.forEach((item) => {
        const card = createCard(item);
        fragment.appendChild(card);
      });

      results.appendChild(fragment);
      showEmptyState(false);
      setCountText(`${data.results.length} result${data.results.length > 1 ? "s" : ""} found.`);
    } catch (err) {
      if (err.name === "AbortError") {
        return;
      }

      console.error("Search error:", err);
      clearResults();
      showEmptyState(false);
      setCountText("Something went wrong while searching.");
      results.innerHTML = `
        <div class="record-empty">
          <div class="record-empty-icon">⚠️</div>
          <h3>Search unavailable</h3>
          <p>Please try again in a moment.</p>
        </div>
      `;
    }
  }

  // =========================
  // CREATE CARD
  // =========================
  function createCard(item) {
    const card = document.createElement("article");
    card.className = "record-card";

    const type = escapeHTML(item.type || "Item");
    const title = escapeHTML(item.title || "Untitled");
    const meta = escapeHTML(item.meta || "Unknown author");
    const normalizedType = String(item.type || "").toLowerCase();

    card.innerHTML = `
      <div class="record-card-top">
        <span class="record-type">${type}</span>
      </div>

      <div class="record-card-body">
        <h3 class="record-title">${title}</h3>
        <p class="record-meta">${meta}</p>
      </div>

      <div class="record-actions">
        <button class="record-btn" type="button">Record</button>
        <button class="save-btn" type="button">Save</button>
      </div>
    `;

    const recordBtn = card.querySelector(".record-btn");
    const saveBtn = card.querySelector(".save-btn");

    recordBtn.addEventListener("click", async () => {
      await handleAction({
        button: recordBtn,
        otherButton: saveBtn,
        type: normalizedType,
        id: item.id,
        action: "recorded",
        loadingText: "Recording...",
        successText: "Recorded"
      });
    });

    saveBtn.addEventListener("click", async () => {
      await handleAction({
        button: saveBtn,
        otherButton: recordBtn,
        type: normalizedType,
        id: item.id,
        action: "saved",
        loadingText: "Saving...",
        successText: "Saved"
      });
    });

    return card;
  }

  // =========================
  // HANDLE ACTION
  // =========================
  async function handleAction({
    button,
    otherButton,
    type,
    id,
    action,
    loadingText,
    successText
  }) {
    const originalText = button.textContent;
    const otherOriginalText = otherButton.textContent;

    try {
      setButtonsLoading(button, otherButton, loadingText);

      const res = await fetch("/kiosk/api/library-action/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
          "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify({
          content_type: type,
          content_id: id,
          action: action
        })
      });

      let data = {};
      try {
        data = await res.json();
      } catch (_) {
        data = {};
      }

      console.log("STATUS:", res.status);
      console.log("RESPONSE:", data);

      if (!res.ok) {
        throw new Error(data.error || "Request failed");
      }

      button.textContent = successText;
      button.disabled = true;
      otherButton.disabled = true;

      setTimeout(() => {
        window.location.href = "/kiosk/account/";
      }, 350);
    } catch (err) {
      console.error("Submit error:", err);
      restoreButtons(button, otherButton, originalText, otherOriginalText);
      showToast("Action failed. Please try again.");
    }
  }

  // =========================
  // UI HELPERS
  // =========================
  function clearResults() {
    results.innerHTML = "";
  }

  function showEmptyState(show) {
    if (!emptyState) return;
    emptyState.hidden = !show;
  }

  function setCountText(text) {
    if (recordCount) {
      recordCount.textContent = text;
    }
  }

  function renderSkeletonCards(count = 4) {
    clearResults();

    const fragment = document.createDocumentFragment();

    for (let i = 0; i < count; i++) {
      const skeleton = document.createElement("article");
      skeleton.className = "record-card record-card-skeleton";
      skeleton.innerHTML = `
        <div class="record-card-top">
          <span class="record-type skeleton-box" style="width: 64px; height: 28px;"></span>
        </div>

        <div class="record-card-body">
          <div class="skeleton-box" style="height: 28px; width: 85%; border-radius: 12px; margin-bottom: 12px;"></div>
          <div class="skeleton-box" style="height: 28px; width: 60%; border-radius: 12px; margin-bottom: 18px;"></div>
          <div class="skeleton-box" style="height: 18px; width: 50%; border-radius: 10px;"></div>
        </div>

        <div class="record-actions">
          <div class="skeleton-box" style="height: 48px; flex: 1; border-radius: 999px;"></div>
          <div class="skeleton-box" style="height: 48px; flex: 1; border-radius: 999px;"></div>
        </div>
      `;
      fragment.appendChild(skeleton);
    }

    results.appendChild(fragment);
  }

  function setButtonsLoading(button, otherButton, loadingText) {
    button.disabled = true;
    otherButton.disabled = true;
    button.textContent = loadingText;
  }

  function restoreButtons(button, otherButton, originalText, otherOriginalText) {
    button.disabled = false;
    otherButton.disabled = false;
    button.textContent = originalText;
    otherButton.textContent = otherOriginalText;
  }

  function abortActiveRequest() {
    if (activeController) {
      activeController.abort();
      activeController = null;
    }
  }

  function showToast(message) {
    let toast = document.querySelector(".record-toast");

    if (!toast) {
      toast = document.createElement("div");
      toast.className = "record-toast";
      document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.classList.add("show");

    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.classList.remove("show");
    }, 2400);
  }

  function escapeHTML(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  // =========================
  // CSRF HELPER
  // =========================
  function getCSRFToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }

    return "";
  }
});