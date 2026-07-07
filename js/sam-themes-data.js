---
---
window.__SAM_THEMES = {{ site.data.sam_themes | jsonify }};

// 安全网：始终按电影年份升序排列（稳定排序，同年保持 _data/sam_themes.yml 里的顺序）。
// 这样即使有人把新色卡追加到 yml 末尾而忘了插对位置，选色器 / polaroid 的
// 显示顺序也不会乱。缺 year 的条目排到最前（提醒补上）。
if (Array.isArray(window.__SAM_THEMES)) {
  window.__SAM_THEMES.sort(function (a, b) {
    return ((a && a.year) || 0) - ((b && b.year) || 0);
  });
}
