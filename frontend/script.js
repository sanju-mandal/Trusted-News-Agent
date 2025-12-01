// ==== CONFIG ====
const API_BASE_URL = "http://127.0.0.1:8000"; // change if backend different

// ==== DOM ELEMENTS ====
const tabButtons = document.querySelectorAll(".tab-btn");
const views = document.querySelectorAll(".view");

const userIdInput = document.getElementById("userId");
const userBarStatus = document.getElementById("userBarStatus");

const topicInput = document.getElementById("topicInput");
const searchBtn = document.getElementById("searchBtn");
const searchStatus = document.getElementById("searchStatus");
const searchResultSection = document.getElementById("searchResult");
const summaryText = document.getElementById("summaryText");
const articlesList = document.getElementById("articlesList");

const userNewsTitle = document.getElementById("userNewsTitle");
const userNewsUrl = document.getElementById("userNewsUrl");
const userNewsText = document.getElementById("userNewsText");
const checkNewsBtn = document.getElementById("checkNewsBtn");
const checkStatus = document.getElementById("checkStatus");
const checkResultSection = document.getElementById("checkResult");
const verdictLabel = document.getElementById("verdictLabel");
const verdictConfidence = document.getElementById("verdictConfidence");
const verdictReasons = document.getElementById("verdictReasons");
const checkSummaryText = document.getElementById("checkSummaryText");

const createUserBtn = document.getElementById("createUserBtn");
const loadHistoryBtn = document.getElementById("loadHistoryBtn");
const historyList = document.getElementById("historyList");

// ==== TAB HANDLING ====
tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const targetId = btn.dataset.target;

    tabButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");

    views.forEach((view) => {
      if (view.id === targetId) {
        view.classList.add("active");
      } else {
        view.classList.remove("active");
      }
    });

    if (targetId === "view-history") {
      loadHistory();
    }
  });
});

// ==== HELPERS ====
function getUserId() {
  const val = parseInt(userIdInput.value, 10);
  return Number.isNaN(val) ? null : val;
}

function setStatus(el, msg, isError = false) {
  el.textContent = msg || "";
  el.style.color = isError ? "#b91c1c" : "#6b7280";
}

function labelBadgeClass(label) {
  if (label === "real") return "badge badge-real";
  if (label === "fake") return "badge badge-fake";
  return "badge badge-uncertain";
}

// ==== SEARCH TRUSTED NEWS FLOW ====
searchBtn.addEventListener("click", async () => {
  const query = topicInput.value.trim();
  const userId = getUserId();

  if (!query) {
    setStatus(searchStatus, "Please enter a topic first.", true);
    return;
  }

  setStatus(searchStatus, "Fetching and verifying news...");
  searchResultSection.classList.add("hidden");

  try {
    const res = await fetch(`${API_BASE_URL}/api/news/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        query: query,
      }),
    });

    if (!res.ok) throw new Error("Server error");

    const data = await res.json();

    summaryText.textContent = data.summary || "No summary available.";
    articlesList.innerHTML = "";

    (data.articles || []).forEach((art) => {
      const card = document.createElement("div");
      card.className = "result-card";

      const badge = document.createElement("span");
      badge.className = labelBadgeClass(art.label);
      badge.textContent = art.label.toUpperCase();
      card.appendChild(badge);

      const title = document.createElement("h4");
      title.textContent = art.title || "Untitled article";
      card.appendChild(title);

      if (art.url) {
        const link = document.createElement("a");
        link.href = art.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = art.source_domain || art.url;
        card.appendChild(link);
      }

      const conf = document.createElement("p");
      conf.innerHTML = `<strong>Confidence:</strong> ${(art.confidence * 100).toFixed(
        1
      )}%`;
      card.appendChild(conf);

      articlesList.appendChild(card);
    });

    searchResultSection.classList.remove("hidden");
    setStatus(
      searchStatus,
      data.articles && data.articles.length
        ? "Done. Showing trusted, summarized news."
        : "No high-confidence trusted news found for this topic."
    );
  } catch (err) {
    console.error(err);
    setStatus(searchStatus, "Something went wrong. Please try again.", true);
  }
});

// ==== VERIFY USER NEWS FLOW ====
checkNewsBtn.addEventListener("click", async () => {
  const title = userNewsTitle.value.trim();
  const url = userNewsUrl.value.trim();
  const text = userNewsText.value.trim();
  const userId = getUserId();

  if (!title && !url && !text) {
    setStatus(checkStatus, "Provide at least a URL, headline, or text.", true);
    return;
  }

  setStatus(checkStatus, "Checking realism...");
  checkResultSection.classList.add("hidden");

  try {
    const res = await fetch(`${API_BASE_URL}/api/news/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        title: title || null,
        url: url || null,
        text: text || null,
      }),
    });

    if (!res.ok) throw new Error("Server error");
    const data = await res.json();

    const verdict = data.verdict || {};
    const label = verdict.label || "uncertain";

    verdictLabel.textContent = label.toUpperCase();
    verdictLabel.className = labelBadgeClass(label);

    verdictConfidence.textContent = verdict.confidence
      ? `${(verdict.confidence * 100).toFixed(1)}%`
      : "N/A";

    verdictReasons.innerHTML = "";
    (verdict.reasons || []).forEach((r) => {
      const li = document.createElement("li");
      li.textContent = r;
      verdictReasons.appendChild(li);
    });

    checkSummaryText.textContent =
      data.summary || "No summary generated for this news.";

    checkResultSection.classList.remove("hidden");
    setStatus(checkStatus, "Verdict generated.");
  } catch (err) {
    console.error(err);
    setStatus(checkStatus, "Something went wrong. Please try again.", true);
  }
});

// ==== HISTORY FLOW ====
loadHistoryBtn.addEventListener("click", () => {
  loadHistory();
});

async function loadHistory() {
  const userId = getUserId();
  if (!userId) {
    setStatus(userBarStatus, "Enter a valid User ID to load history.", true);
    return;
  }

  setStatus(userBarStatus, "Loading history...");
  historyList.innerHTML = "";

  try {
    const res = await fetch(`${API_BASE_URL}/api/history/${userId}`);
    if (!res.ok) throw new Error("Server error");

    const data = await res.json();

    if (!data.length) {
      historyList.innerHTML =
        '<p class="status-text">No history yet for this user.</p>';
      setStatus(userBarStatus, "No history found.");
      return;
    }

    data.forEach((item) => {
      const card = document.createElement("div");
      card.className = "result-card";

      const badge = document.createElement("span");
      badge.className = labelBadgeClass(item.label);
      badge.textContent = (item.label || "unknown").toUpperCase();
      card.appendChild(badge);

      const title = document.createElement("h4");
      title.textContent =
        item.title || item.topic || "(no title / topic stored)";
      card.appendChild(title);

      const meta = document.createElement("p");
      meta.className = "history-meta";

      let formattedDate = "";
      if (item.created_at) {
        formattedDate = new Date(item.created_at).toLocaleString("en-IN", {
          timeZone: "Asia/Kolkata",
          hour12: true,
          day: "2-digit",
          month: "short",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit"
        });
      }

      meta.textContent = `${item.type} • ${formattedDate}`;
      card.appendChild(meta);


      if (item.url) {
        const link = document.createElement("a");
        link.href = item.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = item.url;
        card.appendChild(link);
      }

      if (item.summary) {
        const summary = document.createElement("p");
        summary.textContent = item.summary.slice(0, 220) + (item.summary.length > 220 ? "..." : "");
        card.appendChild(summary);
      }

      // --- Delete Button ---
      const delBtn = document.createElement("button");
      delBtn.textContent = "Delete";
      delBtn.className = "secondary-btn";
      delBtn.style.marginTop = "8px";

      delBtn.addEventListener("click", async () => {
        if (!confirm("Delete this history item?")) return;

        try {
          const res = await fetch(`${API_BASE_URL}/api/history/delete/${item.id}`, {
            method: "DELETE",
          });

          const data = await res.json();

          if (data.status === "success") {
            card.remove(); // remove from UI
          } else {
            alert("Delete failed: " + data.message);
          }
        } catch (err) {
          console.error(err);
          alert("Error deleting item.");
        }
      });

      card.appendChild(delBtn);



      historyList.appendChild(card);
    });

    setStatus(userBarStatus, "History loaded.");
  } catch (err) {
    console.error(err);
    historyList.innerHTML =
      '<p class="status-text">Could not load history.</p>';
    setStatus(userBarStatus, "Error loading history.", true);
  }
}

// ==== CREATE NEW USER ====
createUserBtn.addEventListener("click", async () => {
  const name = "User" + Date.now(); // auto-generated username

  setStatus(userBarStatus, "Creating user...");

  try {
    const res = await fetch(`${API_BASE_URL}/api/users/create?name=${encodeURIComponent(name)}`, {
      method: "POST"
    });

    if (!res.ok) throw new Error("Server error");
    const data = await res.json();

    userIdInput.value = data.user_id;

    setStatus(userBarStatus, `User created! ID = ${data.user_id}`);
  } catch (err) {
    console.error(err);
    setStatus(userBarStatus, "Error creating user.", true);
  }
});
