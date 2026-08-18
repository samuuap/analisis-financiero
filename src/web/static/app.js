/* Market AI Agents — frontend logic (vanilla JS, no external dependencies). */
"use strict";

const I18N = {
  en: {
    eyebrow: "AI-powered equity research",
    heroTitle: "Analyze real companies.",
    heroSubtitle:
      "A clear recommendation — BUY, HOLD, or SELL — backed by news and " +
      "technical indicators.",
    searchPlaceholder: "Search companies…",
    searchEmpty: "No matches",
    trendingHeading: "Trending now",
    trendingHint: "High-momentum names worth a look.",
    allCompaniesHeading: "All companies",
    selectHeading: "Choose a company",
    selectHint: "Select one to begin.",
    selectedLabel: "Selected",
    analyze: "Analyze",
    analyzing: "Analyzing…",
    noSelection: "Select a company first",
    loadingTickers: "Loading companies…",
    tickerError: "Could not load companies. Please reload the page.",
    errorTitle: "Something went wrong",
    errorRetry: "Please try again.",
    recommendation: "Recommendation",
    confidence: "Confidence",
    technicalSignal: "Technical",
    newsSignal: "News",
    summary: "Summary",
    bullishFactors: "Bullish factors",
    bearishFactors: "Bearish factors",
    riskFactors: "Risk factors",
    invalidatingConditions: "Invalidating conditions",
    keyThemes: "Key themes",
    newsHeadlines: "News headlines",
    technicalMetrics: "Technical metrics",
    sources: "Sources",
    disclaimer: "Disclaimer",
    demoMode: "Demo mode",
    deepen: "Deepen analysis",
    deepening: "Deepening…",
    depthDeep: "Deep",
    prev: "Scroll left",
    next: "Scroll right",
    price: "Price",
    high52w: "52-week high",
    low52w: "52-week low",
    model: "Model",
    generated: "Generated",
    marketData: "Market data",
    newsSearch: "News search",
    executionId: "Execution",
    sma20: "SMA 20",
    sma50: "SMA 50",
    sma200: "SMA 200",
    ema20: "EMA 20",
    rsi14: "RSI 14",
    macd: "MACD",
    macdSignal: "MACD signal",
    macdHistogram: "MACD hist.",
    atr14: "ATR 14",
    volatility: "Volatility",
    volumeRatio: "Volume ratio",
    empty: "None",
    bullish: "Bullish",
    bearish: "Bearish",
    neutral: "Neutral",
    buy: "BUY",
    hold: "HOLD",
    sell: "SELL",
    appTitle: "Market AI Agents — Equity Analysis",
    metaDescription:
      "AI-powered equity research: pick a company and get a BUY, HOLD, or SELL " +
      "recommendation backed by news and technical indicators.",
    footerNote:
      "Market AI Agents is an educational research tool. It generates analysis and " +
      "BUY / HOLD / SELL signals only — it never executes trades and is not connected " +
      "to any broker. Nothing here is financial advice.",
  },
  es: {
    eyebrow: "Investigación bursátil con IA",
    heroTitle: "Analiza empresas reales.",
    heroSubtitle:
      "Una recomendación clara — COMPRAR, MANTENER o VENDER — respaldada por " +
      "noticias e indicadores técnicos.",
    searchPlaceholder: "Buscar empresas…",
    searchEmpty: "Sin resultados",
    trendingHeading: "Tendencias ahora",
    trendingHint: "Nombres con alto impulso que vale la pena revisar.",
    allCompaniesHeading: "Todas las empresas",
    selectHeading: "Elige una empresa",
    selectHint: "Selecciona una para comenzar.",
    selectedLabel: "Seleccionada",
    analyze: "Analizar",
    analyzing: "Analizando…",
    noSelection: "Selecciona primero una empresa",
    loadingTickers: "Cargando empresas…",
    tickerError: "No se pudieron cargar las empresas. Recarga la página.",
    errorTitle: "Algo salió mal",
    errorRetry: "Inténtalo de nuevo.",
    recommendation: "Recomendación",
    confidence: "Confianza",
    technicalSignal: "Técnico",
    newsSignal: "Noticias",
    summary: "Resumen",
    bullishFactors: "Factores alcistas",
    bearishFactors: "Factores bajistas",
    riskFactors: "Factores de riesgo",
    invalidatingConditions: "Condiciones de invalidación",
    keyThemes: "Temas clave",
    newsHeadlines: "Titulares de noticias",
    technicalMetrics: "Métricas técnicas",
    sources: "Fuentes",
    disclaimer: "Aviso legal",
    demoMode: "Modo demo",
    deepen: "Profundizar análisis",
    deepening: "Profundizando…",
    depthDeep: "Profundo",
    prev: "Desplazar a la izquierda",
    next: "Desplazar a la derecha",
    price: "Precio",
    high52w: "Máximo 52 semanas",
    low52w: "Mínimo 52 semanas",
    model: "Modelo",
    generated: "Generado",
    marketData: "Datos de mercado",
    newsSearch: "Búsqueda de noticias",
    executionId: "Ejecución",
    sma20: "SMA 20",
    sma50: "SMA 50",
    sma200: "SMA 200",
    ema20: "EMA 20",
    rsi14: "RSI 14",
    macd: "MACD",
    macdSignal: "Señal MACD",
    macdHistogram: "Hist. MACD",
    atr14: "ATR 14",
    volatility: "Volatilidad",
    volumeRatio: "Ratio de volumen",
    empty: "Ninguno",
    bullish: "Alcista",
    bearish: "Bajista",
    neutral: "Neutral",
    buy: "COMPRAR",
    hold: "MANTENER",
    sell: "VENDER",
    appTitle: "Market AI Agents — Análisis bursátil",
    metaDescription:
      "Investigación bursátil con IA: elige una empresa y recibe una recomendación " +
      "de COMPRAR, MANTENER o VENDER respaldada por noticias e indicadores técnicos.",
    footerNote:
      "Market AI Agents es una herramienta de investigación educativa. Genera análisis " +
      "y señales de COMPRAR / MANTENER / VENDER únicamente — nunca ejecuta operaciones " +
      "y no está conectada a ningún bróker. Nada de esto es asesoramiento financiero.",
  },
};

const state = {
  language: "en",
  selectedSymbol: null,
  selectedName: null,
  analyzing: false,
  lastDepth: "standard",
  allTickers: [],
  carouselPaused: false,
  carouselRaf: null,
};

const els = {
  tickerGrid: document.getElementById("ticker-grid"),
  trendingGrid: document.getElementById("trending-grid"),
  searchInput: document.getElementById("search-input"),
  searchResults: document.getElementById("search-results"),
  selectedName: document.getElementById("selected-name"),
  analyzeBtn: document.getElementById("analyze-btn"),
  results: document.getElementById("results"),
  report: document.getElementById("report"),
  resultsToolbar: document.getElementById("results-toolbar"),
  deepenBtn: document.getElementById("deepen-btn"),
  carouselPrev: document.getElementById("carousel-prev"),
  carouselNext: document.getElementById("carousel-next"),
  langBtns: Array.from(document.querySelectorAll(".lang-btn")),
  carousel: document.querySelector(".carousel"),
};

const CAROUSEL_SPEED_PX_PER_SEC = 36;

function t(key) {
  return (I18N[state.language] && I18N[state.language][key]) || I18N.en[key] || key;
}

function applyStaticText() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.getAttribute("data-i18n"));
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((node) => {
    node.setAttribute("aria-label", t(node.getAttribute("data-i18n-aria")));
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.setAttribute("placeholder", t(node.getAttribute("data-i18n-placeholder")));
  });
  document.querySelectorAll("[data-i18n-content]").forEach((node) => {
    node.setAttribute("content", t(node.getAttribute("data-i18n-content")));
  });
  document.documentElement.lang = state.language;
  els.langBtns.forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-lang") === state.language);
  });
  syncAnalyzeLabel();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined) return t("empty");
  const n = Number(value);
  if (!Number.isFinite(n)) return t("empty");
  return n.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function formatDate(value) {
  if (!value) return t("empty");
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return escapeHtml(String(value));
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function sentimentLabel(value) {
  const map = { BULLISH: t("bullish"), BEARISH: t("bearish"), NEUTRAL: t("neutral") };
  return map[value] || escapeHtml(value || t("neutral"));
}

function sentimentClass(value) {
  const map = { BULLISH: "bullish", BEARISH: "bearish", NEUTRAL: "neutral" };
  return map[value] || "neutral";
}

function actionClass(value) {
  return (value || "HOLD").toLowerCase();
}

function actionLabel(value) {
  const map = { BUY: "buy", HOLD: "hold", SELL: "sell" };
  return t(map[value]) || value || "HOLD";
}

function logoBadge(ticker, sizeClass) {
  const badge = document.createElement("span");
  badge.className = "logo-badge" + (sizeClass ? " " + sizeClass : "");
  badge.style.setProperty("--brand", ticker.color || "var(--accent)");
  const fallback = (ticker.name || ticker.symbol || "?").charAt(0).toUpperCase();

  if (ticker.logo && (/^https?:\/\//i.test(ticker.logo) || ticker.logo.startsWith("/"))) {
    const img = document.createElement("img");
    img.className = "logo-img";
    img.src = ticker.logo;
    img.alt = "";
    img.loading = "lazy";
    img.decoding = "async";
    img.referrerPolicy = "no-referrer";
    img.onerror = () => {
      badge.classList.add("logo-fallback");
      badge.textContent = fallback;
    };
    badge.appendChild(img);
  } else {
    badge.classList.add("logo-fallback");
    badge.textContent = fallback;
  }

  return badge;
}

async function loadTickers() {
  els.tickerGrid.innerHTML = `<p class="status-message">${escapeHtml(t("loadingTickers"))}</p>`;
  try {
    const res = await fetch(`/api/tickers?language=${encodeURIComponent(state.language)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderTickers(data.tickers || []);
  } catch (err) {
    console.error(err);
    els.tickerGrid.innerHTML =
      `<p class="status-message error">${escapeHtml(t("tickerError"))}</p>`;
  }
}

function buildTickerCard(ticker) {
  const card = document.createElement("button");
  card.type = "button";
  card.className = "ticker-card";
  card.dataset.symbol = ticker.symbol;
  card.dataset.name = ticker.name;
  card.style.setProperty("--brand", ticker.color || "var(--accent)");
  if (ticker.symbol === state.selectedSymbol) card.classList.add("selected");

  const name = document.createElement("h3");
  name.className = "ticker-name";
  name.textContent = ticker.name;

  const symbol = document.createElement("span");
  symbol.className = "ticker-symbol";
  symbol.textContent = ticker.symbol;

  const sector = document.createElement("span");
  sector.className = "ticker-sector";
  sector.textContent = ticker.sector;

  const desc = document.createElement("p");
  desc.className = "ticker-desc";
  desc.textContent = ticker.description;

  card.append(logoBadge(ticker, ""), name, symbol, sector, desc);
  card.addEventListener("click", () => selectTicker(ticker.symbol, ticker.name));
  return card;
}

function buildTrendingCard(ticker) {
  const card = document.createElement("button");
  card.type = "button";
  card.className = "featured-card";
  card.dataset.symbol = ticker.symbol;
  card.dataset.name = ticker.name;
  card.style.setProperty("--brand", ticker.color || "var(--accent)");
  if (ticker.symbol === state.selectedSymbol) card.classList.add("selected");

  const name = document.createElement("h3");
  name.className = "featured-name";
  name.textContent = ticker.name;

  const symbol = document.createElement("span");
  symbol.className = "featured-symbol";
  symbol.textContent = ticker.symbol;

  const sector = document.createElement("span");
  sector.className = "featured-sector";
  sector.textContent = ticker.sector;

  const desc = document.createElement("p");
  desc.className = "featured-desc";
  desc.textContent = ticker.description;

  card.append(logoBadge(ticker, "logo-badge-lg"), name, symbol, sector, desc);
  card.addEventListener("click", () => selectTicker(ticker.symbol, ticker.name));
  return card;
}

function renderTickers(tickers) {
  state.allTickers = tickers || [];
  els.tickerGrid.innerHTML = "";
  els.trendingGrid.innerHTML = "";

  // Two identical sets: the duplicate makes the continuous loop seamless.
  const carouselFragment = document.createDocumentFragment();
  state.allTickers.forEach((ticker) => carouselFragment.appendChild(buildTickerCard(ticker)));
  state.allTickers.forEach((ticker) => carouselFragment.appendChild(buildTickerCard(ticker)));
  els.tickerGrid.appendChild(carouselFragment);

  state.allTickers
    .filter((ticker) => ticker.trending)
    .forEach((ticker) => {
      els.trendingGrid.appendChild(buildTrendingCard(ticker));
    });

  updateCarouselNav();
  startCarouselAutoScroll();
}

function updateSelectedCards() {
  document.querySelectorAll(".ticker-card, .featured-card").forEach((card) => {
    card.classList.toggle("selected", card.dataset.symbol === state.selectedSymbol);
  });
}

function selectTicker(symbol, name) {
  state.selectedSymbol = symbol;
  state.selectedName = name;
  updateSelectedCards();
  els.selectedName.textContent = name || symbol;
  els.analyzeBtn.disabled = state.analyzing;
}

function updateCarouselNav() {
  const track = els.tickerGrid;
  const maxScroll = track.scrollWidth - track.clientWidth;
  els.carouselPrev.disabled = track.scrollLeft <= 0;
  els.carouselNext.disabled = track.scrollLeft >= maxScroll - 1;
}

function carouselGap() {
  const style = window.getComputedStyle(els.tickerGrid);
  return parseFloat(style.columnGap || style.gap || "0") || 0;
}

function carouselStep() {
  const card = els.tickerGrid.querySelector(".ticker-card");
  return card ? card.offsetWidth + carouselGap() : 280;
}

// Width of one full set of cards, including the trailing gap — the point at
// which the duplicate set aligns perfectly so the wrap is invisible.
function carouselPeriod() {
  if (!state.allTickers.length) return null;
  const card = els.tickerGrid.querySelector(".ticker-card");
  if (!card) return null;
  return state.allTickers.length * (card.offsetWidth + carouselGap());
}

function scrollCarousel(direction) {
  const step = carouselStep();
  els.tickerGrid.scrollBy({ left: direction * step, behavior: "smooth" });
  pauseCarouselTemporarily();
}

function startCarouselAutoScroll() {
  stopCarouselAutoScroll();
  const track = els.tickerGrid;
  if (!track) return;
  let last = null;
  function frame(timestamp) {
    state.carouselRaf = window.requestAnimationFrame(frame);
    if (last === null) last = timestamp;
    const dt = Math.min((timestamp - last) / 1000, 0.1);
    last = timestamp;
    if (state.carouselPaused || state.analyzing) return;
    if (track.scrollWidth <= track.clientWidth + 1) return;
    const period = carouselPeriod();
    if (!period) return;
    let next = track.scrollLeft + CAROUSEL_SPEED_PX_PER_SEC * dt;
    if (next >= period) next -= period;
    track.scrollLeft = next;
    updateCarouselNav();
  }
  state.carouselRaf = window.requestAnimationFrame(frame);
}

function stopCarouselAutoScroll() {
  if (state.carouselRaf !== null) {
    window.cancelAnimationFrame(state.carouselRaf);
    state.carouselRaf = null;
  }
}

function pauseCarouselTemporarily() {
  state.carouselPaused = true;
  window.setTimeout(() => {
    state.carouselPaused = false;
  }, 5000);
}

function setLanguage(lang) {
  if (lang !== "en" && lang !== "es") return;
  state.language = lang;
  applyStaticText();
  loadTickers();
}

function syncAnalyzeLabel() {
  els.analyzeBtn.innerHTML = `<span>${escapeHtml(t("analyze"))}</span>`;
}

function setAnalyzing(active) {
  state.analyzing = active;
  els.analyzeBtn.disabled = active || !state.selectedSymbol;
  els.analyzeBtn.innerHTML = active
    ? `<span class="spinner" aria-hidden="true"></span><span>${escapeHtml(t("analyzing"))}</span>`
    : `<span>${escapeHtml(t("analyze"))}</span>`;
  els.deepenBtn.disabled = active;
}

async function runAnalysis(depth = "standard") {
  if (!state.selectedSymbol || state.analyzing) return;
  const deepening = depth === "deep";
  setAnalyzing(true);
  els.results.hidden = false;
  els.resultsToolbar.hidden = true;
  els.report.innerHTML = `<p class="status-message">${escapeHtml(
    deepening ? t("deepening") : t("analyzing"),
  )}</p>`;
  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        symbol: state.selectedSymbol,
        language: state.language,
        depth,
      }),
    });
    const payload = await res.json().catch(() => null);
    if (!res.ok) {
      const detail = (payload && payload.detail) || t("errorRetry");
      renderError(detail);
      return;
    }
    state.lastDepth = payload.depth || depth;
    renderReport(payload);
    els.resultsToolbar.hidden = false;
  } catch (err) {
    console.error(err);
    renderError(t("errorRetry"));
  } finally {
    setAnalyzing(false);
  }
}

function deepenAnalysis() {
  runAnalysis("deep");
}

function renderError(detail) {
  els.report.innerHTML =
    `<div class="report-card">` +
    `<div class="status-message error">` +
    `<strong>${escapeHtml(t("errorTitle"))}</strong><br />` +
    `${escapeHtml(detail)}` +
    `</div></div>`;
}

function renderReport(report) {
  const rec = report.recommendation || {};
  const tech = report.technical_analysis || null;
  const news = report.news_analysis || null;
  const action = rec.action || "HOLD";

  const companyName = state.selectedName || report.ticker || "";
  const header = `
    <div class="report-header">
      <div class="report-company">
        <span class="name">${escapeHtml(companyName)}</span>
        <span class="meta">
          ${escapeHtml(report.ticker || "")} · ${escapeHtml(t("model"))}: ${escapeHtml(report.model || "")}
          ${report.mock ? `<span class="demo-badge">${escapeHtml(t("demoMode"))}</span>` : ""}
          ${(report.depth === "deep" || state.lastDepth === "deep")
            ? `<span class="depth-badge">${escapeHtml(t("depthDeep"))}</span>`
            : ""}
        </span>
      </div>
      <div class="verdict">
        <span class="verdict-badge ${actionClass(action)}">${escapeHtml(actionLabel(action))}</span>
        <span class="confidence">${escapeHtml(t("confidence"))}: ${formatNumber((rec.confidence ?? 0) * 100, 0)}%</span>
      </div>
    </div>`;

  const metricGrid = `
    <div class="metric-grid">
      ${metric("price", formatMoney(report.price))}
      ${metric("high52w", formatMoney(report.high_52w))}
      ${metric("low52w", formatMoney(report.low_52w))}
      ${metric("technicalSignal", pill(sentimentLabel(rec.technical_signal), sentimentClass(rec.technical_signal)))}
      ${metric("newsSignal", pill(sentimentLabel(rec.news_signal), sentimentClass(rec.news_signal)))}
    </div>`;

  const summaryBlock = rec.summary
    ? `<div class="summary-block"><h3>${escapeHtml(t("recommendation"))}</h3><p>${escapeHtml(rec.summary)}</p></div>`
    : "";

  const factorsGrid = `
    <div class="factors-grid">
      ${factorColumn("bullish", t("bullishFactors"), rec.bullish_factors)}
      ${factorColumn("bearish", t("bearishFactors"), rec.bearish_factors)}
    </div>`;

  const detailLists = [
    listBlock(t("riskFactors"), rec.risk_factors),
    listBlock(t("invalidatingConditions"), rec.invalidating_conditions),
  ].join("");

  const technicalBlock = tech ? technicalTable(tech) : "";
  const newsBlock = news ? newsList(news) : "";

  const sourcesBlock = listBlock(
    t("sources"),
    report.sources && report.sources.length ? report.sources : [],
  );

  const footer = `
    <div class="report-footer">
      <p class="disclaimer">${escapeHtml(report.disclaimer || "")}</p>
      <p class="meta-line">${escapeHtml(t("generated"))}: ${formatDate(report.timestamp)}</p>
      <p class="meta-line">${escapeHtml(t("marketData"))}: ${formatDate(report.market_data_timestamp)}</p>
      <p class="meta-line">${escapeHtml(t("newsSearch"))}: ${formatDate(report.news_search_timestamp)}</p>
      <p class="meta-line">${escapeHtml(t("executionId"))}: ${escapeHtml(report.execution_id || "")}</p>
    </div>`;

  els.report.innerHTML =
    `<div class="report-card">${header}<div class="report-body">${metricGrid}${summaryBlock}${factorsGrid}${detailLists}${technicalBlock}${newsBlock}${sourcesBlock}</div>${footer}</div>`;
}

function formatMoney(value) {
  if (value === null || value === undefined) return t("empty");
  const n = Number(value);
  if (!Number.isFinite(n)) return t("empty");
  return n.toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function metric(labelKey, valueHtml) {
  return `
    <div class="metric">
      <span class="label">${escapeHtml(t(labelKey))}</span>
      <span class="value small">${valueHtml}</span>
    </div>`;
}

function pill(label, cls) {
  return `<span class="pill ${cls}">${escapeHtml(label)}</span>`;
}

function factorColumn(kind, title, items) {
  const list = (items || []).length
    ? `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
    : `<span class="empty">${escapeHtml(t("empty"))}</span>`;
  return `<div class="factors-col ${kind}"><h3>${escapeHtml(title)}</h3>${list}</div>`;
}

function listBlock(title, items) {
  const list = (items || []).length
    ? `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
    : `<span class="empty">${escapeHtml(t("empty"))}</span>`;
  return `<div class="detail-list"><h3>${escapeHtml(title)}</h3>${list}</div>`;
}

function technicalTable(tech) {
  const rows = [
    [t("sma20"), tech.sma20],
    [t("sma50"), tech.sma50],
    [t("sma200"), tech.sma200],
    [t("ema20"), tech.ema20],
    [t("rsi14"), tech.rsi14],
    [t("macd"), tech.macd],
    [t("macdSignal"), tech.macd_signal],
    [t("macdHistogram"), tech.macd_histogram],
    [t("atr14"), tech.atr14],
    [t("volatility"), tech.volatility],
    [t("volumeRatio"), tech.volume_ratio],
  ].filter(([, value]) => value !== null && value !== undefined);

  const body = rows.length
    ? rows
        .map(
          ([label, value]) =>
            `<tr><th>${escapeHtml(label)}</th><td>${formatNumber(value)}</td></tr>`,
        )
        .join("")
    : `<tr><td class="empty">${escapeHtml(t("empty"))}</td></tr>`;

  const signalLine = tech.summary
    ? `<div class="summary-block"><p>${escapeHtml(tech.summary)}</p></div>`
    : "";

  return `
    <div class="detail-list">
      <h3>${escapeHtml(t("technicalMetrics"))}</h3>
      ${signalLine}
      <table class="tech-table">${body}</table>
    </div>`;
}

function newsList(news) {
  const headlines = (news.items || [])
    .map((item) => {
      const title = item.title || "";
      const source = item.source ? ` — ${item.source}` : "";
      const link = item.url
        ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(title)}</a>`
        : escapeHtml(title);
      return `<li>${link}${escapeHtml(source)}</li>`;
    })
    .join("");

  const summary = news.summary
    ? `<div class="summary-block"><p>${escapeHtml(news.summary)}</p></div>`
    : "";

  const themes = (news.key_themes || []).length
    ? `<div class="detail-list"><h3>${escapeHtml(t("keyThemes"))}</h3><ul>${news.key_themes
        .map((theme) => `<li>${escapeHtml(theme)}</li>`)
        .join("")}</ul></div>`
    : "";

  return `
    <div class="detail-list">
      <h3>${escapeHtml(t("newsHeadlines"))}</h3>
      ${summary}
      ${headlines ? `<ul>${headlines}</ul>` : `<span class="empty">${escapeHtml(t("empty"))}</span>`}
      ${themes}
    </div>`;
}

/* ---------- Search ---------- */

function handleSearchInput() {
  const query = (els.searchInput.value || "").trim().toLowerCase();
  if (!query) {
    closeSearch();
    return;
  }
  const results = state.allTickers.filter((ticker) => {
    const haystack = [ticker.symbol, ticker.name, ticker.sector, ticker.description]
      .join(" ")
      .toLowerCase();
    return haystack.includes(query);
  });
  renderSearchResults(results);
}

function renderSearchResults(results) {
  els.searchResults.innerHTML = "";
  if (!results.length) {
    const empty = document.createElement("p");
    empty.className = "search-empty";
    empty.textContent = t("searchEmpty");
    els.searchResults.appendChild(empty);
  } else {
    results.forEach((ticker) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "search-result";

      const text = document.createElement("span");
      text.className = "sr-text";

      const name = document.createElement("span");
      name.className = "sr-name";
      name.textContent = ticker.name;

      const meta = document.createElement("span");
      meta.className = "sr-meta";
      meta.textContent = `${ticker.symbol} · ${ticker.sector}`;

      text.append(name, meta);
      btn.append(logoBadge(ticker, "logo-badge-sm"), text);
      btn.addEventListener("click", () => {
        selectTicker(ticker.symbol, ticker.name);
        els.searchInput.value = ticker.name;
        closeSearch();
        els.searchInput.blur();
      });
      els.searchResults.appendChild(btn);
    });
  }
  els.searchResults.hidden = false;
}

function closeSearch() {
  els.searchResults.hidden = true;
  els.searchResults.innerHTML = "";
}

/* ---------- Wiring ---------- */

els.langBtns.forEach((btn) => {
  btn.addEventListener("click", () => setLanguage(btn.getAttribute("data-lang")));
});

els.analyzeBtn.addEventListener("click", () => runAnalysis("standard"));
els.deepenBtn.addEventListener("click", deepenAnalysis);
els.carouselPrev.addEventListener("click", () => scrollCarousel(-1));
els.carouselNext.addEventListener("click", () => scrollCarousel(1));
els.tickerGrid.addEventListener("scroll", updateCarouselNav, { passive: true });

els.searchInput.addEventListener("input", handleSearchInput);
els.searchInput.addEventListener("focus", handleSearchInput);
els.searchInput.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeSearch();
    els.searchInput.blur();
  }
});

document.addEventListener("click", (event) => {
  if (!event.target.closest(".search-box")) closeSearch();
});

if (els.carousel) {
  els.carousel.addEventListener("mouseenter", () => {
    state.carouselPaused = true;
  });
  els.carousel.addEventListener("mouseleave", () => {
    state.carouselPaused = false;
  });
  els.carousel.addEventListener("touchstart", () => {
    state.carouselPaused = true;
  });
  els.carousel.addEventListener("touchend", () => {
    pauseCarouselTemporarily();
  });
}

applyStaticText();
loadTickers();
