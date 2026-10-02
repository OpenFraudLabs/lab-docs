/* Open Fraud Labs Academy: header, account menu and course helpers. Requires learn.js (OFL). */
(function () {
    'use strict';
    var el = OFL.el;
    var RAW = 'https://raw.githubusercontent.com/Odugbile1993/openfraudlab-tiktok/main/';
    var MODULES = [[1, 3, 'Module 1: Foundations'], [4, 14, 'Module 2: Statistics and exploring data'],
        [15, 17, 'Module 3: Tools of the trade'], [18, 27, 'Module 4: Machine learning essentials'],
        [28, 30, 'Module 5: Responsible data science and next steps'], [31, 39, 'Module 6: Portfolio projects']];

    function moduleOf(n) {
        for (var i = 0; i < MODULES.length; i++) if (n >= MODULES[i][0] && n <= MODULES[i][1]) return MODULES[i][2];
        return 'Module 6: Going further';
    }
    function initials(name) {
        var p = (name || '').trim().split(/\s+/);
        return ((p[0] || '?')[0] + (p.length > 1 ? p[p.length - 1][0] : '')).toUpperCase();
    }
    var TICK = '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 6.2 5 8.5 9.5 3.5"/></svg>';
    var LOCK = '<svg class="ac-lock" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>';

    // Course state for the signed-in learner: lessons, passed set, and which lesson is next.
    async function courseState(course) {
        var sb = OFL.sb;
        var user = await OFL.getUser();
        var res = await Promise.all([
            sb.from('courses').select('slug, title, total_lessons').eq('slug', course).maybeSingle(),
            sb.from('lessons').select('n, title, released, video_url, video_path, video_seconds').eq('course_slug', course).order('n'),
            user ? sb.from('lesson_progress').select('lesson_n, best_score').eq('course_slug', course) : Promise.resolve({ data: [] }),
            user ? sb.from('profiles').select('is_admin, unlock_all').eq('id', user.id).maybeSingle() : Promise.resolve({ data: null }),
            user ? sb.from('enrollments').select('course_slug').eq('user_id', user.id).eq('course_slug', course).maybeSingle() : Promise.resolve({ data: null })
        ]);
        var prof = res[3].data || {};
        var lessons = res[1].data || [], passed = {};
        (res[2].data || []).forEach(function (p) { passed[p.lesson_n] = p.best_score; });
        var next = null;
        for (var i = 0; i < lessons.length; i++) {
            var l = lessons[i];
            if (!l.released) break;
            if (!(l.n in passed)) { next = l; break; }
        }
        var core = (res[0].data && res[0].data.total_lessons) || lessons.length;
        var done = Object.keys(passed).filter(function (n) { return +n <= core; }).length;
        return { user: user, course: res[0].data, lessons: lessons, passed: passed, next: next, done: done, total: core,
                 isAdmin: !!prof.is_admin, unlockAll: !!(prof.unlock_all || prof.is_admin), enrolled: !!(res[4].data || prof.is_admin) };
    }

    function rowState(l, st, currentN) {
        if (!l.released) return 'soon';
        if (!st.user || !st.enrolled) return 'preview';   // outline only until the learner enrols
        if (l.n in st.passed) return 'done';
        if (currentN && l.n === currentN) return 'current';
        var prevOk = st.unlockAll || l.n === 1 || ((l.n - 1) in st.passed);
        return prevOk ? 'open' : 'locked';
    }

    // Renders the ledger: lessons grouped into collapsible modules, each with its own progress.
    // Only the module you're working in (or the first one) starts open, so the next step stands out.
    function renderLedger(box, st, opts) {
        opts = opts || {};
        box.textContent = '';
        var cur = opts.currentN || (st.next && st.next.n);
        var headText = st.enrolled ? st.done + ' of ' + st.total + ' complete' : st.total + ' lessons and projects';
        var head = el('div', { class: 'ac-ledger__head' + (opts.title === false ? ' ac-ledger__head--bare' : '') },
            opts.title === false ? null : el('strong', { text: opts.title || (st.course ? st.course.title : 'Course') }),
            el('span', { class: 'num', text: headText }));
        box.appendChild(head);
        if (st.enrolled) box.appendChild(el('div', { class: 'ac-ledger__bar', role: 'progressbar', 'aria-valuemin': '0', 'aria-valuemax': String(st.total), 'aria-valuenow': String(st.done), 'aria-label': 'Course progress' },
            el('span', { style: 'width:' + Math.round(100 * st.done / Math.max(1, st.total)) + '%' })));
        var groups = [];
        st.lessons.forEach(function (l) {
            var m = moduleOf(l.n), g = groups[groups.length - 1];
            if (!g || g.name !== m) { g = { name: m, lessons: [] }; groups.push(g); }
            g.lessons.push(l);
        });
        var openIdx = 0;
        groups.forEach(function (g, i) { if (g.lessons.some(function (l) { return l.n === cur; })) openIdx = i; });
        groups.forEach(function (g, gi) {
            var done = g.lessons.filter(function (l) { return l.n in st.passed; }).length;
            var meta = st.enrolled ? done + ' of ' + g.lessons.length : g.lessons.length + (g.lessons.length === 1 ? ' lesson' : ' lessons');
            var sum = el('summary', { class: 'ac-mod__sum' },
                el('span', { class: 'ac-mod__name', text: g.name.replace(/^Module \d+:\s*/, '') }),
                el('span', { class: 'ac-mod__meta num' + (st.enrolled && done === g.lessons.length ? ' is-complete' : ''), text: meta }));
            var det = el('details', { class: 'ac-mod' }, sum);
            if (gi === openIdx || opts.openAll) det.open = true;
            var list = el('ol');
            g.lessons.forEach(function (l) {
                var state = rowState(l, st, cur);
                var s = el('span', { class: 'ac-row__s' });
                if (state === 'done') { s.innerHTML = '<span class="ac-tick">' + TICK + '</span>'; s.setAttribute('aria-label', 'Passed'); }
                else if (state === 'locked') { s.innerHTML = LOCK; s.setAttribute('aria-label', 'Locked'); }
                else if (state === 'current' && opts.currentN !== l.n) s.textContent = 'Up next';
                else if (state === 'soon') s.textContent = 'Coming soon';
                var linkable = st.user && (state === 'done' || state === 'current' || state === 'open');
                var row = el(linkable ? 'a' : 'div', { class: 'ac-row is-' + state, href: linkable ? '/academy/lesson/?course=' + opts.course + '&n=' + l.n : null,
                    'aria-current': opts.currentN === l.n ? 'step' : null },
                    el('span', { class: 'ac-row__n', text: (l.n < 10 ? '0' : '') + l.n }), el('span', { class: 'ac-row__t', text: l.title }), s);
                list.appendChild(el('li', {}, row));
            });
            det.appendChild(list);
            box.appendChild(det);
        });
        if (opts.currentN) {
            var here = box.querySelector('[aria-current="step"]');
            var scroller = box.closest('.ac-player__side');
            if (here && scroller) setTimeout(function () { var y = here.getBoundingClientRect().top - scroller.getBoundingClientRect().top + scroller.scrollTop; scroller.scrollTop = Math.max(0, y - scroller.clientHeight / 3); }, 0);
        }
    }

    async function header() {
        var slot = document.getElementById('ac-account');
        var burger = document.querySelector('.ac-burger'), nav = document.querySelector('.ac-nav');
        if (burger && nav) burger.addEventListener('click', function () {
            var open = nav.classList.toggle('is-open'); burger.setAttribute('aria-expanded', String(open));
        });
        if (!slot) return;
        var user = await OFL.getUser();
        slot.textContent = '';
        if (!user) {
            var next = encodeURIComponent(location.pathname + location.search);
            slot.appendChild(el('a', { class: 'ac-btn ac-btn--ghost ac-btn--sm', href: '/account/?mode=login&next=' + next, text: 'Log in' }));
            slot.appendChild(el('a', { class: 'ac-btn ac-btn--primary ac-btn--sm', href: '/account/?next=' + next, text: 'Sign up free' }));
            return;
        }
        var p = (await OFL.sb.from('profiles').select('full_name, is_admin, staff_role').eq('id', user.id).maybeSingle()).data || {};
        var panel = el('div', { class: 'ac-menu__panel', hidden: true, role: 'menu' },
            el('div', { class: 'ac-menu__who' }, el('strong', { text: p.full_name || 'Your account' }), el('span', { text: user.email })),
            el('a', { href: '/academy/dashboard/', role: 'menuitem', text: 'My learning' }),
            el('a', { href: '/account/', role: 'menuitem', text: 'Account settings' }),
            p.staff_role ? el('a', { href: '/academy/admin/', role: 'menuitem', text: 'Staff dashboard' }) : null,
            el('button', { type: 'button', role: 'menuitem', text: 'Log out', onclick: async function () { await OFL.sb.auth.signOut(); location.href = '/academy/'; } }));
        var btn = el('button', { class: 'ac-avatar', type: 'button', 'aria-haspopup': 'menu', 'aria-expanded': 'false', 'aria-label': 'Account menu', text: initials(p.full_name || user.email) });
        btn.addEventListener('click', function (e) {
            e.stopPropagation(); panel.hidden = !panel.hidden; btn.setAttribute('aria-expanded', String(!panel.hidden));
        });
        document.addEventListener('click', function () { panel.hidden = true; btn.setAttribute('aria-expanded', 'false'); });
        document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { panel.hidden = true; btn.setAttribute('aria-expanded', 'false'); } });
        slot.appendChild(el('div', { class: 'ac-menu' }, btn, panel));
        bell(slot, user);
    }

    // Messages: enrolment, project reviews, course completion and certificates.
    async function bell(slot, user) {
        var r = await OFL.sb.from('notifications').select('id, title, body, link, read_at, created_at').eq('user_id', user.id).order('created_at', { ascending: false }).limit(15);
        var items = r.data || [];
        var unread = items.filter(function (x) { return !x.read_at; }).length;
        var badge = el('span', { class: 'ac-bell__n', text: String(unread), hidden: !unread });
        var b = el('button', { class: 'ac-bell', type: 'button', 'aria-haspopup': 'true', 'aria-expanded': 'false', 'aria-label': unread ? unread + ' new messages' : 'Messages' });
        b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>';
        b.appendChild(badge);
        var list = el('div', { class: 'ac-bell__panel', hidden: true, role: 'region', 'aria-label': 'Messages' }, el('strong', { class: 'ac-bell__head', text: 'Messages' }));
        if (!items.length) list.appendChild(el('p', { class: 'ac-muted', text: 'No messages yet.' }));
        items.forEach(function (x) {
            list.appendChild(el(x.link ? 'a' : 'div', { class: 'ac-bell__item' + (x.read_at ? '' : ' is-new'), href: x.link || null },
                el('b', { text: x.title }), el('span', { text: x.body }), el('small', { text: OFL.formatDate(x.created_at) })));
        });
        b.addEventListener('click', function (e) {
            e.stopPropagation(); list.hidden = !list.hidden; b.setAttribute('aria-expanded', String(!list.hidden));
            if (!list.hidden && unread) { OFL.sb.rpc('mark_notifications_read'); unread = 0; badge.hidden = true; }
        });
        list.addEventListener('click', function (e) { e.stopPropagation(); });
        document.addEventListener('click', function () { list.hidden = true; b.setAttribute('aria-expanded', 'false'); });
        slot.insertBefore(el('div', { class: 'ac-bell-wrap' }, b, list), slot.firstChild);
    }

    window.ACADEMY = { RAW: RAW, moduleOf: moduleOf, courseState: courseState, renderLedger: renderLedger, rowState: rowState, TICK: TICK, LOCK: LOCK };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', header); else header();
})();
