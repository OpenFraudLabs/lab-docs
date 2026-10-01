"""Builds the Open Fraud Labs Academy (static pages + Supabase) in the lab-docs repo.

Run from the repo root:  python3 tools/build_academy.py
Ports account/verify/capstone/admin pages into the Academy shell and adds redirects from old URLs.
"""
import json, os, re, urllib.request

V = "20261001f"
TT = "https://www.tiktok.com/@_drhola"
REPO = "https://github.com/Odugbile1993/openfraudlab-tiktok"
RAW = "https://raw.githubusercontent.com/Odugbile1993/openfraudlab-tiktok/main/"
MODULES = [(1, 3, "Module 1: Foundations"), (4, 14, "Module 2: Statistics and exploring data"),
           (15, 17, "Module 3: Tools of the trade"), (18, 27, "Module 4: Machine learning essentials"),
           (28, 30, "Module 5: Responsible data science and next steps")]

def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

curriculum = json.load(urllib.request.urlopen(RAW + "curriculum.json"))["lessons"]
state = json.load(urllib.request.urlopen(RAW + "state.json"))
released_n = state["next_lesson"] - 1

def module_of(n):
    for lo, hi, name in MODULES:
        if lo <= n <= hi:
            return name
    return "Module 6: Going further"

GTM_HEAD = """    <!-- Google Tag Manager -->
    <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
    new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','GTM-WGCFJFHR');</script>
    <!-- End Google Tag Manager -->"""

def head(title, desc, noindex=False):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{GTM_HEAD}
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(desc)}">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(desc)}">
    <meta property="og:site_name" content="Open Fraud Labs Academy">
    <meta name="theme-color" content="#0E1A2B">
    {'<meta name="robots" content="noindex">' if noindex else ''}
    <link rel="icon" href="/assets/logo.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/assets/css/academy.css?v={V}">
</head>
<body>
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WGCFJFHR" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
    <a class="ac-skip" href="#main">Skip to content</a>
"""

def header(active=""):
    def link(href, label, key):
        cur = ' aria-current="page"' if key == active else ''
        return f'<a href="{href}"{cur}>{label}</a>'
    return f"""    <header class="ac-header">
        <div class="ac-wrap ac-header__bar">
            <a class="ac-brand" href="/academy/" aria-label="Open Fraud Labs Academy home">
                <img src="/assets/logo.png" alt=""><strong>Open Fraud Labs</strong><span>Academy</span>
            </a>
            <nav class="ac-nav" aria-label="Academy">
                {link('/academy/#courses', 'Courses', 'courses')}
                {link('/academy/dashboard/', 'My learning', 'dashboard')}
                {link('/verify/', 'Verify a certificate', 'verify')}
                <a href="/">Open Fraud Labs</a>
            </nav>
            <div class="ac-account" id="ac-account"></div>
            <button class="ac-burger" type="button" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
        </div>
    </header>
"""

FOOTER = f"""    <footer class="ac-footer">
        <div class="ac-wrap ac-footer__grid">
            <div>
                <h3>Open Fraud Labs Academy</h3>
                <p class="ac-muted">Free, practical data courses from Open Fraud Labs in Lagos, Nigeria. Short video lessons, study notes, quizzes and verifiable certificates.</p>
            </div>
            <div>
                <h3>Learn</h3>
                <ul>
                    <li><a href="/academy/courses/data-science/">Data Science from Scratch</a></li>
                    <li><a href="/academy/dashboard/">My learning</a></li>
                    <li><a href="/verify/">Verify a certificate</a></li>
                    <li><a href="{TT}">Lessons on TikTok</a></li>
                </ul>
            </div>
            <div>
                <h3>Open Fraud Labs</h3>
                <ul>
                    <li><a href="/">Main website</a></li>
                    <li><a href="mailto:hello@openfraudlabs.com">hello@openfraudlabs.com</a></li>
                    <li><a href="/terms/">Terms of Service</a></li>
                    <li><a href="/privacy/">Privacy Policy</a></li>
                </ul>
            </div>
        </div>
        <div class="ac-wrap ac-footer__legal">&copy; 2026 Open Fraud Labs. Certificates are certificates of course completion, not accredited qualifications.</div>
    </footer>
"""

SCRIPTS = f"""    <script src="/assets/js/vendor/supabase-2.117.2.js"></script>
    <script src="/assets/js/learn.js?v={V}"></script>
    <script src="/assets/js/academy.js?v={V}"></script>
"""

def page(path, title, desc, main, script="", active="", noindex=False, extra=""):
    html = head(title, desc, noindex) + header(active) + f'    <main id="main">\n{main}\n    </main>\n' + FOOTER + SCRIPTS + extra
    if script:
        html += f"    <script>\n{script}\n    </script>\n"
    html += "</body>\n</html>\n"
    os.makedirs(path, exist_ok=True)
    open(os.path.join(path, "index.html"), "w").write(html)
    print("wrote", path)

def redirect(path, target_js):
    os.makedirs(path, exist_ok=True)
    open(os.path.join(path, "index.html"), "w").write(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="robots" content="noindex"><title>Moved to the Academy</title>
<script>{target_js}</script></head>
<body><p>This page has moved to the <a href="/academy/">Open Fraud Labs Academy</a>.</p></body></html>
""")
    print("redirect", path)

TICK = '<span class="ac-tick"><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 6.2 5 8.5 9.5 3.5"/></svg></span>'
LOCK = '<svg class="ac-lock" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>'

def static_ledger(rows, title, limit=None, demo=False):
    """Server-rendered ledger (works without JS; replaced with live state when signed in)."""
    out = [f'<div class="ac-ledger__head"><strong>{esc(title)}</strong><span class="num">{released_n} of {len(curriculum)} lessons released</span></div>',
           '<div class="ac-ledger__bar"><span style="width:0%"></span></div>']
    cur = None
    for i, l in enumerate(rows[:limit] if limit else rows):
        m = module_of(l["n"])
        if m != cur:
            if cur is not None:
                out.append("</ol>")
            out.append(f'<div class="ac-ledger__module">{esc(m)}</div><ol>')
            cur = m
        if demo:
            st = ["done", "done", "current", "locked", "locked"][min(i, 4)]
        else:
            st = "open" if l["n"] <= released_n else "soon"
        label = {"done": TICK + "Verified", "current": "Up next", "locked": LOCK + "Locked", "open": "Released", "soon": "Coming soon"}[st]
        out.append(f'<li><div class="ac-row is-{st}"><span class="ac-row__n">{l["n"]:02d}</span><span class="ac-row__t">{esc(l["title"])}</span><span class="ac-row__s">{label}</span></div></li>')
    out.append("</ol>")
    return "\n".join(out)

# ============================================================== Academy home
COMING = [("Data Analysis", "Spreadsheets, SQL and dashboards that turn raw data into clear business answers."),
          ("Data Engineering", "Pipelines, warehouses and data models: how reliable data reaches analysts and models."),
          ("Machine Learning", "Build, evaluate and explain models, from regression to gradient boosting."),
          ("Financial Analysis", "Financial statements, ratios, forecasting and valuation for better decisions."),
          ("Live classes", "Live sessions with Q&A for the Academy community.")]
coming_html = "\n".join(f'<li><strong>{esc(t)}</strong><span>{esc(d)}</span><em>In preparation</em></li>' for t, d in COMING)

home_main = f"""        <section class="ac-hero">
            <div class="ac-wrap ac-hero__grid">
                <div>
                    <h1>Practical data skills, one short lesson at a time.</h1>
                    <p class="ac-lead">Free courses from Open Fraud Labs. Watch a 90-second lesson, read the notes, pass the quiz, and work towards a certificate anyone can verify.</p>
                    <div class="ac-hero__actions">
                        <a class="ac-btn ac-btn--primary" href="/academy/courses/data-science/" id="hero-cta">Start Data Science from Scratch</a>
                        <a class="ac-btn ac-btn--secondary" href="#how">How it works</a>
                    </div>
                    <p class="ac-hero__note">No experience needed. New lessons every day.</p>
                </div>
                <div class="ac-ledger" aria-label="Example of course progress">
{static_ledger(curriculum, "Data Science from Scratch", limit=5, demo=True)}
                </div>
            </div>
        </section>

        <section class="ac-section ac-section--white" id="courses">
            <div class="ac-wrap">
                <div class="ac-section__head">
                    <h2>Courses</h2>
                    <p>Start with Data Science from Scratch. More tracks open as they're ready.</p>
                </div>
                <article class="ac-feature">
                    <div class="ac-feature__body">
                        <span class="ac-status ac-status--live">Open for enrolment</span>
                        <h3>Data Science from Scratch</h3>
                        <p class="ac-muted">From &ldquo;what is data science?&rdquo; to building and explaining your first models, with examples from lending, payments and fraud.</p>
                        <ul class="ac-outcomes">
                            <li>Describe and clean real datasets with confidence</li>
                            <li>Understand the statistics behind everyday analysis</li>
                            <li>Train, evaluate and explain simple machine learning models</li>
                        </ul>
                        <div class="ac-hero__actions">
                            <a class="ac-btn ac-btn--primary" href="/academy/courses/data-science/">View course</a>
                        </div>
                    </div>
                    <div class="ac-feature__aside">
                        <dl>
                            <dt>Lessons</dt><dd class="num">30, about 90 seconds each</dd>
                            <dt>Each lesson</dt><dd>Video, study notes, quiz</dd>
                            <dt>Final step</dt><dd>Capstone project</dd>
                            <dt>Cost</dt><dd>Free</dd>
                            <dt>Certificate</dt><dd>Yes, with public verification</dd>
                        </dl>
                    </div>
                </article>
                <div class="ac-coming">
                    <h3 style="margin:1.75rem 0 0.25rem">Coming to the Academy</h3>
                    <ul>
{coming_html}
                    </ul>
                </div>
            </div>
        </section>

        <section class="ac-section" id="how">
            <div class="ac-wrap">
                <div class="ac-section__head">
                    <h2>How a course works</h2>
                    <p>Every lesson follows the same path, and each step unlocks the next. It keeps learning honest, so a certificate means something.</p>
                </div>
                <ol class="ac-steps">
                    <li><h3>Watch</h3><p>A focused 90-second video. It has to be watched to the end.</p></li>
                    <li><h3>Read</h3><p>Study notes with the key ideas, an exercise and the full transcript.</p></li>
                    <li><h3>Quiz</h3><p>Five questions. Score 70% to complete the lesson and unlock the next.</p></li>
                    <li><h3>Capstone</h3><p>Analyse a real public dataset and submit it for review.</p></li>
                    <li><h3>Certificate</h3><p>Earn a certificate with an ID employers can check.</p></li>
                </ol>
            </div>
        </section>

        <section class="ac-section--tight">
            <div class="ac-wrap">
                <div class="ac-social">
                    <div>
                        <h2>New lessons drop daily on TikTok</h2>
                        <p>Follow @_drhola, then like, share and comment. Your questions shape the next lessons.</p>
                    </div>
                    <a class="ac-btn ac-btn--primary" href="{TT}" target="_blank" rel="noopener noreferrer">Follow @_drhola</a>
                </div>
            </div>
        </section>

        <section class="ac-section">
            <div class="ac-narrow ac-faq">
                <h2>Questions</h2>
                <details><summary>Is it really free?</summary><p>Yes. Courses, quizzes and certificates are free. You only need an account so we can save your progress.</p></details>
                <details><summary>Do I need any experience?</summary><p>No. Data Science from Scratch starts from zero. Code is introduced gradually from Module 3.</p></details>
                <details><summary>How long does a course take?</summary><p>Each lesson takes about five minutes including notes and quiz. New lessons are released daily, so most learners finish alongside the release schedule.</p></details>
                <details><summary>Is the certificate accredited?</summary><p>It's a certificate of course completion from Open Fraud Labs, not an accredited academic qualification. Each one has a unique ID that anyone can check on our <a href="/verify/">verification page</a>.</p></details>
                <details><summary>How is my data used?</summary><p>Only to run your account and track your learning. Read the <a href="/privacy/">Privacy Policy</a>.</p></details>
            </div>
        </section>"""

home_script = r"""        (async function () {
            var user = await OFL.getUser();
            if (!user) return;
            var st = await ACADEMY.courseState('data-science');
            var cta = document.getElementById('hero-cta');
            if (st.next) { cta.textContent = 'Continue: Lesson ' + st.next.n; cta.href = '/academy/lesson/?course=data-science&n=' + st.next.n; }
            else if (st.done) { cta.textContent = 'Go to my learning'; cta.href = '/academy/dashboard/'; }
        })();"""

page("academy", "Open Fraud Labs Academy: free practical data courses",
     "Free, beginner-friendly data courses from Open Fraud Labs: 90-second video lessons, study notes, quizzes and verifiable certificates.",
     home_main, home_script, active="courses")

# ============================================================== Course overview
course_main = f"""        <section class="ac-course-hero">
            <div class="ac-wrap ac-course-hero__grid">
                <div>
                    <nav class="ac-crumbs" aria-label="Breadcrumb"><a href="/academy/">Academy</a> / <a href="/academy/#courses">Courses</a> / Data Science from Scratch</nav>
                    <span class="ac-status ac-status--live">Open for enrolment</span>
                    <h1>Data Science from Scratch</h1>
                    <p class="ac-lead">Learn how data becomes decisions: describing and cleaning data, the statistics behind it, and building and explaining your first machine learning models. Examples come from lending, payments and fraud.</p>
                    <p class="ac-muted">Taught by Ayodele Odugbile, data and analytics professional and founder of Open Fraud Labs.</p>
                </div>
                <aside class="ac-facts">
                    <dl>
                        <dt>Lessons</dt><dd class="num">30 (<span data-released>{released_n}</span> released)</dd>
                        <dt>Length</dt><dd>About 5 minutes per lesson</dd>
                        <dt>Level</dt><dd>Beginner</dd>
                        <dt>Cost</dt><dd>Free</dd>
                        <dt>Certificate</dt><dd>Certificate of completion</dd>
                    </dl>
                    <a class="ac-btn ac-btn--primary" id="start-btn" href="/account/?next=/academy/lesson/%3Fcourse%3Ddata-science%26n%3D1">Start the course</a>
                    <a class="ac-btn ac-btn--secondary" href="{TT}" target="_blank" rel="noopener noreferrer">Follow on TikTok</a>
                    <p class="ac-muted" id="start-note" style="margin:0.8rem 0 0;font-size:0.9rem">Free account required to track progress.</p>
                </aside>
            </div>
        </section>

        <section class="ac-section ac-section--white">
            <div class="ac-wrap ac-two">
                <div>
                    <h2>Course outline</h2>
                    <p class="ac-muted">Lessons unlock in order. Complete each one by watching the video, reading the notes and passing the quiz.</p>
                    <div class="ac-ledger" id="ledger">
{static_ledger(curriculum, "Data Science from Scratch")}
                    </div>
                </div>
                <div>
                    <div class="ac-aside-card">
                        <h3>What you'll be able to do</h3>
                        <ul class="ac-outcomes">
                            <li>Explain what data science is and how projects run</li>
                            <li>Identify data types and read a dataset's structure</li>
                            <li>Summarise data with averages, spread and distributions</li>
                            <li>Spot outliers, handle missing data and clean datasets</li>
                            <li>Choose the right chart and avoid common traps</li>
                            <li>Train, test and evaluate simple models, including for fraud</li>
                            <li>Explain model decisions and recognise bias</li>
                        </ul>
                    </div>
                    <div class="ac-aside-card">
                        <h3>Earn your certificate</h3>
                        <p>Pass all 30 lesson quizzes and get your capstone project approved. Your certificate shows your registered name and an ID anyone can verify.</p>
                        <div class="ac-mini-cert"><small>Certificate of Completion</small><b>Your name here</b><small>Data Science from Scratch</small></div>
                        <p style="margin:1rem 0 0"><a href="/academy/capstone/?course=data-science">Read the capstone brief</a></p>
                    </div>
                </div>
            </div>
        </section>"""

course_script = r"""        (async function () {
            var st = await ACADEMY.courseState('data-science');
            if (!st.lessons.length) return;
            ACADEMY.renderLedger(document.getElementById('ledger'), st, { course: 'data-science' });
            var rel = st.lessons.filter(function (l) { return l.released; }).length;
            document.querySelectorAll('[data-released]').forEach(function (e) { e.textContent = rel; });
            var btn = document.getElementById('start-btn'), note = document.getElementById('start-note');
            if (!st.user) return;
            note.textContent = st.done + ' of ' + st.total + ' lessons complete';
            if (st.next) { btn.textContent = st.done ? 'Continue: Lesson ' + st.next.n : 'Start Lesson 1'; btn.href = '/academy/lesson/?course=data-science&n=' + st.next.n; }
            else { btn.textContent = 'Go to my learning'; btn.href = '/academy/dashboard/'; note.textContent = 'You’re up to date. The next lesson is released soon.'; }
        })();"""

page("academy/courses/data-science", "Data Science from Scratch | Open Fraud Labs Academy",
     "A free beginner course: 30 short video lessons with study notes, quizzes, a capstone project and a verifiable certificate.",
     course_main, course_script, active="courses")

# ============================================================== Lesson player
lesson_main = """        <div class="ac-wrap ac-player">
            <aside class="ac-player__side" id="side">
                <button class="ac-btn ac-btn--secondary ac-side-toggle" type="button" id="side-toggle" aria-expanded="false">Course outline <span aria-hidden="true">&#9662;</span></button>
                <div class="ac-ledger" id="ledger"><div class="ac-ledger__head"><strong>Loading…</strong></div></div>
            </aside>
            <section class="ac-stage" id="stage">
                <nav class="ac-crumbs" aria-label="Breadcrumb"><a href="/academy/courses/data-science/">Data Science from Scratch</a> / <span id="crumb-mod"></span></nav>
                <h1 id="lesson-title">Loading lesson…</h1>
                <div id="msg"></div>
                <div class="ac-tabs" role="tablist" id="tabs" hidden>
                    <button class="ac-tab" role="tab" data-step="watch" aria-selected="true"><i>1</i><span>Watch<small id="tab-watch-sub">Video</small></span></button>
                    <button class="ac-tab" role="tab" data-step="read" aria-selected="false"><i>2</i><span>Read<small id="tab-read-sub">Study notes</small></span></button>
                    <button class="ac-tab" role="tab" data-step="quiz" aria-selected="false"><i>3</i><span>Quiz<small id="tab-quiz-sub">5 questions</small></span></button>
                    <button class="ac-tab ac-tab--lab" role="tab" data-step="lab" aria-selected="false" hidden><i>&lt;/&gt;</i><span>Practice<small id="tab-lab-sub">Code lab</small></span></button>
                </div>
                <div class="ac-panel" data-panel="watch" hidden>
                    <div class="ac-watch" id="watch">
                        <div class="ac-video"><video id="video" playsinline preload="metadata" controls controlslist="nodownload noplaybackrate" disablepictureinpicture></video></div>
                        <div class="ac-watch__meta">
                            <h3>Watch the full video</h3>
                            <p>The notes unlock when you reach the end. You can pause and rewind, but you can't skip ahead.</p>
                            <div class="ac-meter" id="meter"><span></span></div>
                            <p class="ac-muted num" id="meter-text">0:00 watched</p>
                            <div id="watch-next"></div>
                            <div class="ac-follow">
                                <strong>Enjoying the lesson?</strong>
                                <p>Follow @_drhola on TikTok, then like, share and comment on this lesson. It helps more people learn.</p>
                                <a class="ac-btn ac-btn--secondary ac-btn--sm" href="https://www.tiktok.com/@_drhola" target="_blank" rel="noopener noreferrer">Follow on TikTok</a>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="ac-panel" data-panel="read" hidden>
                    <article class="ac-notes" id="notes"><p class="ac-muted">Loading notes…</p></article>
                    <div id="notes-end" aria-hidden="true"></div>
                    <div class="ac-gate"><p id="read-hint">Read to the end of the notes to continue.</p><button class="ac-btn ac-btn--primary" type="button" id="read-done" disabled>I've read the notes</button></div>
                </div>
                <div class="ac-panel" data-panel="lab" hidden><div id="lab"></div></div>
                <div class="ac-panel" data-panel="quiz" hidden>
                    <div id="quiz-wait"></div>
                    <form id="quiz" hidden></form>
                    <div id="quiz-result"></div>
                </div>
            </section>
        </div>"""

lesson_script = r"""        (async function () {
            var sb = OFL.sb, el = OFL.el, A = ACADEMY;
            var course = OFL.qs('course') || 'data-science', n = parseInt(OFL.qs('n') || '1', 10);
            var msg = document.getElementById('msg');
            var here = location.pathname + location.search;
            var user = await OFL.requireUser(here); if (!user) return;
            var prof = (await sb.from('profiles').select('terms_accepted_at').eq('id', user.id).maybeSingle()).data;
            if (!prof || !prof.terms_accepted_at) { location.href = '/account/?next=' + encodeURIComponent(here); return; }

            var side = document.getElementById('side'), tog = document.getElementById('side-toggle');
            side.classList.add('is-collapsed');
            tog.addEventListener('click', function () { var c = side.classList.toggle('is-collapsed'); tog.setAttribute('aria-expanded', String(!c)); });

            var st = await A.courseState(course);
            A.renderLedger(document.getElementById('ledger'), st, { course: course, currentN: n });
            var lesson = st.lessons.find(function (l) { return l.n === n; });
            document.getElementById('crumb-mod').textContent = A.moduleOf(n);
            var titleEl = document.getElementById('lesson-title');

            function lockedPanel(heading, text, href, label) {
                titleEl.textContent = heading;
                var box = el('div', { class: 'ac-panel ac-locked' });
                box.innerHTML = A.LOCK.replace('ac-lock', '');
                box.appendChild(el('p', { text: text }));
                if (href) box.appendChild(el('a', { class: 'ac-btn ac-btn--primary', href: href, text: label }));
                msg.appendChild(box);
            }
            if (!lesson || !lesson.released) {
                return lockedPanel('Lesson ' + n + ' is coming soon', 'New lessons are released daily. Follow @_drhola on TikTok to catch it first.', st.next ? '/academy/lesson/?course=' + course + '&n=' + st.next.n : '/academy/dashboard/', st.next ? 'Go to Lesson ' + st.next.n : 'My learning');
            }
            titleEl.textContent = 'Lesson ' + n + ': ' + lesson.title;
            document.title = 'Lesson ' + n + ': ' + lesson.title + ' | Open Fraud Labs Academy';
            if (n > 1 && !((n - 1) in st.passed)) {
                return lockedPanel('Lesson ' + n + ' is locked', 'Lessons unlock in order. Complete Lesson ' + (st.next ? st.next.n : n - 1) + ' first.',
                    '/academy/lesson/?course=' + course + '&n=' + (st.next ? st.next.n : n - 1), 'Go to Lesson ' + (st.next ? st.next.n : n - 1));
            }

            var act = (await sb.from('lesson_activity').select('*').eq('course_slug', course).eq('lesson_n', n).maybeSingle()).data || {};
            var passed = n in st.passed;
            var tabs = document.getElementById('tabs'); tabs.hidden = false;
            // Long-form lessons (spec in longform/) add rich reading and a code lab.
            var nn = (n < 10 ? '0' : '') + n, labDone = false;
            try { labDone = localStorage.getItem('ofl-lab-done:' + course + ':' + n) === '1'; } catch (e) {}
            var long = null;
            try { var lr = await fetch(A.RAW + 'longform/ds' + nn + '.json', { cache: 'no-cache' }); if (lr.ok) long = await lr.json(); } catch (e) {}
            var tabEls = {}; tabs.querySelectorAll('.ac-tab').forEach(function (t) { tabEls[t.getAttribute('data-step')] = t; });
            var panels = {}; document.querySelectorAll('[data-panel]').forEach(function (p) { panels[p.getAttribute('data-panel')] = p; });

            function unlocked(step) {
                if (step === 'watch' || step === 'lab') return true;
                if (step === 'read') return !!act.video_completed_at || passed;
                return !!act.notes_completed_at || passed;
            }
            function refreshTabs() {
                tabEls.watch.classList.toggle('is-done', !!act.video_completed_at || passed);
                tabEls.read.classList.toggle('is-done', !!act.notes_completed_at || passed);
                tabEls.quiz.classList.toggle('is-done', passed);
                tabEls.lab.classList.toggle('is-done', !!labDone);
                ['read', 'quiz'].forEach(function (s) { tabEls[s].disabled = !unlocked(s); });
                document.getElementById('tab-quiz-sub').textContent = passed ? 'Passed' : '5 questions';
            }
            function show(step) {
                if (!unlocked(step)) return;
                Object.keys(panels).forEach(function (k) { panels[k].hidden = k !== step; tabEls[k].setAttribute('aria-selected', String(k === step)); });
                if (step === 'read') openNotes();
                if (step === 'quiz') loadQuiz();
                if (step === 'lab') openLab();
            }
            if (long && long.practice) { tabEls.lab.hidden = false; tabs.classList.add('ac-tabs--4'); }
            Object.keys(tabEls).forEach(function (k) { tabEls[k].addEventListener('click', function () { show(k); }); });
            refreshTabs();

            // ---------------- Watch ----------------
            var video = document.getElementById('video'), meter = document.getElementById('meter'), meterText = document.getElementById('meter-text');
            video.src = lesson.video_url;
            var maxSeen = 0, done = !!act.video_completed_at || passed, dur = lesson.video_seconds || 0;
            function fmt(s) { s = Math.max(0, Math.floor(s)); return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2); }
            function paintMeter() {
                var total = video.duration || dur || 1;
                var pct = done ? 100 : Math.min(100, 100 * maxSeen / total);
                meter.firstChild.style.width = pct + '%'; meter.classList.toggle('is-done', done);
                meterText.textContent = done ? 'Video complete' : fmt(maxSeen) + ' of ' + fmt(total) + ' watched';
            }
            paintMeter();
            video.addEventListener('loadedmetadata', function () {
                document.getElementById('watch').classList.toggle('ac-watch--wide', video.videoWidth > video.videoHeight);
                paintMeter();
            });
            if (long) document.getElementById('watch').classList.add('ac-watch--wide');
            video.addEventListener('ratechange', function () { if (!done && video.playbackRate !== 1) video.playbackRate = 1; });
            video.addEventListener('timeupdate', function () {
                if (!video.seeking && video.currentTime - maxSeen < 1.5) maxSeen = Math.max(maxSeen, video.currentTime);
                paintMeter();
            });
            video.addEventListener('seeking', function () { if (!done && video.currentTime > maxSeen + 0.75) video.currentTime = maxSeen; });
            var started = !!act.video_started_at;
            video.addEventListener('play', async function () {
                if (started || done) return;
                started = true;
                var r = await sb.rpc('start_video', { p_course: course, p_lesson: n });
                if (r.error) { started = false; video.pause(); OFL.notice(msg, OFL.friendlyError(r.error), 'error'); }
            });
            video.addEventListener('ended', async function () {
                if (done) return;
                var r = await sb.rpc('complete_video', { p_course: course, p_lesson: n });
                if (r.error) return OFL.notice(msg, OFL.friendlyError(r.error), 'error');
                done = true; act.video_completed_at = new Date().toISOString(); paintMeter(); refreshTabs();
                watchNext();
            });
            function watchNext() {
                var box = document.getElementById('watch-next'); box.textContent = '';
                if (done) box.appendChild(el('button', { class: 'ac-btn ac-btn--primary', type: 'button', text: 'Continue to the notes', onclick: function () { show('read'); } }));
            }
            watchNext();

            // ---------------- Read ----------------
            var notesLoaded = false, sawEnd = false, openedAt = act.notes_opened_at ? new Date(act.notes_opened_at).getTime() : null, timer = null;
            var readBtn = document.getElementById('read-done'), hint = document.getElementById('read-hint');
            async function openNotes() {
                if (!notesLoaded) {
                    notesLoaded = true;
                    try {
                        if (long && long.reading) renderReading(long);
                        else renderNotes(await (await fetch(A.RAW + 'lessons/ds' + nn + '.json', { cache: 'no-cache' })).json());
                    } catch (e) { document.getElementById('notes').textContent = 'The notes could not be loaded. Please refresh the page.'; }
                }
                if (act.notes_completed_at || passed) { readBtn.hidden = true; hint.textContent = 'Notes complete.'; return; }
                if (!openedAt) {
                    var r = await sb.rpc('open_notes', { p_course: course, p_lesson: n });
                    if (r.error) return OFL.notice(msg, OFL.friendlyError(r.error), 'error');
                    openedAt = Date.now();
                }
                tick();
            }
            function tick() {
                clearTimeout(timer);
                var left = Math.ceil(45 - (Date.now() - openedAt) / 1000);
                if (!sawEnd) hint.textContent = 'Read to the end of the notes to continue.';
                else if (left > 0) hint.textContent = 'Take a moment with the notes. You can continue in ' + left + 's.';
                else hint.textContent = 'Done reading? Continue to the quiz.';
                readBtn.disabled = !(sawEnd && left <= 0);
                if (left > 0 || !sawEnd) timer = setTimeout(tick, 1000);
            }
            new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting && notesLoaded) { sawEnd = true; if (openedAt) tick(); } }); })
                .observe(document.getElementById('notes-end'));
            readBtn.addEventListener('click', async function () {
                readBtn.disabled = true;
                var r = await sb.rpc('complete_notes', { p_course: course, p_lesson: n });
                if (r.error) { readBtn.disabled = false; return OFL.notice(msg, OFL.friendlyError(r.error), 'error'); }
                act.notes_completed_at = new Date().toISOString(); refreshTabs(); show('quiz');
            });
            function renderReading(spec) {
                var box = document.getElementById('notes'); box.textContent = '';
                if (spec.objectives) {
                    var ob = el('div', { class: 'ac-objectives' }, el('h2', { text: 'By the end of this lesson you can' }));
                    var ol = el('ul'); spec.objectives.forEach(function (o) { ol.appendChild(el('li', { text: o })); }); ob.appendChild(ol); box.appendChild(ob);
                }
                var body = el('div', { class: 'ac-reading' });
                body.innerHTML = window.marked.parse(spec.reading); // our own course content, from the course repo
                body.querySelectorAll('table').forEach(function (t) { var w = el('div', { class: 'ac-table-wrap' }); t.parentNode.insertBefore(w, t); w.appendChild(t); });
                box.appendChild(body);
                if (spec.practice) box.appendChild(el('p', { class: 'ac-callout' }, 'Practise in your browser: open the ', el('strong', { text: 'Practice' }), ' tab above to write and run the code yourself.'));
                var d = el('details', {}, el('summary', { text: 'Full transcript' }));
                spec.chapters.forEach(function (c) {
                    d.appendChild(el('h3', { text: c.title }));
                    c.segments.forEach(function (sg) {
                        var parts = sg.steps ? sg.steps.map(function (x) { return x.say; }) : [sg.say, sg.run_say];
                        parts.forEach(function (t) { if (t) d.appendChild(el('p', { text: t })); });
                    });
                });
                box.appendChild(d);
            }
            var labMounted = false;
            function openLab() {
                if (labMounted || !long || !long.practice) return; labMounted = true;
                CODELAB.mount(document.getElementById('lab'), long.practice, { course: course, lesson: n, onPass: function () {
                    labDone = true; try { localStorage.setItem('ofl-lab-done:' + course + ':' + n, '1'); } catch (e) {} refreshTabs();
                    document.getElementById('tab-lab-sub').textContent = 'Solved';
                } });
            }
            if (labDone) document.getElementById('tab-lab-sub').textContent = 'Solved';
            function renderNotes(spec) {
                var box = document.getElementById('notes'); box.textContent = '';
                var skip = { 'NEXT LESSON': 1, 'THANKS FOR WATCHING': 1, 'NEXT': 1 };
                if (spec.summary) { box.appendChild(el('h2', { text: 'In a nutshell' })); box.appendChild(el('p', { class: 'ac-summary', text: spec.summary })); }
                var ul = el('ul');
                spec.slides.slice(1).forEach(function (s) {
                    if (skip[(s.tag || '').toUpperCase()]) return;
                    var t = (s.tag || '').toLowerCase(); t = t.charAt(0).toUpperCase() + t.slice(1);
                    ul.appendChild(el('li', {}, el('strong', { text: t + ': ' }), (s.text || '').replace(/\n/g, ' / ') + (s.sub ? ' (' + s.sub + ')' : '')));
                });
                box.appendChild(el('h2', { text: 'Key ideas' })); box.appendChild(ul);
                if (spec.practice) { box.appendChild(el('h2', { text: 'Try it yourself' })); box.appendChild(el('p', { text: spec.practice })); }
                var d = el('details', {}, el('summary', { text: 'Full transcript' }));
                spec.slides.forEach(function (s) { d.appendChild(el('p', { text: s.say })); });
                box.appendChild(d);
            }

            // ---------------- Quiz ----------------
            var quizLoaded = false, qs = [], order = [];
            var form = document.getElementById('quiz'), waitBox = document.getElementById('quiz-wait'), result = document.getElementById('quiz-result');
            function shuffle(a) { for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var x = a[i]; a[i] = a[j]; a[j] = x; } return a; }
            // keepResults: leave the marked answers visible while the learner waits.
            function cooldown(seconds, keepResults) {
                if (!keepResults) form.hidden = true;
                waitBox.textContent = '';
                var box = el('div', { class: 'ac-wait', role: 'status' }); waitBox.appendChild(box);
                var end = Date.now() + seconds * 1000;
                (function loop() {
                    var s = Math.ceil((end - Date.now()) / 1000);
                    if (s <= 0) {
                        box.className = 'ofl-notice ofl-notice--info'; box.textContent = 'You can try the quiz again now. The questions have been reshuffled. ';
                        box.appendChild(el('button', { class: 'ac-btn ac-btn--primary ac-btn--sm', type: 'button', text: 'Try again', onclick: function () { waitBox.textContent = ''; buildQuiz(); } }));
                        return;
                    }
                    box.textContent = 'Review the video and notes, then try again in ' + fmt(s) + '.';
                    setTimeout(loop, 1000);
                })();
            }
            async function loadQuiz() {
                if (quizLoaded) return; quizLoaded = true;
                var q = await sb.from('quiz_questions').select('position, question, options').eq('course_slug', course).eq('lesson_n', n).order('position');
                qs = q.data || [];
                if (!qs.length) { waitBox.appendChild(el('p', { class: 'ac-muted', text: 'The quiz for this lesson is being prepared. Please check back soon.' })); return; }
                var last = (await sb.from('quiz_attempts').select('passed, created_at').eq('course_slug', course).eq('lesson_n', n).order('created_at', { ascending: false }).limit(1)).data;
                if (last && last[0] && !last[0].passed) {
                    var left = 600 - (Date.now() - new Date(last[0].created_at).getTime()) / 1000;
                    if (left > 0) return cooldown(left);
                }
                buildQuiz();
            }
            function buildQuiz() {
                form.textContent = ''; result.textContent = '';
                if (passed) form.appendChild(el('p', { class: 'ofl-notice ofl-notice--success', text: 'You’ve passed this lesson. You can take the quiz again to practise.' }));
                order = shuffle(qs.map(function (_, i) { return i; }));
                order.forEach(function (qi, k) {
                    var item = qs[qi], fs = el('fieldset', { class: 'ac-q', 'data-q': qi }, el('legend', { text: (k + 1) + '. ' + item.question }));
                    shuffle(item.options.map(function (_, j) { return j; })).forEach(function (j) {
                        fs.appendChild(el('label', { class: 'ac-opt' }, el('input', { type: 'radio', name: 'q' + qi, value: j, required: true }), el('span', { text: item.options[j] })));
                    });
                    fs.appendChild(el('p', { class: 'ac-q__fb', hidden: true }));
                    form.appendChild(fs);
                });
                form.appendChild(el('button', { class: 'ac-btn ac-btn--primary', type: 'submit', text: 'Submit answers' }));
                form.hidden = false;
            }
            form.addEventListener('submit', async function (e) {
                e.preventDefault();
                var answers = qs.map(function (_, i) { return parseInt(form['q' + i].value, 10); });
                var btn = form.querySelector('button[type=submit]'); btn.disabled = true;
                var r = await sb.rpc('submit_quiz', { p_course: course, p_lesson: n, p_answers: answers });
                if (r.error) {
                    btn.disabled = false;
                    var m = /COOLDOWN:(\d+)/.exec(r.error.message || '');
                    if (m) return cooldown(+m[1]);
                    return OFL.notice(result, OFL.friendlyError(r.error), 'error');
                }
                var res = r.data, pct = Math.round(res.score * 100);
                btn.hidden = true; form.querySelectorAll('input').forEach(function (i) { i.disabled = true; });
                res.results.forEach(function (x, i) {
                    var fs = form.querySelector('[data-q="' + i + '"]'), fb = fs.querySelector('.ac-q__fb');
                    fs.classList.add(x.correct ? 'is-right' : 'is-wrong'); fb.hidden = false;
                    fb.textContent = x.correct ? 'Correct. ' + (x.explanation || '') :
                        (res.passed ? 'The answer is “' + qs[i].options[x.correct_index] + '”. ' + (x.explanation || '') : 'Not quite.');
                });
                var actions = el('div', { class: 'ofl-actions' });
                if (res.passed) {
                    passed = true; st.passed[n] = res.score; st.done = Object.keys(st.passed).length; refreshTabs();
                    A.renderLedger(document.getElementById('ledger'), st, { course: course, currentN: n });
                    var nl = st.lessons.find(function (l) { return l.n === n + 1; });
                    if (nl && nl.released) actions.appendChild(el('a', { class: 'ac-btn ac-btn--primary', href: '/academy/lesson/?course=' + course + '&n=' + (n + 1), text: 'Start Lesson ' + (n + 1) }));
                    else if (n >= st.total) actions.appendChild(el('a', { class: 'ac-btn ac-btn--primary', href: '/academy/capstone/?course=' + course, text: 'Go to the capstone project' }));
                    actions.appendChild(el('a', { class: 'ac-btn ac-btn--secondary', href: '/academy/dashboard/', text: 'My learning' }));
                } else {
                    actions.appendChild(el('button', { class: 'ac-btn ac-btn--secondary', type: 'button', text: 'Rewatch the video', onclick: function () { show('watch'); } }));
                }
                var next = res.passed && !(st.lessons.find(function (l) { return l.n === n + 1 && l.released; })) && n < st.total;
                result.textContent = '';
                result.appendChild(el('div', { class: 'ac-result ' + (res.passed ? 'is-pass' : 'is-fail') },
                    el('h3', { text: (res.passed ? 'Lesson complete: ' : 'Not passed yet: ') + pct + '% (' + res.correct + ' of ' + res.total + ')' }),
                    el('p', { text: res.passed ? (next ? 'Lesson ' + (n + 1) + ' is released soon. Follow @_drhola on TikTok to catch it.' : 'Nice work. Your progress is saved.')
                        : 'You need 70% to pass. Answers are shown once you pass. You can try again in 10 minutes.' }), actions));
                if (!res.passed) cooldown(600, true);
                result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            });

            // Start on the first unfinished step.
            show(passed || !act.video_completed_at ? 'watch' : (!act.notes_completed_at ? 'read' : 'quiz'));
        })();"""

page("academy/lesson", "Lesson | Open Fraud Labs Academy", "Watch, read, practise and take the quiz for this Open Fraud Labs Academy lesson.",
     lesson_main, lesson_script, noindex=True,
     extra=f'''    <script src="/assets/js/vendor/marked-18.0.14.js"></script>
    <script src="/assets/js/codelab.js?v={V}"></script>
''')

# ============================================================== Dashboard
dash_main = """        <div class="ac-wrap">
            <div class="ac-dash-head">
                <h1 id="hello">My learning</h1>
                <div id="msg"></div>
            </div>
            <div id="next"></div>
            <div class="ac-two">
                <div>
                    <h2>Data Science from Scratch</h2>
                    <div class="ac-ledger" id="ledger"><div class="ac-ledger__head"><strong>Loading…</strong></div></div>
                </div>
                <div>
                    <div class="ac-aside-card">
                        <h3>Your path to the certificate</h3>
                        <ul class="ac-checklist" id="checklist"></ul>
                        <div id="cert-action"></div>
                    </div>
                    <div class="ac-aside-card">
                        <h3>Stay in the loop</h3>
                        <p>New lessons drop daily on TikTok. Follow @_drhola, then like, share and comment.</p>
                        <a class="ac-btn ac-btn--secondary ac-btn--sm" href="https://www.tiktok.com/@_drhola" target="_blank" rel="noopener noreferrer">Follow on TikTok</a>
                    </div>
                </div>
            </div>
        </div>"""

dash_script = r"""        (async function () {
            var sb = OFL.sb, el = OFL.el, A = ACADEMY, msg = document.getElementById('msg');
            var user = await OFL.requireUser('/academy/dashboard/'); if (!user) return;
            var prof = (await sb.from('profiles').select('full_name, terms_accepted_at').eq('id', user.id).maybeSingle()).data || {};
            if (!prof.terms_accepted_at) { location.href = '/account/?next=/academy/dashboard/'; return; }
            document.getElementById('hello').textContent = prof.full_name ? 'Welcome back, ' + prof.full_name.split(' ')[0] : 'My learning';
            var course = 'data-science';
            var st = await A.courseState(course);
            A.renderLedger(document.getElementById('ledger'), st, { course: course });
            var cap = ((await sb.from('capstone_submissions').select('status, feedback, submitted_at').eq('course_slug', course).order('submitted_at', { ascending: false }).limit(1)).data || [])[0];
            var cert = ((await sb.from('certificates').select('id').eq('course_slug', course)).data || [])[0];

            var next = document.getElementById('next');
            var released = st.lessons.filter(function (l) { return l.released; }).length;
            var title, text, href, label;
            if (st.next) {
                title = st.done ? 'Continue with Lesson ' + st.next.n : 'Start your first lesson';
                text = st.next.title; href = '/academy/lesson/?course=' + course + '&n=' + st.next.n; label = st.done ? 'Continue' : 'Start Lesson 1';
            } else if (st.done < st.total) {
                title = 'You’re up to date'; text = 'You’ve completed every released lesson. The next one is released soon.'; href = 'https://www.tiktok.com/@_drhola'; label = 'Follow on TikTok';
            } else if (!cap || cap.status === 'changes_requested') {
                title = 'All lessons complete'; text = 'Submit your capstone project to earn your certificate.'; href = '/academy/capstone/?course=' + course; label = 'Go to the capstone';
            } else if (cert) {
                title = 'Course complete'; text = 'Your certificate is ready to share.'; href = '/verify/?id=' + cert.id; label = 'View certificate';
            } else {
                title = 'Capstone ' + (cap.status === 'approved' ? 'approved' : 'under review'); text = cap.status === 'approved' ? 'Claim your certificate below.' : 'You’ll see the result here.'; href = '/academy/capstone/?course=' + course; label = 'View submission';
            }
            next.appendChild(el('div', { class: 'ac-next' },
                el('div', {}, el('h2', { text: title }), el('p', { text: text })),
                el('a', { class: 'ac-btn ac-btn--primary', href: href, text: label, target: href.indexOf('http') === 0 ? '_blank' : null, rel: href.indexOf('http') === 0 ? 'noopener noreferrer' : null })));

            var list = document.getElementById('checklist');
            function item(isDone, text, link) {
                list.appendChild(el('li', { class: isDone ? 'is-done' : '' }, el('span', { class: 'ac-dot' }), el('span', { text: text }), link || el('span')));
            }
            item(st.done >= st.total, 'Pass all ' + st.total + ' lesson quizzes (' + st.done + ' done, ' + released + ' released)');
            var capText = !cap ? 'Submit your capstone project' : cap.status === 'approved' ? 'Capstone approved' : cap.status === 'submitted' ? 'Capstone under review' : 'Capstone: changes requested';
            item(cap && cap.status === 'approved', capText, el('a', { href: '/academy/capstone/?course=' + course, text: cap ? 'View' : 'Brief' }));
            item(!!cert, cert ? 'Certificate issued' : 'Claim your certificate');
            var ca = document.getElementById('cert-action');
            if (cert) ca.appendChild(el('a', { class: 'ac-btn ac-btn--primary', href: '/verify/?id=' + cert.id, text: 'View certificate' }));
            else if (st.done >= st.total && cap && cap.status === 'approved') {
                ca.appendChild(el('button', { class: 'ac-btn ac-btn--primary', type: 'button', text: 'Claim your certificate', onclick: async function (e) {
                    e.target.disabled = true;
                    var r = await sb.rpc('claim_certificate', { p_course: course });
                    if (r.error) { e.target.disabled = false; return OFL.notice(msg, OFL.friendlyError(r.error), 'error'); }
                    location.href = '/verify/?id=' + r.data.id;
                } }));
            }
        })();"""

page("academy/dashboard", "My learning | Open Fraud Labs Academy", "Your courses, progress and certificates.",
     dash_main, dash_script, active="dashboard", noindex=True)

# ============================================================== Ported pages
def extract(path):
    html = open(os.path.join(path, "index.html")).read()
    main = re.search(r'<main id="main-content">\n(.*?)\n    </main>', html, re.S).group(1)
    scripts = re.findall(r"    <script>\n(.*?)\n    </script>\n", html, re.S)
    script = [s for s in scripts if "OFL." in s]
    return main, (script[0] if script else "")

PORT_FIX = [("'/my-learning/'", "'/academy/dashboard/'"), ('"/my-learning/"', '"/academy/dashboard/"'), ("/my-learning/", "/academy/dashboard/"),
            ("/learn/capstone/", "/academy/capstone/"), ("OFL.requireUser('/admin/')", "OFL.requireUser('/academy/admin/')"),
            ("'/learn/' + c.slug + '/'", "'/academy/courses/' + c.slug + '/'")]

def port(src, dest, title, desc, active="", noindex=False):
    srcfile = os.path.join(src, "index.html")
    html = open(srcfile).read() if os.path.exists(srcfile) else ""
    if src in PORTED and (not html or "ac-header" in html or "Moved to the Academy" in html):
        main, script = PORTED[src]
    else:
        main, script = extract(src)
        PORTED[src] = (main, script)
    for a, b in PORT_FIX:
        main = main.replace(a, b); script = script.replace(a, b)
    page(dest, title, desc, main, script, active=active, noindex=noindex)

CACHE = "tools/.ported.json"
PORTED = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
PORTED = {k: tuple(v) for k, v in PORTED.items()}
port("learn/capstone", "academy/capstone", "Capstone project | Open Fraud Labs Academy", "Brief and submission for the Data Science from Scratch capstone project.")
port("admin", "academy/admin", "Admin | Open Fraud Labs Academy", "Academy admin.", noindex=True)
port("account", "account", "Your account | Open Fraud Labs Academy", "Create a free Academy account or log in.", noindex=True)
port("verify", "verify", "Verify a certificate | Open Fraud Labs Academy", "Check that an Open Fraud Labs Academy certificate is genuine.", active="verify")
json.dump(PORTED, open(CACHE, "w"))

# ============================================================== Redirects from old URLs
redirect("learn/data-science", "location.replace('/academy/courses/data-science/');")
redirect("learn/quiz", "var p=new URLSearchParams(location.search);location.replace('/academy/lesson/?course='+(p.get('course')||'data-science')+'&n='+(p.get('lesson')||'1'));")
redirect("learn/capstone", "location.replace('/academy/capstone/'+location.search);")
redirect("my-learning", "location.replace('/academy/dashboard/');")
redirect("admin", "location.replace('/academy/admin/');")
