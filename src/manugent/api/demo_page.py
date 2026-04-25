"""HTML demo page for ManuGent."""

DEMO_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ManuGent MES Agent</title>
  <style>
    :root {
      --bg: #f7f3ea;
      --panel: #fffdf7;
      --ink: #1b2622;
      --muted: #6e7a73;
      --line: #ded5c5;
      --soft: #eee7d8;
      --green: #17734f;
      --amber: #c77a25;
      --red: #b44444;
      --blue: #315f86;
      --shadow: 0 24px 70px rgba(30, 25, 16, 0.12);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      font-family: ui-serif, "Noto Serif SC", "Songti SC", Georgia, serif;
      background:
        radial-gradient(circle at 15% 5%, rgba(199, 122, 37, 0.18), transparent 26rem),
        radial-gradient(circle at 85% 10%, rgba(23, 115, 79, 0.14), transparent 24rem),
        linear-gradient(135deg, #f9f6ee 0%, #efe5d2 100%);
    }

    button,
    textarea {
      font: inherit;
    }

    .shell {
      width: min(1160px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 48px;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 36px;
      color: #37443e;
      font-family: ui-sans-serif, "Noto Sans SC", system-ui, sans-serif;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 800;
      letter-spacing: -0.03em;
    }

    .mark {
      width: 30px;
      height: 30px;
      display: grid;
      place-items: center;
      color: #fff8e8;
      background: var(--green);
      border-radius: 10px;
      font-size: 13px;
      box-shadow: 0 10px 24px rgba(23, 115, 79, 0.24);
    }

    .topbar span {
      color: var(--muted);
      font-size: 13px;
    }

    .hero {
      text-align: center;
      margin: 0 auto 26px;
      max-width: 860px;
    }

    h1 {
      margin: 0;
      font-size: clamp(42px, 7vw, 78px);
      line-height: 0.96;
      letter-spacing: -0.07em;
      font-weight: 760;
    }

    .subtitle {
      max-width: 680px;
      margin: 18px auto 0;
      color: var(--muted);
      font-size: 18px;
      line-height: 1.8;
    }

    .ask-card {
      position: sticky;
      top: 16px;
      z-index: 2;
      margin: 0 auto;
      max-width: 900px;
      padding: 12px;
      border: 1px solid rgba(39, 48, 43, 0.12);
      border-radius: 28px;
      background: rgba(255, 253, 247, 0.88);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
    }

    .composer {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: end;
    }

    textarea {
      width: 100%;
      min-height: 62px;
      max-height: 180px;
      resize: vertical;
      border: 0;
      outline: 0;
      padding: 16px 18px;
      color: var(--ink);
      background: transparent;
      font-size: 17px;
      line-height: 1.7;
    }

    .run-button {
      min-width: 112px;
      height: 54px;
      border: 0;
      border-radius: 18px;
      color: #fff8e8;
      background: linear-gradient(135deg, var(--green), #0c4f36);
      cursor: pointer;
      font-family: ui-sans-serif, "Noto Sans SC", system-ui, sans-serif;
      font-weight: 800;
      box-shadow: 0 14px 26px rgba(23, 115, 79, 0.22);
    }

    .run-button:disabled {
      cursor: wait;
      opacity: 0.62;
    }

    .examples {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      padding: 2px 8px 8px;
      font-family: ui-sans-serif, "Noto Sans SC", system-ui, sans-serif;
    }

    .chip {
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fffaf0;
      color: #58645e;
      padding: 7px 10px;
      cursor: pointer;
      font-size: 12px;
    }

    .chip:hover {
      color: var(--green);
      border-color: rgba(23, 115, 79, 0.32);
    }

    .answer {
      display: grid;
      gap: 18px;
      margin-top: 34px;
    }

    .panel {
      border: 1px solid rgba(39, 48, 43, 0.12);
      border-radius: 30px;
      background: rgba(255, 253, 247, 0.78);
      box-shadow: 0 16px 46px rgba(30, 25, 16, 0.08);
      overflow: hidden;
    }

    .panel-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 22px;
      border-bottom: 1px solid rgba(39, 48, 43, 0.09);
      font-family: ui-sans-serif, "Noto Sans SC", system-ui, sans-serif;
    }

    .panel-head h2 {
      margin: 0;
      font-size: 16px;
      letter-spacing: -0.02em;
    }

    .meta {
      color: var(--muted);
      font-size: 13px;
    }

    .summary {
      padding: 24px;
      font-size: clamp(20px, 2.4vw, 30px);
      line-height: 1.55;
      letter-spacing: -0.04em;
    }

    .line-map {
      padding: 24px;
    }

    .line-track {
      display: grid;
      grid-template-columns: repeat(6, minmax(120px, 1fr));
      gap: 12px;
      position: relative;
    }

    .station {
      position: relative;
      min-height: 176px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 22px;
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(246, 238, 220, 0.72));
    }

    .station::after {
      content: "";
      position: absolute;
      top: 42px;
      right: -18px;
      width: 24px;
      height: 1px;
      background: var(--line);
    }

    .station:last-child::after {
      display: none;
    }

    .station.issue {
      border-color: rgba(180, 68, 68, 0.5);
      background:
        radial-gradient(circle at 80% 10%, rgba(180, 68, 68, 0.18), transparent 7rem),
        linear-gradient(180deg, #fffdf7, #f6eadb);
    }

    .station.warning {
      border-color: rgba(199, 122, 37, 0.5);
      background:
        radial-gradient(circle at 80% 10%, rgba(199, 122, 37, 0.18), transparent 7rem),
        linear-gradient(180deg, #fffdf7, #f6eadb);
    }

    .station.ok {
      border-color: rgba(23, 115, 79, 0.24);
    }

    .station-code {
      color: var(--muted);
      font-family: ui-sans-serif, "Noto Sans SC", system-ui, sans-serif;
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .station-name {
      margin-top: 8px;
      font-size: 20px;
      font-weight: 760;
      letter-spacing: -0.04em;
    }

    .station-desc {
      margin-top: 8px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.55;
    }

    .badge {
      display: inline-flex;
      margin-top: 12px;
      padding: 6px 8px;
      border-radius: 999px;
      font-family: ui-sans-serif, "Noto Sans SC", system-ui, sans-serif;
      font-size: 11px;
      font-weight: 800;
    }

    .badge.issue {
      color: #7d2020;
      background: rgba(180, 68, 68, 0.13);
    }

    .badge.warning {
      color: #814907;
      background: rgba(199, 122, 37, 0.14);
    }

    .badge.ok {
      color: #0b573b;
      background: rgba(23, 115, 79, 0.12);
    }

    .node-note {
      margin-top: 12px;
      color: #3d4a44;
      font-size: 13px;
      line-height: 1.55;
    }

    .details {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }

    .list {
      padding: 20px 22px 22px;
      display: grid;
      gap: 12px;
    }

    .item {
      padding: 15px;
      border: 1px solid rgba(39, 48, 43, 0.1);
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.52);
    }

    .item-type {
      color: var(--green);
      font-family: ui-sans-serif, "Noto Sans SC", system-ui, sans-serif;
      font-size: 12px;
      font-weight: 900;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 7px;
    }

    .item-type.boundary {
      color: var(--red);
    }

    .item-text {
      color: #304039;
      line-height: 1.65;
      font-size: 14px;
    }

    .empty {
      padding: 44px 24px;
      color: var(--muted);
      text-align: center;
      line-height: 1.8;
    }

    .toast {
      display: none;
      position: fixed;
      left: 50%;
      bottom: 24px;
      transform: translateX(-50%);
      max-width: min(560px, calc(100vw - 32px));
      padding: 12px 16px;
      border-radius: 16px;
      color: #fff8e8;
      background: rgba(180, 68, 68, 0.94);
      box-shadow: 0 20px 50px rgba(180, 68, 68, 0.26);
      z-index: 20;
    }

    .toast.show {
      display: block;
    }

    @media (max-width: 980px) {
      .line-track {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .station::after {
        display: none;
      }

      .details {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 640px) {
      .shell {
        width: min(100vw - 20px, 1160px);
        padding-top: 18px;
      }

      .topbar {
        align-items: flex-start;
        flex-direction: column;
        margin-bottom: 24px;
      }

      .composer {
        grid-template-columns: 1fr;
      }

      .run-button {
        width: 100%;
      }

      .line-track {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <div class="mark">M</div>
        <div>ManuGent</div>
      </div>
      <span>MES Agent · 自然语言分析 · 产线问题定位</span>
    </header>

    <section class="hero">
      <h1>问一句话，看懂整条产线。</h1>
      <p class="subtitle">
        像 ChatGPT 一样输入问题，ManuGent 会查询 MES 数据，把异常、证据和建议
        动态落到产线节点上。
      </p>
    </section>

    <section class="ask-card">
      <div class="composer">
        <textarea id="question">SMT-03 最近 24 小时良率为什么下降？</textarea>
        <button id="run-button" class="run-button" onclick="runRca()">分析</button>
      </div>
      <div class="examples">
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
          输入一个 MES 现场问题后，系统会展示整条产线，并把问题和建议挂到对应节点。
        </div>
      </article>
    </section>
  </div>

  <div id="error" class="toast"></div>

  <script>
    const stations = [
      {
        id: "printer",
        code: "01",
        name: "印刷",
        desc: "锡膏印刷 / 批次输入",
        evidenceTypes: ["material"]
      },
      {
        id: "spi",
        code: "02",
        name: "SPI",
        desc: "锡膏检测 / 早期质量信号",
        evidenceTypes: ["production", "quality", "material"]
      },
      {
        id: "mounter",
        code: "03",
        name: "贴片",
        desc: "MOUNTER-03A / 吸嘴与飞达",
        evidenceTypes: ["equipment"]
      },
      {
        id: "reflow",
        code: "04",
        name: "回流焊",
        desc: "温区稳定性 / 焊接窗口",
        evidenceTypes: []
      },
      {
        id: "aoi",
        code: "05",
        name: "AOI",
        desc: "缺陷检出 / 良率结果",
        evidenceTypes: ["quality", "production"]
      },
      {
        id: "pack",
        code: "06",
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
      button.textContent = isLoading ? "分析中" : "分析";
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
      return { status: "warning", related };
    }

    function renderLineMap(data) {
      const evidence = data.evidence || [];
      return stations.map(station => {
        const result = stationStatus(station, evidence);
        const badgeText = {
          ok: "运行链路",
          warning: "指标波动",
          issue: "问题关联"
        }[result.status];
        const note = result.related[0]?.summary || "当前问题未直接指向该节点。";

        return `
          <div class="station ${result.status}">
            <div class="station-code">${station.code} · ${station.id}</div>
            <div class="station-name">${station.name}</div>
            <div class="station-desc">${station.desc}</div>
            <div class="badge ${result.status}">${badgeText}</div>
            <div class="node-note">${escapeHtml(note)}</div>
          </div>
        `;
      }).join("");
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

    function renderReport(data, question, lineId, timeRange) {
      const confidence = Math.round((data.confidence || 0) * 100);
      document.getElementById("answer").innerHTML = `
        <article class="panel">
          <div class="panel-head">
            <h2>AI 分析结论</h2>
            <span class="meta">${escapeHtml(lineId)} · ${escapeHtml(timeRange)}
              · 置信度 ${confidence}%</span>
          </div>
          <div class="summary">${escapeHtml(data.finding)}</div>
        </article>

        <article class="panel">
          <div class="panel-head">
            <h2>产线定位图</h2>
            <span class="meta">问题会落在对应工艺节点上</span>
          </div>
          <div class="line-map">
            <div class="line-track">${renderLineMap(data)}</div>
          </div>
        </article>

        <section class="details">
          <article class="panel">
            <div class="panel-head">
              <h2>证据链</h2>
              <span class="meta">${(data.evidence || []).length} 条</span>
            </div>
            <div class="list">${renderEvidence(data)}</div>
          </article>
          <article class="panel">
            <div class="panel-head">
              <h2>建议动作</h2>
              <span class="meta">${(data.recommendations || []).length} 条</span>
            </div>
            <div class="list">${renderActions(data)}</div>
          </article>
        </section>
      `;
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
        renderReport(data, question, lineId, timeRange);
      } catch (error) {
        setError(`分析失败：${error.message}`);
      } finally {
        setLoading(false);
      }
    }

    document.getElementById("question").addEventListener("keydown", event => {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        runRca();
      }
    });
  </script>
</body>
</html>
"""
