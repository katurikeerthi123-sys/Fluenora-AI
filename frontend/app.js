/**
 * Fluenora AI ✨ - Frontend Application Controller
 * Handles real-time API communication, UI state, tabs, and analytics.
 * Auth-gated: login wall shown until a valid JWT is present.
 */

const API_BASE = "";
const CLASS_COLORS = {
  CORRECT: "#10b981",
  TENSE_ERROR: "#ef4444",
  SVA_ERROR: "#f97316",
  ARTICLE_ERROR: "#eab308",
  PREPOSITION_ERROR: "#3b82f6",
  SPELLING_ERROR: "#a855f7",
  STRUCTURE_ERROR: "#ec4899"
};

// Will be set after login/token verification
let CURRENT_USER_ID = "default_user";
let CURRENT_USERNAME = "";

// ─────────────────────────────────────────────────────────────
// Login-Wall Helpers (called by inline onclick in index.html)
// ─────────────────────────────────────────────────────────────
window.lwShowTab = function(tab) {
  document.getElementById("lw-signin-form").style.display   = tab === "signin"   ? "" : "none";
  document.getElementById("lw-register-form").style.display = tab === "register" ? "" : "none";
  document.getElementById("lw-tab-signin").classList.toggle("active",   tab === "signin");
  document.getElementById("lw-tab-register").classList.toggle("active", tab === "register");
  lwClearMessages();
};

window.lwToggleEye = function(inputId, btn) {
  const el = document.getElementById(inputId);
  if (!el) return;
  el.type = el.type === "password" ? "text" : "password";
  btn.textContent = el.type === "password" ? "👁" : "🙈";
};

/** Safely convert any API error (string | array | object) to a readable message. */
function lwParseError(detail, fallback) {
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    // Pydantic validation errors: [{loc:[...], msg:"...", type:"..."}, ...]
    return detail.map(e => {
      const field = e.loc ? e.loc.slice(-1)[0] : "";
      return field ? `${field}: ${e.msg}` : e.msg;
    }).join(" · ");
  }
  if (typeof detail === "object" && detail.msg) return detail.msg;
  return fallback;
}

function lwShowError(msg) {
  const el = document.getElementById("lw-error");
  el.textContent = msg; el.style.display = "block";
  document.getElementById("lw-success").style.display = "none";
}
function lwShowSuccess(msg) {
  const el = document.getElementById("lw-success");
  el.textContent = msg; el.style.display = "block";
  document.getElementById("lw-error").style.display = "none";
}
function lwClearMessages() {
  document.getElementById("lw-error").style.display = "none";
  document.getElementById("lw-success").style.display = "none";
}

window.lwSignIn = async function() {
  const username = document.getElementById("lw-si-username").value.trim();
  const password = document.getElementById("lw-si-password").value;
  if (!username || !password) { lwShowError("Please enter username and password."); return; }

  const btn = document.getElementById("lw-signin-btn");
  btn.disabled = true; btn.textContent = "Signing in...";
  lwClearMessages();

  try {
    const res = await fetch("/api/academy/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username_or_email: username, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(lwParseError(data.detail, "Login failed."));
    localStorage.setItem("academy_token", data.access_token);
    lwOnAuthenticated(data.user || { username, full_name: username });
  } catch (err) {
    lwShowError(err.message);
  } finally {
    btn.disabled = false; btn.textContent = "Sign In →";
  }
};

window.lwRegister = async function() {
  const full_name = document.getElementById("lw-reg-fullname").value.trim();
  const username  = document.getElementById("lw-reg-username").value.trim();
  const email     = document.getElementById("lw-reg-email").value.trim();
  const password  = document.getElementById("lw-reg-password").value;

  if (!full_name || !username || !email || !password) {
    lwShowError("All fields are required."); return;
  }
  if (password.length < 6) { lwShowError("Password must be at least 6 characters."); return; }

  const btn = document.getElementById("lw-register-btn");
  btn.disabled = true; btn.textContent = "Creating account...";
  lwClearMessages();

  try {
    const res = await fetch("/api/academy/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_name, username, email, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(lwParseError(data.detail, "Registration failed."));
    lwShowSuccess("Account created! Signing you in...");
    // Auto-login after register
    await new Promise(r => setTimeout(r, 700));
    const lr = await fetch("/api/academy/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username_or_email: username, password })
    });
    const ld = await lr.json();
    if (!lr.ok) throw new Error(lwParseError(ld.detail, "Auto-login failed."));
    localStorage.setItem("academy_token", ld.access_token);
    lwOnAuthenticated(ld.user || { username, full_name });
  } catch (err) {
    lwShowError(err.message);
  } finally {
    btn.disabled = false; btn.textContent = "Create Account →";
  }
};

window.lwLogout = function() {
  localStorage.removeItem("academy_token");
  location.reload();
};

function lwOnAuthenticated(user) {
  CURRENT_USERNAME = user.full_name || user.username || "Learner";
  CURRENT_USER_ID  = user.username || "default_user";

  // Update header name
  const nameEl = document.getElementById("header-username");
  if (nameEl) nameEl.textContent = CURRENT_USERNAME;

  // Hide login wall, reveal app
  const wall = document.getElementById("login-wall");
  if (wall) wall.style.display = "none";
  document.body.classList.remove("auth-pending");

  // Init app modules if not already initialised
  if (!window._appInitialised) {
    window._appInitialised = true;
    initTabs();
    initAnalyzer();
    initPractice();
    initProgress();
    checkSystemHealth();
  }
}

// ─────────────────────────────────────────────────────────────
// Boot: verify token, show wall or enter app
// ─────────────────────────────────────────────────────────────
async function lwBoot() {
  const token = localStorage.getItem("academy_token");
  if (!token) return; // stay on login wall

  try {
    const res = await fetch("/api/academy/auth/me", {
      headers: { "Authorization": "Bearer " + token }
    });
    if (!res.ok) { localStorage.removeItem("academy_token"); return; }
    const user = await res.json();
    lwOnAuthenticated(user);
  } catch (e) {
    localStorage.removeItem("academy_token");
  }
}

// ─────────────────────────────────────────────────────────────
// Initialization & Tab Navigation
// ─────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  // Add Enter-key support for login/register forms
  document.getElementById("lw-si-password")?.addEventListener("keydown", e => {
    if (e.key === "Enter") window.lwSignIn();
  });
  document.getElementById("lw-si-username")?.addEventListener("keydown", e => {
    if (e.key === "Enter") window.lwSignIn();
  });
  document.getElementById("lw-reg-password")?.addEventListener("keydown", e => {
    if (e.key === "Enter") window.lwRegister();
  });

  lwBoot();
});

function initTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const targetId = tab.getAttribute("data-tab");
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add("active");
      }

      // Auto-refresh data when tabs become active
      if (targetId === "tab-practice") {
        loadDailyQuestions();
        updateWeaknessFocusBanner();
      } else if (targetId === "tab-progress") {
        loadUserProgress();
      }
    });
  });
}

// -------------------------------------------------------------
// System Health Check
// -------------------------------------------------------------
async function checkSystemHealth() {
  const dot = document.getElementById("system-status-dot");
  const text = document.getElementById("system-status-text");

  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      const data = await res.json();
      if (data.model_status === "ready") {
        dot.className = "status-dot ready";
        text.textContent = "Bi-LSTM Model Ready (84.70%)";
      } else {
        dot.className = "status-dot degraded";
        text.textContent = `Model ${data.model_status}`;
      }
    } else {
      dot.className = "status-dot degraded";
      text.textContent = "Service Degraded";
    }
  } catch (err) {
    dot.className = "status-dot degraded";
    text.textContent = "Offline / Connecting...";
  }
}

// -------------------------------------------------------------
// Tab 1: Interactive Analyzer
// -------------------------------------------------------------
function initAnalyzer() {
  const input = document.getElementById("analyzer-input");
  const charCount = document.getElementById("char-count");
  const btnAnalyze = document.getElementById("btn-run-analyzer");
  const btnClear = document.getElementById("btn-clear-analyzer");
  const spinner = document.getElementById("analyzer-spinner");
  const errorAlert = document.getElementById("analyzer-error-alert");
  const resultsContainer = document.getElementById("analyzer-results");

  // Sample Chips
  document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const sample = chip.getAttribute("data-sample");
      input.value = sample;
      input.dispatchEvent(new Event("input"));
      input.focus();
    });
  });

  // Character Counter
  input.addEventListener("input", () => {
    const len = input.value.length;
    charCount.textContent = `${len} / 1000 characters`;
    if (len > 1000) {
      charCount.style.color = "#ef4444";
    } else {
      charCount.style.color = "var(--text-dim)";
    }
  });

  // Clear button
  btnClear.addEventListener("click", () => {
    input.value = "";
    input.dispatchEvent(new Event("input"));
    resultsContainer.classList.add("hidden");
    errorAlert.classList.add("hidden");
    input.focus();
  });

  // Speech-to-Text Microphone button
  const btnMic = document.getElementById("btn-mic-analyzer");
  if (btnMic) {
    btnMic.addEventListener("click", () => toggleSpeech(input, btnMic));
  }

  // Analyze button
  btnAnalyze.addEventListener("click", async () => {
    const text = input.value.trim();
    errorAlert.classList.add("hidden");
    resultsContainer.classList.add("hidden");

    if (!text) {
      showAnalyzerError("Please enter a sentence or answer before analyzing.");
      input.focus();
      return;
    }

    if (text.length > 1000) {
      showAnalyzerError("Input text exceeds the maximum allowed limit of 1,000 characters.");
      return;
    }

    // Set loading state
    btnAnalyze.disabled = true;
    spinner.classList.remove("hidden");

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          user_id: CURRENT_USER_ID
        })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Analysis request failed.");
      }

      renderAnalyzerResults(data);
    } catch (err) {
      showAnalyzerError(err.message || "Failed to contact analysis server.");
    } finally {
      btnAnalyze.disabled = false;
      spinner.classList.add("hidden");
    }
  });
}

function showAnalyzerError(msg) {
  const alert = document.getElementById("analyzer-error-alert");
  alert.textContent = msg;
  alert.classList.remove("hidden");
}

function renderAnalyzerResults(data) {
  const resultsContainer = document.getElementById("analyzer-results");
  const badge = document.getElementById("res-category-badge");
  const confidencePill = document.getElementById("res-confidence-pill");
  const top3Container = document.getElementById("res-top3-bars");
  const providerTag = document.getElementById("res-provider-tag");
  const correctedText = document.getElementById("res-corrected-text");
  const explanationText = document.getElementById("res-explanation-text");
  const disclaimerText = document.getElementById("res-disclaimer-text");

  // Model Prediction Badge
  const cat = data.label_name;
  badge.textContent = cat;
  badge.className = `category-badge category-${cat}`;

  const pct = Math.round(data.confidence * 1000) / 10;
  confidencePill.textContent = `${pct}% confidence`;

  // Top-3 Bars
  top3Container.innerHTML = "";
  if (data.top3 && Array.isArray(data.top3)) {
    data.top3.forEach(item => {
      const barItem = document.createElement("div");
      barItem.className = "dist-bar-item";
      const itemPct = Math.round(item.confidence * 1000) / 10;
      const color = CLASS_COLORS[item.label] || "#8b5cf6";

      barItem.innerHTML = `
        <div class="dist-bar-labels">
          <span class="dist-bar-name">${item.label}</span>
          <span class="dist-bar-pct">${itemPct}%</span>
        </div>
        <div class="dist-bar-track">
          <div class="dist-bar-fill" style="width: ${itemPct}%; background: ${color};"></div>
        </div>
      `;
      top3Container.appendChild(barItem);
    });
  }

  // Grammar Rule & Example additions
  const ruleEl = document.getElementById("res-grammar-rule");
  const exampleEl = document.getElementById("res-grammar-example");
  if (ruleEl) {
    ruleEl.textContent = data.grammar_rule || "Adheres to standard English grammar conventions.";
  }
  if (exampleEl) {
    exampleEl.textContent = data.example || data.correction;
  }

  // Dedicated Sentence Correction
  if (data.correction) {
    correctedText.textContent = data.correction;
  } else {
    correctedText.innerHTML = `<em>${data.sentence}</em> <span class="badge badge-outline ml-2">No correction generated</span>`;
  }

  explanationText.textContent = data.explanation || "No explanation available.";

  // Provider Tag
  const provider = data.correction_provider || "rule_based";
  if (provider === "corpus_match") {
    providerTag.textContent = "Verified Corpus Match";
    providerTag.className = "tag-pill tag-corrector";
  } else if (provider === "rule_based") {
    providerTag.textContent = "L1 Rule Transformation";
    providerTag.className = "tag-pill tag-corrector";
  } else if (provider === "none" || data.correction_status === "unavailable") {
    providerTag.textContent = "Provider Unavailable";
    providerTag.className = "tag-pill badge-warning";
  } else {
    providerTag.textContent = provider;
  }

  // Disclaimer
  if (data.disclaimer) {
    disclaimerText.textContent = data.disclaimer;
  }

  resultsContainer.classList.remove("hidden");
  resultsContainer.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// -------------------------------------------------------------
// Tab 2: Daily Practice & Personalized Learning
// -------------------------------------------------------------
function initPractice() {
  document.getElementById("btn-refresh-daily").addEventListener("click", loadDailyQuestions);
  document.getElementById("btn-fetch-personalized").addEventListener("click", loadPersonalizedQuestion);

  const btnMicPersonalized = document.getElementById("btn-mic-personalized");
  if (btnMicPersonalized) {
    btnMicPersonalized.addEventListener("click", () => {
      const recInput = document.getElementById("rec-answer-input");
      toggleSpeech(recInput, btnMicPersonalized);
    });
  }

  document.getElementById("btn-submit-personalized").addEventListener("click", async () => {
    const input = document.getElementById("rec-answer-input");
    const qCard = document.getElementById("personalized-question-card");
    const qId = qCard.getAttribute("data-qid");
    const feedback = document.getElementById("rec-feedback-area");

    const text = input.value.trim();
    if (!text) {
      alert("Please enter your answer first.");
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          user_id: CURRENT_USER_ID,
          question_id: qId ? parseInt(qId, 10) : null
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);

      const isCorrectSentence = (data.label_name === "CORRECT" || data.is_correct);
      const correctionDisplay = isCorrectSentence
        ? `<span style="color:#6ee7b7; font-weight:600;">No grammatical error found. Your sentence is clear and natural!</span>`
        : `<span style="color:#a7f3d0; font-weight:600;">${data.correction || data.sentence}</span>`;

      feedback.innerHTML = `
        <div class="feedback-result" style="display:flex; flex-direction:column; gap:0.5rem; padding:1rem; border-radius:10px; background:rgba(15,23,42,0.6); border:1px solid rgba(255,255,255,0.08);">
          <div style="font-size:0.88rem; color:#94a3b8;">
            <strong>1. Original Sentence:</strong> <span style="color:#f1f5f9;">"${data.sentence}"</span>
          </div>
          <div style="display:flex; align-items:center; gap:0.6rem;">
            <strong>2. Diagnosis:</strong> 
            <span class="category-badge category-${data.label_name}">${data.label_name}</span>
            <span class="confidence-pill">${Math.round(data.confidence * 100)}%</span>
          </div>
          <div style="font-size:0.92rem;">
            <strong>3. Corrected Sentence:</strong> ${correctionDisplay}
          </div>
          <div style="font-size:0.86rem; color:#cbd5e1;">
            <strong>4. Explanation:</strong> ${data.explanation}
          </div>
          <div style="font-size:0.84rem; color:#cbd5e1; background:rgba(255,255,255,0.04); padding:6px 10px; border-radius:6px; border-left:3px solid #8b5cf6;">
            <strong>5. Grammar Rule:</strong> ${data.grammar_rule || "Adheres to standard English grammar conventions."}
          </div>
          <div style="font-size:0.84rem; color:#93c5fd; font-style:italic;">
            <strong>6. Additional Example:</strong> "${data.example || data.correction}"
          </div>
        </div>
      `;
      feedback.classList.remove("hidden");
      loadUserProgress();
    } catch (e) {
      alert("Submission error: " + e.message);
    }
  });
}

async function loadDailyQuestions() {
  const container = document.getElementById("daily-questions-list");
  container.innerHTML = `<div class="loading-state">Fetching today's practice challenges...</div>`;

  try {
    const res = await fetch(`${API_BASE}/api/questions/daily?limit=5`);
    if (!res.ok) throw new Error("Failed to load daily questions");
    const questions = await res.json();

    if (!questions || questions.length === 0) {
      container.innerHTML = `<p class="empty-state">No daily questions available.</p>`;
      return;
    }

    container.innerHTML = "";
    questions.forEach((q, idx) => {
      const card = document.createElement("div");
      card.className = "question-card";
      card.innerHTML = `
        <div class="q-meta-row">
          <span class="badge badge-outline">${q.difficulty || "Beginner"}</span>
          <span class="badge badge-purple">${q.category_target}</span>
        </div>
        <h4 class="q-prompt-title">Question ${idx + 1} of 5: ${q.prompt}</h4>
        <p class="q-context-desc">${q.context || ""}</p>
        
        <div class="q-submission-box">
          <textarea class="text-input" rows="2" placeholder="Write or speak your response here..." id="daily-input-${q.id}"></textarea>
          <div class="d-flex justify-between align-center mt-2">
            <button type="button" class="btn btn-secondary btn-sm" onclick="toggleSpeech('daily-input-${q.id}', this)" title="Speak via Microphone">🎤 Speak</button>
            <button class="btn btn-primary btn-sm" onclick="submitDailyAnswer(${q.id})">Submit Answer ✨</button>
          </div>
          <div id="daily-feedback-${q.id}" class="feedback-area hidden"></div>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

// Global scope for onclick
window.submitDailyAnswer = async function(questionId) {
  const input = document.getElementById(`daily-input-${questionId}`);
  const feedback = document.getElementById(`daily-feedback-${questionId}`);
  const text = input.value.trim();

  if (!text) {
    alert("Please write an answer before submitting.");
    return;
  }

  feedback.classList.remove("hidden");
  feedback.innerHTML = `<em>Evaluating grammar with Bi-LSTM...</em>`;

  try {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: text,
        user_id: CURRENT_USER_ID,
        question_id: questionId
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail);

    const isCorrectSentence = (data.label_name === "CORRECT" || data.is_correct);
    const correctionDisplay = isCorrectSentence
      ? `<span style="color:#6ee7b7; font-weight:600;">No grammatical error found. Your sentence is clear and natural!</span>`
      : `<span style="color:#a7f3d0; font-weight:600;">${data.correction || data.sentence}</span>`;

    feedback.innerHTML = `
      <div class="feedback-result" style="display:flex; flex-direction:column; gap:0.5rem; padding:1rem; border-radius:10px; background:rgba(15,23,42,0.6); border:1px solid rgba(255,255,255,0.08);">
        <div style="font-size:0.88rem; color:#94a3b8;">
          <strong>1. Original Sentence:</strong> <span style="color:#f1f5f9;">"${data.sentence}"</span>
        </div>
        <div style="display:flex; align-items:center; gap:0.6rem;">
          <strong>2. Diagnosis:</strong> 
          <span class="category-badge category-${data.label_name}">${data.label_name}</span>
          <span class="confidence-pill">${Math.round(data.confidence * 100)}%</span>
        </div>
        <div style="font-size:0.92rem;">
          <strong>3. Corrected Sentence:</strong> ${correctionDisplay}
        </div>
        <div style="font-size:0.86rem; color:#cbd5e1;">
          <strong>4. Explanation:</strong> ${data.explanation}
        </div>
        <div style="font-size:0.84rem; color:#cbd5e1; background:rgba(255,255,255,0.04); padding:6px 10px; border-radius:6px; border-left:3px solid #8b5cf6;">
          <strong>5. Grammar Rule:</strong> ${data.grammar_rule || "Adheres to standard English grammar conventions."}
        </div>
        <div style="font-size:0.84rem; color:#93c5fd; font-style:italic;">
          <strong>6. Additional Example:</strong> "${data.example || data.correction}"
        </div>
      </div>
    `;

    loadUserProgress();
    updateWeaknessFocusBanner();
  } catch (e) {
    feedback.innerHTML = `<span class="text-accent">Error: ${e.message}</span>`;
  }
};

async function updateWeaknessFocusBanner() {
  try {
    const res = await fetch(`${API_BASE}/api/user/${CURRENT_USER_ID}/progress`);
    if (!res.ok) return;
    const data = await res.json();
    const weaknessEl = document.getElementById("rec-weakness-name");
    weaknessEl.textContent = data.primary_weakness || "None detected yet";
  } catch (e) {}
}

async function loadPersonalizedQuestion() {
  const btn = document.getElementById("btn-fetch-personalized");
  const card = document.getElementById("personalized-question-card");
  const reasonText = document.getElementById("rec-reason");

  btn.disabled = true;
  btn.textContent = "Selecting Best Practice Prompt...";

  try {
    const res = await fetch(`${API_BASE}/api/questions/next?user_id=${CURRENT_USER_ID}`);
    if (!res.ok) throw new Error("Failed to fetch next question");
    const q = await res.json();

    card.setAttribute("data-qid", q.id);
    document.getElementById("rec-difficulty").textContent = q.difficulty || "Adaptive";
    document.getElementById("rec-category").textContent = q.category_target || "All";
    document.getElementById("rec-prompt").textContent = q.prompt;
    document.getElementById("rec-context").textContent = q.context || "";
    document.getElementById("rec-answer-input").value = "";
    document.getElementById("rec-feedback-area").classList.add("hidden");

    reasonText.textContent = q.recommendation_reason || "Selected based on your weakness profile.";
    card.classList.remove("hidden");
  } catch (err) {
    alert("Could not load personalized prompt: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Get Personalized Question Target 🎯";
  }
}

// -------------------------------------------------------------
// Tab 3: Weakness Tracker & Progress
// -------------------------------------------------------------
function initProgress() {
  document.getElementById("btn-refresh-history").addEventListener("click", loadUserProgress);
}

async function loadUserProgress() {
  try {
    const res = await fetch(`${API_BASE}/api/user/${CURRENT_USER_ID}/progress`);
    if (!res.ok) throw new Error("Failed to load progress data");
    const data = await res.json();

    // Stats Row
    document.getElementById("stat-total-submissions").textContent = data.total_submissions || 0;
    document.getElementById("stat-accuracy").textContent = `${data.accuracy_percentage || 0}%`;
    document.getElementById("stat-streak").textContent = `${data.current_streak || 0} Day${data.current_streak === 1 ? '' : 's'}`;
    document.getElementById("stat-primary-weakness").textContent = data.primary_weakness || "None";

    // Category Breakdown Bars
    const barsContainer = document.getElementById("category-weakness-bars");
    const breakdown = data.category_breakdown || {};
    const categories = Object.keys(breakdown);

    if (categories.length === 0) {
      barsContainer.innerHTML = `<p class="empty-state">No error frequency data recorded yet. Submit sentences in Analyzer or Practice!</p>`;
    } else {
      barsContainer.innerHTML = "";
      // Calculate max error count for relative bar scaling
      let maxErr = 1;
      categories.forEach(c => {
        if (breakdown[c].error_count > maxErr) maxErr = breakdown[c].error_count;
      });

      categories.forEach(cat => {
        const item = breakdown[cat];
        const barItem = document.createElement("div");
        barItem.className = "cat-bar-item";
        const widthPct = Math.min(100, Math.round((item.error_count / maxErr) * 100));
        const color = CLASS_COLORS[cat] || "#8b5cf6";

        barItem.innerHTML = `
          <div class="cat-bar-header">
            <span>${cat}</span>
            <span>${item.error_count} error${item.error_count === 1 ? '' : 's'} (${item.total_count} total tests)</span>
          </div>
          <div class="cat-bar-track">
            <div class="cat-bar-fill" style="width: ${widthPct}%; background: ${color};"></div>
          </div>
        `;
        barsContainer.appendChild(barItem);
      });
    }

    // Submissions History Table
    const tableBody = document.getElementById("submissions-table-body");
    const recents = data.recent_submissions || [];

    if (recents.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="5" class="text-center">No submissions recorded yet.</td></tr>`;
    } else {
      tableBody.innerHTML = "";
      recents.forEach(sub => {
        const tr = document.createElement("tr");
        const dateStr = sub.submitted_at ? new Date(sub.submitted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Just now";
        const confPct = Math.round(sub.confidence * 100);

        tr.innerHTML = `
          <td><small class="text-muted">${dateStr}</small></td>
          <td><strong>${escapeHtml(sub.user_answer)}</strong></td>
          <td><span class="category-badge category-${sub.predicted_label_name}">${sub.predicted_label_name}</span></td>
          <td><code>${confPct}%</code></td>
          <td>
            <div style="font-weight: 600; color: #a7f3d0;">${escapeHtml(sub.correction || sub.user_answer)}</div>
            <div class="text-muted"><small>${escapeHtml(sub.explanation || "")}</small></div>
          </td>
        `;
        tableBody.appendChild(tr);
      });
    }

  } catch (err) {
    console.warn("Could not load user progress:", err);
  }
}


function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// -------------------------------------------------------------
// Web Speech API Integration (Speech-to-Text Input)
// -------------------------------------------------------------
let activeRecognition = null;
let activeMicBtn = null;

function toggleSpeech(targetInputOrId, btnElement) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.");
    return;
  }

  const targetInput = typeof targetInputOrId === "string" ? document.getElementById(targetInputOrId) : targetInputOrId;
  if (!targetInput) return;

  if (activeRecognition) {
    activeRecognition.stop();
    if (activeMicBtn) {
      activeMicBtn.classList.remove("btn-mic-recording");
      activeMicBtn.innerHTML = "🎤 Speak";
    }
    if (activeMicBtn === btnElement) {
      activeRecognition = null;
      activeMicBtn = null;
      return;
    }
  }

  const recognition = new SpeechRecognition();
  recognition.lang = "en-IN"; // English (India)
  recognition.interimResults = true;
  recognition.continuous = false;

  let originalValue = targetInput.value;
  if (originalValue && !originalValue.endsWith(" ")) {
    originalValue += " ";
  }

  btnElement.classList.add("btn-mic-recording");
  btnElement.innerHTML = "🔴 Listening...";
  activeRecognition = recognition;
  activeMicBtn = btnElement;

  recognition.onresult = (event) => {
    let transcript = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }
    targetInput.value = originalValue + transcript;
    targetInput.dispatchEvent(new Event("input"));
  };

  recognition.onerror = (event) => {
    console.warn("Speech recognition error:", event.error);
    btnElement.classList.remove("btn-mic-recording");
    btnElement.innerHTML = "🎤 Speak";
    activeRecognition = null;
    activeMicBtn = null;
  };

  recognition.onend = () => {
    btnElement.classList.remove("btn-mic-recording");
    btnElement.innerHTML = "🎤 Speak";
    activeRecognition = null;
    activeMicBtn = null;
  };

  try {
    recognition.start();
  } catch (e) {
    console.error("Speech start error:", e);
    btnElement.classList.remove("btn-mic-recording");
    btnElement.innerHTML = "🎤 Speak";
    activeRecognition = null;
    activeMicBtn = null;
  }
}
window.toggleSpeech = toggleSpeech;

