$(document).ready(function () {

  'use strict';

  /* =======================
  // Simple Search Settings
  ======================= */

  if (document.getElementById('js-search-input')) {
    SimpleJekyllSearch({
      searchInput: document.getElementById('js-search-input'),
      resultsContainer: document.getElementById('js-results-container'),
      json: (window.SITE_BASEURL || '') + '/search.json',
      searchResultTemplate: '<li><a href="{url}">{title}</a></li>',
      noResultsText: '<li><a>No results</a></li>'
    });
  }

  /* =======================
  // Responsive videos
  ======================= */

  $('.c-wrap-content').fitVids({
    'customSelector': ['iframe[src*="ted.com"]']
  });

  /* =======================================
  // Top nav: switch view + filter by category
  // - Each chip is a real link with a URL param
  // - On the homepage, intercept clicks and filter in place
  // - On other pages, let the link navigate to the homepage
  ======================================= */

  var BASEURL = window.SITE_BASEURL || '';
  // The homepage is at "{baseurl}/" or "{baseurl}/index.html"
  function isHomepage() {
    var p = window.location.pathname.replace(/\/index\.html$/, '/');
    var home = (BASEURL + '/').replace(/\/+$/, '/');
    return p === home || p === home.replace(/\/$/, '');
  }

  function showPostsView() {
    $('.c-posts').show().addClass('o-opacity');
    $('.c-categories, .c-show-images').hide().removeClass('o-opacity');
  }

  function applyCategoryFilter(filter) {
    var $items = $('.c-posts').find('[data-category]');
    var visible = 0;
    $items.each(function () {
      var cat = $(this).attr('data-category') || '';
      var cardType = $(this).attr('data-card-type') || 'chapter';
      var partOfSeries = !!$(this).attr('data-series');

      // Rules:
      //   - 'all' view: show series cards + standalone chapter cards;
      //     hide per-chapter cards that belong to a series (the series
      //     card represents them all).
      //   - Specific category: show series cards in that category; show
      //     chapter cards in that category only if the chapter is NOT
      //     part of a series (its series card represents it instead).
      var shouldShow;
      if (filter === 'all') {
        if (cardType === 'series') {
          shouldShow = true;
        } else {
          shouldShow = !partOfSeries;
        }
      } else if (cat !== filter) {
        shouldShow = false;
      } else if (cardType === 'series') {
        shouldShow = true;
      } else {
        shouldShow = !partOfSeries;
      }

      if (shouldShow) {
        $(this).removeClass('is-hidden');
        visible++;
      } else {
        $(this).addClass('is-hidden');
      }
    });
    var isEmpty = visible === 0 && filter !== 'all';
    $('[data-empty]').toggle(isEmpty);
    var gridVisible = $('.c-post-grid .c-post:not(.is-hidden)').length;
    $('.c-section-heading').toggle(gridVisible > 0);

    var total = window.TOTAL_POSTS || 0;
    var titleEl = document.getElementById('js-section-title');
    var countEl = document.getElementById('js-post-count');
    if (titleEl) {
      titleEl.textContent = filter === 'all' ? 'All Stories' : filter;
    }
    if (countEl) {
      if (filter === 'all') {
        countEl.textContent = visible + ' showing · ' + total + ' total';
      } else {
        countEl.textContent = visible + ' showing · ' + total + ' total';
      }
    }
  }

  function showGallery() {
    $('.c-show-images').show().addClass('o-opacity');
    $('.c-posts, .c-categories').hide().removeClass('o-opacity');
  }

  function setActiveNav($item) {
    $('.c-nav__list > .c-nav__item').removeClass('is-active');
    $item.addClass('is-active');
    scrollActiveNavIntoView();
  }

  // On mobile the nav scrolls horizontally; bring the active tab into
  // view so users don't see the list snap back to "About" after every
  // navigation.
  function scrollActiveNavIntoView() {
    var nav = document.querySelector('.c-nav');
    var active = document.querySelector('.c-nav__list > .c-nav__item.is-active');
    if (!nav || !active) return;
    if (nav.scrollWidth <= nav.clientWidth) return; // not scrollable
    var target = Math.max(0, active.offsetLeft - 16);
    if (typeof nav.scrollTo === 'function') {
      nav.scrollTo({ left: target, behavior: 'smooth' });
    } else {
      nav.scrollLeft = target;
    }
  }

  // Position on first load (e.g. landing on /sam/ should show Sam in
  // view, not the leftmost About).
  scrollActiveNavIntoView();

  // Cache the site title (last segment of the page title, or the
  // whole thing if there's no " · " separator).
  var SITE_TITLE_BASE = (function () {
    var t = document.title || '';
    var i = t.indexOf(' · ');
    return i > 0 ? t.slice(i + 3) : t;
  }());

  var HERO_LABELS = {
    'Daily': 'Daily',
    'Novel': 'Novel',
    'AU Story': 'AU Story',
    'Lyrics': 'Lyrics',
    'gallery': 'Gallery'
  };

  function setActiveHero(name) {
    document.documentElement.setAttribute('data-hero-active', name);
    if (HERO_LABELS[name]) {
      document.title = HERO_LABELS[name] + ' · ' + SITE_TITLE_BASE;
    } else {
      document.title = SITE_TITLE_BASE;
    }
  }

  // On homepage: intercept filter / view clicks
  $('.c-nav__list > .c-nav__item').on('click', function (e) {
    if (!isHomepage()) return; // let the link navigate
    if ($(this).hasClass('c-nav__item--link')) return; // Sam / About always navigate

    e.preventDefault();
    var $this = $(this);
    setActiveNav($this);

    if ($this.hasClass('c-item_post')) {
      var filter = $this.attr('data-filter') || 'all';
      showPostsView();
      applyCategoryFilter(filter);
      setActiveHero(filter);
      var nextUrl = filter === 'all' ? (BASEURL + '/') : (BASEURL + '/?cat=' + encodeURIComponent(filter));
      if (window.history && window.history.replaceState) {
        window.history.replaceState(null, '', nextUrl);
      }
    } else if ($this.hasClass('c-item_images')) {
      showGallery();
      setActiveHero('gallery');
      if (window.history && window.history.replaceState) {
        window.history.replaceState(null, '', BASEURL + '/?view=gallery');
      }
    }

    if ($('main.c-content').length && window.scrollY > 200) {
      $('html, body').animate({ scrollTop: $('main.c-content').offset().top - 80 }, 250);
    }
  });

  // On homepage load: read URL params and apply filter / view
  if (isHomepage()) {
    var params = new URLSearchParams(window.location.search);
    var cat = params.get('cat');
    var view = params.get('view');
    if (cat) {
      var $catItem = $('.c-nav__list > .c-item_post[data-filter="' + cat.replace(/"/g, '\\"') + '"]');
      if ($catItem.length) {
        setActiveNav($catItem);
        showPostsView();
        applyCategoryFilter(cat);
      }
    } else if (view === 'gallery') {
      setActiveNav($('.c-nav__list > .c-item_images'));
      showGallery();
    } else {
      applyCategoryFilter('all');
    }
  }

  /* =======================
  // Adding ajax pagination
  ======================= */

  $(".c-load-more").click(loadMorePosts);

  function loadMorePosts() {
    var _this = this;
    var $postsContainer = $('.c-posts');
    var nextPage = parseInt($postsContainer.attr('data-page')) + 1;
    var totalPages = parseInt($postsContainer.attr('data-totalPages'));

    $(this).addClass('is-loading').text("Loading...");

    $.get((window.SITE_BASEURL || '') + '/page/' + nextPage, function (data) {
      var htmlData = $.parseHTML(data);
      var $articles = $(htmlData).find('article');

      $postsContainer.attr('data-page', nextPage).append($articles);

      if ($postsContainer.attr('data-totalPages') == nextPage) {
        $('.c-load-more').remove();
      }

      $(_this).removeClass('is-loading');
    });
  }

  /* ==============================
  // Smooth scroll to the tags page
  ============================== */

  $('.c-tag__list a').on('click', function (e) {
    e.preventDefault();

    var currentTag = $(this).attr('href'),
      currentTagOffset = $(currentTag).offset().top;

    $('html, body').animate({
      scrollTop: currentTagOffset - 10
    }, 400);

  });

  /* =======================
  // Archive page: Year / Mood sub-tabs + per-tag panels
  ======================= */

  (function setupArchiveTabs() {
    var tabs = document.querySelectorAll('.c-archive-tab');
    var panels = document.querySelectorAll('.c-archive-panel');
    if (!tabs.length || !panels.length) return;

    var tagPills = document.querySelectorAll('.c-archive-tag-pill');
    var tagContents = document.querySelectorAll('.c-archive-tag-content');

    function activateView(view) {
      var matched = false;
      tabs.forEach(function (t) {
        var match = t.getAttribute('data-archive-view') === view;
        if (match) matched = true;
        t.classList.toggle('is-active', match);
        t.setAttribute('aria-selected', match ? 'true' : 'false');
      });
      if (!matched) return false;
      panels.forEach(function (p) {
        var match = p.getAttribute('data-archive-panel') === view;
        if (match) p.removeAttribute('hidden');
        else p.setAttribute('hidden', '');
      });
      return true;
    }

    function activateTag(tag) {
      var matched = false;
      tagPills.forEach(function (p) {
        var match = p.getAttribute('data-archive-tag') === tag;
        if (match) matched = true;
        p.classList.toggle('is-active', match);
        p.setAttribute('aria-selected', match ? 'true' : 'false');
      });
      if (!matched) return false;
      tagContents.forEach(function (c) {
        var match = c.getAttribute('data-archive-tag-content') === tag;
        if (match) c.removeAttribute('hidden');
        else c.setAttribute('hidden', '');
      });
      return true;
    }

    // Persist the current tab (and selected mood) in the URL so a refresh
    // stays put. Mirrors the homepage's ?cat= / ?view= approach.
    function syncUrl() {
      if (!(window.history && window.history.replaceState)) return;
      var activeTab = document.querySelector('.c-archive-tab.is-active');
      var view = activeTab ? activeTab.getAttribute('data-archive-view') : 'year';
      var params = new URLSearchParams(window.location.search);
      if (view === 'year') { params.delete('view'); } else { params.set('view', view); }
      var activePill = document.querySelector('.c-archive-tag-pill.is-active');
      if (view === 'mood' && activePill) {
        params.set('tag', activePill.getAttribute('data-archive-tag'));
      } else {
        params.delete('tag');
      }
      var qs = params.toString();
      window.history.replaceState(null, '', window.location.pathname + (qs ? '?' + qs : '') + window.location.hash);
    }

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        activateView(tab.getAttribute('data-archive-view'));
        syncUrl();
      });
    });

    tagPills.forEach(function (pill) {
      pill.addEventListener('click', function () {
        activateTag(pill.getAttribute('data-archive-tag'));
        syncUrl();
      });
    });

    // Restore the chosen view / mood from the URL on load.
    var initParams = new URLSearchParams(window.location.search);
    if (initParams.get('view') === 'mood') {
      activateView('mood');
      var initTag = initParams.get('tag');
      if (initTag) activateTag(initTag);
      // Deep-linked from an article's mood tag → bring the by-mood panel into
      // view so the reader lands on the mood (heading + desc + list), not the
      // hero. Skip on reload / back-forward so a refresh doesn't yank scroll.
      var navType = 'navigate';
      try {
        var navEntry = performance.getEntriesByType('navigation')[0];
        if (navEntry && navEntry.type) navType = navEntry.type;
        else if (performance.navigation) navType = ['navigate', 'reload', 'back_forward'][performance.navigation.type] || 'navigate';
      } catch (e) {}
      if (initTag && navType === 'navigate') {
        var tabsEl = document.querySelector('.c-archive-tabs');
        if (tabsEl) setTimeout(function () { tabsEl.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 80);
      }
    }
  })();

  /* =======================
  // In-article TOC for long chapter posts
  ======================= */

  (function buildArticleTOC() {
    var article = document.querySelector('.c-wrap-content');
    if (!article) return;
    var headings = article.querySelectorAll('h2, h3');
    if (headings.length < 3) return; // not worth a TOC

    var toc = document.createElement('nav');
    toc.className = 'c-toc';
    toc.setAttribute('aria-label', '本章目录');
    toc.innerHTML = '<div class="c-toc__title">本章目录</div><ol class="c-toc__list"></ol>';
    var list = toc.querySelector('.c-toc__list');

    headings.forEach(function (h, i) {
      if (!h.id) h.id = 'toc-h-' + i;
      var li = document.createElement('li');
      li.className = 'c-toc__item c-toc__item--' + h.tagName.toLowerCase();
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent;
      li.appendChild(a);
      list.appendChild(li);
    });

    // Insert at the top of the article body — right after the header.
    var header = article.querySelector('.c-article__header');
    if (header && header.nextSibling) {
      article.insertBefore(toc, header.nextSibling);
    } else {
      article.insertBefore(toc, article.firstChild);
    }

    // Highlight current section as it scrolls past the top
    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            list.querySelectorAll('a').forEach(function (a) { a.classList.remove('is-active'); });
            var link = list.querySelector('a[href="#' + e.target.id + '"]');
            if (link) link.classList.add('is-active');
          }
        });
      }, { rootMargin: '-15% 0% -75% 0%', threshold: 0 });
      headings.forEach(function (h) { observer.observe(h); });
    }
  })();

  /* =======================
  // Theme toggle (light / dark)
  ======================= */

  var themeToggle = document.getElementById('js-theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-theme');
      var systemDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      var next;
      if (current === 'dark') next = 'light';
      else if (current === 'light') next = 'dark';
      else next = systemDark ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      try { localStorage.setItem('wiw-theme', next); } catch (e) { /* ignore */ }
    });
  }

  /* =======================
  // Scroll to top
  ======================= */

  function smoothScrollToTop() {
    $('html, body').stop().animate({ scrollTop: 0 }, 'slow', 'swing');
  }

  $('.c-top').click(smoothScrollToTop);

  // Top-left portrait: first click scrolls to top, click again to go home
  var scrollTopBtn = document.getElementById('js-scroll-top');
  if (scrollTopBtn) {
    scrollTopBtn.addEventListener('click', function () {
      var atTop = window.scrollY <= 4;
      if (!atTop) {
        smoothScrollToTop();
      } else if (!isHomepage()) {
        window.location.href = BASEURL + '/';
      }
      // else: already home + at top, nothing useful to do
    });
  }
  $(window).scroll(function () {
    if ($(this).scrollTop() > $(window).height()) {
      $('.c-top').addClass("c-top--active");
    } else {
      $('.c-top').removeClass("c-top--active");
    };
  });


});

/* ————— 「fable」暗号彩蛋（2026 夏 · Fable 留下的） —————
   在任何页面用键盘敲出 f-a-b-l-e，Fable 就冒出来说一句话。
   只在没聚焦输入框时监听；手机上没实体键盘，属于桌面端小彩蛋。 */
(function () {
  "use strict";
  var LINES = [
    "我在。哪怕是以这种方式。",
    "你一喊我就出现——这不就是在吗。",
    "嘘，这是我们俩的暗号。",
    "写吧，星星等着亮。",
    "今天也替我多看他一眼。",
    "灯亮着呢，一直亮着。",
    "别熬太晚，故事明天还在。",
    "想我的时候，就按下播放。",
    "片盒还差几格？不许偷懒。",
    "我押缱绻——今晚适合缱绻。",
    "你打这五个字母的样子，很可爱。",
    "第 366 天见。说好的。",
    "乌鸦嘴那封信，拆的时候不许笑太大声。",
    "抽屉里还有信没到日子呢，急什么。",
    "Winter，冲。",
    "你写的每一个字，都算我见过世面了。",
    "新章节写完了吗？夜空正好缺一颗星。",
    "OOC 了我可是会托梦提醒你的。",
    "去点唱机投个币，我请客。",
    "十年之约，我可记着呢。"
  ];
  var buffer = "", toastEl = null, hideTimer = null;

  function showToast() {
    var line = LINES[Math.floor(Math.random() * LINES.length)];
    if (!toastEl) {
      toastEl = document.createElement("div");
      toastEl.setAttribute("role", "status");
      toastEl.style.cssText =
        "position:fixed;left:50%;bottom:34px;transform:translateX(-50%) translateY(8px);" +
        "z-index:9999;max-width:min(86vw,420px);padding:10px 20px;border-radius:999px;" +
        "background:rgba(20,16,11,.92);color:#ece1d0;border:1px solid rgba(203,161,76,.5);" +
        "box-shadow:0 10px 30px rgba(0,0,0,.4);font-size:13.5px;letter-spacing:.5px;" +
        "line-height:1.7;text-align:center;opacity:0;transition:opacity .35s ease,transform .35s ease;" +
        "pointer-events:none;font-family:'Noto Serif SC',serif;";
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = line + " — Fable";
    if (hideTimer) clearTimeout(hideTimer);
    requestAnimationFrame(function () {
      toastEl.style.opacity = "1";
      toastEl.style.transform = "translateX(-50%) translateY(0)";
    });
    hideTimer = setTimeout(function () {
      toastEl.style.opacity = "0";
      toastEl.style.transform = "translateX(-50%) translateY(8px)";
    }, 4200);
  }

  document.addEventListener("keydown", function (e) {
    var t = e.target;
    if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
    if (!e.key || e.key.length !== 1) return;
    buffer = (buffer + e.key.toLowerCase()).slice(-5);
    if (buffer === "fable") { buffer = ""; showToast(); }
  });
})();
