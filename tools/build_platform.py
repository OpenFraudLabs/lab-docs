"""Builds the learning-platform pages for openfraudlabs.com (lab-docs repo).

Run from the lab-docs repo root: python3 build_platform.py
Pages reuse the homepage <head>, header and footer so they match the site.
"""
import os, re

CSSV = "20261001c"
S = open("index.html").read()

def head(title, desc):
    h = S[:S.index("</head>")]
    h = re.sub(r"<title>.*?</title>", f"<title>{title} | Open Fraud Labs</title>", h, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', h)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title} | Open Fraud Labs">', h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">', h)
    h = re.sub(r'href="/?assets/css/style\.css\?v=\w+"', f'href="/assets/css/style.css?v={CSSV}"', h)
    return h + "</head>\n"

def header():
    h = S[S.index("<body>"):S.index("</header>") + len("</header>")]
    h = h.replace('src="assets/logo.png"', 'src="/assets/logo.png"')
    for a in ["services", "approach", "learn", "contact"]:
        h = h.replace(f'href="#{a}"', f'href="/#{a}"')
    return h

def footer():
    f = S[S.index('    <script>\n        const navToggle'):]
    f = re.sub(r'    <script>\n        // Keeps lesson counts.*?</script>\n', '', f, flags=re.S)
    f = re.sub(r'    <script src="/assets/js/[^"]+"></script>\n', '', f)
    f = f.replace('src="assets/logo.png"', 'src="/assets/logo.png"')
    for a in ["services", "approach", "learn", "contact"]:
        f = f.replace(f'href="#{a}"', f'href="/#{a}"')
    return f

SCRIPTS = '''    <script src="/assets/js/vendor/supabase-2.117.2.js"></script>
    <script src="/assets/js/learn.js?v=''' + CSSV + '''"></script>
'''

def page(path, title, desc, body, script="", noindex=False):
    h = head(title, desc)
    if noindex:
        h = h.replace("</head>", '    <meta name="robots" content="noindex">\n</head>')
    html = h + header() + "\n\n    <main id=\"main-content\">\n" + body + "\n    </main>\n\n" + SCRIPTS + (f"    <script>\n{script}\n    </script>\n" if script else "") + footer()
    os.makedirs(path, exist_ok=True)
    open(os.path.join(path, "index.html"), "w").write(html)
    print("wrote", path)

def shell(kicker, h1, intro, inner, cls=""):
    return f'''        <section class="section ofl-page {cls}">
            <div class="container ofl-narrow">
                <div class="section-header section-heading">
                    <p class="section-kicker">{kicker}</p>
                    <h1>{h1}</h1>
                    {f"<p>{intro}</p>" if intro else ""}
                </div>
{inner}
            </div>
        </section>'''

# ------------------------------------------------------------------ account
page("account", "Log in or create an account",
     "Create a free Open Fraud Labs account to track your course progress, take quizzes and earn certificates.",
     shell("Your account", "Learn, track progress, earn certificates",
           "A free account lets you take lesson quizzes, save your progress, submit capstone projects and claim certificates of completion.",
           '''                <div id="msg"></div>
                <div id="auth-box" class="ofl-card card" hidden>
                    <div class="ofl-tabs" role="tablist">
                        <button type="button" class="ofl-tab is-active" data-tab="signup" role="tab">Create account</button>
                        <button type="button" class="ofl-tab" data-tab="login" role="tab">Log in</button>
                    </div>
                    <form id="signup-form" class="ofl-form" data-panel="signup">
                        <label>Full name <small>(as it should appear on your certificate)</small>
                            <input name="full_name" required maxlength="120" autocomplete="name"></label>
                        <label>Email <input name="email" type="email" required autocomplete="email"></label>
                        <label>Password <small>(at least 8 characters)</small>
                            <input name="password" type="password" required minlength="8" autocomplete="new-password"></label>
                        <label class="ofl-check"><input type="checkbox" name="agree" required>
                            <span>I agree to the <a href="/privacy/" target="_blank">Privacy Policy</a>.</span></label>
                        <button class="btn btn-primary" type="submit">Create free account</button>
                    </form>
                    <form id="login-form" class="ofl-form" data-panel="login" hidden>
                        <label>Email <input name="email" type="email" required autocomplete="email"></label>
                        <label>Password <input name="password" type="password" required autocomplete="current-password"></label>
                        <button class="btn btn-primary" type="submit">Log in</button>
                        <button class="ofl-link" type="button" id="forgot">Forgot your password?</button>
                    </form>
                    <form id="forgot-form" class="ofl-form" data-panel="forgot" hidden>
                        <p>Enter your email and we’ll send you a link to set a new password.</p>
                        <label>Email <input name="email" type="email" required autocomplete="email"></label>
                        <button class="btn btn-primary" type="submit">Send reset link</button>
                    </form>
                </div>
                <form id="reset-form" class="ofl-card card ofl-form" hidden>
                    <h2>Set a new password</h2>
                    <label>New password <input name="password" type="password" required minlength="8" autocomplete="new-password"></label>
                    <button class="btn btn-primary" type="submit">Save new password</button>
                </form>
                <div id="profile-box" class="ofl-card card" hidden>
                    <h2>Your profile</h2>
                    <p class="ofl-muted">Signed in as <strong id="me-email"></strong></p>
                    <form id="profile-form" class="ofl-form">
                        <label>Full name <small>(shown on your certificates)</small>
                            <input name="full_name" required maxlength="120" autocomplete="name"></label>
                        <button class="btn btn-secondary" type="submit">Save name</button>
                    </form>
                    <div class="ofl-actions">
                        <a class="btn btn-primary" href="/my-learning/">Go to My Learning</a>
                        <button class="btn btn-secondary" type="button" id="logout">Log out</button>
                    </div>
                </div>'''),
     r'''        (async function () {
            var sb = OFL.sb, msg = document.getElementById('msg');
            var next = OFL.qs('next') || '/my-learning/';
            if (!next.startsWith('/')) next = '/my-learning/';
            var authBox = document.getElementById('auth-box'), profileBox = document.getElementById('profile-box'), resetForm = document.getElementById('reset-form');

            function show(tab) {
                document.querySelectorAll('[data-panel]').forEach(function (p) { p.hidden = p.getAttribute('data-panel') !== tab; });
                document.querySelectorAll('.ofl-tab').forEach(function (t) { t.classList.toggle('is-active', t.getAttribute('data-tab') === tab); });
            }
            document.querySelectorAll('.ofl-tab').forEach(function (t) { t.addEventListener('click', function () { OFL.notice(msg, ''); show(t.getAttribute('data-tab')); }); });
            document.getElementById('forgot').addEventListener('click', function () { show('forgot'); });

            async function renderProfile(user) {
                authBox.hidden = true; profileBox.hidden = false;
                document.getElementById('me-email').textContent = user.email;
                var res = await sb.from('profiles').select('full_name').eq('id', user.id).maybeSingle();
                document.querySelector('#profile-form [name=full_name]').value = (res.data && res.data.full_name) || '';
            }

            var recovering = /type=recovery/.test(location.hash) || OFL.qs('reset') === '1';
            sb.auth.onAuthStateChange(function (event) {
                if (event === 'PASSWORD_RECOVERY') { recovering = true; authBox.hidden = true; profileBox.hidden = true; resetForm.hidden = false; }
            });

            var user = await OFL.getUser();
            if (recovering && user) { resetForm.hidden = false; }
            else if (user) { if (OFL.qs('next')) { location.href = next; return; } renderProfile(user); }
            else { authBox.hidden = false; if (OFL.qs('mode') === 'login') show('login'); }

            document.getElementById('signup-form').addEventListener('submit', async function (e) {
                e.preventDefault();
                var f = e.target, btn = f.querySelector('button[type=submit]'); btn.disabled = true;
                var res = await sb.auth.signUp({
                    email: f.email.value.trim(), password: f.password.value,
                    options: { data: { full_name: f.full_name.value.trim() }, emailRedirectTo: location.origin + '/account/?next=' + encodeURIComponent(next) }
                });
                btn.disabled = false;
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                if (res.data.session) { location.href = next; return; }
                f.reset();
                OFL.notice(msg, 'Almost done! We’ve sent a confirmation link to your email. Click it to activate your account (check your spam folder too).', 'success');
            });

            document.getElementById('login-form').addEventListener('submit', async function (e) {
                e.preventDefault();
                var f = e.target, btn = f.querySelector('button[type=submit]'); btn.disabled = true;
                var res = await sb.auth.signInWithPassword({ email: f.email.value.trim(), password: f.password.value });
                btn.disabled = false;
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                location.href = next;
            });

            document.getElementById('forgot-form').addEventListener('submit', async function (e) {
                e.preventDefault();
                var f = e.target;
                var res = await sb.auth.resetPasswordForEmail(f.email.value.trim(), { redirectTo: location.origin + '/account/?reset=1' });
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                OFL.notice(msg, 'If an account exists for that email, a reset link is on its way.', 'success');
            });

            resetForm.addEventListener('submit', async function (e) {
                e.preventDefault();
                var res = await sb.auth.updateUser({ password: resetForm.password.value });
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                resetForm.hidden = true;
                OFL.notice(msg, 'Your password has been updated.', 'success');
                renderProfile((await sb.auth.getUser()).data.user);
            });

            document.getElementById('profile-form').addEventListener('submit', async function (e) {
                e.preventDefault();
                var u = await OFL.getUser();
                var res = await sb.from('profiles').update({ full_name: e.target.full_name.value.trim() }).eq('id', u.id);
                OFL.notice(msg, res.error ? OFL.friendlyError(res.error) : 'Name saved.', res.error ? 'error' : 'success');
            });

            document.getElementById('logout').addEventListener('click', async function () {
                await sb.auth.signOut(); location.href = '/';
            });
        })();''', noindex=True)

# ------------------------------------------------------------------ quiz
page("learn/quiz", "Lesson quiz", "Check your understanding of each Data Science from Scratch lesson.",
     shell("Lesson quiz", '<span id="quiz-title">Loading quiz…</span>', "",
           '''                <p class="ofl-muted" id="quiz-sub"></p>
                <div id="msg"></div>
                <form id="quiz-form" class="ofl-quiz" hidden></form>
                <div id="quiz-result"></div>'''),
     r'''        (async function () {
            var sb = OFL.sb, el = OFL.el, msg = document.getElementById('msg');
            var course = OFL.qs('course') || 'data-science', lesson = parseInt(OFL.qs('lesson') || '1', 10);
            var form = document.getElementById('quiz-form'), result = document.getElementById('quiz-result');

            var l = await sb.from('lessons').select('title, released').eq('course_slug', course).eq('n', lesson).maybeSingle();
            if (!l.data || !l.data.released) { document.getElementById('quiz-title').textContent = 'Quiz not available yet'; return OFL.notice(msg, 'This lesson hasn’t been released yet. Follow @_drhola on TikTok to catch it when it drops.', 'info'); }
            document.getElementById('quiz-title').textContent = 'Lesson ' + lesson + ': ' + l.data.title;
            var sub = document.getElementById('quiz-sub');
            sub.appendChild(document.createTextNode('Score 70% or more to complete this lesson. Haven’t watched it yet? '));
            sub.appendChild(el('a', { href: OFL.TIKTOK, target: '_blank', rel: 'noopener noreferrer', text: 'Watch on TikTok' }));
            sub.appendChild(document.createTextNode(' (follow, like, share and comment!).'));

            var user = await OFL.getUser();
            if (!user) {
                var box = el('div', { class: 'ofl-card card' },
                    el('h2', { text: 'Log in to take this quiz' }),
                    el('p', { text: 'A free account saves your progress and counts each passed quiz towards your certificate.' }),
                    el('div', { class: 'ofl-actions' },
                        el('a', { class: 'btn btn-primary', href: '/account/?next=' + encodeURIComponent(location.pathname + location.search), text: 'Create free account' }),
                        el('a', { class: 'btn btn-secondary', href: '/account/?mode=login&next=' + encodeURIComponent(location.pathname + location.search), text: 'Log in' })));
                return msg.appendChild(box);
            }

            var q = await sb.from('quiz_questions').select('position, question, options').eq('course_slug', course).eq('lesson_n', lesson).order('position');
            if (q.error || !q.data.length) return OFL.notice(msg, 'The quiz for this lesson is being prepared. Please check back soon.', 'info');
            var prog = await sb.from('lesson_progress').select('best_score').eq('course_slug', course).eq('lesson_n', lesson).maybeSingle();
            if (prog.data) OFL.notice(msg, 'You’ve already passed this quiz (best score ' + Math.round(prog.data.best_score * 100) + '%). You can take it again to practise.', 'success');

            q.data.forEach(function (item, i) {
                var fs = el('fieldset', { class: 'ofl-question card', 'data-q': i },
                    el('legend', { text: (i + 1) + '. ' + item.question }));
                item.options.forEach(function (opt, j) {
                    fs.appendChild(el('label', { class: 'ofl-option' },
                        el('input', { type: 'radio', name: 'q' + i, value: j, required: true }), el('span', { text: opt })));
                });
                fs.appendChild(el('p', { class: 'ofl-feedback', hidden: true }));
                form.appendChild(fs);
            });
            var submitBtn = el('button', { class: 'btn btn-primary', type: 'submit', text: 'Submit answers' });
            form.appendChild(submitBtn);
            form.hidden = false;

            form.addEventListener('submit', async function (e) {
                e.preventDefault();
                var answers = q.data.map(function (_, i) { return parseInt(form['q' + i].value, 10); });
                submitBtn.disabled = true;
                var res = await sb.rpc('submit_quiz', { p_course: course, p_lesson: lesson, p_answers: answers });
                submitBtn.disabled = false;
                if (res.error) return OFL.notice(result, OFL.friendlyError(res.error), 'error');
                var r = res.data, pct = Math.round(r.score * 100);
                r.results.forEach(function (x, i) {
                    var fs = form.querySelector('[data-q="' + i + '"]'), fb = fs.querySelector('.ofl-feedback');
                    fs.classList.toggle('is-right', x.correct); fs.classList.toggle('is-wrong', !x.correct);
                    fb.hidden = false;
                    fb.textContent = x.correct ? 'Correct. ' + (x.explanation || '') :
                        (r.passed ? 'The right answer was “' + q.data[i].options[x.correct_index] + '”. ' + (x.explanation || '') : 'Not quite. Review the lesson and try again.');
                });
                result.textContent = '';
                submitBtn.hidden = true;
                form.querySelectorAll('input').forEach(function (i) { i.disabled = true; });
                var actions = el('div', { class: 'ofl-actions' });
                if (r.passed) {
                    var nl = await sb.from('lessons').select('n, released').eq('course_slug', course).eq('n', lesson + 1).maybeSingle();
                    if (nl.data && nl.data.released) actions.appendChild(el('a', { class: 'btn btn-primary', href: '/learn/quiz/?course=' + course + '&lesson=' + (lesson + 1), text: 'Next lesson quiz →' }));
                    actions.appendChild(el('a', { class: 'btn btn-secondary', href: '/my-learning/', text: 'My Learning' }));
                } else {
                    actions.appendChild(el('button', { class: 'btn btn-primary', type: 'button', text: 'Try again', onclick: function () { location.reload(); } }));
                    actions.appendChild(el('a', { class: 'btn btn-secondary', href: OFL.TIKTOK, target: '_blank', rel: 'noopener noreferrer', text: 'Rewatch on TikTok' }));
                }
                result.appendChild(el('div', { class: 'ofl-card card ofl-score ' + (r.passed ? 'is-pass' : 'is-fail') },
                    el('h2', { text: (r.passed ? 'Passed! ' : 'Not passed yet: ') + pct + '% (' + r.correct + ' of ' + r.total + ')' }),
                    el('p', { text: r.passed ? 'This lesson is now marked complete.' : 'You need 70% to pass. Answers are revealed once you pass.' }),
                    actions));
                result.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        })();''')

# ------------------------------------------------------------------ capstone
page("learn/capstone", "Capstone project: Data Science from Scratch",
     "Brief and submission page for the Data Science from Scratch capstone project.",
     shell("Capstone project", "Data Science from Scratch capstone",
           "Bring the whole course together in one small, real analysis. Once it’s approved and all lesson quizzes are passed, you can claim your certificate.",
           '''                <div class="ofl-card card ofl-prose">
                    <h2>The brief</h2>
                    <p>Pick a public dataset that interests you (for example from Kaggle, the World Bank, or a government open-data portal). Then:</p>
                    <ol>
                        <li><strong>Ask one clear question</strong> the data can help answer.</li>
                        <li><strong>Describe the data:</strong> source, rows and columns, data types, and the target if you build a model.</li>
                        <li><strong>Clean it:</strong> handle missing values, duplicates and obvious errors, and explain each choice.</li>
                        <li><strong>Explore it:</strong> summary statistics and at least three well-labelled charts.</li>
                        <li><strong>Model it (optional but encouraged):</strong> a simple model with a train/test split and a fair evaluation metric.</li>
                        <li><strong>Communicate it:</strong> state your answer, your evidence, and the limitations.</li>
                    </ol>
                    <h3>What to submit</h3>
                    <ul>
                        <li>A <strong>public GitHub repository</strong> with your notebook or code and a README that walks through the steps above.</li>
                        <li>A <strong>short write-up</strong> (at least 50 characters) in the form below: your question and what you found.</li>
                    </ul>
                    <h3>How it’s reviewed</h3>
                    <p>Each submission is reviewed by Open Fraud Labs. You’ll see the result here and in My Learning: <em>Approved</em>, or <em>Changes requested</em> with feedback. You can resubmit as many times as you need.</p>
                </div>
                <div id="msg"></div>
                <div id="history"></div>
                <form id="cap-form" class="ofl-card card ofl-form" hidden>
                    <h2>Submit your project</h2>
                    <label>GitHub repository link <input name="repo_url" type="url" required placeholder="https://github.com/you/your-project"></label>
                    <label>Write-up <small>(your question and what you found)</small>
                        <textarea name="writeup" rows="7" required minlength="50" maxlength="5000"></textarea></label>
                    <button class="btn btn-primary" type="submit">Submit for review</button>
                </form>'''),
     r'''        (async function () {
            var sb = OFL.sb, el = OFL.el, msg = document.getElementById('msg');
            var course = OFL.qs('course') || 'data-science';
            var form = document.getElementById('cap-form'), hist = document.getElementById('history');
            var user = await OFL.getUser();
            if (!user) {
                return msg.appendChild(el('div', { class: 'ofl-card card' }, el('h2', { text: 'Log in to submit your capstone' }),
                    el('div', { class: 'ofl-actions' }, el('a', { class: 'btn btn-primary', href: '/account/?next=' + encodeURIComponent(location.pathname + location.search), text: 'Create free account / Log in' }))));
            }
            async function loadHistory() {
                var r = await sb.from('capstone_submissions').select('repo_url, status, feedback, submitted_at, reviewed_at').eq('course_slug', course).order('submitted_at', { ascending: false });
                hist.textContent = '';
                if (!r.data || !r.data.length) { form.hidden = false; return; }
                var latest = r.data[0];
                var label = { submitted: 'Waiting for review', approved: 'Approved', changes_requested: 'Changes requested' }[latest.status];
                var card = el('div', { class: 'ofl-card card' }, el('h2', { text: 'Your submission' }),
                    el('p', {}, el('span', { class: 'ofl-badge ofl-badge--' + latest.status, text: label }), ' submitted ' + OFL.formatDate(latest.submitted_at)),
                    el('p', {}, el('a', { href: latest.repo_url, target: '_blank', rel: 'noopener noreferrer', text: latest.repo_url })));
                if (latest.feedback) card.appendChild(el('blockquote', { class: 'ofl-feedback-box', text: latest.feedback }));
                hist.appendChild(card);
                form.hidden = latest.status === 'approved' || latest.status === 'submitted';
                if (latest.status === 'changes_requested') form.querySelector('h2').textContent = 'Resubmit your project';
            }
            await loadHistory();
            form.addEventListener('submit', async function (e) {
                e.preventDefault();
                var btn = form.querySelector('button'); btn.disabled = true;
                var res = await sb.from('capstone_submissions').insert({ user_id: user.id, course_slug: course, repo_url: form.repo_url.value.trim(), writeup: form.writeup.value.trim() });
                btn.disabled = false;
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                form.reset();
                OFL.notice(msg, 'Submitted! You’ll see the review result here and in My Learning.', 'success');
                loadHistory();
            });
        })();''')

# ------------------------------------------------------------------ my learning
page("my-learning", "My Learning", "Your courses, progress, capstone and certificates at Open Fraud Labs.",
     shell("My learning", '<span id="hello">My Learning</span>', "",
           '''                <div id="msg"></div>
                <div id="courses"></div>'''),
     r'''        (async function () {
            var sb = OFL.sb, el = OFL.el, msg = document.getElementById('msg'), box = document.getElementById('courses');
            var user = await OFL.requireUser('/my-learning/'); if (!user) return;
            var results = await Promise.all([
                sb.from('profiles').select('full_name').eq('id', user.id).maybeSingle(),
                sb.from('courses').select('slug, title, total_lessons').eq('status', 'live'),
                sb.from('lessons').select('course_slug, n, title, released').order('n'),
                sb.from('lesson_progress').select('course_slug, lesson_n, best_score'),
                sb.from('capstone_submissions').select('course_slug, status, feedback, submitted_at').order('submitted_at', { ascending: false }),
                sb.from('certificates').select('id, course_slug, issued_at')
            ]);
            var profile = results[0].data, courses = results[1].data || [], lessons = results[2].data || [],
                progress = results[3].data || [], caps = results[4].data || [], certs = results[5].data || [];
            var name = profile && profile.full_name;
            document.getElementById('hello').textContent = name ? 'Welcome back, ' + name.split(' ')[0] : 'My Learning';
            if (!name) OFL.notice(msg, 'Add your full name in your account settings so it can appear on your certificate.', 'info');

            courses.forEach(function (c) {
                var cl = lessons.filter(function (l) { return l.course_slug === c.slug; });
                var done = progress.filter(function (p) { return p.course_slug === c.slug; });
                var doneSet = {}; done.forEach(function (p) { doneSet[p.lesson_n] = p.best_score; });
                var released = cl.filter(function (l) { return l.released; });
                var cap = caps.find(function (x) { return x.course_slug === c.slug; });
                var cert = certs.find(function (x) { return x.course_slug === c.slug; });
                var pct = Math.round(100 * done.length / c.total_lessons);
                var nextLesson = released.find(function (l) { return !(l.n in doneSet); });

                var card = el('article', { class: 'ofl-card card ofl-course' },
                    el('div', { class: 'ofl-course__head' },
                        el('h2', {}, el('a', { href: '/learn/' + c.slug + '/', text: c.title })),
                        el('span', { class: 'ofl-muted', text: done.length + ' of ' + c.total_lessons + ' lessons completed' })),
                    el('div', { class: 'ofl-progress', role: 'progressbar', 'aria-valuenow': pct, 'aria-valuemin': 0, 'aria-valuemax': 100 },
                        el('span', { style: 'width:' + pct + '%' })));

                var steps = el('ul', { class: 'ofl-steps' });
                steps.appendChild(el('li', { class: done.length >= c.total_lessons ? 'is-done' : '' },
                    'Lesson quizzes: ' + done.length + '/' + c.total_lessons + ' passed' +
                    (released.length < c.total_lessons ? ' (' + released.length + ' released so far, new lessons daily)' : '')));
                var capText = !cap ? 'Capstone project: not submitted yet' :
                    cap.status === 'approved' ? 'Capstone project: approved' :
                    cap.status === 'submitted' ? 'Capstone project: waiting for review' : 'Capstone project: changes requested';
                steps.appendChild(el('li', { class: cap && cap.status === 'approved' ? 'is-done' : '' }, capText, ' · ',
                    el('a', { href: '/learn/capstone/?course=' + c.slug, text: cap ? 'View' : 'See the brief' })));
                steps.appendChild(el('li', { class: cert ? 'is-done' : '' }, cert ? 'Certificate: issued' : 'Certificate: available when both of the above are complete'));
                card.appendChild(steps);

                var actions = el('div', { class: 'ofl-actions' });
                if (nextLesson) actions.appendChild(el('a', { class: 'btn btn-primary', href: '/learn/quiz/?course=' + c.slug + '&lesson=' + nextLesson.n, text: 'Continue: Lesson ' + nextLesson.n + ' quiz' }));
                if (cert) actions.appendChild(el('a', { class: 'btn btn-primary', href: '/verify/?id=' + cert.id, text: 'View certificate' }));
                else if (done.length >= c.total_lessons && cap && cap.status === 'approved') {
                    actions.appendChild(el('button', { class: 'btn btn-primary', type: 'button', text: 'Claim your certificate', onclick: async function (e) {
                        e.target.disabled = true;
                        var r = await sb.rpc('claim_certificate', { p_course: c.slug });
                        if (r.error) { e.target.disabled = false; return OFL.notice(msg, OFL.friendlyError(r.error), 'error'); }
                        location.href = '/verify/?id=' + r.data.id;
                    } }));
                }
                actions.appendChild(el('a', { class: 'btn btn-secondary', href: OFL.TIKTOK, target: '_blank', rel: 'noopener noreferrer', text: 'Watch lessons on TikTok' }));
                card.appendChild(actions);
                box.appendChild(card);
            });
            box.appendChild(el('p', { class: 'ofl-muted' }, 'More courses are coming soon. ', el('a', { href: '/account/', text: 'Account settings' })));
        })();''', noindex=True)

# ------------------------------------------------------------------ verify / certificate
page("verify", "Verify a certificate", "Check that an Open Fraud Labs certificate of completion is genuine.",
     '''        <section class="section ofl-page">
            <div class="container ofl-narrow ofl-noprint">
                <div class="section-header section-heading">
                    <p class="section-kicker">Certificate verification</p>
                    <h1>Verify a certificate</h1>
                    <p>Enter the certificate ID (for example OFL-1A2B-3C4D) to confirm it was issued by Open Fraud Labs.</p>
                </div>
                <form id="verify-form" class="ofl-form ofl-inline">
                    <label class="u-sr-only" for="cid">Certificate ID</label>
                    <input id="cid" name="id" required placeholder="OFL-XXXX-XXXX" autocomplete="off">
                    <button class="btn btn-primary" type="submit">Verify</button>
                </form>
                <div id="msg"></div>
            </div>
            <div class="container" id="cert-wrap" hidden>
                <div class="ofl-cert" id="cert">
                    <div class="ofl-cert__inner">
                        <img src="/assets/logo.png" alt="" class="ofl-cert__logo">
                        <p class="ofl-cert__org">Open Fraud Labs</p>
                        <p class="ofl-cert__kicker">Certificate of Completion</p>
                        <p class="ofl-cert__small">This certifies that</p>
                        <p class="ofl-cert__name" id="c-name"></p>
                        <p class="ofl-cert__small">has successfully completed</p>
                        <p class="ofl-cert__course" id="c-course"></p>
                        <p class="ofl-cert__desc">including all lesson quizzes and an approved capstone project.</p>
                        <div class="ofl-cert__foot">
                            <div><span class="ofl-cert__sig">Ayodele Odugbile</span><span>Founder, Open Fraud Labs</span></div>
                            <div><span id="c-date"></span><span>Date issued</span></div>
                            <div><span id="c-id"></span><span>Certificate ID</span></div>
                        </div>
                        <p class="ofl-cert__note">Verify at openfraudlabs.com/verify. This is a certificate of course completion, not an accredited academic qualification.</p>
                    </div>
                </div>
                <div class="ofl-actions ofl-noprint ofl-center">
                    <button class="btn btn-primary" type="button" onclick="window.print()">Download / Print (save as PDF)</button>
                    <button class="btn btn-secondary" type="button" id="copy-link">Copy verification link</button>
                </div>
            </div>
        </section>''',
     r'''        (async function () {
            var sb = OFL.sb, msg = document.getElementById('msg');
            var form = document.getElementById('verify-form'), wrap = document.getElementById('cert-wrap');
            async function check(id) {
                OFL.notice(msg, ''); wrap.hidden = true;
                var r = await sb.rpc('verify_certificate', { p_id: id });
                if (r.error) return OFL.notice(msg, OFL.friendlyError(r.error), 'error');
                if (!r.data) return OFL.notice(msg, 'No certificate found with ID “' + id + '”. Check the ID and try again.', 'error');
                document.getElementById('c-name').textContent = r.data.full_name;
                document.getElementById('c-course').textContent = r.data.course;
                document.getElementById('c-date').textContent = OFL.formatDate(r.data.issued_at);
                document.getElementById('c-id').textContent = r.data.id;
                document.title = r.data.full_name + ' – ' + r.data.course + ' certificate | Open Fraud Labs';
                OFL.notice(msg, '✓ Genuine certificate issued by Open Fraud Labs to ' + r.data.full_name + ' on ' + OFL.formatDate(r.data.issued_at) + '.', 'success');
                wrap.hidden = false;
                history.replaceState(null, '', '/verify/?id=' + encodeURIComponent(r.data.id));
            }
            form.addEventListener('submit', function (e) { e.preventDefault(); check(form.id.value.trim()); });
            document.getElementById('copy-link').addEventListener('click', function () {
                navigator.clipboard && navigator.clipboard.writeText(location.href).then(function () { OFL.notice(msg, 'Verification link copied.', 'success'); });
            });
            var id = OFL.qs('id');
            if (id) { form.id.value = id; check(id); }
        })();''')

# ------------------------------------------------------------------ admin
page("admin", "Admin", "Open Fraud Labs learning admin.",
     shell("Admin", "Learning admin", "",
           '''                <div id="msg"></div>
                <div id="stats" class="ofl-stats"></div>
                <div class="ofl-tabs" id="filters" hidden>
                    <button type="button" class="ofl-tab is-active" data-status="submitted">Waiting for review</button>
                    <button type="button" class="ofl-tab" data-status="changes_requested">Changes requested</button>
                    <button type="button" class="ofl-tab" data-status="approved">Approved</button>
                </div>
                <div id="subs"></div>'''),
     r'''        (async function () {
            var sb = OFL.sb, el = OFL.el, msg = document.getElementById('msg');
            var user = await OFL.requireUser('/admin/'); if (!user) return;
            if (!(await OFL.isAdmin())) return OFL.notice(msg, 'This page is only for Open Fraud Labs admins.', 'error');
            document.getElementById('filters').hidden = false;

            var counts = await Promise.all([
                sb.from('profiles').select('id', { count: 'exact', head: true }),
                sb.from('quiz_attempts').select('id', { count: 'exact', head: true }),
                sb.from('lesson_progress').select('user_id', { count: 'exact', head: true }),
                sb.from('certificates').select('id', { count: 'exact', head: true })
            ]);
            var stats = document.getElementById('stats');
            [['Learners', counts[0].count], ['Quiz attempts', counts[1].count], ['Lessons completed', counts[2].count], ['Certificates', counts[3].count]]
                .forEach(function (s) { stats.appendChild(el('div', { class: 'ofl-card card ofl-stat' }, el('strong', { text: String(s[1] || 0) }), el('span', { text: s[0] }))); });

            var status = 'submitted';
            document.querySelectorAll('#filters .ofl-tab').forEach(function (t) {
                t.addEventListener('click', function () {
                    document.querySelectorAll('#filters .ofl-tab').forEach(function (x) { x.classList.remove('is-active'); });
                    t.classList.add('is-active'); status = t.getAttribute('data-status'); load();
                });
            });

            async function load() {
                var box = document.getElementById('subs'); box.textContent = 'Loading…';
                var r = await sb.from('capstone_submissions').select('*').eq('status', status).order('submitted_at', { ascending: true });
                if (r.error) return OFL.notice(box, OFL.friendlyError(r.error), 'error');
                var ids = r.data.map(function (s) { return s.user_id; });
                var names = {};
                if (ids.length) {
                    var p = await sb.from('profiles').select('id, full_name').in('id', ids);
                    (p.data || []).forEach(function (x) { names[x.id] = x.full_name || '(no name yet)'; });
                }
                box.textContent = '';
                if (!r.data.length) return box.appendChild(el('p', { class: 'ofl-muted', text: 'Nothing here.' }));
                r.data.forEach(function (s) {
                    var fb = el('textarea', { rows: 3, placeholder: 'Feedback for the learner (required when requesting changes)' });
                    fb.value = s.feedback || '';
                    async function review(newStatus) {
                        if (newStatus === 'changes_requested' && !fb.value.trim()) return OFL.notice(msg, 'Please add feedback explaining what to change.', 'error');
                        var u = await sb.from('capstone_submissions').update({ status: newStatus, feedback: fb.value.trim(), reviewed_at: new Date().toISOString() }).eq('id', s.id);
                        if (u.error) return OFL.notice(msg, OFL.friendlyError(u.error), 'error');
                        OFL.notice(msg, 'Saved: ' + (names[s.user_id] || 'learner') + ' → ' + newStatus.replace('_', ' '), 'success');
                        load();
                    }
                    box.appendChild(el('article', { class: 'ofl-card card ofl-sub' },
                        el('h3', { text: (names[s.user_id] || 'Learner') + ' · ' + s.course_slug }),
                        el('p', { class: 'ofl-muted', text: 'Submitted ' + OFL.formatDate(s.submitted_at) + (s.reviewed_at ? ' · reviewed ' + OFL.formatDate(s.reviewed_at) : '') }),
                        el('p', {}, el('a', { href: s.repo_url, target: '_blank', rel: 'noopener noreferrer', text: s.repo_url })),
                        el('p', { class: 'ofl-writeup', text: s.writeup }),
                        fb,
                        el('div', { class: 'ofl-actions' },
                            el('button', { class: 'btn btn-primary', type: 'button', text: 'Approve', onclick: function () { review('approved'); } }),
                            el('button', { class: 'btn btn-secondary', type: 'button', text: 'Request changes', onclick: function () { review('changes_requested'); } }))));
                });
            }
            load();
        })();''', noindex=True)

# ------------------------------------------------------------------ privacy
page("privacy", "Privacy Policy", "How Open Fraud Labs collects, uses and protects personal data.",
     shell("Legal", "Privacy Policy", "Last updated: 1 October 2026",
           '''                <div class="ofl-card card ofl-prose">
                    <p>This policy explains what personal data Open Fraud Labs (“we”) collects through openfraudlabs.com, why, and the choices you have. We aim to follow the Nigeria Data Protection Act 2023.</p>
                    <h2>Who we are</h2>
                    <p>Open Fraud Labs, Lagos, Nigeria. Contact: <a href="mailto:hello@openfraudlabs.com">hello@openfraudlabs.com</a>.</p>
                    <h2>What we collect</h2>
                    <ul>
                        <li><strong>Account details:</strong> your full name, email address and password (stored securely by our authentication provider; we never see your password).</li>
                        <li><strong>Learning records:</strong> courses you take, quiz attempts and scores, lessons completed, capstone submissions (including the links and write-ups you provide) and reviewer feedback.</li>
                        <li><strong>Certificates:</strong> your name, course, issue date and certificate ID.</li>
                        <li><strong>Website analytics:</strong> this site uses Google Tag Manager, which may collect standard usage data such as pages visited and device information.</li>
                    </ul>
                    <h2>Why we use it</h2>
                    <ul>
                        <li>To provide your account, save your progress and mark quizzes.</li>
                        <li>To review capstone projects and issue certificates.</li>
                        <li>To understand how the courses are used so we can improve them, mostly using aggregated, non-identifying figures.</li>
                        <li>To contact you about your account or learning (for example password resets).</li>
                    </ul>
                    <p>We use your data on the basis of your consent when you create an account, and to deliver the service you sign up for. We do not sell your personal data.</p>
                    <h2>What is public</h2>
                    <p>If you earn a certificate, anyone with its certificate ID can view your name, the course and the issue date on our verification page, so employers can confirm it is genuine. Nothing else about your account is public.</p>
                    <h2>Who processes data for us</h2>
                    <ul>
                        <li><strong>Supabase</strong> hosts our database and logins (servers in London, United Kingdom).</li>
                        <li><strong>GitHub Pages</strong> hosts the website.</li>
                        <li><strong>Google</strong> provides website analytics via Google Tag Manager.</li>
                    </ul>
                    <h2>How long we keep it</h2>
                    <p>We keep your account and learning records while your account is active. Certificates are kept so they can continue to be verified. You can ask us to delete your account at any time; if you do, your certificates will no longer be verifiable.</p>
                    <h2>Your rights</h2>
                    <p>You can ask to access, correct or delete your personal data, object to or restrict its use, receive a copy of it, or withdraw your consent. Email <a href="mailto:hello@openfraudlabs.com">hello@openfraudlabs.com</a> and we will respond as soon as we can. You may also complain to the Nigeria Data Protection Commission.</p>
                    <h2>Security</h2>
                    <p>Data is sent over encrypted connections, and database access rules ensure each learner can only see their own records.</p>
                    <h2>Changes</h2>
                    <p>We may update this policy and will change the date above when we do.</p>
                </div>'''))
