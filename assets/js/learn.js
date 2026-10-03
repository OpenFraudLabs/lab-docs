/* Open Fraud Labs — learning platform helpers (accounts, progress, quizzes, certificates). */
(function () {
    'use strict';

    var SUPABASE_URL = 'https://virxrqwxvgsbcnmhdwlp.supabase.co';
    // Publishable key: safe to expose. Access is enforced by row-level security in the database.
    var SUPABASE_KEY = 'sb_publishable_8IenXF_4F5ew8hLai8RfVA_dNHq4I72';
    var TIKTOK = 'https://www.tiktok.com/@_drhola';

    var sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY, {
        auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true }
    });

    function el(tag, attrs) {
        var node = document.createElement(tag);
        attrs = attrs || {};
        Object.keys(attrs).forEach(function (k) {
            if (k === 'text') node.textContent = attrs[k];
            else if (k === 'class') node.className = attrs[k];
            else if (k.indexOf('on') === 0 && typeof attrs[k] === 'function') node.addEventListener(k.slice(2), attrs[k]);
            else if (attrs[k] !== null && attrs[k] !== undefined && attrs[k] !== false) node.setAttribute(k, attrs[k]);
        });
        for (var i = 2; i < arguments.length; i++) {
            var kid = arguments[i];
            if (kid === null || kid === undefined || kid === false) continue;
            node.appendChild(typeof kid === 'string' ? document.createTextNode(kid) : kid);
        }
        return node;
    }

    function qs(name) {
        return new URLSearchParams(window.location.search).get(name);
    }

    function notice(container, text, kind) {
        container.textContent = '';
        if (!text) return;
        container.appendChild(el('div', { class: 'ofl-notice ofl-notice--' + (kind || 'info'), role: kind === 'error' ? 'alert' : 'status', text: text }));
    }

    function friendlyError(err) {
        var m = (err && (err.message || err.error_description)) || String(err || 'Something went wrong');
        if (/Invalid login credentials/i.test(m)) return 'That email and password don’t match. Try again or reset your password.';
        if (/Email not confirmed/i.test(m)) return 'Please confirm your email first. Check your inbox (and spam folder) for the link.';
        if (/rate limit/i.test(m)) return 'Too many attempts. Please wait a few minutes and try again.';
        if (/not authorized/i.test(m)) return 'Sign-ups are being switched on right now. Please try again shortly, or email hello@openfraudlabs.com.';
        if (/^SUSPENDED:|banned/i.test(m)) return 'This account is suspended. If you think this is a mistake, email hello@openfraudlabs.com.';
        if (/^PRACTICE:/.test(m)) return m.replace(/^PRACTICE:\s*/, '') + '. Open the Practice tab.';
        if (/^APPLY:/.test(m)) return 'During pre-launch this course is open to shortlisted applicants. Apply for the Founding Cohort at openfraudlabs.com/academy/apply/.';
        if (/^ENROL:/.test(m)) return 'Enrol in this course first: open the course page and choose "Enrol for free".';
        if (/^PAID:/.test(m)) return 'This lesson is part of the full course. See the plans at openfraudlabs.com/academy/pricing/ to unlock it.';
        if (/already registered/i.test(m)) return 'An account with this email already exists. Try logging in instead.';
        return m;
    }

    async function getUser() {
        var res = await sb.auth.getSession();
        return res.data && res.data.session ? res.data.session.user : null;
    }

    async function requireUser(nextPath) {
        var user = await getUser();
        if (!user) {
            window.location.href = '/account/?next=' + encodeURIComponent(nextPath || (location.pathname + location.search));
            return null;
        }
        return user;
    }

    async function isAdmin() {
        var res = await sb.rpc('is_admin');
        return !res.error && res.data === true;
    }

    function formatDate(iso) {
        try {
            return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
        } catch (e) { return iso; }
    }

    // Adds "Log in" or "My Learning" to the top navigation on every page.
    async function navAccount() {
        var list = document.querySelector('.nav-links');
        if (!list || list.querySelector('[data-ofl-account]')) return;
        var user = await getUser();
        var li = el('li', { 'data-ofl-account': '1' },
            el('a', { href: user ? '/academy/dashboard/' : '/account/?mode=login&next=/academy/dashboard/', text: user ? 'My learning' : 'Log in' }));
        var gh = list.querySelector('.nav-link--button');
        list.insertBefore(li, gh ? gh.parentNode : null);
    }

    // Record genuine sign-ins (not page reloads) for the admin reports.
    sb.auth.onAuthStateChange(function (event) {
        if (event !== 'SIGNED_IN') return;
        try { if (sessionStorage.getItem('ofl-login-logged')) return; sessionStorage.setItem('ofl-login-logged', '1'); } catch (e) {}
        setTimeout(function () { sb.rpc('log_event', { p_event: 'login' }); }, 0);
    });
    function track(event, course, lesson, detail) {
        return sb.rpc('log_event', { p_event: event, p_course: course || null, p_lesson: lesson || null, p_detail: detail || null }).then(function () {}, function () {});
    }

    window.OFL = {
        sb: sb, el: el, qs: qs, notice: notice, friendlyError: friendlyError,
        getUser: getUser, requireUser: requireUser, isAdmin: isAdmin, formatDate: formatDate,
        TIKTOK: TIKTOK, track: track
    };

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', navAccount);
    else navAccount();
})();
