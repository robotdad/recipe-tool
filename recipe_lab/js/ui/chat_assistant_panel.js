// chat_assistant_panel.js
// ES module implementing ChatAssistantPanel UI

export function init(containerEl, editor, config) {
  console.debug(
    "ChatAssistantPanel initialized with container, editor, and config",
    { containerEl, editor, config }
  );

  // Merge i18n defaults
  const defaultI18n = {
    send: "Send",
    retry: "Retry",
    placeholder: "Type a message...",
    errorGeneric: "Unexpected error occurred",
  };
  const i18n = Object.assign({}, defaultI18n, config.i18n || {});

  // State
  let messageCounter = 0;
  const messages = [];
  const listeners = {};
  let pendingUser = null;

  // Cleanup refs
  const cleanupFns = [];

  // Build DOM
  containerEl.classList.add("chat-panel");
  containerEl.innerHTML = `
    <div class="chat-panel__history" role="log" aria-live="polite"></div>
    <div class="chat-panel__input-area">
      <textarea class="chat-panel__textarea" rows="2" placeholder="${i18n.placeholder}" aria-label="${i18n.placeholder}"></textarea>
      <button class="chat-panel__send-btn" type="button">${i18n.send}</button>
    </div>
  `;
  const historyEl = containerEl.querySelector(".chat-panel__history");
  const textareaEl = containerEl.querySelector(".chat-panel__textarea");
  const sendBtn = containerEl.querySelector(".chat-panel__send-btn");

  // Helper: emit events
  function emit(event, payload) {
    (listeners[event] || []).forEach((cb) => {
      try {
        cb(payload);
      } catch (e) {
        console.error(e);
      }
    });
  }

  // Helpers: timestamp
  function nowTimestamp() {
    const d = new Date();
    const hh = d.getHours().toString().padStart(2, "0");
    const mm = d.getMinutes().toString().padStart(2, "0");
    return `${hh}:${mm}`;
  }

  // Auto-scroll
  function scrollIfNeeded() {
    const { scrollTop, scrollHeight, clientHeight } = historyEl;
    if (scrollHeight - scrollTop - clientHeight <= 50) {
      historyEl.scrollTop = scrollHeight;
      console.debug("Auto-scrolled to newest message");
    }
  }

  // Trim history to last 100
  function pruneHistory() {
    while (messages.length > 100) {
      messages.shift();
      const first = historyEl.firstChild;
      if (first) historyEl.removeChild(first);
    }
  }

  // Render a message object into DOM
  function appendMessage(msg) {
    const wrapper = document.createElement("div");
    wrapper.className = `chat-panel__message chat-panel__message--${msg.role}`;
    wrapper.dataset.id = msg.id;

    const label = document.createElement("div");
    label.className = "chat-panel__label";
    label.textContent = msg.role === "user" ? "You" : "Assistant";
    wrapper.appendChild(label);

    const time = document.createElement("div");
    time.className = "chat-panel__timestamp";
    time.textContent = msg.timestamp;
    wrapper.appendChild(time);

    const content = document.createElement("div");
    content.className = "chat-panel__content";
    content.textContent = msg.content;
    wrapper.appendChild(content);

    // If assistant and successful, add insert-node icon
    if (msg.role === "assistant" && !msg.errorType) {
      const icon = document.createElement("button");
      icon.type = "button";
      icon.className = "chat-panel__insert-icon";
      icon.title = "Insert Node";
      icon.textContent = "+";
      icon.addEventListener("click", () => handleInsertNode(msg));
      wrapper.appendChild(icon);
    }

    // If error, show inline error and retry
    if (msg.errorType) {
      const errDiv = document.createElement("div");
      errDiv.className = "chat-panel__error";
      const em = document.createElement("em");
      em.textContent = msg.errorMessage;
      errDiv.appendChild(em);
      const retryBtn = document.createElement("button");
      retryBtn.type = "button";
      retryBtn.className = "chat-panel__retry-btn";
      retryBtn.textContent = i18n.retry;
      retryBtn.addEventListener("click", () => {
        // retry original prompt
        send(msg.originalPrompt);
      });
      errDiv.appendChild(retryBtn);
      wrapper.appendChild(errDiv);
    }

    historyEl.appendChild(wrapper);
    pruneHistory();
    scrollIfNeeded();
  }

  // Handle Drawflow insert/update
  function handleInsertNode(msg) {
    const cfg = {
      position: { x: 0, y: 0 },
      data: {
        prompt: msg.originalPrompt || "",
        model: config.model || "",
        max_tokens:
          (msg.usage &&
            (msg.usage.completion_tokens || msg.usage.total_tokens)) ||
          0,
        output_format: "text",
        output_key: "output",
      },
    };
    // detect selected node
    let action, nodeId;
    if (
      typeof editor.getSelectedNodes === "function" &&
      editor.getSelectedNodes().length
    ) {
      const sel = editor.getSelectedNodes()[0];
      nodeId = sel;
      editor.updateNode(nodeId, cfg);
      action = "updateNode";
      emit("nodeUpdated", { nodeId, config: cfg });
    } else if (editor.selected) {
      nodeId = editor.selected;
      editor.updateNode(nodeId, cfg);
      action = "updateNode";
      emit("nodeUpdated", { nodeId, config: cfg });
    } else {
      nodeId = editor.addNode("llm_generate", cfg);
      action = "addNode";
      emit("nodeAdded", { nodeId, config: cfg });
    }
    console.debug("Invoked Drawflow editor API", { action, config: cfg });
  }

  // Send text to LLM
  async function send(text) {
    if (!text || sendBtn.disabled) return;
    sendBtn.disabled = true;
    const ts = nowTimestamp();
    const userMsg = {
      id: ++messageCounter,
      role: "user",
      content: text,
      timestamp: ts,
    };
    messages.push(userMsg);
    appendMessage(userMsg);
    emit("messageSent", { content: text, timestamp: ts });
    pendingUser = text;

    // prepare payload
    const payload = {
      messages: messages.map((m) => ({
        role: m.role,
        content: m.content,
        timestamp: m.timestamp,
      })),
    };
    console.debug("Sending LLM request payload:", {
      messages: payload,
      endpointUrl: config.endpointUrl,
    });
    const start = performance.now();
    try {
      const resp = await fetch(config.endpointUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${config.apiKey}`,
        },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      console.debug("Received raw LLM response:", data);
      const duration = Math.round(performance.now() - start);
      if (
        !data ||
        !data.choices ||
        !Array.isArray(data.choices) ||
        !data.choices[0].message
      ) {
        console.debug("Invalid response payload", data);
        throw new Error("InvalidResponse");
      }
      const choice = data.choices[0];
      const content = choice.message.content;
      const timestamp = data.timestamp || nowTimestamp();
      const usage = data.usage || {};
      const assistantMsg = {
        id: ++messageCounter,
        role: "assistant",
        content,
        timestamp,
        originalPrompt: pendingUser,
        usage,
      };
      messages.push(assistantMsg);
      appendMessage(assistantMsg);
      console.info("Assistant response rendered:", content);
      emit("messageReceived", { content, timestamp });
      console.info(`LLM request completed in ${duration}ms with usage`, usage);
    } catch (err) {
      console.error(err);
      const errorType =
        err.message === "InvalidResponse"
          ? "InvalidResponseError"
          : "NetworkError";
      const msgError =
        errorType === "NetworkError"
          ? "Failed to fetch LLM response"
          : i18n.errorGeneric;
      const errMsgObj = {
        id: ++messageCounter,
        role: "assistant",
        content: "",
        timestamp: nowTimestamp(),
        errorType,
        errorMessage: msgError,
        originalPrompt: pendingUser,
      };
      messages.push(errMsgObj);
      appendMessage(errMsgObj);
      emit("error", { errorType, messageId: errMsgObj.id });
    } finally {
      sendBtn.disabled = false;
    }
  }

  // Public methods
  function sendMessage(text) {
    send(text);
  }

  function clearHistory() {
    messages.length = 0;
    historyEl.innerHTML = "";
    emit("historyCleared");
    console.info("Chat history cleared");
  }

  function on(event, callback) {
    listeners[event] = listeners[event] || [];
    listeners[event].push(callback);
  }

  function teardown() {
    // remove all event listeners
    cleanupFns.forEach((fn) => fn());
    containerEl.innerHTML = "";
    Object.keys(listeners).forEach((k) => delete listeners[k]);
  }

  // Wire up input events
  const keydownHandler = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(textareaEl.value.trim());
      textareaEl.value = "";
    }
  };
  textareaEl.addEventListener("keydown", keydownHandler);
  cleanupFns.push(() =>
    textareaEl.removeEventListener("keydown", keydownHandler)
  );

  const clickHandler = () => {
    const text = textareaEl.value.trim();
    if (!text) return;
    send(text);
    textareaEl.value = "";
  };
  sendBtn.addEventListener("click", clickHandler);
  cleanupFns.push(() => sendBtn.removeEventListener("click", clickHandler));

  return { sendMessage, clearHistory, teardown, on };
}
