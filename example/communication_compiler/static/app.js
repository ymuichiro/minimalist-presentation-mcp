const state = {
  sessionId: null,
  session: null,
  markdownUrl: null,
  step: "freeTalk",
  locale: localStorage.getItem("communicationCompilerLocale") || "ja",
  chatMessages: [],
  recorder: null,
  recordedChunks: [],
  recordingStream: null,
};

const samples = {
  ja: {
    freeTalk: `最近、社内で AI 活用を進めたいんだけど、みんな Copilot を入れればいいと思っていて、
でも実際には業務に入っていない気がしている。現場はプロンプトを書く時間もないし、
ナレッジも散らばっているし、PoC は増えるけど定着しない。
だから、単にライセンスを配るより、業務単位で Agent を作る方に予算を寄せたい。
ただ、経営層にはコスト削減だけで説明したくない。
むしろ、業務プロセスの再設計として伝えたい。`,
    audience: "役員会",
    desiredAction: "次四半期の AI 投資方針を決める",
  },
  en: {
    freeTalk: `We want to expand AI adoption internally, but the current approach assumes that distributing Copilot is enough.
In reality, it does not feel embedded in the work. Teams do not have time to write prompts, knowledge is scattered, and PoCs keep increasing without becoming operational.
I want to shift budget from broad license distribution toward workflow-level Agents.
For executives, I do not want to explain this only as cost reduction. I want to frame it as business process redesign.`,
    audience: "Executive committee",
    desiredAction: "Decide next quarter's AI investment direction",
  },
};

const i18n = {
  ja: {
    "nav.input": "入力",
    "nav.claims": "主張",
    "nav.kernel": "Kernel",
    "nav.deck": "資料",
    "step1.title": "自由入力",
    "step1.description": "未整理のまま入力してください。",
    "step1.freeTalkLabel": "思っていることをそのまま話してください",
    "step1.freeTalkPlaceholder": "整理されていなくて構いません。例: AI 活用を進めたいが、今の Copilot 配布中心の進め方では成果につながっていない気がする...",
    "step2.title": "主張候補",
    "step2.description": "近い主張を選択してください。",
    "step3.title": "Kernel Studio",
    "step3.description": "4 行の核を対話で磨きます。",
    "step3.messageTitle": "メッセージ",
    "step4.title": "資料出力",
    "step4.description": "生成された資料を確認してください。",
    "field.audience": "聞き手",
    "field.audiencePlaceholder": "役員会",
    "field.desiredAction": "求める判断",
    "field.desiredActionPlaceholder": "次四半期の AI 投資方針を決める",
    "field.tone": "トーン",
    "field.additionalInfo": "追加情報",
    "field.additionalInfoPlaceholder": "例: 4行目には、対象業務・期間・予算振替・決裁者を明記してください。",
    "tone.executive": "役員向け",
    "tone.direct": "端的",
    "tone.cautious": "慎重",
    "tone.technical": "技術寄り",
    "tone.narrative": "ストーリー重視",
    "button.sample": "サンプル",
    "button.voiceInput": "音声入力",
    "button.stopRecording": "停止",
    "button.transcribing": "文字起こし中...",
    "button.next": "次へ",
    "button.back": "戻る",
    "button.refine": "改善する",
    "button.send": "送信",
    "button.generateDeck": "資料化する",
    "button.brief": "要約を作る",
    "button.copyMarkdown": "Markdown をコピー",
    "button.openDeck": "資料を開く",
    "button.selectClaim": "この方向で4行に圧縮する",
    "button.working": "処理中...",
    "agent.review": "レビュー",
    "agent.chat": "対話",
    "kernel.premise": "相手の現在の前提",
    "kernel.complication": "その前提では足りない理由",
    "kernel.claim": "こちらが通したい主張",
    "kernel.action": "相手に求める判断・行動",
    "diagnosis.strengths": "強み",
    "diagnosis.issues": "課題",
    "diagnosis.nextQuestion": "次の問い",
    "empty.claims": "主張候補がここに表示されます。",
    "empty.kernel": "主張を選ぶと 4 行が生成されます。",
    "empty.diagnosis": "評価がここに表示されます。",
    "empty.outputs": "生成されたリンクがここに表示されます。",
    "empty.finalKernel": "最終版の 4-Line Message Kernel がここに表示されます。",
    "empty.agent": "主張を選ぶと、Agent の診断と次の質問がここに表示されます。",
    "empty.noStrengths": "記録された強みはまだありません。",
    "empty.noIssues": "重大な課題はありません。",
    "link.deck": "資料を開く",
    "link.brief": "要約を開く",
    "link.htmlBrief": "HTML 要約",
    "finalKernel.title": "最終版 4-Line Message Kernel",
    "agent.scoreIntro": "現在の 4 行は",
    "agent.scoreOutro": " です。弱点を潰しながら、判断文をより具体化します。",
    "agent.initialChat": "4 行を確認しました。気になる点や追加条件を送ってください。必要に応じて Message Kernel を更新します。",
    "agent.updatedChat": "内容を反映して 4-Line Message Kernel を更新しました。",
    "status.ready": "準備完了",
    "status.savingFreeTalk": "入力を保存中",
    "status.extractingClaims": "主張候補を抽出中",
    "status.claimCandidatesReady": "主張候補を確認してください",
    "status.selectingClaim": "主張を選択中",
    "status.kernelReady": "Kernel を確認してください",
    "status.kernelRevised": "Kernel を更新しました",
    "status.groundingEvidence": "根拠を整理中",
    "status.generatingDeck": "資料を生成中",
    "status.deckGenerated": "資料を生成しました",
    "status.bootError": "起動エラー",
    "toast.kernelRevised": "Kernel を更新しました。",
    "toast.deckGenerated": "資料を生成しました。",
    "toast.briefGenerated": "要約を生成しました。",
    "toast.copyMarkdownFirst": "先に要約を作成してください。",
    "toast.markdownCopied": "Markdown をコピーしました。",
    "toast.sampleInserted": "サンプルを入力しました。",
    "toast.voiceUnsupported": "このブラウザでは録音機能を利用できません。",
    "toast.recordingStarted": "録音を開始しました。",
    "toast.transcriptionAdded": "文字起こし結果を追記しました。",
    "error.requestFailed": "リクエストに失敗しました",
    "session.label": "セッション",
    "session.preparing": "セッション: 準備中",
  },
  en: {
    "nav.input": "Input",
    "nav.claims": "Claims",
    "nav.kernel": "Kernel",
    "nav.deck": "Deck",
    "step1.title": "Free Talk",
    "step1.description": "Start with unstructured thoughts.",
    "step1.freeTalkLabel": "Write what you are thinking",
    "step1.freeTalkPlaceholder": "No need to organize it yet. Example: We want to expand AI adoption, but our Copilot-first approach does not seem connected to business outcomes...",
    "step2.title": "Claim Candidates",
    "step2.description": "Choose the claim that feels closest.",
    "step3.title": "Kernel Studio",
    "step3.description": "Refine the four-line message through dialogue.",
    "step3.messageTitle": "Message",
    "step4.title": "Deck Output",
    "step4.description": "Review the generated presentation.",
    "field.audience": "Audience",
    "field.audiencePlaceholder": "Executive committee",
    "field.desiredAction": "Desired action",
    "field.desiredActionPlaceholder": "Decide next quarter's AI investment direction",
    "field.tone": "Tone",
    "field.additionalInfo": "Additional context",
    "field.additionalInfoPlaceholder": "Example: In line 4, include target workflows, timeline, budget shift, and decision owner.",
    "tone.executive": "Executive",
    "tone.direct": "Direct",
    "tone.cautious": "Cautious",
    "tone.technical": "Technical",
    "tone.narrative": "Narrative",
    "button.sample": "Sample",
    "button.voiceInput": "Voice input",
    "button.stopRecording": "Stop",
    "button.transcribing": "Transcribing...",
    "button.next": "Next",
    "button.back": "Back",
    "button.refine": "Refine",
    "button.send": "Send",
    "button.generateDeck": "Create deck",
    "button.brief": "Create brief",
    "button.copyMarkdown": "Copy Markdown",
    "button.openDeck": "Open deck",
    "button.selectClaim": "Compress into 4 lines",
    "button.working": "Working...",
    "agent.review": "Review",
    "agent.chat": "Chat",
    "kernel.premise": "Audience's current premise",
    "kernel.complication": "Why that premise is insufficient",
    "kernel.claim": "Claim to advance",
    "kernel.action": "Decision or action requested",
    "diagnosis.strengths": "Strengths",
    "diagnosis.issues": "Issues",
    "diagnosis.nextQuestion": "Next question",
    "empty.claims": "Claim candidates will appear here.",
    "empty.kernel": "Select a claim to create the kernel.",
    "empty.diagnosis": "Kernel diagnosis will appear here.",
    "empty.outputs": "Output links will appear here.",
    "empty.finalKernel": "Final 4-Line Message Kernel will stay visible here.",
    "empty.agent": "After you select a claim, the Agent's diagnosis and next questions will appear here.",
    "empty.noStrengths": "No strengths recorded yet.",
    "empty.noIssues": "No critical issues.",
    "link.deck": "Open deck",
    "link.brief": "Open brief",
    "link.htmlBrief": "HTML brief",
    "finalKernel.title": "Final 4-Line Message Kernel",
    "agent.scoreIntro": "The current 4-line message is",
    "agent.scoreOutro": ". The Agent will make the decision statement more specific while resolving weak points.",
    "agent.initialChat": "I reviewed the four lines. Send any concerns or additional constraints, and I will update the Message Kernel when the context requires it.",
    "agent.updatedChat": "I updated the 4-Line Message Kernel based on your message.",
    "status.ready": "ready",
    "status.savingFreeTalk": "saving input",
    "status.extractingClaims": "extracting claims",
    "status.claimCandidatesReady": "claim candidates ready",
    "status.selectingClaim": "selecting claim",
    "status.kernelReady": "kernel ready",
    "status.kernelRevised": "kernel revised",
    "status.groundingEvidence": "grounding evidence",
    "status.generatingDeck": "generating deck",
    "status.deckGenerated": "deck generated",
    "status.bootError": "boot error",
    "toast.kernelRevised": "Kernel revised.",
    "toast.deckGenerated": "Deck generated.",
    "toast.briefGenerated": "Brief generated.",
    "toast.copyMarkdownFirst": "Create a brief first.",
    "toast.markdownCopied": "Markdown copied.",
    "toast.sampleInserted": "Sample inserted.",
    "toast.voiceUnsupported": "Voice recording is not available in this browser.",
    "toast.recordingStarted": "Recording started.",
    "toast.transcriptionAdded": "Transcription added.",
    "error.requestFailed": "Request failed",
    "session.label": "Session",
    "session.preparing": "Session: preparing",
  },
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.error?.message || `${t("error.requestFailed")}: ${response.status}`;
    const error = new Error(message);
    error.code = data.error?.code;
    throw error;
  }
  return data;
}

function t(key) {
  return i18n[state.locale]?.[key] || i18n.en[key] || key;
}

function setLocale(locale) {
  state.locale = locale === "en" ? "en" : "ja";
  localStorage.setItem("communicationCompilerLocale", state.locale);
  applyI18n();
  updateSession(state.session || {});
  setStatus(statusKeyForCurrentState());
}

function applyI18n() {
  document.documentElement.lang = state.locale;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.setAttribute("placeholder", t(node.dataset.i18nPlaceholder));
  });
  document.querySelectorAll("[data-locale]").forEach((button) => {
    button.classList.toggle("active", button.dataset.locale === state.locale);
  });
  if (!state.recorder || state.recorder.state === "inactive") setVoiceButtonState("idle");
  updateSessionBadge();
}

function updateSessionBadge() {
  const badge = document.getElementById("sessionBadge");
  if (!badge) return;
  badge.textContent = state.sessionId ? `${t("session.label")}: ${state.sessionId}` : t("session.preparing");
}

function statusKeyForCurrentState() {
  if (state.step === "outputs" && state.session?.artifacts?.deck_url) return "status.deckGenerated";
  if (state.step === "kernel" && state.session?.current_message_kernel) return "status.kernelReady";
  if (state.step === "claims" && state.session?.claim_candidates?.length) return "status.claimCandidatesReady";
  return "status.ready";
}

function setBusy(id, busy) {
  const button = document.getElementById(id);
  if (!button) return;
  setButtonBusy(button, busy, t(button.dataset.i18n || ""));
  if (!busy) applyI18n();
}

function setButtonBusy(button, busy, idleLabel = "") {
  if (!button) return;
  const label = idleLabel || button.dataset.idleLabel || button.textContent.trim();
  button.dataset.idleLabel = label;
  button.disabled = busy;
  button.classList.toggle("is-loading", busy);
  if (busy) {
    button.innerHTML = `<span class="button-label">${escapeHtml(t("button.working"))}</span><span class="button-loader" aria-hidden="true"></span>`;
    button.setAttribute("aria-busy", "true");
    return;
  }
  button.removeAttribute("aria-busy");
  button.textContent = label;
}

function setVoiceButtonState(mode) {
  const button = document.getElementById("voiceInput");
  if (!button) return;
  button.classList.toggle("is-recording", mode === "recording");
  button.classList.toggle("is-loading", mode === "transcribing");
  button.disabled = mode === "transcribing";
  button.removeAttribute("aria-busy");
  if (mode === "recording") {
    button.textContent = t("button.stopRecording");
    return;
  }
  if (mode === "transcribing") {
    button.innerHTML = `<span class="button-label">${escapeHtml(t("button.transcribing"))}</span><span class="button-loader" aria-hidden="true"></span>`;
    button.setAttribute("aria-busy", "true");
    return;
  }
  button.textContent = t("button.voiceInput");
}

function toast(message) {
  const node = document.getElementById("toast");
  node.textContent = message;
  node.classList.add("visible");
  window.clearTimeout(toast.timer);
  toast.timer = window.setTimeout(() => node.classList.remove("visible"), 3200);
}

function setStatus(message) {
  document.getElementById("globalStatus").textContent = t(message) || message;
}

function setStep(step) {
  state.step = step;
  document.querySelectorAll("[data-step-panel]").forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.stepPanel === step);
  });
  document.querySelectorAll("[data-step-nav]").forEach((item) => {
    item.classList.toggle("active", item.dataset.stepNav === step);
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function createSession() {
  const data = await api("/api/sessions", { method: "POST", body: "{}" });
  state.sessionId = data.session_id;
  updateSessionBadge();
  setStatus("status.ready");
}

function updateSession(session) {
  state.session = session;
  renderCandidates(session.claim_candidates || []);
  renderKernel(session.current_message_kernel);
  renderDiagnosis(session.diagnosis);
  renderAgentThread(session);
  renderEvidence(session);
  renderOutputs(session);
  renderFinalKernel(session.current_message_kernel);
}

function appendChatMessage(role, text) {
  if (!text?.trim()) return;
  state.chatMessages.push({ role, text: text.trim() });
  renderAgentThread(state.session || {});
}

function ensureAgentGreeting(session) {
  if (!session.current_message_kernel) return;
  if (state.chatMessages.length) return;
  state.chatMessages.push({ role: "agent", text: t("agent.initialChat") });
}

function renderCandidates(candidates) {
  const root = document.getElementById("claimCandidates");
  if (!candidates.length) {
    root.innerHTML = `<p class="empty">${escapeHtml(t("empty.claims"))}</p>`;
    return;
  }
  root.innerHTML = candidates.map((candidate) => `
    <article class="candidate">
      <div class="candidate-top">
        <span class="badge">${escapeHtml(candidate.angle)}</span>
      </div>
      <div class="candidate-copy">
        <h3>${escapeHtml(candidate.title)}</h3>
        <p>${escapeHtml(candidate.summary)}</p>
      </div>
      <div class="candidate-detail">
        <div class="candidate-section">
          <p><strong>${escapeHtml(state.locale === "ja" ? "理由" : "Why")}</strong></p>
          <ul>${candidate.why_this_may_be_true.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
        </div>
        <div class="candidate-section">
          <p><strong>${escapeHtml(state.locale === "ja" ? "弱点" : "Weakness")}</strong></p>
          <ul>${candidate.potential_weakness.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
        </div>
      </div>
      <button type="button" data-claim="${escapeHtml(candidate.claim_id)}">${escapeHtml(t("button.selectClaim"))}</button>
    </article>
  `).join("");
  root.querySelectorAll("[data-claim]").forEach((button) => {
    button.addEventListener("click", () => selectClaim(button.dataset.claim, button));
  });
}

function renderKernel(kernel) {
  const root = document.getElementById("kernelRows");
  if (!kernel) {
    root.innerHTML = `<p class="empty">${escapeHtml(t("empty.kernel"))}</p>`;
    return;
  }
  const fields = ["premise", "complication", "claim", "action"];
  root.innerHTML = fields.map((field, index) => `
    <div class="kernel-line">
      <div class="kernel-index">${index + 1}</div>
      <label>
        ${escapeHtml(t(`kernel.${field}`))}
        <textarea data-kernel-field="${field}">${escapeHtml(kernel[field] || "")}</textarea>
      </label>
    </div>
  `).join("");
}

function renderDiagnosis(diagnosis) {
  const root = document.getElementById("diagnosisPanel");
  if (!root) return;
  if (!diagnosis) {
    root.innerHTML = `<p class="empty">${escapeHtml(t("empty.diagnosis"))}</p>`;
    return;
  }
  root.innerHTML = `
    <div class="score"><strong>${diagnosis.overall_score}</strong><span>/ 100</span></div>
    <h3>${escapeHtml(t("diagnosis.strengths"))}</h3>
    <ul>${(diagnosis.strengths || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("") || `<li>${escapeHtml(t("empty.noStrengths"))}</li>`}</ul>
    <h3>${escapeHtml(t("diagnosis.issues"))}</h3>
    <ul>${(diagnosis.issues || []).map((item) => `<li><span class="badge">${escapeHtml(item.severity)}</span> ${escapeHtml(item.message)}</li>`).join("") || `<li>${escapeHtml(t("empty.noIssues"))}</li>`}</ul>
    <h3>${escapeHtml(t("diagnosis.nextQuestion"))}</h3>
    <ul>${(diagnosis.recommended_questions || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
  `;
}

function renderEvidence(session) {
  if (!document.getElementById("evidenceList")) return;
  renderItemList("evidenceList", session.supporting_evidence || [], (item) => `
    <div class="item">
      <span class="badge">${escapeHtml(item.strength)}</span>
      <strong>${escapeHtml(item.title)}</strong>
      <p>${escapeHtml(item.summary)}</p>
      <small>${escapeHtml(item.source_ref)} / ${escapeHtml(item.supports_kernel_line)}</small>
    </div>
  `, "Supporting evidence will appear here.");
  renderItemList("gapList", session.evidence_gaps || [], (item) => `
    <div class="item">
      <strong>${escapeHtml(item.description)}</strong>
      <p>${escapeHtml(item.why_it_matters)}</p>
      <small>${escapeHtml(item.suggested_source)}</small>
    </div>
  `, "Evidence gaps will appear here.");
  renderItemList("objectionList", session.objections || [], (item) => `
    <div class="item">
      <strong>${escapeHtml(item.objection)}</strong>
      <p>${escapeHtml(item.response_strategy)}</p>
      <small>${escapeHtml(item.evidence_needed)}</small>
    </div>
  `, "Likely objections will appear here.");
}

function renderItemList(id, items, render, empty) {
  const root = document.getElementById(id);
  if (!root) return;
  root.innerHTML = items.length ? items.map(render).join("") : `<p class="empty">${empty}</p>`;
}

function renderIdeaMap(ideaMap) {
  const root = document.getElementById("ideaMap");
  if (!root) return;
  if (!ideaMap || !ideaMap.nodes?.length) {
    root.innerHTML = `<p class="empty">Idea Map will appear after the kernel is generated.</p>`;
    return;
  }
  const byType = (type) => ideaMap.nodes.filter((node) => node.type === type);
  const coreIds = ["premise", "complication", "claim", "action"];
  const core = coreIds.map((id) => ideaMap.nodes.find((node) => node.id === id)).filter(Boolean);
  const support = ideaMap.nodes.filter((node) => !coreIds.includes(node.id));
  root.innerHTML = `
    <div class="map-row">${core.map(renderMapNode).join("")}</div>
    <div class="map-support">${support.map(renderMapNode).join("")}</div>
  `;
}

function renderMapNode(node) {
  return `
    <article class="map-node ${escapeHtml(node.type)}">
      <span>${escapeHtml(node.label)}</span>
      <p>${escapeHtml(node.text)}</p>
    </article>
  `;
}

function renderOutputs(session) {
  const root = document.getElementById("outputLinks");
  const links = [];
  if (session.artifacts?.deck_url) {
    links.push(`<a href="${escapeAttr(session.artifacts.deck_url)}" target="_blank" rel="noreferrer">${escapeHtml(t("link.deck"))}</a>`);
  }
  if (session.artifacts?.brief_url) {
    state.markdownUrl = session.artifacts.brief_url;
    links.push(`<a href="${escapeAttr(session.artifacts.brief_url)}" target="_blank" rel="noreferrer">${escapeHtml(t("link.brief"))}</a>`);
  }
  if (session.artifacts?.brief_html_url) {
    links.push(`<a href="${escapeAttr(session.artifacts.brief_html_url)}" target="_blank" rel="noreferrer">${escapeHtml(t("link.htmlBrief"))}</a>`);
  }
  if (session.warnings?.length) {
    links.push(`<span class="badge">${escapeHtml(session.warnings.join(", "))}</span>`);
  }
  root.innerHTML = links.join("") || `<p class="empty">${escapeHtml(t("empty.outputs"))}</p>`;
  const shortcut = document.getElementById("openDeckShortcut");
  if (shortcut) {
    const deckUrl = session.artifacts?.deck_url;
    shortcut.href = deckUrl || "#";
    shortcut.setAttribute("aria-disabled", deckUrl ? "false" : "true");
  }
}

function renderFinalKernel(kernel) {
  const root = document.getElementById("finalKernel");
  if (!kernel) {
    root.innerHTML = `<p class="empty">${escapeHtml(t("empty.finalKernel"))}</p>`;
    return;
  }
  root.innerHTML = `
    <h3>${escapeHtml(t("finalKernel.title"))}</h3>
    <ol>
      <li>${escapeHtml(kernel.premise)}</li>
      <li>${escapeHtml(kernel.complication)}</li>
      <li>${escapeHtml(kernel.claim)}</li>
      <li>${escapeHtml(kernel.action)}</li>
    </ol>
  `;
}

function renderAgentThread(session) {
  const root = document.getElementById("agentThread");
  if (!root) return;
  if (!session.current_message_kernel) {
    root.innerHTML = `<p class="empty">${escapeHtml(t("empty.agent"))}</p>`;
    return;
  }
  ensureAgentGreeting(session);
  root.innerHTML = `
    ${state.chatMessages.map((message) => `
      <div class="chat-message ${escapeHtml(message.role)}">
        <span>${escapeHtml(message.role === "user" ? "You" : "Agent")}</span>
        <p>${escapeHtml(message.text)}</p>
      </div>
    `).join("")}
  `;
  root.scrollTop = root.scrollHeight;
}

async function extractClaims() {
  setBusy("extractClaims", true);
  setStatus("status.savingFreeTalk");
  try {
    await api(`/api/sessions/${state.sessionId}/free-talk`, {
      method: "POST",
      body: JSON.stringify({
        free_talk: document.getElementById("freeTalk").value,
        audience: document.getElementById("audience").value,
        desired_action: document.getElementById("desiredAction").value,
        tone: document.getElementById("tone").value,
      }),
    });
    setStatus("status.extractingClaims");
    const data = await api(`/api/sessions/${state.sessionId}/extract-claims`, {
      method: "POST",
      body: JSON.stringify({ max_candidates: 3 }),
    });
    updateSession(data.session);
    toast(data.recommended_next_question);
    setStatus("status.claimCandidatesReady");
    setStep("claims");
  } catch (error) {
    toast(error.message);
    setStatus(error.code || "error");
  } finally {
    setBusy("extractClaims", false);
  }
}

async function selectClaim(claimId, sourceButton) {
  setStatus("status.selectingClaim");
  document.querySelectorAll("[data-claim]").forEach((button) => {
    button.disabled = true;
  });
  setButtonBusy(sourceButton, true, t("button.selectClaim"));
  try {
    let data = await api(`/api/sessions/${state.sessionId}/select-claim`, {
      method: "POST",
      body: JSON.stringify({ claim_id: claimId }),
    });
    updateSession(data.session);
    data = await api(`/api/sessions/${state.sessionId}/refine-kernel`, {
      method: "POST",
      body: JSON.stringify({ additional_user_input: "" }),
    });
    updateSession(data.session);
    setStatus("status.kernelReady");
    setStep("kernel");
  } catch (error) {
    toast(error.message);
    setStatus(error.code || "error");
  } finally {
    if (sourceButton?.isConnected) {
      setButtonBusy(sourceButton, false, t("button.selectClaim"));
      document.querySelectorAll("[data-claim]").forEach((button) => {
        button.disabled = false;
      });
    }
  }
}

function buildKernelRefinementContext(userMessage, editedKernel) {
  const recentChat = state.chatMessages
    .slice(-8)
    .map((message) => `${message.role}: ${message.text}`)
    .join("\n");
  return [
    "User is continuing a chat with the Agent on the Kernel Studio page.",
    "Use the conversation context to decide whether the 4-Line Message Kernel should be updated.",
    "If the user's message is only a question, answer by improving the diagnosis only when needed; if it clearly asks for changed constraints, specificity, audience, action, or wording, update the kernel.",
    "",
    "Recent chat:",
    recentChat,
    "",
    "Latest user message:",
    userMessage,
    "",
    "Current editable kernel:",
    editedKernel,
  ].join("\n");
}

async function refineKernel(event) {
  event?.preventDefault();
  setBusy("refineKernel", true);
  try {
    const edited = Array.from(document.querySelectorAll("[data-kernel-field]"))
      .map((node) => `${node.dataset.kernelField}: ${node.value}`)
      .join("\n");
    const feedbackNode = document.getElementById("kernelFeedback");
    const userMessage = feedbackNode.value.trim();
    if (!userMessage) return;
    appendChatMessage("user", userMessage);
    const feedback = buildKernelRefinementContext(userMessage, edited);
    const data = await api(`/api/sessions/${state.sessionId}/refine-kernel`, {
      method: "POST",
      body: JSON.stringify({ additional_user_input: feedback }),
    });
    updateSession(data.session);
    feedbackNode.value = "";
    appendChatMessage("agent", t("agent.updatedChat"));
    toast(t("toast.kernelRevised"));
    setStatus("status.kernelRevised");
  } catch (error) {
    toast(error.message);
    setStatus(error.code || "error");
  } finally {
    setBusy("refineKernel", false);
  }
}

async function groundEvidence() {
  setBusy("groundEvidence", true);
  try {
    const data = await runGroundEvidence();
    await refreshIdeaMap();
    toast(data.grounding_summary);
  } catch (error) {
    toast(error.message);
  } finally {
    setBusy("groundEvidence", false);
  }
}

async function runGroundEvidence() {
  const data = await api(`/api/sessions/${state.sessionId}/ground-evidence`, {
    method: "POST",
    body: JSON.stringify({ use_mock_evidence: false }),
  });
  updateSession(data.session);
  return data;
}

function hasGrounding(session) {
  return Boolean(
    (session?.supporting_evidence || []).length
      || (session?.evidence_gaps || []).length
      || (session?.objections || []).length
  );
}

async function refreshIdeaMap() {
  const data = await api(`/api/sessions/${state.sessionId}/generate-idea-map`, {
    method: "POST",
    body: "{}",
  });
  renderIdeaMap(data.idea_map);
  if (data.session) updateSession(data.session);
}

async function generateDeck() {
  setBusy("generateDeck", true);
  try {
    if (!hasGrounding(state.session)) {
      setStatus("status.groundingEvidence");
      await runGroundEvidence();
    }
    setStatus("status.generatingDeck");
    const data = await api(`/api/sessions/${state.sessionId}/generate-deck`, {
      method: "POST",
      body: JSON.stringify({ language: state.locale === "ja" ? "ja-JP" : "en-US", force: false }),
    });
    updateSession(data.session);
    toast(t("toast.deckGenerated"));
    setStatus("status.deckGenerated");
    setStep("outputs");
  } catch (error) {
    toast(error.message);
    setStatus(error.code || "error");
  } finally {
    setBusy("generateDeck", false);
  }
}

async function generateBrief() {
  setBusy("generateBrief", true);
  try {
    const data = await api(`/api/sessions/${state.sessionId}/generate-brief`, {
      method: "POST",
      body: JSON.stringify({ format: "markdown" }),
    });
    updateSession(data.session);
    toast(t("toast.briefGenerated"));
  } catch (error) {
    toast(error.message);
  } finally {
    setBusy("generateBrief", false);
  }
}

async function copyMarkdown() {
  if (!state.markdownUrl) {
    toast(t("toast.copyMarkdownFirst"));
    return;
  }
  const response = await fetch(state.markdownUrl);
  const markdown = await response.text();
  await navigator.clipboard.writeText(markdown);
  toast(t("toast.markdownCopied"));
}

function fillDemo() {
  const sample = samples[state.locale] || samples.ja;
  document.getElementById("freeTalk").value = sample.freeTalk;
  document.getElementById("audience").value = sample.audience;
  document.getElementById("desiredAction").value = sample.desiredAction;
  document.getElementById("tone").value = "executive";
  toast(t("toast.sampleInserted"));
}

function preferredRecordingMimeType() {
  const candidates = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/ogg;codecs=opus"];
  return candidates.find((type) => window.MediaRecorder?.isTypeSupported(type)) || "";
}

async function toggleVoiceInput() {
  if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
    toast(t("toast.voiceUnsupported"));
    return;
  }
  if (state.recorder && state.recorder.state === "recording") {
    state.recorder.stop();
    return;
  }

  try {
    state.recordedChunks = [];
    state.recordingStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mimeType = preferredRecordingMimeType();
    state.recorder = new MediaRecorder(state.recordingStream, mimeType ? { mimeType } : undefined);
    state.recorder.addEventListener("dataavailable", (event) => {
      if (event.data.size > 0) state.recordedChunks.push(event.data);
    });
    state.recorder.addEventListener("stop", () => {
      void uploadRecordedAudio();
    });
    state.recorder.start();
    setVoiceButtonState("recording");
    toast(t("toast.recordingStarted"));
  } catch (error) {
    stopRecordingStream();
    toast(error.message || t("toast.voiceUnsupported"));
    setVoiceButtonState("idle");
  }
}

async function uploadRecordedAudio() {
  setVoiceButtonState("transcribing");
  try {
    stopRecordingStream();
    const mimeType = state.recorder?.mimeType || "audio/webm";
    const blob = new Blob(state.recordedChunks, { type: mimeType });
    const form = new FormData();
    form.append("audio", blob, filenameForMimeType(mimeType));
    form.append("language", state.locale === "ja" ? "ja-JP" : "en-US");
    const response = await fetch("/api/speech/transcribe", { method: "POST", body: form });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.error?.message || `${t("error.requestFailed")}: ${response.status}`);
    }
    appendFreeTalkText(data.text || "");
    toast(t("toast.transcriptionAdded"));
  } catch (error) {
    toast(error.message);
  } finally {
    state.recorder = null;
    state.recordedChunks = [];
    setVoiceButtonState("idle");
  }
}

function stopRecordingStream() {
  state.recordingStream?.getTracks().forEach((track) => track.stop());
  state.recordingStream = null;
}

function appendFreeTalkText(text) {
  const node = document.getElementById("freeTalk");
  const cleaned = text.trim();
  if (!cleaned) return;
  node.value = [node.value.trim(), cleaned].filter(Boolean).join("\n");
  node.focus();
}

function filenameForMimeType(mimeType) {
  if (mimeType.includes("mp4")) return "speech.m4a";
  if (mimeType.includes("ogg")) return "speech.ogg";
  if (mimeType.includes("wav")) return "speech.wav";
  return "speech.webm";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll("`", "&#096;");
}

document.getElementById("demoPreset").addEventListener("click", fillDemo);
document.getElementById("voiceInput").addEventListener("click", toggleVoiceInput);
document.getElementById("extractClaims").addEventListener("click", extractClaims);
document.getElementById("kernelChatForm").addEventListener("submit", refineKernel);
document.getElementById("generateDeck").addEventListener("click", generateDeck);
document.getElementById("generateBrief").addEventListener("click", generateBrief);
document.getElementById("copyMarkdown").addEventListener("click", () => copyMarkdown().catch((error) => toast(error.message)));
document.getElementById("backToFreeTalk").addEventListener("click", () => setStep("freeTalk"));
document.getElementById("backToClaims").addEventListener("click", () => setStep("claims"));
document.getElementById("backToKernel").addEventListener("click", () => setStep("kernel"));
document.querySelectorAll("[data-locale]").forEach((button) => {
  button.addEventListener("click", () => setLocale(button.dataset.locale));
});

applyI18n();
renderCandidates([]);
renderKernel(null);
renderDiagnosis(null);
renderEvidence({});
renderIdeaMap(null);
renderOutputs({});
renderFinalKernel(null);
renderAgentThread({});
setStep("freeTalk");
createSession().catch((error) => {
  setStatus("status.bootError");
  toast(error.message);
});
