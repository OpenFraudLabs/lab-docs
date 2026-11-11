/* CheckAm shareable warning cards on the website.
   Cards show a scam type with a blurred example we wrote. They never contain what a visitor pasted,
   a person, an account or a phone number. Events are counted anonymously (no cookies, no IP). */
(function () {
  var API = 'https://ifbkvqazedhghtguanjf.supabase.co/rest/v1/', K = 'sb_publishable_9I-s_mRycqI_gv4i7mXN4Q_l0zph5nq';
  var BASE = '/assets/checkam/cards/', OK = /^[a-z0-9-]{2,40}$/;
  var vid = null; try { vid = localStorage.getItem('ckv'); } catch (e) {}
  function log(ev, key) {
    try { fetch(API + 'rpc/log_card_event', { method: 'POST', keepalive: true, headers: { 'Content-Type': 'application/json', apikey: K, Authorization: 'Bearer ' + K }, body: JSON.stringify({ p_event: ev, p_key: key, p_vid: vid }) }); } catch (e) {}
  }
  function el(tag, attrs, text) { var n = document.createElement(tag); for (var k in attrs) n.setAttribute(k, attrs[k]); if (text) n.textContent = text; return n; }

  // Builds the card block: image, Share (phone share sheet with the image, or WhatsApp link) and Download buttons.
  function cardBlock(key, title) {
    if (!OK.test(key)) return null;
    var sq = BASE + key + '-square.jpg', st = BASE + key + '-story.jpg';
    var wrap = el('div', { 'class': 'wcard' });
    var img = el('img', { src: sq, alt: 'CheckAm scam warning card: ' + (title || 'scam warning'), width: '1080', height: '1080', loading: 'lazy', decoding: 'async' });
    wrap.appendChild(img);
    var row = el('div', { 'class': 'wcard-actions' });
    var share = el('button', { type: 'button', 'class': 'btn primary' }, 'Share this warning');
    var dl = el('a', { href: sq, download: 'checkam-warning-' + key + '.jpg', 'class': 'btn' }, 'Download');
    var dls = el('a', { href: st, download: 'checkam-status-' + key + '.jpg', 'class': 'btn' }, 'Status size');
    share.addEventListener('click', function () {
      log('web_share', key);
      var text = 'Scam warning from CheckAm. Before you pay, check it free on WhatsApp: https://wa.me/2347038317433?text=CARD';
      fetch(sq).then(function (r) { return r.blob(); }).then(function (b) {
        var f = new File([b], 'checkam-warning.jpg', { type: 'image/jpeg' });
        if (navigator.canShare && navigator.canShare({ files: [f] })) return navigator.share({ files: [f], text: text });
        window.open('https://wa.me/?text=' + encodeURIComponent(text + '\n' + location.origin + sq), '_blank', 'noopener');
      }).catch(function () {});
    });
    [dl, dls].forEach(function (a) { a.addEventListener('click', function () { log('web_download', key); }); });
    row.appendChild(share); row.appendChild(dl); row.appendChild(dls);
    wrap.appendChild(row);
    log('web_shown', key);
    return wrap;
  }
  window.CheckAmCards = { block: cardBlock };

  // "This week's scam warning": the card the team has featured in admin.
  var spot = document.getElementById('weekly-card');
  if (spot) {
    fetch(API + 'warning_cards?select=key,title&featured=is.true&active=is.true&limit=1', { headers: { apikey: K, Authorization: 'Bearer ' + K } })
      .then(function (r) { return r.json(); })
      .then(function (rows) {
        var c = rows && rows[0]; if (!c) return;
        var b = cardBlock(c.key, c.title); if (!b) return;
        var t = document.getElementById('weekly-title'); if (t) t.textContent = c.title;
        spot.textContent = ''; spot.appendChild(b);
        var sec = document.getElementById('weekly'); if (sec) sec.hidden = false;
      }).catch(function () {});
  }
})();
