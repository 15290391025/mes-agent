"""HTML demo page for ManuGent."""

DEMO_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ManuGent MES Agent</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/p5.min.js"></script>
  <style>
    :root {
      --void: #02030a;
      --glass: rgba(8, 14, 30, 0.68);
      --line: rgba(118, 194, 255, 0.24);
      --text: #f5fbff;
      --muted: #8da4ba;
      --cyan: #31e7ff;
      --violet: #9b6cff;
      --amber: #ffb84d;
      --red: #ff4d6d;
      --green: #37f29b;
    }

    * { box-sizing: border-box; }
    html { background: var(--void); }

    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      background:
        radial-gradient(circle at 50% -10%, rgba(49, 231, 255, 0.22), transparent 34rem),
        radial-gradient(circle at 16% 8%, rgba(155, 108, 255, 0.22), transparent 28rem),
        radial-gradient(circle at 84% 12%, rgba(255, 77, 109, 0.16), transparent 24rem),
        linear-gradient(180deg, #02030a 0%, #071020 56%, #02030a 100%);
      font-family: "Segoe UI", "Noto Sans SC", system-ui, sans-serif;
      overflow-x: hidden;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      z-index: 0;
      pointer-events: none;
      background:
        linear-gradient(rgba(49, 231, 255, 0.055) 1px, transparent 1px),
        linear-gradient(90deg, rgba(49, 231, 255, 0.04) 1px, transparent 1px);
      background-size: 64px 64px;
      mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.75), transparent 82%);
      transform: perspective(900px) rotateX(62deg) translateY(-20vh);
      transform-origin: top;
    }

    #factory-field {
      position: fixed;
      inset: 0;
      z-index: 0;
      pointer-events: none;
      opacity: 0.92;
    }

    .shell {
      position: relative;
      z-index: 1;
      width: min(1280px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 26px 0 58px;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 58px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      color: var(--text);
      font-weight: 800;
      letter-spacing: -0.03em;
    }

    .mark {
      width: 36px;
      height: 36px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(49, 231, 255, 0.48);
      border-radius: 12px;
      color: var(--cyan);
      background:
        linear-gradient(145deg, rgba(49, 231, 255, 0.2), rgba(155, 108, 255, 0.12)),
        rgba(255, 255, 255, 0.035);
      box-shadow:
        0 0 34px rgba(49, 231, 255, 0.22),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }

    .top-meta {
      display: flex;
      gap: 9px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .top-meta span {
      padding: 7px 10px;
      border: 1px solid rgba(118, 194, 255, 0.18);
      border-radius: 999px;
      color: #aac4d8;
      background: rgba(255, 255, 255, 0.035);
      font-size: 12px;
      backdrop-filter: blur(16px);
    }

    .hero {
      max-width: 940px;
      margin: 0 auto 28px;
      text-align: center;
    }

    h1 {
      margin: 0;
      font-size: clamp(46px, 8vw, 96px);
      line-height: 0.92;
      letter-spacing: -0.08em;
      font-weight: 850;
      text-wrap: balance;
      text-shadow: 0 0 44px rgba(49, 231, 255, 0.22);
    }

    .hero strong {
      color: transparent;
      background: linear-gradient(90deg, var(--cyan), #f5fbff, var(--violet));
      -webkit-background-clip: text;
      background-clip: text;
    }

    .subtitle {
      max-width: 720px;
      margin: 24px auto 0;
      color: var(--muted);
      font-size: 17px;
      line-height: 1.85;
    }

    .ask {
      max-width: 900px;
      margin: 34px auto 0;
      border: 1px solid rgba(118, 194, 255, 0.24);
      border-radius: 28px;
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.09), rgba(255, 255, 255, 0.025)),
        rgba(4, 9, 22, 0.76);
      box-shadow:
        0 30px 90px rgba(0, 0, 0, 0.52),
        0 0 70px rgba(49, 231, 255, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(24px);
      overflow: hidden;
    }

    .input-row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 12px;
      align-items: end;
      padding: 14px;
    }

    textarea {
      width: 100%;
      min-height: 86px;
      max-height: 190px;
      resize: vertical;
      border: 0;
      outline: 0;
      padding: 17px 18px;
      color: var(--text);
      background: transparent;
      font: inherit;
      font-size: 17px;
      line-height: 1.75;
    }

    textarea::placeholder { color: #61798f; }

    .run {
      width: 86px;
      height: 60px;
      border: 1px solid rgba(49, 231, 255, 0.42);
      border-radius: 20px;
      color: #001018;
      background: linear-gradient(135deg, #64f3ff, #37f29b 54%, #a5ffcb);
      cursor: pointer;
      font: 900 14px "Segoe UI", sans-serif;
      box-shadow:
        0 18px 44px rgba(49, 231, 255, 0.28),
        inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }

    .run:disabled {
      cursor: wait;
      opacity: 0.62;
      filter: grayscale(0.4);
    }

    .prompts {
      display: flex;
      gap: 9px;
      flex-wrap: wrap;
      padding: 0 16px 16px;
    }

    .chip {
      border: 1px solid rgba(118, 194, 255, 0.18);
      border-radius: 999px;
      color: #a8c6dd;
      background: rgba(255, 255, 255, 0.035);
      padding: 8px 11px;
      cursor: pointer;
      font: 700 12px "Segoe UI", sans-serif;
    }

    .chip:hover {
      color: var(--cyan);
      border-color: rgba(49, 231, 255, 0.48);
      box-shadow: 0 0 24px rgba(49, 231, 255, 0.12);
    }

    .answer {
      display: grid;
      gap: 18px;
      margin-top: 34px;
    }

    .panel {
      border: 1px solid rgba(118, 194, 255, 0.18);
      border-radius: 28px;
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.07), rgba(255, 255, 255, 0.018)),
        var(--glass);
      box-shadow: 0 24px 80px rgba(0, 0, 0, 0.38);
      backdrop-filter: blur(22px);
      overflow: hidden;
    }

    .panel-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      padding: 17px 20px;
      border-bottom: 1px solid rgba(118, 194, 255, 0.14);
    }

    .panel-head h2 {
      margin: 0;
      font-size: 14px;
      font-weight: 850;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }

    .meta {
      color: var(--muted);
      font-size: 12px;
      text-align: right;
    }

    .summary {
      padding: 24px 24px 28px;
      color: #eaf9ff;
      font-size: clamp(21px, 2.15vw, 30px);
      line-height: 1.58;
      letter-spacing: -0.045em;
    }

    .line-wrap {
      padding: 32px 24px 44px;
      overflow-x: auto;
      perspective: 1400px;
      perspective-origin: 50% 20%;
    }

    .line-stage {
      position: relative;
      min-width: 1060px;
      display: grid;
      grid-template-columns: repeat(6, minmax(150px, 1fr));
      gap: 22px;
      padding: 54px 10px 30px;
      transform-style: preserve-3d;
      transform: rotateX(58deg) rotateZ(-3deg);
    }

    .line-stage::before {
      content: "";
      position: absolute;
      left: 2%;
      right: 2%;
      top: 126px;
      height: 18px;
      border-radius: 999px;
      background:
        linear-gradient(90deg, transparent, rgba(49, 231, 255, 0.85), transparent),
        linear-gradient(180deg, rgba(255, 255, 255, 0.32), rgba(49, 231, 255, 0.12));
      box-shadow:
        0 0 34px rgba(49, 231, 255, 0.42),
        0 30px 80px rgba(49, 231, 255, 0.18);
      transform: translateZ(-40px);
    }

    .station {
      position: relative;
      min-height: 220px;
      transform-style: preserve-3d;
      transform: translateZ(34px);
      animation: floatNode 5.8s ease-in-out infinite;
    }

    .station:nth-child(2) { animation-delay: -0.8s; }
    .station:nth-child(3) { animation-delay: -1.6s; }
    .station:nth-child(4) { animation-delay: -2.4s; }
    .station:nth-child(5) { animation-delay: -3.2s; }
    .station:nth-child(6) { animation-delay: -4s; }

    @keyframes floatNode {
      0%, 100% { transform: translateZ(34px) translateY(0); }
      50% { transform: translateZ(52px) translateY(-8px); }
    }

    .machine {
      position: absolute;
      inset: 0;
      border: 1px solid rgba(118, 194, 255, 0.28);
      border-radius: 22px;
      background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.025) 45%),
        linear-gradient(180deg, rgba(13, 34, 62, 0.96), rgba(4, 10, 24, 0.98));
      box-shadow:
        0 24px 60px rgba(0, 0, 0, 0.46),
        0 0 44px rgba(49, 231, 255, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
      transform-style: preserve-3d;
      overflow: hidden;
    }

    .machine::before {
      content: "";
      position: absolute;
      inset: 0;
      background:
        linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.12), transparent),
        radial-gradient(circle at 78% 16%, rgba(49, 231, 255, 0.28), transparent 8rem);
      transform: translateX(-70%);
      animation: sweep 4.8s ease-in-out infinite;
    }

    @keyframes sweep {
      0%, 44% { transform: translateX(-85%); opacity: 0; }
      58% { opacity: 1; }
      100% { transform: translateX(85%); opacity: 0; }
    }

    .machine::after {
      content: "";
      position: absolute;
      left: 12px;
      right: 12px;
      bottom: -24px;
      height: 52px;
      border-radius: 50%;
      background: rgba(49, 231, 255, 0.2);
      filter: blur(24px);
      transform: translateZ(-60px);
    }

    .station.issue .machine {
      border-color: rgba(255, 77, 109, 0.74);
      box-shadow:
        0 28px 80px rgba(0, 0, 0, 0.52),
        0 0 70px rgba(255, 77, 109, 0.32),
        inset 0 1px 0 rgba(255, 255, 255, 0.22);
    }

    .station.issue .machine::after { background: rgba(255, 77, 109, 0.44); }

    .station.signal .machine {
      border-color: rgba(255, 184, 77, 0.66);
      box-shadow:
        0 28px 70px rgba(0, 0, 0, 0.48),
        0 0 58px rgba(255, 184, 77, 0.24),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }

    .machine-face {
      position: relative;
      z-index: 1;
      height: 100%;
      padding: 16px;
      transform: rotateX(-58deg) rotateZ(3deg) translateY(20px);
      transform-origin: 50% 0;
    }

    .station-code {
      color: var(--cyan);
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 11px;
      letter-spacing: 0.08em;
    }

    .station-name {
      margin-top: 8px;
      color: var(--text);
      font-size: 23px;
      font-weight: 900;
      letter-spacing: -0.05em;
      text-shadow: 0 0 22px rgba(49, 231, 255, 0.18);
    }

    .station-desc {
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.55;
    }

    .state {
      display: inline-flex;
      margin-top: 12px;
      padding: 6px 8px;
      border-radius: 999px;
      color: #031018;
      background: var(--green);
      font-size: 11px;
      font-weight: 900;
    }

    .state.issue { color: white; background: var(--red); }
    .state.signal { color: #160d00; background: var(--amber); }

    .node-note {
      margin-top: 12px;
      color: #d9f6ff;
      font-size: 12px;
      line-height: 1.58;
    }

    .details {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }

    .list {
      display: grid;
      gap: 11px;
      padding: 17px;
    }

    .item {
      padding: 15px;
      border: 1px solid rgba(118, 194, 255, 0.16);
      border-radius: 18px;
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.055), rgba(255, 255, 255, 0.02)),
        rgba(5, 12, 27, 0.74);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }

    .item-type {
      margin-bottom: 8px;
      color: var(--cyan);
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 11px;
      text-transform: uppercase;
    }

    .item-type.boundary { color: var(--red); }

    .item-text {
      color: #d8e9f3;
      font-size: 13px;
      line-height: 1.68;
    }

    .empty {
      padding: 54px 20px;
      color: var(--muted);
      text-align: center;
      line-height: 1.85;
    }

    .toast {
      display: none;
      position: fixed;
      left: 50%;
      bottom: 24px;
      z-index: 5;
      transform: translateX(-50%);
      max-width: min(520px, calc(100vw - 28px));
      padding: 12px 14px;
      border: 1px solid rgba(255, 77, 109, 0.42);
      border-radius: 14px;
      color: #ffecec;
      background: rgba(80, 12, 28, 0.92);
      box-shadow: 0 16px 50px rgba(0, 0, 0, 0.38);
    }

    .toast.show { display: block; }

    @media (max-width: 980px) {
      .line-wrap { perspective: none; }
      .line-stage {
        min-width: 0;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        transform: none;
      }
      .line-stage::before { display: none; }
      .station,
      .station:nth-child(n) {
        transform: none;
        animation: none;
      }
      .machine-face { transform: none; }
      .details { grid-template-columns: 1fr; }
    }

    @media (max-width: 700px) {
      .topbar { align-items: flex-start; flex-direction: column; margin-bottom: 44px; }
      .input-row { grid-template-columns: 1fr; }
      .run { width: 100%; }
      .line-stage { grid-template-columns: 1fr; }
      .hero { text-align: left; }
    }
  </style>
</head>
<body>
  <div id="factory-field"></div>

  <main class="shell">
    <header class="topbar">
      <div class="brand">
        <div class="mark">M</div>
        <div>ManuGent</div>
      </div>
      <div class="top-meta">
        <span>3D MES Line</span>
        <span>LangGraph RCA</span>
        <span>AI Evidence Overlay</span>
      </div>
    </header>

    <section class="hero">
      <h1>Ask the MES.<br><strong>See the line in 3D.</strong></h1>
      <p class="subtitle">
        用一句自然语言询问现场，ManuGent 将良率、缺陷、物料批次、设备告警和历史记忆
        投射到立体产线节点上，直接看到问题发生在哪一段流程。
      </p>
    </section>

    <section class="ask">
      <div class="input-row">
        <textarea
          id="question"
          placeholder="例如：SMT-03 最近 24 小时良率为什么下降？"
        >SMT-03 最近 24 小时良率为什么下降？</textarea>
        <button id="run-button" class="run" onclick="runRca()">分析</button>
      </div>
      <div class="prompts">
        <button class="chip" onclick="useExample('SMT-03 最近 24 小时良率为什么下降？')">
          良率下降
        </button>
        <button class="chip" onclick="useExample('帮我分析 SMT-03 今天 AOI 缺陷集中在哪个环节')">
          AOI 缺陷
        </button>
        <button class="chip" onclick="useExample('SMT-03 最近是不是设备和物料一起影响了质量？')">
          设备 + 物料
        </button>
      </div>
    </section>

    <section id="answer" class="answer">
      <article class="panel">
        <div class="empty">
          输入 MES 现场问题后，系统会生成 3D 产线视图，并把异常、证据和建议挂到设备节点上。
        </div>
      </article>
    </section>
  </main>

  <div id="error" class="toast"></div>

  <script>
    window.manuState = { active: false, issueNodes: [] };

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
      document.getElementById("question").value = text;
      document.getElementById("question").focus();
    }

    function setLoading(isLoading) {
      const button = document.getElementById("run-button");
      button.disabled = isLoading;
      button.textContent = isLoading ? "扫描中" : "分析";
      window.manuState.active = isLoading;
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

    function renderLineMap(data) {
      const evidence = data.evidence || [];
      const issueNodes = [];
      const html = stations.map(station => {
        const result = stationStatus(station, evidence);
        const stateText = {
          ok: "稳定",
          signal: "波动",
          issue: "异常关联"
        }[result.status];
        const note = result.related[0]?.summary || "当前问题未直接指向该节点。";
        if (result.status === "issue") issueNodes.push(station.id);

        return `
          <div class="station ${result.status}" data-station="${station.id}">
            <div class="machine">
              <div class="machine-face">
                <div class="station-code">${station.code}</div>
                <div class="station-name">${station.name}</div>
                <div class="station-desc">${station.desc}</div>
                <div class="state ${result.status}">${stateText}</div>
                <div class="node-note">${escapeHtml(note)}</div>
              </div>
            </div>
          </div>
        `;
      }).join("");
      window.manuState.issueNodes = issueNodes;
      return html;
    }

    function renderEvidence(data) {
      return (data.evidence || []).map(item => `
        <div class="item">
          <div class="item-type">${escapeHtml(item.type)} · ${escapeHtml(item.source_tool)}</div>
          <div class="item-text">${escapeHtml(item.summary)}</div>
        </div>
      `).join("");
    }

    function renderActions(data) {
      return (data.recommendations || []).map(item => `
        <div class="item">
          <div class="item-type ${item.requires_approval ? "boundary" : ""}">
            ${item.requires_approval ? "生产控制边界" : "建议动作"} · ${escapeHtml(item.owner)}
          </div>
          <div class="item-text">${escapeHtml(item.action)}</div>
          <div class="item-text" style="color:var(--muted);margin-top:6px;">
            ${escapeHtml(item.rationale || "基于当前证据链生成。")}
          </div>
        </div>
      `).join("");
    }

    function renderReport(data, lineId, timeRange) {
      const confidence = Math.round((data.confidence || 0) * 100);
      document.getElementById("answer").innerHTML = `
        <article class="panel">
          <div class="panel-head">
            <h2>AI 分析结论</h2>
            <span class="meta">${escapeHtml(lineId)} · ${escapeHtml(timeRange)}
              · ${confidence}% confidence</span>
          </div>
          <div class="summary">${escapeHtml(data.finding)}</div>
        </article>

        <article class="panel">
          <div class="panel-head">
            <h2>3D MES 流程节点</h2>
            <span class="meta">异常证据会贴到对应立体设备节点</span>
          </div>
          <div class="line-wrap">
            <div class="line-stage">${renderLineMap(data)}</div>
          </div>
        </article>

        <section class="details">
          <article class="panel">
            <div class="panel-head">
              <h2>证据链</h2>
              <span class="meta">${(data.evidence || []).length} records</span>
            </div>
            <div class="list">${renderEvidence(data)}</div>
          </article>
          <article class="panel">
            <div class="panel-head">
              <h2>建议动作</h2>
              <span class="meta">${(data.recommendations || []).length} actions</span>
            </div>
            <div class="list">${renderActions(data)}</div>
          </article>
        </section>
      `;
      window.manuState.active = true;
    }

    async function runRca() {
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
        const response = await fetch("/workflows/root-cause/yield-drop", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            line_id: lineId,
            time_range: timeRange,
            session_id: "web-demo"
          })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        renderReport(data, lineId, timeRange);
      } catch (error) {
        setError(`分析失败：${error.message}`);
        window.manuState.active = false;
      } finally {
        setLoading(false);
      }
    }

    document.getElementById("question").addEventListener("keydown", event => {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        runRca();
      }
    });

    let stars = [];
    let beams = [];

    function setup() {
      const canvas = createCanvas(windowWidth, windowHeight, WEBGL);
      canvas.parent("factory-field");
      pixelDensity(1);
      for (let i = 0; i < 170; i++) {
        stars.push({
          x: random(-width, width),
          y: random(-height, height),
          z: random(-900, 220),
          size: random(1, 3),
          speed: random(0.8, 3.2)
        });
      }
      for (let i = 0; i < 24; i++) {
        beams.push({
          x: random(-width, width),
          z: random(-700, 200),
          offset: random(TAU),
          speed: random(0.006, 0.018)
        });
      }
    }

    function drawGrid() {
      push();
      rotateX(PI / 2.2);
      translate(0, 280, -260);
      stroke(49, 231, 255, 34);
      strokeWeight(1);
      for (let i = -1200; i <= 1200; i += 80) {
        line(i, -900, i, 900);
        line(-1200, i, 1200, i);
      }
      pop();
    }

    function draw() {
      clear();
      const activeBoost = window.manuState.active ? 2.6 : 1;
      ambientLight(18, 32, 48);
      pointLight(49, 231, 255, -240, -160, 260);
      pointLight(155, 108, 255, 260, -120, 140);
      drawGrid();

      noStroke();
      for (const star of stars) {
        star.z += star.speed * activeBoost;
        if (star.z > 260) {
          star.z = -900;
          star.x = random(-width, width);
          star.y = random(-height, height);
        }
        push();
        translate(star.x, star.y, star.z);
        fill(49, 231, 255, window.manuState.active ? 190 : 96);
        sphere(star.size, 6, 4);
        pop();
      }

      for (const beam of beams) {
        const y = sin(frameCount * beam.speed + beam.offset) * 180;
        push();
        translate(beam.x, y, beam.z);
        rotateZ(frameCount * 0.002 + beam.offset);
        stroke(49, 231, 255, window.manuState.active ? 70 : 28);
        strokeWeight(1.2);
        line(-120, 0, 120, 0);
        pop();
      }

      if (window.manuState.issueNodes.length) {
        push();
        noFill();
        stroke(255, 77, 109, 90 + sin(frameCount * 0.08) * 55);
        strokeWeight(2);
        rotateX(frameCount * 0.006);
        rotateY(frameCount * 0.008);
        torus(190 + sin(frameCount * 0.04) * 18, 1.8, 90, 8);
        pop();
      }
    }

    function windowResized() {
      resizeCanvas(windowWidth, windowHeight);
    }
  </script>
</body>
</html>
"""
