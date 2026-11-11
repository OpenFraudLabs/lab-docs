/* Products page: menu, live CheckAm numbers, Threat Brief sign-up, anonymous visit count.
   Talks only to the CheckAm database through public, rate-limited functions that return totals, never rows. */
(function () {
  'use strict';
  // Refuse to run inside another site's frame (clickjacking protection; GitHub Pages cannot send frame headers).
  if (window.top !== window.self) { try { window.top.location = window.self.location.href; } catch (e) { document.documentElement.hidden = true; } return; }

  var API = 'https://ifbkvqazedhghtguanjf.supabase.co/rest/v1/rpc/', K = 'sb_publishable_9I-s_mRycqI_gv4i7mXN4Q_l0zph5nq';
  function rpc(fn, body) {
    return fetch(API + fn, { method: 'POST', headers: { 'Content-Type': 'application/json', apikey: K, Authorization: 'Bearer ' + K }, body: JSON.stringify(body || {}), credentials: 'omit', referrerPolicy: 'strict-origin-when-cross-origin' })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error((j && j.message) || 'Request failed'); return j; }); });
  }
  function $(id) { return document.getElementById(id); }

  // Mobile menu
  var btn = document.querySelector('.menu-btn'), nav = $('nav');
  if (btn && nav) btn.addEventListener('click', function () {
    var open = btn.getAttribute('aria-expanded') !== 'true';
    btn.setAttribute('aria-expanded', String(open)); btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    nav.classList.toggle('open', open);
  });

  // Live numbers (totals only)
  var fmt = function (n) { return Number(n || 0).toLocaleString('en-NG'); };
  rpc('checkam_public_stats').then(function (s) {
    if (!s || typeof s !== 'object') return;
    $('n-checks').textContent = fmt(s.checks);
    $('n-reports').textContent = fmt(s.reports);
    if (Number(s.multi_reported) > 0) { $('n-third').textContent = fmt(s.multi_reported); }
    else { $('n-third').textContent = fmt(s.alerts_tracked); $('n-third-label').textContent = 'Scam and cyber alerts tracked'; }
  }).catch(function () { $('n-note').textContent = 'Live numbers could not load right now.'; });

  // Threat Brief sign-up (double opt-in: a confirmation email is sent first)
  var f = $('brief-form');
  if (f) f.addEventListener('submit', function (e) {
    e.preventDefault();
    var email = $('brief-email').value.trim(), msg = $('brief-msg'), b = f.querySelector('button[type=submit]');
    msg.hidden = false; msg.className = 'msg';
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { msg.className = 'msg err'; msg.textContent = 'Please enter a valid email address.'; return; }
    b.disabled = true; b.textContent = 'Sending…';
    var q = new URLSearchParams(location.search);
    rpc('brief_subscribe', { p_email: email, p_source: (q.get('utm_source') || 'products').slice(0, 60), p_website: $('brief-hp').value || null })
      .then(function () { msg.textContent = 'Almost done. Check your inbox for a confirmation email and tap the button in it.'; f.reset(); })
      .catch(function (err) { msg.className = 'msg err'; msg.textContent = err.message || 'Could not subscribe right now. Please try again.'; })
      .then(function () { b.disabled = false; b.textContent = 'Subscribe'; });
  });

  // Anonymous visit count: no cookies, no IP, a random code in this browser.
  var vid = null; try { vid = localStorage.getItem('ckv'); if (!vid) { vid = (crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2)); localStorage.setItem('ckv', vid); } } catch (e) {}
  var q2 = new URLSearchParams(location.search), ref = '';
  try { ref = document.referrer ? new URL(document.referrer).hostname.replace(/^www\./, '') : ''; } catch (e) {}
  var src = q2.get('utm_source') || (/linkedin|lnkd/.test(ref) ? 'linkedin' : /facebook|fb\./.test(ref) ? 'facebook' : /openfraudlabs/.test(ref) ? 'openfraudlabs' : /google\./.test(ref) ? 'google' : ref) || 'direct';
  rpc('log_visit', { p_event: 'view', p_path: location.pathname, p_source: src.slice(0, 40), p_ref: ref || null, p_vid: vid }).catch(function () {});
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href*="wa.me"]'); if (!a) return;
    rpc('log_visit', { p_event: 'wa_click', p_path: location.pathname, p_source: src.slice(0, 40), p_ref: ref || null, p_vid: vid }).catch(function () {});
  });
})();
