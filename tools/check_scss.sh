#!/usr/bin/env bash
# 样式自检 —— 用 GitHub Pages 同一个版本的 Sass（ruby-sass 3.7.4）把整份样式编一遍。
#
# 为什么需要这个：GitHub Pages 锁在很老的 ruby-sass 上，很多新 CSS 写法它不认识
# （例：@supports not selector(...) 直接让整站构建失败）。而一次构建要跑 ~20 分钟，
# 靠推上去试错的代价太高。改完 _sass/ 下任何文件，先跑这个。
#
# 用法：  bash tools/check_scss.sh
# 返回：  编译通过 → exit 0；有语法错 → 打印错误并 exit 1。

set -uo pipefail
cd "$(dirname "$0")/.."

export PATH="$PATH:$(ruby -e 'print Gem.bindir' 2>/dev/null)"
export RUBYOPT="-EUTF-8"

# 一定要用 ruby-sass 3.7.4 本尊：机器上常常另装着 dart-sass（sass-embedded），PATH 上的 `sass` 是它，
# 新写法它都认、什么都查不出来，而且报错为空（2026-10-27 踩过）。所以不走 PATH，按版本号直接点名那个 gem。
if ! gem list -i sass -v 3.7.4 >/dev/null 2>&1; then
  echo "· 没有 ruby-sass 3.7.4，正在装（跟线上同版本）…"
  gem install sass -v 3.7.4 --no-document --force >/dev/null 2>&1
fi
sass() { ruby -e "gem 'sass','3.7.4'; load Gem.bin_path('sass','sass','3.7.4')" -- "$@"; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# main.scss 顶上有 Jekyll 的 front matter 和 Liquid，编译前剥掉
sed -e '/^---$/d' -e 's/{{[^}]*}}//g' -e 's/{%[^%]*%}//g' _includes/main.scss > "$TMP/main.scss"

if sass --scss --default-encoding utf-8 --load-path _sass "$TMP/main.scss" > "$TMP/out.css" 2> "$TMP/err.txt"; then
  echo "✓ 样式编译通过（$(wc -c < "$TMP/out.css") 字节）"
  exit 0
else
  echo "✗ 样式编译失败："
  cat "$TMP/err.txt"
  exit 1
fi
