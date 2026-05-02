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
    $('.c-categories, .c-blog-tags, .c-show-images').hide().removeClass('o-opacity');
  }

  function applyCategoryFilter(filter) {
    var $items = $('.c-posts').find('[data-category]');
    var visible = 0;
    $items.each(function () {
      var cat = $(this).attr('data-category') || '';
      var cardType = $(this).attr('data-card-type') || 'chapter';
      var partOfSeries = !!$(this).attr('data-series');

      // Rules:
      //   - 'all' view: show chapter cards (each post once); hide series
      //     cards so series don't duplicate the chapters they group.
      //   - Specific category: show series cards in that category; show
      //     chapter cards in that category only if the chapter is NOT
      //     part of a series (its series card represents it instead).
      var shouldShow;
      if (filter === 'all') {
        shouldShow = cardType !== 'series';
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
  }

  function showGallery() {
    $('.c-show-images').show().addClass('o-opacity');
    $('.c-posts, .c-categories, .c-blog-tags').hide().removeClass('o-opacity');
  }

  function showTags() {
    $('.c-blog-tags').show().addClass('o-opacity');
    $('.c-posts, .c-categories, .c-show-images').hide().removeClass('o-opacity');
  }

  function setActiveNav($item) {
    $('.c-nav__list > .c-nav__item').removeClass('is-active');
    $item.addClass('is-active');
  }

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
    'gallery': 'Gallery',
    'tags': 'Tags'
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
    } else if ($this.hasClass('c-item_tags')) {
      showTags();
      setActiveHero('tags');
      if (window.history && window.history.replaceState) {
        window.history.replaceState(null, '', BASEURL + '/?view=tags');
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
    } else if (view === 'tags') {
      setActiveNav($('.c-nav__list > .c-item_tags'));
      showTags();
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
