// ADHD Focus - Scriptable medium widget
//
// Setup:
// 1. Paste this file into Scriptable.
// 2. Set BASE_URL below, for example: https://focus.example.com
// 3. Set TOKEN to base64(username:password), raw username:password, or fill USERNAME and PASSWORD.
//
// Alternative: leave BASE_URL/TOKEN empty and set the widget parameter to one of:
// https://focus.example.com|base64_username_password
// https://focus.example.com|username:password
// https://focus.example.com/widget/progress?token=base64_username_password
// https://focus.example.com/tasks/widget/progress?token=base64_username_password

const BASE_URL = "";
const TOKEN = "";
const USERNAME = "";
const PASSWORD = "";
const MODULE_LIMIT = 4;
const REFRESH_MINUTES = 15;

const COLORS = {
  bgTop: "#172033",
  bgBottom: "#0f172a",
  panel: "#1f2937",
  panelSoft: "#243145",
  text: "#f8fafc",
  muted: "#94a3b8",
  line: "#334155",
  green: "#22c55e",
  cyan: "#22d3ee",
  amber: "#f59e0b",
  red: "#fb7185",
  track: "#334155",
};

main();

async function main() {
  const widget = new ListWidget();
  try {
    const configData = resolveConfig();
    await buildWidget(widget, configData);
  } catch (error) {
    widget.backgroundGradient = makeBackground();
    renderError(widget, error);
  }

  if (config.runsInWidget) {
    Script.setWidget(widget);
  } else {
    await widget.presentMedium();
  }

  Script.complete();
}

function resolveConfig() {
  const parameter = String(args.widgetParameter || "").trim();
  const parts = parameter.split("|").map((part) => part.trim());
  const parameterUrl = parts[0] || "";
  const parameterCredential = parts.slice(1).join("|").trim();
  const target = resolveTarget(parameterUrl || BASE_URL);

  const token = normalizeCredential(parameterCredential || target.token || TOKEN);
  const username = USERNAME.trim();
  const password = PASSWORD;

  return {
    apiUrl: target.apiUrl,
    token,
    username,
    password,
  };
}

function resolveTarget(raw) {
  const clean = String(raw || "").trim().replace(/\/+$/, "");
  if (!clean) {
    throw new Error("Brak BASE_URL albo parametru widgetu.");
  }
  if (!/^https?:\/\//i.test(clean)) {
    throw new Error("BASE_URL musi zaczynac sie od http:// albo https://.");
  }

  let parsed;
  try {
    parsed = new URL(clean);
  } catch (error) {
    throw new Error("BASE_URL nie jest poprawnym URL-em.");
  }

  const token = parsed.searchParams.get("token") || "";
  const path = parsed.pathname.replace(/\/+$/, "") || "/";
  const origin = parsed.origin;

  if (path.endsWith("/tasks/widget/progress")) {
    return {
      apiUrl: `${origin}${path}`,
      token,
    };
  }

  return {
    apiUrl: `${origin}/tasks/widget/progress`,
    token,
  };
}

function normalizeCredential(raw) {
  const clean = String(raw || "").trim();
  if (!clean) return "";
  if (/^basic\s+/i.test(clean)) return clean.replace(/^basic\s+/i, "").trim();
  if (clean.includes(":")) return Data.fromString(clean).toBase64String();
  return clean;
}

async function buildWidget(widget, configData) {
  widget.setPadding(12, 14, 12, 14);
  widget.backgroundGradient = makeBackground();
  widget.refreshAfterDate = new Date(Date.now() + REFRESH_MINUTES * 60 * 1000);

  const data = await loadProgress(configData);
  renderProgress(widget, data);
}

async function loadProgress(configData) {
  const query = [`limit=${encodeURIComponent(String(MODULE_LIMIT))}`];
  if (configData.token) {
    query.push(`token=${encodeURIComponent(configData.token)}`);
  }

  const request = new Request(`${configData.apiUrl}?${query.join("&")}`);
  request.headers = { Accept: "application/json" };
  if (!configData.token && configData.username && configData.password) {
    request.headers.Authorization = `Basic ${Data.fromString(`${configData.username}:${configData.password}`).toBase64String()}`;
  }

  const responseText = await request.loadString();
  const status = request.response ? Number(request.response.statusCode || 200) : 200;
  if (status === 401) {
    throw new Error("HTTP 401: token/login nie pasuje. Uzyj tokenu base64(login:haslo), surowego login:haslo albo USERNAME/PASSWORD.");
  }
  if (status === 404) {
    throw new Error("HTTP 404: brak /tasks/widget/progress. Zrestartuj backend po aktualizacji albo podaj sam host aplikacji.");
  }
  if (status >= 400) {
    throw new Error(`Backend zwrocil HTTP ${status}.`);
  }

  let payload;
  try {
    payload = JSON.parse(responseText);
  } catch (error) {
    throw new Error("Backend nie zwrocil JSON. Sprawdz, czy URL prowadzi do tej aplikacji, nie do strony logowania.");
  }

  if (!payload || !payload.counts) {
    throw new Error("Brak danych z endpointu progresu.");
  }
  return payload;
}

function renderProgress(widget, data) {
  const counts = data.counts || {};
  const modules = Array.isArray(data.modules) ? data.modules.slice(0, MODULE_LIMIT) : [];
  const percent = clampNumber(counts.percent, 0, 100);
  const open = Number(counts.open || 0);

  const header = widget.addStack();
  header.layoutHorizontally();
  header.centerAlignContent();

  const titleStack = header.addStack();
  titleStack.layoutVertically();
  const title = titleStack.addText("ADHD Focus");
  title.font = Font.boldSystemFont(12);
  title.textColor = new Color(COLORS.text);
  const date = titleStack.addText(formatDate(data.date));
  date.font = Font.mediumSystemFont(9);
  date.textColor = new Color(COLORS.muted);

  header.addSpacer();

  const status = header.addText(`${Math.round(percent)}%`);
  status.font = Font.blackSystemFont(16);
  status.textColor = new Color(accentFor(percent, open));

  widget.addSpacer(8);

  const body = widget.addStack();
  body.layoutHorizontally();
  body.centerAlignContent();

  const summary = body.addStack();
  summary.layoutVertically();
  summary.size = new Size(116, 112);
  summary.backgroundColor = new Color(COLORS.panel, 0.52);
  summary.cornerRadius = 12;
  summary.setPadding(9, 8, 8, 8);

  const ringRow = summary.addStack();
  ringRow.layoutHorizontally();
  ringRow.centerAlignContent();
  ringRow.addSpacer();
  const ring = ringRow.addImage(makeRingImage(percent, 68, accentFor(percent, open), String(Math.round(percent))));
  ring.imageSize = new Size(68, 68);
  ringRow.addSpacer();

  summary.addSpacer(7);
  const stats = summary.addStack();
  stats.layoutHorizontally();
  addStat(stats, counts.today_open, "dzis");
  stats.addSpacer(4);
  addStat(stats, counts.overdue_open, "po term.");
  stats.addSpacer(4);
  addStat(stats, counts.done_today, "zrob.");

  body.addSpacer(8);

  const moduleArea = body.addStack();
  moduleArea.layoutVertically();
  moduleArea.size = new Size(184, 112);

  for (let rowIndex = 0; rowIndex < 2; rowIndex += 1) {
    const row = moduleArea.addStack();
    row.layoutHorizontally();
    row.size = new Size(184, 52);

    for (let colIndex = 0; colIndex < 2; colIndex += 1) {
      const module = modules[rowIndex * 2 + colIndex];
      if (module) {
        addModule(row, module);
      } else {
        addEmptyModule(row);
      }
      if (colIndex === 0) row.addSpacer(6);
    }

    if (rowIndex === 0) moduleArea.addSpacer(8);
  }
}

function addStat(parent, value, label) {
  const box = parent.addStack();
  box.layoutVertically();
  box.centerAlignContent();
  box.size = new Size(30, 27);
  box.backgroundColor = new Color(COLORS.panelSoft, 0.72);
  box.cornerRadius = 7;
  box.setPadding(4, 2, 3, 2);

  const number = box.addText(String(Number(value || 0)));
  number.font = Font.blackSystemFont(11);
  number.textColor = new Color(COLORS.text);
  number.centerAlignText();

  const caption = box.addText(label);
  caption.font = Font.boldSystemFont(6);
  caption.textColor = new Color(COLORS.muted);
  caption.centerAlignText();
  caption.lineLimit = 1;
}

function addModule(parent, module) {
  const percent = clampNumber(module.percent, 0, 100);
  const open = Number(module.open || 0);

  const tile = parent.addStack();
  tile.layoutHorizontally();
  tile.centerAlignContent();
  tile.size = new Size(89, 52);
  tile.backgroundColor = new Color(COLORS.panel, 0.52);
  tile.cornerRadius = 10;
  tile.setPadding(7, 6, 7, 6);

  const ring = tile.addImage(makeRingImage(percent, 36, accentFor(percent, open), String(Math.round(percent))));
  ring.imageSize = new Size(36, 36);

  tile.addSpacer(6);

  const text = tile.addStack();
  text.layoutVertically();
  const name = text.addText(shorten(module.name || "Bez modulu", 14));
  name.font = Font.boldSystemFont(8);
  name.textColor = new Color(COLORS.text);
  name.lineLimit = 1;

  const meta = text.addText(`${Number(module.done || 0)}/${Number(module.total || 0)} zadan`);
  meta.font = Font.mediumSystemFont(7);
  meta.textColor = new Color(COLORS.muted);
  meta.lineLimit = 1;
}

function addEmptyModule(parent) {
  const tile = parent.addStack();
  tile.size = new Size(89, 52);
  tile.backgroundColor = new Color(COLORS.panel, 0.28);
  tile.cornerRadius = 10;
}

function renderError(widget, error) {
  widget.setPadding(14, 14, 14, 14);

  const title = widget.addText("Focus widget");
  title.font = Font.blackSystemFont(16);
  title.textColor = new Color(COLORS.text);

  widget.addSpacer(6);

  const message = widget.addText(String(error && error.message ? error.message : error));
  message.font = Font.mediumSystemFont(11);
  message.textColor = new Color(COLORS.muted);
  message.lineLimit = 5;

  widget.addSpacer();

  const hint = widget.addText("401 = auth, 404 = restart/backend URL.");
  hint.font = Font.boldSystemFont(9);
  hint.textColor = new Color(COLORS.amber);
}

function makeBackground() {
  const gradient = new LinearGradient();
  gradient.locations = [0, 1];
  gradient.colors = [new Color(COLORS.bgTop), new Color(COLORS.bgBottom)];
  return gradient;
}

function makeRingImage(percent, size, accentHex, label) {
  const draw = new DrawContext();
  draw.size = new Size(size, size);
  draw.opaque = false;
  draw.respectScreenScale = true;

  const center = new Point(size / 2, size / 2);
  const lineWidth = Math.max(5, Math.round(size * 0.12));
  const radius = (size / 2) - (lineWidth / 2) - 1;

  const track = new Path();
  track.addEllipse(new Rect(center.x - radius, center.y - radius, radius * 2, radius * 2));
  draw.addPath(track);
  draw.setStrokeColor(new Color(COLORS.track, 0.95));
  draw.setLineWidth(lineWidth);
  draw.strokePath();

  const safePercent = clampNumber(percent, 0, 100);
  if (safePercent > 0) {
    const arc = makeArcPath(center, radius, -90, -90 + (safePercent * 3.6));
    draw.addPath(arc);
    draw.setStrokeColor(new Color(accentHex));
    draw.setLineWidth(lineWidth);
    draw.strokePath();
  }

  const fontSize = size >= 60 ? 17 : 10;
  draw.setFont(Font.blackSystemFont(fontSize));
  draw.setTextColor(new Color(COLORS.text));
  draw.setTextAlignedCenter();
  draw.drawTextInRect(label, new Rect(0, (size - fontSize) / 2 - 2, size, fontSize + 8));

  return draw.getImage();
}

function makeArcPath(center, radius, startDeg, endDeg) {
  const path = new Path();
  const span = Math.max(0, endDeg - startDeg);
  const steps = Math.max(2, Math.ceil(span / 6));

  for (let index = 0; index <= steps; index += 1) {
    const angle = (startDeg + (span * index / steps)) * Math.PI / 180;
    const point = new Point(
      center.x + Math.cos(angle) * radius,
      center.y + Math.sin(angle) * radius
    );
    if (index === 0) {
      path.move(point);
    } else {
      path.addLine(point);
    }
  }

  return path;
}

function accentFor(percent, open) {
  if (Number(open || 0) <= 0) return COLORS.green;
  if (Number(percent || 0) >= 70) return COLORS.cyan;
  if (Number(percent || 0) >= 35) return COLORS.amber;
  return COLORS.red;
}

function clampNumber(value, min, max) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return min;
  return Math.max(min, Math.min(max, parsed));
}

function formatDate(dateKey) {
  const clean = String(dateKey || "").trim();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(clean)) return "dzis";
  const parts = clean.split("-");
  return `${parts[2]}.${parts[1]}.${parts[0]}`;
}

function shorten(value, limit) {
  const clean = String(value || "").trim();
  if (clean.length <= limit) return clean;
  return `${clean.slice(0, Math.max(0, limit - 1)).trim()}...`;
}
