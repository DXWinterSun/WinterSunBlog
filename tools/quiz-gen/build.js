#!/usr/bin/env node
/*
 * Sam quiz — character-affinity generator.
 *
 * The quiz ranks characters by RAW accumulated affinity (the `chars:{}` map on
 * every option), tie-broken by 6-axis profile cosine. Those affinity maps are
 * NOT hand-written — they are generated here so that every character gets an
 * even, fair niche across the 20 questions (each appears in ~8-9 options and is
 * "primary" on at least one). This is what keeps a newly-added character from
 * being buried, and stops any one character from dominating.
 *
 * SINGLE SOURCE OF TRUTH is sam/quiz/index.html itself:
 *   - CHARS[]      : the roster + each character's `profile` (0-10 per axis)
 *   - QUESTIONS[]  : the question text + per-option `dims` (+ optional lineCN)
 * This script reads both from the HTML, regenerates the `chars:{}` maps, and
 * splices the QUESTIONS array back in. Question text/dims/lineCN are preserved.
 *
 * forces.json pins specific characters onto specific options (0-based question
 * index -> option letter -> [ids]), used for signatures that must hold no matter
 * what the fit math says: the English-quote lines belong to their speakers, the
 * colour question matches each character's colour card, and a few otherwise
 * "middling" characters get a guaranteed thematic niche.
 *
 * TO ADD A CHARACTER:
 *   1. Add them to CHARS[] in sam/quiz/index.html (copy their data — including
 *      the 6-axis `profile` — from sam/many-faces/index.html) and to
 *      PALETTE_NAMES; bump the "N 个角色" counts on the intro + sam card.
 *   2. (optional) Add 1-2 signatures in forces.json on options that fit them.
 *   3. Run:  node tools/quiz-gen/build.js
 *   4. Sanity-check the printed report (reachable = N/N, no character dominating),
 *      confirm the page still compiles, and deploy.
 */
const fs = require("fs");
const path = require("path");

const HTML = path.join(__dirname, "..", "..", "sam", "quiz", "index.html");
const FORCES = path.join(__dirname, "forces.json");
const DIMS = ["guile", "forbear", "chaos", "raw", "romance", "grace"];
const PTS = [3, 2, 2, 1];   // primary, then by fit
const NCH = PTS.length;
const COVW = 4;             // coverage-balancing weight

function extractArray(html, name) {
  const s = html.indexOf("const " + name + " = [");
  const f = html.indexOf("[", s);
  let d = 0, i = f;
  for (; i < html.length; i++) {
    if (html[i] === "[") d++;
    else if (html[i] === "]") { d--; if (d === 0) { i++; break; } }
  }
  return { obj: eval(html.slice(f, i)), from: f, to: i, start: s };
}

let html = fs.readFileSync(HTML, "utf8");
const CHARS = extractArray(html, "CHARS").obj;
const Q = extractArray(html, "QUESTIONS").obj;
const FORCE = JSON.parse(fs.readFileSync(FORCES, "utf8"));

const prof = {}; CHARS.forEach(c => prof[c.id] = c.profile);
const IDS = CHARS.map(c => c.id);
const count = {}, primaryCount = {};
IDS.forEach(id => { count[id] = 0; primaryCount[id] = 0; });
const optSlots = Q.reduce((a, q) => a + q.opts.length * NCH, 0);
const targetCount = optSlots / IDS.length;
const targetPrimary = Q.reduce((a, q) => a + q.opts.length, 0) / IDS.length;

function fit(id, dims) {
  let s = 0, tw = 0;
  DIMS.forEach(k => { if (dims[k]) { s += dims[k] * (prof[id][k] / 10); tw += dims[k]; } });
  return tw ? s / tw : 0;
}

Q.forEach((q, qi) => {
  // signature questions where the pinned character MUST be the primary:
  // the English-quote lines (every option has lineCN) and the colour card question.
  const pinPrimary = q.opts.every(o => o.lineCN) || q.q.indexOf("主色调") >= 0;
  q.opts.forEach((o, oi) => {
    const letter = String.fromCharCode(65 + oi);
    const forced = (FORCE[qi] && FORCE[qi][letter]) || [];
    let chosen = [...forced];
    const ranked = IDS.filter(id => !chosen.includes(id))
      .map(id => ({ id, s: fit(id, o.dims) + COVW * Math.max(0, (targetCount - count[id]) / targetCount) }))
      .sort((a, b) => b.s - a.s);
    let k = 0;
    while (chosen.length < NCH && k < ranked.length) { chosen.push(ranked[k].id); k++; }
    chosen = chosen.slice(0, NCH);
    let primary;
    if (pinPrimary && forced.length) {
      primary = forced[0];
    } else {
      // spread the 3-pt slot: least-primaried among the chosen (fit + forced break ties)
      primary = chosen.slice().sort((a, b) =>
        ((targetPrimary - primaryCount[b]) + (forced.includes(b) ? 0.4 : 0) + fit(b, o.dims) * 0.15) -
        ((targetPrimary - primaryCount[a]) + (forced.includes(a) ? 0.4 : 0) + fit(a, o.dims) * 0.15)
      )[0];
    }
    const rest = chosen.filter(id => id !== primary).sort((a, b) => fit(b, o.dims) - fit(a, o.dims));
    const order = [primary, ...rest];
    o.chars = {};
    order.forEach((id, idx) => { o.chars[id] = PTS[idx]; count[id]++; if (idx === 0) primaryCount[id]++; });
  });
});

// ── Splice the regenerated QUESTIONS array back into the HTML ──
const blockComment = {
  1: "  /* ── Block 1: 行为 / 场景 ── */",
  2: "  /* ── Block 2: 偏好 / 吸引力 ── */",
  3: "  /* ── Block 3: 美学 / 感觉 ── */",
};
const objLit = o => "{" + Object.entries(o).map(([k, v]) => k + ":" + v).join(",") + "}";
let lines = ["const QUESTIONS = ["];
let lastBlock = null;
Q.forEach(q => {
  if (q.block !== lastBlock) { lines.push(blockComment[q.block]); lastBlock = q.block; }
  lines.push("  {");
  lines.push(`    block: ${q.block}, q: ${JSON.stringify(q.q)},`);
  lines.push("    opts: [");
  q.opts.forEach(o => {
    const parts = [`text:${JSON.stringify(o.text)}`];
    if (o.lineCN) parts.push(`lineCN:${JSON.stringify(o.lineCN)}`);
    parts.push(`chars:${objLit(o.chars)}`);
    parts.push(`dims:${objLit(o.dims)}`);
    lines.push("      { " + parts.join(", ") + " },");
  });
  lines.push("    ]");
  lines.push("  },");
});
lines.push("];");
const newLit = lines.join("\n");

const loc = extractArray(html, "QUESTIONS");
let after = loc.to; if (html[after] === ";") after++;
html = html.slice(0, loc.start) + newLit + html.slice(after);
fs.writeFileSync(HTML, html);

// ── Report ──
const maxScore = {};
IDS.forEach(id => { let t = 0; Q.forEach(q => { let b = 0; q.opts.forEach(o => b = Math.max(b, o.chars[id] || 0)); t += b; }); maxScore[id] = t; });
const apps = IDS.map(id => count[id]);
const noPrimary = IDS.filter(id => primaryCount[id] === 0);
console.log(`characters: ${IDS.length}`);
console.log(`appearances per character: ${Math.min(...apps)}–${Math.max(...apps)}`);
console.log(`every character is primary at least once: ${noPrimary.length === 0}${noPrimary.length ? " (missing: " + noPrimary.join(", ") + ")" : ""}`);
console.log("spliced QUESTIONS back into sam/quiz/index.html");
console.log("Now verify the page compiles and eyeball a couple of results before deploying.");
