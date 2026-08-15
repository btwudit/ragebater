/* ============================================================
   RAGEBATER — APP.JS
   ============================================================ */

// ============================================================
// 1. DOM ELEMENTS
// ============================================================

const dom = {
  // Header
  chaosFill: document.getElementById("chaos-fill"),
  chaosValue: document.getElementById("chaos-value"),
  chaosBar: document.getElementById("chaos-bar"),
  scoreUser: document.getElementById("score-user"),
  scoreRagebater: document.getElementById("score-ragebater"),

  // Chat
  conversationFeed: document.getElementById("conversation-feed"),
  typingIndicator: document.getElementById("typing-indicator"),

  // Character
  characterWrapper: document.getElementById("character-wrapper"),
  characterFace: document.getElementById("character-face"),
  handLeft: document.getElementById("character-hand-left"),
  handRight: document.getElementById("character-hand-right"),

  // Speech
  speechBubble: document.getElementById("speech-bubble"),
  speechBubbleText: document.getElementById("speech-bubble-text"),

  // Stickers
  stickerZone: document.getElementById("character-sticker-zone"),
  stickerGrid: document.getElementById("sticker-grid"),

  // Input
  textInput: document.getElementById("text-input"),
  sendBtn: document.getElementById("send-text-btn"),
  micBtn: document.getElementById("mic-btn"),
  voiceIndicator: document.getElementById("voice-note-indicator"),

  // Settings
  settingsBtn: document.getElementById("settings-btn"),
  settingsModal: document.getElementById("settings-modal"),
  settingsClose: document.getElementById("settings-modal-close"),

  // Footer
  tipText: document.getElementById("tip-text"),
};

// ============================================================
// 2. STATE
// ============================================================

const state = {
  chaosLevel: 78,
  userScore: 45,
  ragebaterScore: 85,
  isSpeaking: false,
  isRecording: false,
  currentFace: "neutral",
  currentGesture: "idle",
  conversation: [],
  isProcessing: false, // Prevent rapid-fire clicks
};

// ============================================================
// 3. CHARACTER SYSTEM
// ============================================================

/**
 * Change the character's face expression.
 * @param {string} face - The face class suffix (e.g. 'smirk', 'rage')
 */
function setFace(face) {
  const validFaces = [
    "neutral", "smirk", "rage", "laugh", "shocked",
    "annoyed", "deadpan", "evil", "confused"
  ];

  if (!validFaces.includes(face)) {
    console.warn(`Unknown face: "${face}". Falling back to neutral.`);
    face = "neutral";
  }

  // Remove all existing face classes
  dom.characterFace.classList.forEach((cls) => {
    if (cls.startsWith("face--")) {
      dom.characterFace.classList.remove(cls);
    }
  });

  // Add the new face class
  dom.characterFace.classList.add(`face--${face}`);
  state.currentFace = face;
}

/**
 * Change the character's hand gesture (both hands).
 * @param {string} gesture - The gesture class suffix (e.g. 'shrug', 'clap')
 */
function setGesture(gesture) {
  const validGestures = ["idle", "shrug", "point", "facepalm", "clap", "stop"];

  if (!validGestures.includes(gesture)) {
    console.warn(`Unknown gesture: "${gesture}". Falling back to idle.`);
    gesture = "idle";
  }

  // Remove existing gesture classes from both hands
  [dom.handLeft, dom.handRight].forEach((hand) => {
    hand.classList.forEach((cls) => {
      if (cls.startsWith("hand--")) {
        hand.classList.remove(cls);
      }
    });
  });

  // Add the new gesture class to both hands
  dom.handLeft.classList.add(`hand--${gesture}`);
  dom.handRight.classList.add(`hand--${gesture}`);
  state.currentGesture = gesture;
}

// ============================================================
// 4. ANIMATION SYSTEM
// ============================================================

/**
 * Play a character animation on the wrapper element.
 * @param {string} animation - The animation type ('bounce', 'shake', 'float', 'pulse', 'none')
 */
function playCharacterAnimation(animation) {
  const validAnimations = ["bounce", "shake", "float", "pulse", "none"];

  if (!validAnimations.includes(animation)) {
    console.warn(`Unknown animation: "${animation}". Skipping.`);
    return;
  }

  if (animation === "none") {
    dom.characterWrapper.classList.remove(
      "character--bounce",
      "character--shake",
      "character--float",
      "character--pulse"
    );
    return;
  }

  // Remove any existing animation classes to restart the animation
  dom.characterWrapper.classList.remove(
    "character--bounce",
    "character--shake",
    "character--float",
    "character--pulse"
  );

  // Force a reflow to restart the CSS animation
  void dom.characterWrapper.offsetWidth;

  // Add the new animation class
  dom.characterWrapper.classList.add(`character--${animation}`);

  // Remove the class after the animation finishes (approx. 800ms)
  setTimeout(() => {
    dom.characterWrapper.classList.remove(`character--${animation}`);
  }, 800);
}


let speechTimeout = null;

/**
 * Show the speech bubble with the given text.
 * Hides automatically after 4 seconds unless a new message replaces it.
 * @param {string} text - The text to display.
 */
function showSpeech(text) {
  // Clear any existing auto-hide timer
  if (speechTimeout) {
    clearTimeout(speechTimeout);
    speechTimeout = null;
  }

  dom.speechBubbleText.textContent = text;
  dom.speechBubble.classList.remove("speech-bubble--hidden");
  dom.speechBubble.classList.add("speech-bubble--visible");

  // Auto-hide after 4 seconds
  speechTimeout = setTimeout(() => {
    hideSpeech();
  }, 4000);
}

/** Hide the speech bubble. */
function hideSpeech() {
  if (speechTimeout) {
    clearTimeout(speechTimeout);
    speechTimeout = null;
  }
  dom.speechBubble.classList.remove("speech-bubble--visible");
  dom.speechBubble.classList.add("speech-bubble--hidden");
}

// ============================================================
// 6. STICKER SYSTEM
// ============================================================

/**
 * Find a sticker by its ID, clone it, and float it on the character stage.
 * @param {string} stickerId - The data-sticker-id of the sticker to show.
 */
function showSticker(stickerId) {
  // Find the sticker button in the grid
  const stickerButton = dom.stickerGrid.querySelector(
    `[data-sticker-id="${stickerId}"]`
  );

  if (!stickerButton) {
    console.warn(`Sticker "${stickerId}" not found in the grid.`);
    return;
  }

  // Get the image inside the button
  const stickerImg = stickerButton.querySelector(".sticker-item__img");
  if (!stickerImg) {
    console.warn(`Sticker "${stickerId}" has no image element.`);
    return;
  }

  // Clone the image (not the entire button)
  const floatingSticker = stickerImg.cloneNode(true);
  floatingSticker.classList.add("floating-sticker");

  // Add entrance animation class
  floatingSticker.style.position = "absolute";
  floatingSticker.style.width = "80px";
  floatingSticker.style.aspectRatio = "1/1";
  floatingSticker.style.objectFit = "contain";
  floatingSticker.style.borderRadius = "8px";
  floatingSticker.style.zIndex = "5";
  floatingSticker.style.pointerEvents = "none";

  // Random position within the sticker zone (70% of the stage width/height)
  const randomX = 15 + Math.random() * 70; // % from left
  const randomY = 15 + Math.random() * 70; // % from top
  floatingSticker.style.left = `${randomX}%`;
  floatingSticker.style.top = `${randomY}%`;

  // Add a custom entrance + float animation via inline style for simplicity
  floatingSticker.style.animation =
    "stickerEntrance 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards, " +
    "float 3s ease-in-out 0.6s infinite alternate";

  dom.stickerZone.appendChild(floatingSticker);

  // Remove the sticker after 4 seconds
  setTimeout(() => {
    if (floatingSticker.parentNode) {
      floatingSticker.style.opacity = "0";
      floatingSticker.style.transition = "opacity 0.3s ease";
      setTimeout(() => {
        if (floatingSticker.parentNode) {
          floatingSticker.parentNode.removeChild(floatingSticker);
        }
      }, 300);
    }
  }, 4000);
}

// Add the sticker animation keyframes dynamically (we can't modify CSS, so we inject them)
(function injectStickerStyles() {
  const style = document.createElement("style");
  style.textContent = `
    @keyframes stickerEntrance {
      0% { transform: scale(0) rotate(-20deg); opacity: 0; }
      100% { transform: scale(1) rotate(0deg); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
})();

// ============================================================
// 7. CHAT SYSTEM
// ============================================================

/**
 * Add a new message to the conversation feed.
 * @param {"user"|"ragebater"} sender - Who sent the message.
 * @param {string} text - The message content.
 */
function addMessage(sender, text) {
  if (!text || text.trim() === "") return;

  // Make sure typing indicator stays at the bottom
  ensureTypingIndicatorPosition();

  const li = document.createElement("li");
  li.className = `message message--${sender}`;

  // Timestamp
  const now = new Date();
  const timeStr = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  // Meta row
  const meta = document.createElement("div");
  meta.className = "message__meta";
  const senderSpan = document.createElement("span");
  senderSpan.className = `message__sender${sender === "ragebater" ? " message__sender--ragebater" : ""}`;
  senderSpan.textContent = sender === "ragebater" ? "RageBater" : "You";
  const timeSpan = document.createElement("time");
  timeSpan.className = "message__time";
  timeSpan.textContent = timeStr;
  meta.appendChild(senderSpan);
  meta.appendChild(timeSpan);
  li.appendChild(meta);

  // Bubble
  const bubble = document.createElement("div");
  bubble.className = `message__bubble${sender === "ragebater" ? " message__bubble--ragebater" : ""}`;
  const p = document.createElement("p");
  p.className = "message__text";
  p.textContent = text;
  bubble.appendChild(p);
  li.appendChild(bubble);

  // Sticker slot (empty placeholder)
  const stickerSlot = document.createElement("div");
  stickerSlot.className = "message__sticker-slot";
  li.appendChild(stickerSlot);

  // Insert before the typing indicator
  dom.conversationFeed.insertBefore(li, dom.typingIndicator);

  // Store in state
  state.conversation.push({ sender, text, timestamp: now });

  // Auto-scroll to bottom
  scrollToBottom();
}

/**
 * Ensure the typing indicator is the last child of the feed.
 */
function ensureTypingIndicatorPosition() {
  if (dom.typingIndicator.parentNode !== dom.conversationFeed) return;
  if (dom.conversationFeed.lastChild !== dom.typingIndicator) {
    dom.conversationFeed.appendChild(dom.typingIndicator);
  }
}

/**
 * Scroll the conversation feed to the bottom.
 */
function scrollToBottom() {
  dom.conversationFeed.scrollTop = dom.conversationFeed.scrollHeight;
}

// ============================================================
// 8. TYPING SYSTEM
// ============================================================

/** Show the typing indicator (RageBater is thinking). */
function showTyping() {
  dom.typingIndicator.hidden = false;
  ensureTypingIndicatorPosition();
  scrollToBottom();
}

/** Hide the typing indicator. */
function hideTyping() {
  dom.typingIndicator.hidden = true;
}

// ============================================================
// 9. CHAOS + SCORE
// ============================================================

/**
 * Update the Chaos Level meter.
 * @param {number} level - The chaos level (0-100).
 */
function updateChaos(level) {
  // Clamp between 0 and 100
  const clamped = Math.max(0, Math.min(100, level));
  state.chaosLevel = clamped;

  dom.chaosValue.textContent = `${clamped}%`;
  dom.chaosFill.style.width = `${clamped}%`;
  dom.chaosBar.setAttribute("aria-valuenow", clamped);
}

/**
 * Update the Argument Score board.
 * @param {number} userScore - The user's score (0-100).
 * @param {number} ragebaterScore - RageBater's score (0-100).
 */
function updateScores(userScore, ragebaterScore) {
  const userClamped = Math.max(0, Math.min(100, userScore));
  const rageClamped = Math.max(0, Math.min(100, ragebaterScore));

  state.userScore = userClamped;
  state.ragebaterScore = rageClamped;

  dom.scoreUser.textContent = userClamped;
  dom.scoreRagebater.textContent = rageClamped;
}

// ============================================================
// 10. RESPONSE CONTROLLER
// ============================================================

/**
 * Execute a full RageBater response sequence from a structured response object.
 * @param {Object} response - The response object from the AI.
 */
/**
 * Execute a full RageBater response sequence from a structured
 * response received from the real backend.
 *
 * Expected backend response:
 *
 * {
 *   response: "...",
 *   face: "...",
 *   gesture: "...",
 *   animation: "...",
 *   sticker: "...",
 *   delay_ms: 700,
 *   chaos_level: 60
 * }
 *
 * @param {Object} response - Backend character response.
 */
function renderRageResponse(response) {
  if (!response || typeof response !== "object") {
    console.error("Invalid RageBater response:", response);
    return;
  }

  const responseText =
    typeof response.response === "string" && response.response.trim()
      ? response.response.trim()
      : "Interesting. Try making a stronger argument.";

  const delayMs = Number.isFinite(Number(response.delay_ms))
    ? Math.max(0, Number(response.delay_ms))
    : 700;

  // Show RageBater thinking while the response delay runs.
  showTyping();

  setTimeout(() => {
    hideTyping();

    // Character expression.
    setFace(response.face || "neutral");

    // Character gesture.
    setGesture(response.gesture || "idle");

    // Character animation.
    playCharacterAnimation(response.animation || "none");

    // Speech bubble.
    showSpeech(responseText);

    // Conversation feed.
    addMessage("ragebater", responseText);

    // Sticker.
    if (response.sticker) {
      showSticker(response.sticker);
    }

    // Chaos meter.
    if (response.chaos_level !== undefined) {
      updateChaos(response.chaos_level);
    }

    // Dynamic tip.
    updateTip();

    // Response finished.
    state.isProcessing = false;
  }, delayMs);
}

// ============================================================
// 11. TEXT INPUT
// ============================================================

/** Handle the user submitting a text message. */
async function handleTextSubmit() {
  if (state.isProcessing) return;

  const text = dom.textInput.value.trim();

  if (!text) return;

  state.isProcessing = true;

  // Clear input and hide send button.
  dom.textInput.value = "";
  dom.sendBtn.hidden = true;

  // Immediately show the user's message.
  addMessage("user", text);

  // RageBater is now processing the message.
  showTyping();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: text,
      }),
    });

    let payload;

    try {
      payload = await response.json();
    } catch (jsonError) {
      throw new Error(
        `Backend returned invalid JSON (HTTP ${response.status}).`
      );
    }

    if (!response.ok) {
      throw new Error(
        payload.error || `RageBater API request failed (${response.status}).`
      );
    }

    if (!payload.success || !payload.data) {
      throw new Error(
        "RageBater API returned an invalid response structure."
      );
    }

    const responseData = payload.data;

    // The backend now provides the complete character command.
    renderRageResponse(responseData);

  } catch (error) {
    console.error("RageBater API error:", error);

    hideTyping();

    const fallbackMessage =
      "My brain temporarily disconnected. Try that again.";

    addMessage("ragebater", fallbackMessage);
    showSpeech(fallbackMessage);

    setFace("confused");
    setGesture("idle");
    playCharacterAnimation("none");

    state.isProcessing = false;
  }
}

// ============================================================
// 12. MICROPHONE
// ============================================================

/** Toggle the microphone recording UI (simulated). */
function toggleMicrophone() {
  if (state.isRecording) {
    stopRecording();
  } else {
    startRecording();
  }
}

function startRecording() {
  state.isRecording = true;

  dom.micBtn.classList.add("mic-btn--recording");
  dom.micBtn.setAttribute("aria-pressed", "true");
  dom.voiceIndicator.hidden = false;
}

function stopRecording() {
  state.isRecording = false;
  dom.micBtn.classList.remove("mic-btn--recording");
  dom.micBtn.setAttribute("aria-pressed", "false");
  dom.voiceIndicator.hidden = true;
}

// ============================================================
// 13. SETTINGS
// ============================================================

/** Open the settings modal. */
function openSettings() {
  dom.settingsModal.hidden = false;
  dom.settingsModal.showModal();
}

/** Close the settings modal. */
function closeSettings() {
  dom.settingsModal.close();
  dom.settingsModal.hidden = true;
}

// ============================================================
// 14. MEME FILTERS
// ============================================================

/** Filter the sticker grid by category. */
function filterStickers(category) {
  const stickers = dom.stickerGrid.querySelectorAll(".sticker-item");

  stickers.forEach((sticker) => {
    const stickerCategory = sticker.getAttribute("data-category") || "all";

    if (category === "all" || stickerCategory === category) {
      sticker.style.display = "flex";
    } else {
      sticker.style.display = "none";
    }
  });
}

/** Handle clicking a category tab. */
function handleCategoryClick(event) {
  const tab = event.currentTarget;
  const category = tab.getAttribute("data-category");

  // Update active tab
  const allTabs = document.querySelectorAll(".sticker-tab");
  allTabs.forEach((t) => {
    t.classList.remove("sticker-tab--active");
    t.setAttribute("aria-pressed", "false");
  });
  tab.classList.add("sticker-tab--active");
  tab.setAttribute("aria-pressed", "true");

  // Filter the grid
  filterStickers(category);
}

// ============================================================
// 15. TIPS
// ============================================================

const TIPS = [
  "Tip: Ask, argue, challenge... I'll handle the rest. 😈",
  "Tip: Confidence is free. Logic isn't.",
  "Tip: Choose your next argument carefully.",
  "Tip: I react, I don't just answer. Keep up.",
  "Tip: Sarcasm is my native language.",
  "Tip: If you're not sure, you've already lost.",
  "Tip: Stickers > Words. Always.",
];

let tipIndex = 0;

/** Update the footer tip with a random tip from the list. */
function updateTip() {
  // Pick a random tip, but avoid repeating the last one if possible
  let newIndex;
  do {
    newIndex = Math.floor(Math.random() * TIPS.length);
  } while (TIPS.length > 1 && newIndex === tipIndex);
  tipIndex = newIndex;

  dom.tipText.innerHTML = TIPS[tipIndex];
}

// ============================================================
// 16. INITIALIZATION
// ============================================================

function init() {
  // --- DOM References already set in `dom` object ---

  // --- State Initialization ---
  updateChaos(state.chaosLevel);
  updateScores(state.userScore, state.ragebaterScore);
  setFace(state.currentFace);
  setGesture(state.currentGesture);
  hideTyping();
  dom.voiceIndicator.hidden = true;
  dom.settingsModal.hidden = true;
  updateTip();

  // --- Event Listeners ---

  // Text input: Send on Enter
  dom.textInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleTextSubmit();
    }
  });

  // Text input: Show/hide send button based on content
  dom.textInput.addEventListener("input", () => {
    const hasText = dom.textInput.value.trim().length > 0;
    dom.sendBtn.hidden = !hasText;
  });

  // Send button click
  dom.sendBtn.addEventListener("click", handleTextSubmit);

  // Microphone button
  dom.micBtn.addEventListener("click", toggleMicrophone);

  // Settings modal
  dom.settingsBtn.addEventListener("click", openSettings);
  dom.settingsClose.addEventListener("click", closeSettings);
  dom.settingsModal.addEventListener("click", (e) => {
    if (e.target === dom.settingsModal) {
      closeSettings();
    }
  });

  // Meme category tabs
  const tabs = document.querySelectorAll(".sticker-tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", handleCategoryClick);
  });

  // "Add Custom Meme" button
  const addMemeBtn = document.getElementById("add-custom-meme-btn");
  addMemeBtn.addEventListener("click", () => {
    alert("Custom meme upload will be added later.");
  });

  // --- Initial sticker filter state ---
  filterStickers("all");

  // --- Add a small welcome message ---
  // We'll add a subtle hint: the speech bubble is already showing a placeholder text,
  // but we can leave it as is.
}

// Kick off the app
init();