/* ============================================================
   Mohammad Balouchi — lean-construction.ir
   اسکریپت اصلی — همان کارکردهای قبل + انیمیشن‌های جدید
   برای افزودن پروژه/مقاله فقط data/*.json را ویرایش کنید.
   ============================================================ */

(function () {
  'use strict';

  document.documentElement.classList.remove('no-js');

  /* ---------- کمکی‌ها ---------- */
  function isFa() { return (document.documentElement.getAttribute('lang') || 'fa') === 'fa'; }
  function faDigits(s) {
    return String(s).replace(/\d/g, function (d) { return '۰۱۲۳۴۵۶۷۸۹'[d]; });
  }
  function formatNum(n, prefix) {
    var out = (prefix || '') + n;
    return isFa() ? faDigits(out) : out;
  }

  document.addEventListener('DOMContentLoaded', function () {

    /* ---------- نوار پیشرفت اسکرول + حالت هدر ---------- */
    var header = document.querySelector('.site-header');
    var progress = document.createElement('div');
    progress.className = 'scroll-progress';
    progress.setAttribute('aria-hidden', 'true');
    document.body.appendChild(progress);

    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        var y = window.scrollY || 0;
        var max = document.documentElement.scrollHeight - window.innerHeight;
        progress.style.transform = 'scaleX(' + (max > 0 ? Math.min(y / max, 1) : 0) + ')';
        if (header) header.classList.toggle('scrolled', y > 10);
        ticking = false;
      });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    /* ---------- منوی موبایل ---------- */
    var toggle = document.querySelector('.nav-toggle');
    var links = document.querySelector('.nav-links');
    if (toggle && links) {
      toggle.addEventListener('click', function () {
        links.classList.toggle('open');
      });
      links.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', function () { links.classList.remove('open'); });
      });
      document.addEventListener('click', function (e) {
        if (links.classList.contains('open') && !links.contains(e.target) && !toggle.contains(e.target)) {
          links.classList.remove('open');
        }
      });
    }

    /* ---------- نمایان‌شدن هنگام اسکرول (reveal) ---------- */
    var els = document.querySelectorAll('.reveal');
    if ('IntersectionObserver' in window && els.length) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
      els.forEach(function (el) { io.observe(el); });
    } else {
      els.forEach(function (el) { el.classList.add('in'); });
    }

    /* ---------- شمارنده‌های آمار (data-count) ---------- */
    var counters = document.querySelectorAll('.stat b[data-count]');
    function runCounter(el) {
      var target = parseInt(el.getAttribute('data-count'), 10) || 0;
      var prefix = el.getAttribute('data-prefix') || '';
      var dur = 1500, t0 = null;
      function frame(t) {
        if (!t0) t0 = t;
        var p = Math.min((t - t0) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = formatNum(Math.round(target * eased), prefix);
        if (p < 1) requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }
    if ('IntersectionObserver' in window && counters.length) {
      var cio = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { runCounter(e.target); cio.unobserve(e.target); }
        });
      }, { threshold: 0.6 });
      counters.forEach(function (el) { cio.observe(el); });
    }

    /* ---------- نمودار گانت: برچسب میله‌های باریک بیرون میله ---------- */
    document.querySelectorAll('.gantt-bar').forEach(function (bar) {
      var w = parseFloat(bar.style.width) || 0;
      if (w < 15) {
        bar.classList.add('bar-thin');
        var ext = document.createElement('span');
        ext.className = 'bar-ext';
        ext.textContent = bar.textContent.trim();
        bar.textContent = '';
        bar.appendChild(ext);
      }
    });

    /* ---------- نورافکن کارت‌ها (spotlight) ---------- */
    document.querySelectorAll('.card').forEach(function (card) {
      card.addEventListener('mousemove', function (e) {
        var r = card.getBoundingClientRect();
        card.style.setProperty('--mx', (e.clientX - r.left) + 'px');
        card.style.setProperty('--my', (e.clientY - r.top) + 'px');
      });
    });

    renderProjects();
    renderPosts();
  });

  /* ---------- آیکون‌های مقالات ---------- */
  var POST_ICONS = {
    lean: '<svg viewBox="0 0 24 24"><path d="M3 17l4-5 4 3 6-8" stroke-linecap="round" stroke-linejoin="round"/><path d="M13 7h4v4" stroke-linecap="round" stroke-linejoin="round"/><path d="M3 21h18" stroke-linecap="round"/></svg>',
    pm: '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="17" rx="1.5"/><path d="M3 9h18M8 2v4M16 2v4" stroke-linecap="round"/><path d="M6.5 13h5M6.5 16.5h8" stroke-linecap="round"/></svg>',
    km: '<svg viewBox="0 0 24 24"><circle cx="6" cy="6" r="2.3"/><circle cx="18" cy="6" r="2.3"/><circle cx="12" cy="18" r="2.3"/><path d="M7.8 7.3L10.5 16M16.2 7.3L13.5 16M8.3 6h7.4" stroke-linecap="round"/></svg>',
    risk: '<svg viewBox="0 0 24 24"><path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z" stroke-linejoin="round"/><path d="M9 12l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    training: '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="12" rx="1"/><path d="M8 20h8M12 16v4" stroke-linecap="round"/><path d="M7 10l3 2 4-4 3 2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    expert: '<svg viewBox="0 0 24 24"><path d="M12 3v18M7 7h10M4 8l3-1 3 1-3 6-3-6zM14 8l3-1 3 1-3 6-3-6z" stroke-linecap="round" stroke-linejoin="round"/><path d="M4 14a3 3 0 006 0M14 14a3 3 0 006 0" stroke-linecap="round"/><path d="M8 21h8" stroke-linecap="round"/></svg>',
    generic: '<svg viewBox="0 0 24 24"><path d="M3 21h18M5 21V9l7-5 7 5v12M9 21v-6h6v6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  };

  /**
   * نمایش مقالات از data/posts.json
   * برای افزودن/ویرایش مقاله فقط posts.json را تغییر دهید.
   */
  function renderPosts() {
    var container = document.getElementById('posts-grid');
    if (!container) return;
    var root = window.SITE_ROOT || '';
    var lang = window.SITE_LANG || 'fa';
    var limit = parseInt(container.getAttribute('data-limit'), 10) || null;
    var moreLabel = lang === 'en' ? 'Read more' : 'ادامه مطلب';
    var soonLabel = lang === 'en' ? 'COMING SOON' : 'به‌زودی';

    fetch(root + 'data/posts.json')
      .then(function (res) { return res.json(); })
      .then(function (data) {
        var posts = data.posts || [];
        if (limit) posts = posts.slice(0, limit);
        container.innerHTML = posts.map(function (p, i) {
          var title = lang === 'en' ? p.title_en : p.title_fa;
          var excerpt = lang === 'en' ? p.excerpt_en : p.excerpt_fa;
          var tag = lang === 'en' ? p.tag_en : p.tag_fa;
          var link = lang === 'en' ? p.link_en : p.link_fa;
          var icon = POST_ICONS[p.icon] || POST_ICONS.generic;
          var isSoon = p.status !== 'published' || !link;
          var idx = (i + 1 < 10 ? '0' : '') + (i + 1);
          return (
            '<div class="post-card' + (isSoon ? ' soon' : '') + '">' +
              '<div class="post-thumb">' + icon + '</div>' +
              '<div class="post-body">' +
                '<div class="post-meta">' + (isSoon ? soonLabel : tag) + '</div>' +
                '<h3>' + title + '</h3>' +
                '<p>' + excerpt + '</p>' +
                (isSoon ? '' : '<a class="more" href="' + root + link + '">' + moreLabel + '</a>') +
              '</div>' +
            '</div>'
          );
        }).join('');
      })
      .catch(function (err) {
        console.error('Could not load posts.json', err);
      });
  }

  /**
   * نمایش پروژه‌ها از data/projects.json — با عکس واقعی، نقش و شماره ردیف
   * برای افزودن پروژه فقط projects.json را ویرایش کنید.
   */
  function renderProjects() {
    var container = document.getElementById('projects-grid');
    if (!container) return;
    var root = window.SITE_ROOT || '';
    var lang = window.SITE_LANG || 'fa';

    fetch(root + 'data/projects.json')
      .then(function (res) { return res.json(); })
      .then(function (data) {
        var projects = data.projects || [];
        container.innerHTML = projects.map(function (p, i) {
          var title = lang === 'en' ? p.title_en : p.title_fa;
          var role = lang === 'en' ? (p.role_en || '') : (p.role_fa || '');
          var idx = (i + 1 < 10 ? '0' : '') + (i + 1);
          return (
            '<div class="card project-card">' +
              '<div class="project-thumb">' +
                '<img src="' + root + p.image + '" alt="' + title + '" loading="lazy">' +
                '<span class="project-index">' + idx + '</span>' +
              '</div>' +
              '<div class="project-body">' +
                '<h3>' + title + '</h3>' +
                (role ? '<p>' + role + '</p>' : '') +
              '</div>' +
            '</div>'
          );
        }).join('');
      })
      .catch(function (err) {
        console.error('Could not load projects.json', err);
      });
  }
})();
