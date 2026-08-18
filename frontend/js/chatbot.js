/**
 * =========================================================
 * Innovate AI Hackathon - RAG AI Chatbot Client Widget
 * =========================================================
 */

(function () {
  const STORAGE_KEY = "innovate_ai_chat_history";
  const IS_OPEN_KEY = "innovate_ai_chat_is_open";

  let chatHistory = [];
  let isThinking = false;

  // Initialize Chat Widget HTML into the page
  function initWidget() {
    if (document.getElementById("ai-chat-widget-container")) return;

    const container = document.createElement("div");
    container.id = "ai-chat-widget-container";
    container.innerHTML = `
      <!-- Floating Launcher Button -->
      <button id="ai-chat-launcher" class="ai-chat-launcher" aria-label="Open AI Assistant" title="Ask Innovate AI Assistant">
        <div class="launcher-icon-wrap">
          <img src="/assets/logo.svg" alt="Innovate AI Logo" class="launcher-logo-animated" />
          <span class="launcher-badge-pulse"></span>
        </div>
        <span>Ask AI Assistant</span>
      </button>

      <!-- Chat Modal Window -->
      <div id="ai-chat-modal" class="ai-chat-modal" role="dialog" aria-modal="true" aria-labelledby="chat-title">
        <!-- Header -->
        <div class="ai-chat-header">
          <div class="chat-header-info">
            <div class="chat-avatar">
              <img src="/assets/logo.svg" alt="Innovate AI Logo" class="chat-logo-animated" />
              <span class="chat-status-dot"></span>
            </div>
            <div class="chat-title-group">
              <h3 id="chat-title">Innovate AI Assistant</h3>
              <span>⚡ Official Rulebook RAG</span>
            </div>
          </div>
          <div class="chat-header-actions">
            <button id="ai-chat-clear" class="chat-tool-btn" title="Clear Conversation" aria-label="Clear Conversation">
              <svg viewBox="0 0 24 24"><path fill="currentColor" d="M19 4h-3.5l-1-1h-5l-1 1H5v2h14M6 19a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7H6v12Z"/></svg>
            </button>
            <button id="ai-chat-close" class="chat-tool-btn" title="Close Chat" aria-label="Close Chat">
              <svg viewBox="0 0 24 24"><path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41Z"/></svg>
            </button>
          </div>
        </div>

        <!-- Message Body -->
        <div id="ai-chat-messages" class="ai-chat-messages"></div>

        <!-- Footer / Input -->
        <div class="ai-chat-footer">
          <form id="ai-chat-form" class="chat-input-form">
            <input type="text" id="ai-chat-input" class="chat-input-field" placeholder="Ask about rules, food, teams, prizes..." autocomplete="off" />
            <button type="submit" id="ai-chat-send" class="chat-send-btn" aria-label="Send message">
              <svg viewBox="0 0 24 24"><path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
          </form>
          <div class="chat-disclaimer">Grounded in the official Innovate AI Hackathon 2026 Rulebook</div>
        </div>
      </div>
    `;

    document.body.appendChild(container);
    bindEvents();
    loadHistory();
  }

  function bindEvents() {
    const launcher = document.getElementById("ai-chat-launcher");
    const modal = document.getElementById("ai-chat-modal");
    const closeBtn = document.getElementById("ai-chat-close");
    const clearBtn = document.getElementById("ai-chat-clear");
    const form = document.getElementById("ai-chat-form");
    const input = document.getElementById("ai-chat-input");

    launcher.addEventListener("click", () => {
      toggleModal(true);
    });

    closeBtn.addEventListener("click", () => {
      toggleModal(false);
    });

    clearBtn.addEventListener("click", () => {
      chatHistory = [];
      sessionStorage.removeItem(STORAGE_KEY);
      renderMessages();
      loadWelcomeMessage();
    });

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const message = input.value.trim();
      if (!message || isThinking) return;

      input.value = "";
      sendMessage(message);
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modal.classList.contains("is-open")) {
        toggleModal(false);
      }
    });
  }

  function toggleModal(open) {
    const modal = document.getElementById("ai-chat-modal");
    const launcher = document.getElementById("ai-chat-launcher");
    const input = document.getElementById("ai-chat-input");

    if (open) {
      modal.classList.add("is-open");
      sessionStorage.setItem(IS_OPEN_KEY, "true");
      setTimeout(() => input.focus(), 200);
      scrollToBottom();
    } else {
      modal.classList.remove("is-open");
      sessionStorage.setItem(IS_OPEN_KEY, "false");
    }
  }

  function formatMarkdown(text) {
    if (!text) return "";
    let html = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    // Italic
    html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
    // Inline code
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
    // Bullet points
    html = html.replace(/^\s*-\s+(.*)$/gm, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>");
    // Numbered lists
    html = html.replace(/^\s*(\d+)\.\s+(.*)$/gm, "<li>$2</li>");
    // Paragraphs
    html = html.replace(/\n\n+/g, "</p><p>");
    html = `<p>${html}</p>`;
    // Fix cleanups
    html = html.replace(/<p><\/p>/g, "");
    return html;
  }

  function scrollToBottom() {
    const messagesContainer = document.getElementById("ai-chat-messages");
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  }

  function loadWelcomeMessage() {
    const messagesContainer = document.getElementById("ai-chat-messages");
    if (!messagesContainer) return;

    fetch("/api/chat/faq")
      .then((res) => res.json())
      .then((data) => {
        const welcomeHtml = `
          <div class="chat-message bot-message">
            <div class="bot-avatar-mini">
              <img src="/assets/logo.svg" alt="AI Logo" class="mini-logo-animated" />
            </div>
            <div class="message-bubble">
              <p>👋 <strong>Welcome to Innovate AI Hackathon 2026 Assistant!</strong></p>
              <p>I am your dedicated AI guide powered by the <strong>Official Hackathon Rulebook</strong>. Ask me anything about rules, team sizes, permitted AI tools, food, schedule, prizes, or emergency support!</p>
              <div class="suggested-chips-container">
                <span class="suggested-chip-title">💡 Frequently Asked Questions:</span>
                ${(data.faqs || [])
                  .slice(0, 4)
                  .map(
                    (faq) =>
                      `<button class="suggested-chip" onclick="window.askAiChat('${faq.question.replace(/'/g, "\\'")}')">${faq.question}</button>`
                  )
                  .join("")}
              </div>
            </div>
          </div>
        `;
        messagesContainer.innerHTML = welcomeHtml;
      })
      .catch(() => {
        messagesContainer.innerHTML = `
          <div class="chat-message bot-message">
            <div class="bot-avatar-mini">
              <img src="/assets/logo.svg" alt="AI Logo" class="mini-logo-animated" />
            </div>
            <div class="message-bubble">
              <p>👋 <strong>Welcome to Innovate AI Hackathon 2026 Assistant!</strong></p>
              <p>Ask me anything about rules, team sizes, permitted AI tools, food, schedule, prizes, or emergency support!</p>
            </div>
          </div>
        `;
      });
  }

  function renderMessages() {
    const messagesContainer = document.getElementById("ai-chat-messages");
    if (!messagesContainer) return;

    if (chatHistory.length === 0) {
      loadWelcomeMessage();
      return;
    }

    messagesContainer.innerHTML = chatHistory
      .map((msg) => {
        if (msg.role === "user") {
          return `
            <div class="chat-message user-message">
              <div class="message-bubble">${escapeHtml(msg.content)}</div>
            </div>
          `;
        } else {
          let sourcesHtml = "";
          if (msg.sources && msg.sources.length > 0) {
            sourcesHtml = `
              <div class="message-citations">
                <span>📚 Sources: </span>
                ${msg.sources
                  .map(
                    (s) =>
                      `<span class="citation-pill" title="${escapeHtml(s.excerpt)}">§ ${s.section_id}</span>`
                  )
                  .join("")}
              </div>
            `;
          }

          let suggestedHtml = "";
          if (msg.suggested && msg.suggested.length > 0) {
            suggestedHtml = `
              <div class="suggested-chips-container">
                <span class="suggested-chip-title">Explore Next:</span>
                ${msg.suggested
                  .map(
                    (q) =>
                      `<button class="suggested-chip" onclick="window.askAiChat('${q.replace(/'/g, "\\'")}')">${q}</button>`
                  )
                  .join("")}
              </div>
            `;
          }

          return `
            <div class="chat-message bot-message">
              <div class="bot-avatar-mini">
                <img src="/assets/logo.svg" alt="AI Logo" class="mini-logo-animated" />
              </div>
              <div class="message-bubble">
                ${formatMarkdown(msg.content)}
                ${sourcesHtml}
                ${suggestedHtml}
              </div>
            </div>
          `;
        }
      })
      .join("");

    scrollToBottom();
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function showTypingIndicator() {
    const messagesContainer = document.getElementById("ai-chat-messages");
    if (!messagesContainer) return;

    const typingEl = document.createElement("div");
    typingEl.id = "ai-chat-typing";
    typingEl.className = "chat-message bot-message";
    typingEl.innerHTML = `
      <div class="bot-avatar-mini">
        <img src="/assets/logo.svg" alt="AI Logo" class="mini-logo-animated" />
      </div>
      <div class="typing-indicator">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    `;
    messagesContainer.appendChild(typingEl);
    scrollToBottom();
  }

  function removeTypingIndicator() {
    const typingEl = document.getElementById("ai-chat-typing");
    if (typingEl) {
      typingEl.remove();
    }
  }

  async function sendMessage(text) {
    chatHistory.push({ role: "user", content: text });
    saveHistory();
    renderMessages();

    isThinking = true;
    showTypingIndicator();

    const sendBtn = document.getElementById("ai-chat-send");
    if (sendBtn) sendBtn.disabled = true;

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          history: chatHistory.map((m) => ({ role: m.role, content: m.content })),
        }),
      });

      const data = await response.json();
      removeTypingIndicator();

      if (!response.ok) {
        chatHistory.push({
          role: "assistant",
          content: "Sorry, I encountered an error connecting to the knowledge base. Please try again.",
        });
      } else {
        chatHistory.push({
          role: "assistant",
          content: data.reply,
          sources: data.sources || [],
          suggested: data.suggested_questions || [],
        });
      }
    } catch {
      removeTypingIndicator();
      chatHistory.push({
        role: "assistant",
        content: "Unable to reach the server. Please check your connection and try again.",
      });
    } finally {
      isThinking = false;
      if (sendBtn) sendBtn.disabled = false;
      saveHistory();
      renderMessages();
    }
  }

  function saveHistory() {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(chatHistory));
    } catch {
      // Ignore storage quota errors
    }
  }

  function loadHistory() {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY);
      if (saved) {
        chatHistory = JSON.parse(saved);
      }
      renderMessages();

      const wasOpen = sessionStorage.getItem(IS_OPEN_KEY);
      if (wasOpen === "true") {
        toggleModal(true);
      }
    } catch {
      chatHistory = [];
      renderMessages();
    }
  }

  // Global helper for suggested questions
  window.askAiChat = function (query) {
    const input = document.getElementById("ai-chat-input");
    if (input) {
      input.value = "";
    }
    const modal = document.getElementById("ai-chat-modal");
    if (!modal.classList.contains("is-open")) {
      toggleModal(true);
    }
    sendMessage(query);
  };

  // Run on DOM ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initWidget);
  } else {
    initWidget();
  }
})();
