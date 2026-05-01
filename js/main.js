$(document).ready(function () {

  'use strict';

  /* =======================
  // Simple Search Settings
  ======================= */

  if (document.getElementById('js-search-input')) {
    SimpleJekyllSearch({
      searchInput: document.getElementById('js-search-input'),
      resultsContainer: document.getElementById('js-results-container'),
      json: '/search.json',
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
  ======================================= */

  function showPostsView() {
    $('.c-posts').show().addClass('o-opacity');
    $('.c-categories, .c-blog-tags, .c-show-images').hide().removeClass('o-opacity');
  }

  function applyCategoryFilter(filter) {
    var $items = $('.c-posts').find('[data-category]');
    var visible = 0;
    $items.each(function () {
      var cat = $(this).attr('data-category') || '';
      if (filter === 'all' || cat === filter) {
        $(this).removeClass('is-hidden');
        visible++;
      } else {
        $(this).addClass('is-hidden');
      }
    });
    $('[data-empty]').toggle(visible === 0 && filter !== 'all');
  }

  $('.c-nav__list > .c-nav__item').on('click', function () {
    var $this = $(this);
    $('.c-nav__list > .c-nav__item').removeClass('is-active');
    $this.addClass('is-active');

    if ($this.hasClass('c-item_post')) {
      showPostsView();
      applyCategoryFilter($this.attr('data-filter') || 'all');
    } else if ($this.hasClass('c-item_category')) {
      $('.c-categories').show().addClass('o-opacity');
      $('.c-posts, .c-blog-tags, .c-show-images').hide().removeClass('o-opacity');
    } else if ($this.hasClass('c-item_tags')) {
      $('.c-blog-tags').show().addClass('o-opacity');
      $('.c-posts, .c-categories, .c-show-images').hide().removeClass('o-opacity');
    } else if ($this.hasClass('c-item_images')) {
      $('.c-show-images').show().addClass('o-opacity');
      $('.c-posts, .c-categories, .c-blog-tags').hide().removeClass('o-opacity');
    }
  });

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

    $.get('/page/' + nextPage, function (data) {
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
  // Scroll to top
  ======================= */

  $('.c-top').click(function () {
    $('html, body').stop().animate({ scrollTop: 0 }, 'slow', 'swing');
  });
  $(window).scroll(function () {
    if ($(this).scrollTop() > $(window).height()) {
      $('.c-top').addClass("c-top--active");
    } else {
      $('.c-top').removeClass("c-top--active");
    };
  });


});
