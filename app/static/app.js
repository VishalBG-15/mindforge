(() => {
  "use strict";

  const API = "/api/v1/habits";
  const $ = (selector) => document.querySelector(selector);
  const elements = {
    today: $("#today-label"),
    activeCount: $("#active-count"),
    checkinCount: $("#checkin-count"),
    streakCount: $("#streak-count"),
    list: $("#habit-list"),
    loading: $("#habits-loading"),
    empty: $("#empty-state"),
    globalMessage: $("#global-message"),
    createPanel: $("#create-panel"),
    createForm: $("#create-form"),
    createSubmit: $("#create-submit"),
    createMessage: $("#create-message"),
    selectedTitle: $("#selected-title"),
    selectedDescription: $("#selected-description"),
    checkinForm: $("#checkin-form"),
    checkinPlaceholder: $("#checkin-placeholder"),
    checkinMessage: $("#checkin-message"),
    checkinSubmit: $("#checkin-submit"),
    logList: $("#log-list"),
    logsLoading: $("#logs-loading"),
    logsEmpty: $("#logs-empty"),
    historyCount: $("#history-count"),
    councilButton: $("#council-button"),
    councilMessage: $("#council-message"),
    councilLoading: $("#council-loading"),
    councilResult: $("#council-result"),
  };
  let habits = [];
  let selectedHabit = null;
  let logs = [];
  let councilRequestId = 0;

  elements.today.textContent = new Intl.DateTimeFormat(undefined, {
    weekday: "long", month: "long", day: "numeric",
  }).format(new Date());

  function setMessage(element, message, visible = true) {
    element.textContent = message;
    element.hidden = !visible;
  }

  function friendlyError(error, fallback) {
    const detail = error && error.message ? error.message : "";
    return detail ? `${fallback} ${detail}` : fallback;
  }

  async function request(url, options = {}) {
    let response;
    try {
      response = await fetch(url, {
        ...options,
        headers: { Accept: "application/json", ...(options.body ? { "Content-Type": "application/json" } : {}), ...options.headers },
      });
    } catch {
      throw new Error("Could not reach the API. Check that the service is running and try again.");
    }

    const text = await response.text();
    let data = null;
    if (text) {
      try { data = JSON.parse(text); } catch { data = text; }
    }
    if (!response.ok) {
      let detail = data && typeof data === "object" ? data.detail : null;
      if (Array.isArray(detail)) {
        detail = detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
      }
      if (detail && typeof detail === "object") detail = JSON.stringify(detail);
      throw new Error(detail || `Request failed (${response.status}).`);
    }
    return data;
  }

  function make(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function formatDate(value, includeTime = false) {
    if (!value) return "Date unavailable";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    const options = includeTime
      ? { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }
      : { month: "short", day: "numeric", year: "numeric" };
    return new Intl.DateTimeFormat(undefined, options).format(date);
  }

  function renderHabits() {
    elements.list.replaceChildren();
    elements.activeCount.textContent = String(habits.length);
    elements.empty.hidden = habits.length !== 0;
    habits.forEach((habit, index) => {
      const button = make("button", "habit-card");
      button.type = "button";
      button.setAttribute("aria-pressed", selectedHabit && selectedHabit.id === habit.id ? "true" : "false");
      button.setAttribute("aria-label", `Select habit ${habit.title}`);
      const icon = make("span", "habit-symbol", ["✳", "◌", "↗", "◇", "✦"][index % 5]);
      icon.setAttribute("aria-hidden", "true");
      const copy = make("span", "habit-copy");
      copy.append(make("span", "habit-title", habit.title));
      copy.append(make("span", "habit-description", habit.description || "A small step, made your own"));
      const tag = make("span", "habit-tag", "Active");
      const arrow = make("span", "habit-arrow", "›");
      arrow.setAttribute("aria-hidden", "true");
      button.append(icon, copy, tag, arrow);
      button.addEventListener("click", () => selectHabit(habit));
      elements.list.append(button);
    });
  }

  function renderLogs() {
    elements.logList.replaceChildren();
    elements.historyCount.textContent = `${logs.length} ${logs.length === 1 ? "entry" : "entries"}`;
    elements.checkinCount.textContent = String(logs.length);
    let streak = 0;
    for (const log of logs) {
      if (!log.completed) break;
      streak += 1;
    }
    elements.streakCount.textContent = String(streak);
    elements.logsEmpty.hidden = logs.length > 0 || elements.logsLoading.hidden === false;
    logs.forEach((log) => {
      const row = make("article", "log-row");
      const indicator = make("span", `log-indicator ${log.completed ? "done" : "missed"}`, log.completed ? "✓" : "–");
      indicator.setAttribute("aria-label", log.completed ? "Completed" : "Not completed");
      const content = make("div");
      const meta = make("div", "log-meta");
      meta.append(make("span", "", log.completed ? "Completed" : "Not today"));
      const time = make("time", "", formatDate(log.logged_at, true));
      if (log.logged_at) time.dateTime = String(log.logged_at);
      meta.append(time);
      content.append(meta);
      if (log.notes) content.append(make("p", "log-note", log.notes));
      row.append(indicator, content);
      elements.logList.append(row);
    });
  }

  async function loadHabits() {
    elements.loading.hidden = false;
    setMessage(elements.globalMessage, "", false);
    try {
      const data = await request(`${API}/`);
      if (!Array.isArray(data)) throw new Error("The habits endpoint returned an unexpected response.");
      habits = data;
      renderHabits();
      elements.loading.hidden = true;
      if (selectedHabit && !habits.some((habit) => habit.id === selectedHabit.id)) {
        selectedHabit = null;
        resetSelectedHabit();
      }
      if (!selectedHabit && habits.length) await selectHabit(habits[0]);
      if (!habits.length) resetSelectedHabit();
    } catch (error) {
      elements.loading.hidden = true;
      setMessage(elements.globalMessage, friendlyError(error, "Could not load habits."));
    }
  }

  function resetSelectedHabit() {
    elements.selectedTitle.textContent = "Pick a habit";
    elements.selectedDescription.textContent = "Choose a habit to see its check-in history and add a reflection.";
    elements.checkinForm.hidden = true;
    elements.checkinPlaceholder.hidden = false;
    elements.councilButton.disabled = true;
    logs = [];
    renderLogs();
  }

  async function selectHabit(habit) {
    selectedHabit = habit;
    renderHabits();
    setMessage(elements.globalMessage, "", false);
    elements.selectedTitle.textContent = habit.title || "Untitled habit";
    elements.selectedDescription.textContent = habit.description || "Make space for this habit in a way that works for you.";
    elements.checkinForm.hidden = false;
    elements.checkinPlaceholder.hidden = true;
    elements.checkinMessage.textContent = "";
    elements.councilButton.disabled = false;
    elements.councilResult.replaceChildren();
    elements.councilResult.hidden = true;
    setMessage(elements.councilMessage, "", false);
    elements.logsLoading.hidden = false;
    elements.logsEmpty.hidden = true;
    elements.logList.replaceChildren();
    elements.checkinCount.textContent = "—";
    elements.streakCount.textContent = "—";
    const habitId = habit.id;
    try {
      const data = await request(`${API}/${encodeURIComponent(habitId)}/logs?limit=14`);
      if (selectedHabit?.id !== habitId) return;
      if (!Array.isArray(data)) throw new Error("The check-in history endpoint returned an unexpected response.");
      logs = data;
      renderLogs();
    } catch (error) {
      if (selectedHabit?.id !== habitId) return;
      logs = [];
      renderLogs();
      setMessage(elements.globalMessage, friendlyError(error, "Could not load check-in history."));
    } finally {
      if (selectedHabit?.id === habitId) {
        elements.logsLoading.hidden = true;
        elements.logsEmpty.hidden = logs.length > 0;
      }
    }
  }

  $("#show-create").addEventListener("click", () => {
    elements.createPanel.hidden = false;
    elements.createForm.elements.title.focus();
  });
  $("#empty-create").addEventListener("click", () => $("#show-create").click());
  $("#hide-create").addEventListener("click", () => { elements.createPanel.hidden = true; });

  elements.createForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(elements.createForm);
    const title = String(form.get("title") || "").trim();
    const description = String(form.get("description") || "").trim();
    if (!title) {
      setMessage(elements.createMessage, "Add a name for your habit.");
      return;
    }
    elements.createSubmit.disabled = true;
    elements.createMessage.textContent = "";
    try {
      const created = await request(`${API}/`, {
        method: "POST",
        body: JSON.stringify({ title, description: description || null }),
      });
      elements.createForm.reset();
      elements.createPanel.hidden = true;
      await loadHabits();
      if (created && habits.some((habit) => habit.id === created.id)) await selectHabit(habits.find((habit) => habit.id === created.id));
    } catch (error) {
      setMessage(elements.createMessage, friendlyError(error, "Could not create the habit."));
    } finally {
      elements.createSubmit.disabled = false;
    }
  });

  elements.checkinForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!selectedHabit) return;
    const habitId = selectedHabit.id;
    const form = new FormData(elements.checkinForm);
    const notes = String(form.get("notes") || "").trim();
    const completed = form.get("completed") === "true";
    elements.checkinSubmit.disabled = true;
    elements.checkinMessage.textContent = "";
    try {
      await request(`${API}/${encodeURIComponent(habitId)}/logs`, {
        method: "POST",
        body: JSON.stringify({ completed, notes: notes || null }),
      });
      elements.checkinForm.elements.notes.value = "";
      await selectHabit(selectedHabit);
    } catch (error) {
      setMessage(elements.checkinMessage, friendlyError(error, "Could not save your check-in."));
    } finally {
      elements.checkinSubmit.disabled = false;
    }
  });

  function displayValue(value) {
    if (value === null || value === undefined || value === "") return "";
    if (typeof value === "object") return JSON.stringify(value, null, 2);
    if (typeof value === "number" && value >= 0 && value <= 1 && !Number.isInteger(value)) return `${Math.round(value * 100)}%`;
    return String(value);
  }

  function firstDefined(source, keys) {
    for (const key of keys) {
      if (source && source[key] !== null && source[key] !== undefined && source[key] !== "") return source[key];
    }
    return null;
  }

  const agentSpecs = [
    { title: "Diagnostic profiler", keys: ["diagnosed_friction", "diagnostic_reasoning", "surface_excuse", "actual_mechanism", "diagnosis", "diagnostic"] },
    { title: "Strategy architect", keys: ["selected_strategy", "strategy_rationale", "strategy", "proposed_target"] },
    { title: "Feasibility critic", keys: ["audit_verdict", "critic_rationale", "coaching_mandate", "final_adjusted_target", "feasibility"] },
    { title: "Coaching communicator", keys: ["coaching_message", "communication", "message", "coaching"] },
  ];

  function agentArray(data) {
    for (const key of ["agents", "agent_deliberations", "deliberations", "deliberation", "council"]) {
      if (Array.isArray(data && data[key])) return data[key];
    }
    return null;
  }

  function agentContent(agent) {
    if (agent === null || agent === undefined) return "";
    if (typeof agent !== "object") return displayValue(agent);
    const fields = ["deliberation", "reasoning", "analysis", "response", "content", "message", "output", "summary"];
    const values = fields.map((key) => agent[key]).filter((value) => value !== null && value !== undefined && value !== "");
    if (values.length) return values.map(displayValue).join("\n\n");
    const excluded = new Set(["name", "agent", "role", "title", "agent_name"]);
    return Object.entries(agent).filter(([key]) => !excluded.has(key)).map(([key, value]) => `${key.replaceAll("_", " ")}: ${displayValue(value)}`).join("\n");
  }

  function renderCouncil(data) {
    const root = elements.councilResult;
    root.replaceChildren();
    let payload = data;
    if (payload && typeof payload === "object" && payload.result && typeof payload.result === "object") payload = payload.result;
    if (Array.isArray(payload)) payload = { agents: payload };
    if (!payload || typeof payload !== "object") payload = { response: payload };

    const analytics = payload.analytics || payload.metrics || payload.statistics;
    if (analytics && typeof analytics === "object") {
      const block = make("section", "analytics-block");
      const heading = make("div", "result-heading");
      heading.append(make("h3", "", "Habit analytics"), make("span", "", "From the Council response"));
      block.append(heading);
      const grid = make("dl", "analytics-grid");
      Object.entries(analytics).forEach(([key, value]) => {
        const item = make("div", "analytics-item");
        item.append(make("dt", "", key.replaceAll("_", " ")), make("dd", "", displayValue(value)));
        grid.append(item);
      });
      block.append(grid);
      root.append(block);
    }

    const providedAgents = agentArray(payload);
    const grid = make("div", "agent-grid");
    agentSpecs.forEach((spec, index) => {
      const supplied = providedAgents && providedAgents[index];
      const content = supplied ? agentContent(supplied) : agentSpecs[index].keys
        .map((key) => payload[key] !== undefined && payload[key] !== null ? `${key.replaceAll("_", " ")}: ${displayValue(payload[key])}` : "")
        .filter(Boolean).join("\n");
      const card = make("article", "agent-card");
      card.append(make("span", "agent-number", `Agent 0${index + 1}`));
      const suppliedName = supplied && typeof supplied === "object"
        ? firstDefined(supplied, ["name", "agent_name", "agent", "role", "title"])
        : null;
      card.append(make("h4", "", suppliedName || spec.title));
      card.append(make("p", "", content || "No deliberation details were included for this agent in the response."));
      grid.append(card);
    });
    root.append(grid);

    const directive = firstDefined(payload, ["final_coaching_directive", "coaching_directive", "directive", "final_directive", "coaching_message", "coaching_mandate"]);
    const final = payload.final && typeof payload.final === "object"
      ? firstDefined(payload.final, ["directive", "coaching_directive", "message", "coaching_message"])
      : payload.final;
    const directiveValue = directive || final;
    const directiveCard = make("section", "directive-card");
    directiveCard.append(make("p", "eyebrow", "YOUR NEXT STEP"));
    directiveCard.append(make("p", "", directiveValue
      ? displayValue(directiveValue)
      : "The response did not include a separate final coaching directive."));
    root.append(directiveCard);

    const hasContent = analytics || providedAgents || agentSpecs.some((spec) => spec.keys.some((key) => payload[key] !== undefined)) || directive || final;
    if (!hasContent) {
      const raw = make("pre", "raw-result", JSON.stringify(data, null, 2));
      root.append(raw);
    }
    root.hidden = false;
  }

  elements.councilButton.addEventListener("click", async () => {
    if (!selectedHabit) return;
    const habitId = selectedHabit.id;
    const requestId = ++councilRequestId;
    elements.councilButton.disabled = true;
    elements.councilLoading.hidden = false;
    elements.councilResult.hidden = true;
    setMessage(elements.councilMessage, "", false);
    try {
      const data = await request(`${API}/${encodeURIComponent(habitId)}/council`, {
        method: "POST",
        body: JSON.stringify({}),
      });
      if (requestId !== councilRequestId || selectedHabit?.id !== habitId) return;
      renderCouncil(data);
    } catch (error) {
      if (requestId === councilRequestId && selectedHabit?.id === habitId) {
        setMessage(elements.councilMessage, friendlyError(error, "Could not get Council guidance."));
      }
    } finally {
      if (requestId === councilRequestId) {
        elements.councilLoading.hidden = true;
        elements.councilButton.disabled = !selectedHabit;
      }
    }
  });

  loadHabits();
})();
