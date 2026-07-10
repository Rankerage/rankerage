// ============================================
// Rankerage.com — i18n (Internationalization)
// ============================================
var I18N = (function() {
  'use strict';

  var _langs = {};          // { code: "Native Name" }
  var _ui = {};             // { en: {...}, ko: {...} }
  var _locale1 = 'en';      // Primary display language
  var _locale2 = 'en';      // Secondary (tooltip) language
  var _countryNames = {};   // { code: { locale: "translated name" } }

  // ============================================
  // Init — load language list + UI translations
  // ============================================
  function init() {
    return Promise.all([
      fetch('lang/languages.json').then(function(r) { return r.json(); }),
      fetch('lang/ui.json').then(function(r) { return r.json(); })
    ]).then(function(results) {
      _langs = results[0];
      _ui = results[1];
      loadSaved();
      return true;
    });
  }

  // ============================================
  // Load saved preferences from localStorage
  // ============================================
  function loadSaved() {
    try {
      var saved = JSON.parse(localStorage.getItem('rankerage_prefs') || '{}');
      if (saved.locale1 && _langs[saved.locale1]) _locale1 = saved.locale1;
      if (saved.locale2 && _langs[saved.locale2]) _locale2 = saved.locale2;
    } catch(e) {}
  }

  function savePrefs() {
    try {
      localStorage.setItem('rankerage_prefs', JSON.stringify({
        locale1: _locale1,
        locale2: _locale2
      }));
    } catch(e) {}
  }

  // ============================================
  // Getters/Setters
  // ============================================
  function getLocale1() { return _locale1; }
  function getLocale2() { return _locale2; }
  function setLocales(l1, l2) {
    if (_langs[l1]) _locale1 = l1;
    if (_langs[l2]) _locale2 = l2;
    savePrefs();
  }

  function getLanguages() { return _langs; }

  // ============================================
  // Translate UI string
  // ============================================
  function t(key) {
    // Try primary locale
    if (_ui[_locale1] && _ui[_locale1][key]) return _ui[_locale1][key];
    // Fall back to English
    if (_ui.en && _ui.en[key]) return _ui.en[key];
    return key;
  }

  // ============================================
  // Translate country name using Intl.DisplayNames
  // ============================================
  function countryName(code, locale) {
    if (!code) return '';
    locale = locale || _locale1;
    try {
      var dn = new Intl.DisplayNames([locale], { type: 'region' });
      return dn.of(code.toUpperCase()) || '';
    } catch(e) {
      return '';
    }
  }

  // ============================================
  // Format number per locale
  // ============================================
  function formatNumber(n, locale) {
    if (n == null || isNaN(n)) return '-';
    locale = locale || _locale1;
    try {
      return new Intl.NumberFormat(locale).format(n);
    } catch(e) {
      return n.toLocaleString();
    }
  }

  // ============================================
  // Build language selector HTML
  // ============================================
  function buildSelectorHTML() {
    var options1 = '', options2 = '';
    var codes = Object.keys(_langs);
    for (var i = 0; i < codes.length; i++) {
      var c = codes[i];
      var sel1 = (c === _locale1) ? ' selected' : '';
      var sel2 = (c === _locale2) ? ' selected' : '';
      options1 += '<option value="' + c + '"' + sel1 + '>' + _langs[c] + '</option>';
      options2 += '<option value="' + c + '"' + sel2 + '>' + _langs[c] + '</option>';
    }
    return options1 + '|||' + options2;
  }

  // ============================================
  // Apply translations to UI
  // ============================================
  function applyUI() {
    // Update DOM elements with data-i18n attributes
    var els = document.querySelectorAll('[data-i18n]');
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      var key = el.getAttribute('data-i18n');
      var translated = t(key);
      if (el.tagName === 'INPUT' && el.type === 'text') {
        el.placeholder = translated;
      } else {
        el.textContent = translated;
      }
    }
    // Update search placeholder
    var search = document.getElementById('search');
    if (search) search.placeholder = t('search');
    // Update search button
    var searchBtn = document.querySelector('.search-btn');
    if (searchBtn) searchBtn.textContent = t('searchBtn');
    // Update login
    var login = document.querySelector('.login-text');
    if (login) login.textContent = t('login');
    // Update scroll hint
    var hint = document.querySelector('.scroll-hint');
    if (hint) hint.textContent = t('scrollHint');
  }

  return {
    init: init,
    t: t,
    countryName: countryName,
    formatNumber: formatNumber,
    getLocale1: getLocale1,
    getLocale2: getLocale2,
    setLocales: setLocales,
    getLanguages: getLanguages,
    buildSelectorHTML: buildSelectorHTML,
    applyUI: applyUI
  };
})();
