/* Confirms or cancels a Threat Brief subscription from the link in an email. The token is removed from the address bar straight away. */
(function () {
  'use strict';
  if (window.top !== window.self) { document.documentElement.hidden = true; return; }
  var q = new URLSearchParams(location.search), c = q.get('confirm'), u = q.get('unsubscribe');
  var tok = c || u; if (!tok) return;
  history.replaceState(null, '', location.pathname);
  var title = document.getElementById('tb-title'), text = document.getElementById('tb-text'), btn = document.getElementById('tb-btn');
  if (!/^[0-9a-f]{64}$/.test(tok)) { title.textContent = 'This link is not valid'; text.textContent = 'Please use the latest email we sent you, or subscribe again.'; return; }
  title.textContent = c ? 'Confirming…' : 'Unsubscribing…'; text.textContent = '';
  var K = 'sb_publishable_9I-s_mRycqI_gv4i7mXN4Q_l0zph5nq';
  fetch('https://ifbkvqazedhghtguanjf.supabase.co/rest/v1/rpc/' + (c ? 'brief_confirm' : 'brief_unsubscribe'), {
    method: 'POST', credentials: 'omit', headers: { 'Content-Type': 'application/json', apikey: K, Authorization: 'Bearer ' + K }, body: JSON.stringify({ p_token: tok })
  }).then(function (r) { return r.json(); }).then(function (j) {
    if (c && j && j.ok) { title.textContent = 'You are subscribed'; text.textContent = 'Thank you. The weekly Threat Brief will arrive in your inbox. Every email has an unsubscribe link.'; btn.textContent = 'See our products'; btn.href = '/products/'; }
    else if (c) { title.textContent = 'This link has expired or was already used'; text.textContent = 'If you are not getting the brief, subscribe again and use the newest email.'; }
    else { title.textContent = 'You are unsubscribed'; text.textContent = 'You will not receive the Threat Brief any more. You can subscribe again at any time.'; }
  }).catch(function () { title.textContent = 'Something went wrong'; text.textContent = 'Please try the link again in a minute.'; });
})();
