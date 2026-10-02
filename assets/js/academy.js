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
            sb.from('lessons').select('n, title, released, video_url, video_seconds').eq('course_slug', course).order('n'),
            user ? sb.from('lesson_progress').select('lesson_n, best_score').eq('course_slug', course) : Promise.resolve({ data: [] }),
            user ? sb.from('profiles').select('is_admin, unlock_all').eq('id', user.id).maybeSingle() : Promise.resolve({ data: null })
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
                 isAdmin: !!prof.is_admin, unlockAll: !!(prof.unlock_all || prof.is_admin) };
    }

    function rowState(l, st, currentN) {
        if (l.n in st.passed) return 'done';
        if (!l.released) return 'soon';
        if (currentN && l.n === currentN) return 'current';
        var prevOk = st.unlockAll || l.n === 1 || ((l.n - 1) in st.passed);
        return prevOk ? 'open' : 'locked';
    }

    // Renders the ledger (lesson list grouped by module) into a container.
    function renderLedger(box, st, opts) {
        opts = opts || {};
        box.textContent = '';
        var head = el('div', { class: 'ac-ledger__head' }, el('strong', { text: opts.title || (st.course ? st.course.title : 'Course') }),
            el('span', { class: 'num', text: st.done + ' of ' + st.total + ' complete' }));
        var bar = el('div', { class: 'ac-ledger__bar' }, el('span', { style: 'width:' + Math.round(100 * st.done / Math.max(1, st.total)) + '%' }));
        box.appendChild(head); box.appendChild(bar);
        var current = null, list = null;
        st.lessons.forEach(function (l) {
            var m = moduleOf(l.n);
            if (m !== current) { current = m; box.appendChild(el('div', { class: 'ac-ledger__module', text: m })); list = el('ol'); box.appendChild(list); }
            var state = rowState(l, st, opts.currentN || (st.next && st.next.n));
            var label = { done: 'Verified', current: opts.currentN ? 'Now' : 'Up next', open: 'Open', locked: 'Locked', soon: 'Coming soon' }[state];
            var s = el('span', { class: 'ac-row__s' });
            if (state === 'done') s.innerHTML = '<span class="ac-tick">' + TICK + '</span>' + label;
            else if (state === 'locked') s.innerHTML = LOCK + label;
            else s.textContent = label;
            var linkable = st.user && (state === 'done' || state === 'current' || state === 'open');
            var row = el(linkable ? 'a' : 'div', { class: 'ac-row is-' + state, href: linkable ? '/academy/lesson/?course=' + opts.course + '&n=' + l.n : null,
                'aria-current': opts.currentN === l.n ? 'step' : null },
                el('span', { class: 'ac-row__n', text: (l.n < 10 ? '0' : '') + l.n }), el('span', { class: 'ac-row__t', text: l.title }), s);
            list.appendChild(el('li', {}, row));
        });
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
        var p = (await OFL.sb.from('profiles').select('full_name, is_admin').eq('id', user.id).maybeSingle()).data || {};
        var panel = el('div', { class: 'ac-menu__panel', hidden: true, role: 'menu' },
            el('div', { class: 'ac-menu__who' }, el('strong', { text: p.full_name || 'Your account' }), el('span', { text: user.email })),
            el('a', { href: '/academy/dashboard/', role: 'menuitem', text: 'My learning' }),
            el('a', { href: '/account/', role: 'menuitem', text: 'Account settings' }),
            p.is_admin ? el('a', { href: '/academy/admin/', role: 'menuitem', text: 'Admin' }) : null,
            el('button', { type: 'button', role: 'menuitem', text: 'Log out', onclick: async function () { await OFL.sb.auth.signOut(); location.href = '/academy/'; } }));
        var btn = el('button', { class: 'ac-avatar', type: 'button', 'aria-haspopup': 'menu', 'aria-expanded': 'false', 'aria-label': 'Account menu', text: initials(p.full_name || user.email) });
        btn.addEventListener('click', function (e) {
            e.stopPropagation(); panel.hidden = !panel.hidden; btn.setAttribute('aria-expanded', String(!panel.hidden));
        });
        document.addEventListener('click', function () { panel.hidden = true; btn.setAttribute('aria-expanded', 'false'); });
        document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { panel.hidden = true; btn.setAttribute('aria-expanded', 'false'); } });
        slot.appendChild(el('div', { class: 'ac-menu' }, btn, panel));
    }

    window.ACADEMY = { RAW: RAW, moduleOf: moduleOf, courseState: courseState, renderLedger: renderLedger, rowState: rowState, TICK: TICK, LOCK: LOCK };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', header); else header();
})();
