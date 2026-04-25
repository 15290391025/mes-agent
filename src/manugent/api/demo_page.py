"""HTML demo page for ManuGent."""

DEMO_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ManuGent MES Agent</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f5f0;
      --bg-elevated: #fbfaf7;
      --surface: #ffffff;
      --surface-muted: #f2f0eb;
      --text: #1d1b16;
      --text-soft: #4e4a42;
      --muted: #777165;
      --border: #ded9cf;
      --border-strong: #c6c0b5;
      --primary: #0f766e;
      --primary-strong: #0b4f49;
      --primary-soft: #dff3ee;
      --warning: #a16207;
      --warning-soft: #fff2c7;
      --danger: #b42318;
      --danger-soft: #fde8e4;
      --ink-shadow: 0 18px 50px rgba(32, 29, 23, 0.12);
      --soft-shadow: 0 10px 30px rgba(32, 29, 23, 0.07);
      --radius-lg: 30px;
      --radius-md: 20px;
      --radius-sm: 14px;
      --ease: cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    * {
      box-sizing: border-box;
    }

    html {
      min-height: 100%;
      background: var(--bg);
    }

    body {
      margin: 0;
      min-height: 100dvh;
      color: var(--text);
      background:
        radial-gradient(circle at 16% 10%, rgba(15, 118, 110, 0.12), transparent 28rem),
        radial-gradient(circle at 82% 2%, rgba(161, 98, 7, 0.10), transparent 22rem),
        linear-gradient(180deg, #fbfaf7 0%, var(--bg) 52%, #efebe3 100%);
      font-family:
        "Noto Sans SC",
        "PingFang SC",
        "Microsoft YaHei",
        ui-sans-serif,
        system-ui,
        sans-serif;
      font-size: 16px;
      line-height: 1.5;
    }

    button,
    textarea {
      font: inherit;
    }

    button {
      touch-action: manipulation;
    }

    button:focus-visible,
    textarea:focus-visible {
      outline: 3px solid rgba(15, 118, 110, 0.28);
      outline-offset: 3px;
    }

    .app-shell {
      width: min(1180px, calc(100vw - 32px));
      min-height: 100dvh;
      margin: 0 auto;
      padding: 24px 0 56px;
    }

    .nav {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: clamp(42px, 7vw, 92px);
    }

    .brand {
      display: inline-flex;
      align-items: center;
      gap: 11px;
      min-height: 44px;
      color: var(--text);
      font-weight: 720;
      letter-spacing: -0.02em;
    }

    .brand-mark {
      width: 34px;
      height: 34px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(15, 118, 110, 0.24);
      border-radius: 12px;
      color: var(--primary-strong);
      background:
        linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(223, 243, 238, 0.95));
      box-shadow: inset 0 -8px 18px rgba(15, 118, 110, 0.08);
      font-size: 13px;
    }

    .nav-meta {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 8px;
      flex-wrap: wrap;
    }

    .pill {
      min-height: 36px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 12px;
      border: 1px solid rgba(198, 192, 181, 0.78);
      border-radius: 999px;
      color: var(--text-soft);
      background: rgba(255, 255, 255, 0.62);
      backdrop-filter: blur(14px);
      font-size: 13px;
      white-space: nowrap;
    }

    .dot {
      width: 7px;
      height: 7px;
      border-radius: 999px;
      background: var(--primary);
      box-shadow: 0 0 0 4px rgba(15, 118, 110, 0.12);
    }

    .hero {
      width: min(820px, 100%);
      margin: 0 auto;
      text-align: center;
    }

    .eyebrow {
      width: fit-content;
      margin: 0 auto 16px;
      padding: 7px 12px;
      border: 1px solid rgba(15, 118, 110, 0.2);
      border-radius: 999px;
      color: var(--primary-strong);
      background: rgba(223, 243, 238, 0.72);
      font-size: 13px;
      font-weight: 680;
    }

    h1 {
      margin: 0;
      color: var(--text);
      font-size: clamp(36px, 6vw, 68px);
      line-height: 1.04;
      letter-spacing: -0.065em;
      font-weight: 760;
      text-wrap: balance;
    }

    .subtitle {
      width: min(650px, 100%);
      margin: 18px auto 0;
      color: var(--muted);
      font-size: clamp(15px, 2vw, 17px);
      line-height: 1.8;
      text-wrap: balance;
    }

    .composer {
      width: min(820px, 100%);
      margin: 34px auto 0;
      border: 1px solid rgba(198, 192, 181, 0.72);
      border-radius: var(--radius-lg);
      background: rgba(255, 255, 255, 0.88);
      box-shadow: var(--ink-shadow);
      overflow: hidden;
      backdrop-filter: blur(22px);
    }

    .composer-main {
      display: grid;
      grid-template-columns: 1fr auto;
      align-items: end;
      gap: 12px;
      padding: 12px;
    }

    .field-label {
      position: absolute;
      width: 1px;
      height: 1px;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
    }

    textarea {
      width: 100%;
      min-height: 84px;
      max-height: 210px;
      resize: vertical;
      border: 0;
      border-radius: 20px;
      outline: 0;
      color: var(--text);
      background: transparent;
      padding: 16px 18px;
      font-size: 16px;
      line-height: 1.65;
    }

    textarea::placeholder {
      color: #9a9386;
    }

    .send-button {
      width: 52px;
      height: 52px;
      display: inline-grid;
      place-items: center;
      border: 0;
      border-radius: 18px;
      color: #fff;
      background: var(--text);
      box-shadow: 0 10px 22px rgba(29, 27, 22, 0.18);
      cursor: pointer;
      transition:
        transform 180ms var(--ease),
        background 180ms var(--ease),
        opacity 180ms var(--ease);
    }

    .send-button:hover {
      background: #302d27;
      transform: translateY(-1px);
    }

    .send-button:active {
      transform: translateY(0) scale(0.98);
    }

    .send-button:disabled {
      cursor: wait;
      opacity: 0.48;
      transform: none;
    }

    .send-button svg {
      width: 20px;
      height: 20px;
      stroke-width: 2.4;
    }

    .prompt-row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      padding: 0 16px 16px;
    }

    .prompt-chip {
      min-height: 38px;
      border: 1px solid var(--border);
      border-radius: 999px;
      color: var(--text-soft);
      background: rgba(242, 240, 235, 0.74);
      padding: 8px 12px;
      cursor: pointer;
      font-size: 13px;
      transition:
        border-color 180ms var(--ease),
        background 180ms var(--ease),
        color 180ms var(--ease);
    }

    .prompt-chip:hover {
      border-color: var(--border-strong);
      color: var(--text);
      background: #fff;
    }

    .response {
      display: grid;
      gap: 18px;
      margin: 36px auto 0;
    }

    .panel {
      border: 1px solid rgba(198, 192, 181, 0.72);
      border-radius: var(--radius-md);
      background: rgba(255, 255, 255, 0.86);
      box-shadow: var(--soft-shadow);
      overflow: hidden;
      backdrop-filter: blur(18px);
    }

    .panel-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      padding: 16px 18px;
      border-bottom: 1px solid rgba(222, 217, 207, 0.72);
    }

    .panel-title {
      margin: 0;
      color: var(--text);
      font-size: 15px;
      font-weight: 720;
      letter-spacing: -0.02em;
    }

    .panel-meta {
      color: var(--muted);
      font-size: 13px;
      text-align: right;
      white-space: nowrap;
    }

    .empty-state {
      display: grid;
      place-items: center;
      min-height: 250px;
      padding: 44px 20px;
      color: var(--muted);
      text-align: center;
    }

    .empty-card {
      width: min(520px, 100%);
    }

    .empty-title {
      margin: 0 0 10px;
      color: var(--text);
      font-size: 20px;
      font-weight: 720;
      letter-spacing: -0.035em;
    }

    .empty-text {
      margin: 0;
      line-height: 1.8;
    }

    .summary {
      padding: clamp(20px, 3vw, 28px);
      color: var(--text);
      font-size: clamp(19px, 2.4vw, 29px);
      line-height: 1.62;
      letter-spacing: -0.045em;
    }

    .confidence {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 34px;
      padding: 6px 10px;
      border: 1px solid rgba(15, 118, 110, 0.2);
      border-radius: 999px;
      color: var(--primary-strong);
      background: var(--primary-soft);
      font-size: 13px;
      font-weight: 700;
    }

    .line-section {
      padding: clamp(18px, 3vw, 28px);
    }

    .line-map {
      position: relative;
      display: grid;
      grid-template-columns: repeat(6, minmax(108px, 1fr));
      gap: 14px;
      min-width: 940px;
      padding: 22px 8px 4px;
    }

    .line-map::before {
      content: "";
      position: absolute;
      left: 8%;
      right: 8%;
      top: 68px;
      height: 2px;
      border-radius: 999px;
      background:
        linear-gradient(90deg, transparent, rgba(15, 118, 110, 0.26), transparent),
        var(--border);
    }

    .station {
      position: relative;
      z-index: 1;
      display: grid;
      justify-items: center;
      gap: 13px;
      animation: rise 420ms var(--ease) both;
      animation-delay: calc(var(--i) * 42ms);
    }

    .orb {
      position: relative;
      width: 92px;
      height: 92px;
      border: 1px solid rgba(198, 192, 181, 0.9);
      border-radius: 999px;
      background:
        radial-gradient(circle at 33% 26%, rgba(255, 255, 255, 0.98) 0 10px, transparent 11px),
        radial-gradient(circle at 68% 72%, rgba(15, 118, 110, 0.20), transparent 38px),
        linear-gradient(145deg, #ffffff, #ece8df);
      box-shadow:
        0 16px 34px rgba(32, 29, 23, 0.14),
        inset 12px 12px 18px rgba(255, 255, 255, 0.95),
        inset -14px -16px 22px rgba(32, 29, 23, 0.08);
    }

    .orb::after {
      content: "";
      position: absolute;
      inset: 14px;
      border-radius: inherit;
      border: 1px solid rgba(255, 255, 255, 0.56);
    }

    .station.signal .orb {
      border-color: rgba(161, 98, 7, 0.34);
      background:
        radial-gradient(circle at 33% 26%, rgba(255, 255, 255, 0.98) 0 10px, transparent 11px),
        radial-gradient(circle at 68% 72%, rgba(161, 98, 7, 0.24), transparent 38px),
        linear-gradient(145deg, #fffdf7, #f5e7bd);
    }

    .station.issue .orb {
      border-color: rgba(180, 35, 24, 0.34);
      background:
        radial-gradient(circle at 33% 26%, rgba(255, 255, 255, 0.98) 0 10px, transparent 11px),
        radial-gradient(circle at 68% 72%, rgba(180, 35, 24, 0.25), transparent 38px),
        linear-gradient(145deg, #fffefe, #f9d9d3);
      box-shadow:
        0 18px 36px rgba(180, 35, 24, 0.16),
        inset 12px 12px 18px rgba(255, 255, 255, 0.95),
        inset -14px -16px 22px rgba(32, 29, 23, 0.07);
    }

    .station-card {
      width: 100%;
      min-height: 164px;
      padding: 13px;
      border: 1px solid var(--border);
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.82);
      box-shadow: 0 8px 20px rgba(32, 29, 23, 0.04);
    }

    .station-code {
      color: var(--muted);
      font-size: 11px;
      font-weight: 760;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .station-name {
      margin-top: 6px;
      color: var(--text);
      font-size: 18px;
      font-weight: 780;
      letter-spacing: -0.04em;
    }

    .station-desc {
      margin-top: 7px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.55;
    }

    .badge {
      width: fit-content;
      margin-top: 12px;
      padding: 5px 8px;
      border-radius: 999px;
      color: var(--primary-strong);
      background: var(--primary-soft);
      font-size: 12px;
      font-weight: 720;
    }

    .badge.signal {
      color: var(--warning);
      background: var(--warning-soft);
    }

    .badge.issue {
      color: var(--danger);
      background: var(--danger-soft);
    }

    .station-note {
      margin-top: 10px;
      color: var(--text-soft);
      font-size: 12px;
      line-height: 1.55;
    }

    .split {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 18px;
    }

    .list {
      display: grid;
      gap: 10px;
      padding: 14px;
    }

    .list-item {
      display: grid;
      gap: 8px;
      padding: 15px;
      border: 1px solid rgba(222, 217, 207, 0.86);
      border-radius: 17px;
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(251, 250, 247, 0.9));
    }

    .item-kicker {
      color: var(--primary-strong);
      font-size: 12px;
      font-weight: 780;
      letter-spacing: 0.01em;
    }

    .item-kicker.boundary {
      color: var(--danger);
    }

    .item-text {
      color: var(--text-soft);
      font-size: 14px;
      line-height: 1.68;
    }

    .toast {
      position: fixed;
      left: 50%;
      bottom: 24px;
      z-index: 10;
      display: none;
      width: min(540px, calc(100vw - 28px));
      transform: translateX(-50%);
      padding: 13px 15px;
      border: 1px solid rgba(180, 35, 24, 0.22);
      border-radius: 16px;
      color: var(--danger);
      background: #fff;
      box-shadow: var(--ink-shadow);
    }

    .toast.show {
      display: block;
    }

    @keyframes rise {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @media (prefers-reduced-motion: reduce) {
      *,
      *::before,
      *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
      }
    }

    @media (max-width: 1040px) {
      .line-section {
        overflow-x: auto;
        padding-bottom: 20px;
      }
      .split {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 760px) {
      .app-shell {
        width: min(100vw - 24px, 1180px);
        padding-top: 16px;
      }
      .nav {
        align-items: flex-start;
        flex-direction: column;
      }
      .hero {
        text-align: left;
      }
      .eyebrow {
        margin-left: 0;
      }
      .composer-main {
        grid-template-columns: 1fr;
      }
      .send-button {
        width: 100%;
        min-height: 52px;
      }
      .panel-head {
        align-items: flex-start;
        flex-direction: column;
      }
      .panel-meta {
        text-align: left;
        white-space: normal;
      }
      .line-map {
        min-width: 0;
        grid-template-columns: 1fr;
      }
      .line-map::before {
        display: none;
      }
      .station {
        grid-template-columns: 92px 1fr;
        align-items: center;
        justify-items: stretch;
      }
    }
  </style>
</head>
<body>
  <main class="app-shell">
    <header class="nav" aria-label="页面信息">
      <div class="brand" aria-label="ManuGent">
        <div class="brand-mark" aria-hidden="true">MG</div>
        <span>ManuGent</span>
      </div>
      <div class="nav-meta" aria-label="能力标签">
        <span class="pill"><span class="dot" aria-hidden="true"></span>MES Agent</span>
        <span class="pill">Workflow Registry</span>
        <span class="pill">Evidence Chain</span>
      </div>
    </header>

    <section class="hero" aria-labelledby="page-title">
      <div class="eyebrow">AI manufacturing copilot</div>
      <h1 id="page-title">用一句话定位产线异常。</h1>
      <p class="subtitle">
        输入现场问题，ManuGent 会调用 MES workflow，把生产、质量、物料、设备和历史记忆
        汇总成可解释的证据链，并映射到具体工序节点。
      </p>
    </section>

    <section class="composer" aria-label="MES 问题输入">
      <div class="composer-main">
        <label class="field-label" for="question">MES 现场问题</label>
        <textarea
          id="question"
          placeholder="例如：SMT-03 最近 24 小时良率为什么下降？"
        >SMT-03 最近 24 小时良率为什么下降？</textarea>
        <button
          id="run-button"
          class="send-button"
          onclick="runWorkflow()"
          aria-label="开始分析"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true">
            <path d="M12 19V5"></path>
            <path d="m5 12 7-7 7 7"></path>
          </svg>
        </button>
      </div>
      <div class="prompt-row" aria-label="示例问题">
        <button class="prompt-chip" onclick="useExample('SMT-03 最近 24 小时良率为什么下降？')">
          良率下降
        </button>
        <button
          class="prompt-chip"
          onclick="useExample('帮我分析 SMT-03 今天 AOI 缺陷集中在哪个环节')"
        >
          AOI 缺陷集中
        </button>
        <button
          class="prompt-chip"
          onclick="useExample('SMT-03 最近是不是设备和物料一起影响了质量？')"
        >
          设备与物料关联
        </button>
      </div>
    </section>

    <section id="response" class="response" aria-live="polite">
      <article class="panel">
        <div class="empty-state">
          <div class="empty-card">
            <h2 class="empty-title">等待一次制造诊断</h2>
            <p class="empty-text">
              系统会自动识别产线和时间范围，运行良率下降 RCA workflow，
              然后生成结论、产线节点、证据链和建议动作。
            </p>
          </div>
        </div>
      </article>
    </section>
  </main>

  <div id="error" class="toast" role="alert"></div>

  <script>
    const stations = [
      {
        id: "printer",
        code: "ST-01",
        name: "印刷",
        desc: "锡膏印刷 / 物料批次输入",
        evidenceTypes: ["material"]
      },
      {
        id: "spi",
        code: "ST-02",
        name: "SPI",
        desc: "锡膏厚度 / 早期质量信号",
        evidenceTypes: ["production", "quality", "material"]
      },
      {
        id: "mounter",
        code: "ST-03",
        name: "贴片",
        desc: "MOUNTER-03A / 吸嘴与飞达",
        evidenceTypes: ["equipment"]
      },
      {
        id: "reflow",
        code: "ST-04",
        name: "回流焊",
        desc: "温区曲线 / 焊接窗口",
        evidenceTypes: []
      },
      {
        id: "aoi",
        code: "ST-05",
        name: "AOI",
        desc: "缺陷检出 / 良率结果",
        evidenceTypes: ["quality", "production"]
      },
      {
        id: "pack",
        code: "ST-06",
        name: "包装",
        desc: "放行 / 返工 / 出货",
        evidenceTypes: []
      }
    ];

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function inferLineId(question) {
      const match = question.match(/[A-Z]{2,5}-\\d{1,3}/i);
      return match ? match[0].toUpperCase() : "SMT-03";
    }

    function inferTimeRange(question) {
      if (question.includes("7天") || question.includes("一周")) return "7d";
      if (question.includes("今天")) return "today";
      return "24h";
    }

    function useExample(text) {
      const input = document.getElementById("question");
      input.value = text;
      input.focus();
    }

    function setLoading(isLoading) {
      const button = document.getElementById("run-button");
      button.disabled = isLoading;
      button.innerHTML = isLoading
        ? `<span aria-hidden="true">...</span>`
        : `
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true">
            <path d="M12 19V5"></path>
            <path d="m5 12 7-7 7 7"></path>
          </svg>
        `;
    }

    function setError(message) {
      const error = document.getElementById("error");
      error.textContent = message || "";
      error.classList.toggle("show", Boolean(message));
    }

    function stationStatus(station, evidence) {
      const related = evidence.filter(item => station.evidenceTypes.includes(item.type));
      if (!related.length) return { status: "ok", related };
      if (related.some(item => ["quality", "equipment", "material"].includes(item.type))) {
        return { status: "issue", related };
      }
      return { status: "signal", related };
    }

    function renderLineMap(report) {
      const evidence = report.evidence || [];
      return stations.map((station, index) => {
        const result = stationStatus(station, evidence);
        const stateText = {
          ok: "稳定",
          signal: "波动",
          issue: "异常关联"
        }[result.status];
        const note = result.related[0]?.summary || "当前证据未直接指向该节点。";

        return `
          <div
            class="station ${result.status}"
            style="--i:${index}"
            data-station="${station.id}"
          >
            <div class="orb" aria-hidden="true"></div>
            <div class="station-card">
              <div class="station-code">${station.code}</div>
              <div class="station-name">${station.name}</div>
              <div class="station-desc">${station.desc}</div>
              <div class="badge ${result.status}">${stateText}</div>
              <div class="station-note">${escapeHtml(note)}</div>
            </div>
          </div>
        `;
      }).join("");
    }

    function renderEvidence(report) {
      return (report.evidence || []).map(item => `
        <div class="list-item">
          <div class="item-kicker">
            ${escapeHtml(item.type)} / ${escapeHtml(item.source_tool)}
          </div>
          <div class="item-text">${escapeHtml(item.summary)}</div>
        </div>
      `).join("");
    }

    function renderActions(report) {
      return (report.recommendations || []).map(item => `
        <div class="list-item">
          <div class="item-kicker ${item.requires_approval ? "boundary" : ""}">
            ${item.requires_approval ? "生产控制边界" : "建议动作"} / ${escapeHtml(item.owner)}
          </div>
          <div class="item-text">${escapeHtml(item.action)}</div>
          <div class="item-text">${escapeHtml(item.rationale || "基于当前证据链生成。")}</div>
        </div>
      `).join("");
    }

    function renderReport(report, lineId, timeRange) {
      const confidence = Math.round((report.confidence || 0) * 100);
      document.getElementById("response").innerHTML = `
        <article class="panel">
          <div class="panel-head">
            <h2 class="panel-title">分析结论</h2>
            <span class="confidence">${confidence}% confidence</span>
          </div>
          <div class="summary">${escapeHtml(report.finding)}</div>
        </article>

        <article class="panel">
          <div class="panel-head">
            <h2 class="panel-title">产线节点</h2>
            <span class="panel-meta">${escapeHtml(lineId)} / ${escapeHtml(timeRange)}</span>
          </div>
          <div class="line-section">
            <div class="line-map">${renderLineMap(report)}</div>
          </div>
        </article>

        <section class="split">
          <article class="panel">
            <div class="panel-head">
              <h2 class="panel-title">证据链</h2>
              <span class="panel-meta">${(report.evidence || []).length} 条证据</span>
            </div>
            <div class="list">${renderEvidence(report)}</div>
          </article>
          <article class="panel">
            <div class="panel-head">
              <h2 class="panel-title">建议动作</h2>
              <span class="panel-meta">${(report.recommendations || []).length} 条建议</span>
            </div>
            <div class="list">${renderActions(report)}</div>
          </article>
        </section>
      `;
    }

    async function runWorkflow() {
      const question = document.getElementById("question").value.trim();
      const lineId = inferLineId(question);
      const timeRange = inferTimeRange(question);

      if (!question) {
        setError("请先输入一个 MES 现场问题。");
        return;
      }

      setError("");
      setLoading(true);

      try {
        const response = await fetch("/workflows/yield_drop/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            params: {
              line_id: lineId,
              time_range: timeRange
            },
            session_id: "web-demo"
          })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const payload = await response.json();
        renderReport(payload.result, lineId, timeRange);
      } catch (error) {
        setError(`分析失败：${error.message}`);
      } finally {
        setLoading(false);
      }
    }

    document.getElementById("question").addEventListener("keydown", event => {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        runWorkflow();
      }
    });
  </script>
</body>
</html>
"""
