"""Builds the Open Fraud Labs Academy (static pages + Supabase) in the lab-docs repo.

Run from the repo root:  python3 tools/build_academy.py
Ports account/verify/capstone/admin pages into the Academy shell and adds redirects from old URLs.
"""
import json, os, re, urllib.request

V = "20261003e"
TT = "https://www.tiktok.com/@_drhola"
REPO = "https://github.com/Odugbile1993/openfraudlab-tiktok"
RAW = "https://raw.githubusercontent.com/Odugbile1993/openfraudlab-tiktok/main/"
MODULES = [(1, 3, "Module 1: Foundations"), (4, 14, "Module 2: Statistics and exploring data"),
           (15, 17, "Module 3: Tools of the trade"), (18, 27, "Module 4: Machine learning essentials"),
           (28, 30, "Module 5: Responsible data science and next steps"), (31, 39, "Module 6: Portfolio projects")]

def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

curriculum = json.load(urllib.request.urlopen(RAW + "curriculum.json"))["lessons"]
state = json.load(urllib.request.urlopen(RAW + "state.json"))
released_n = state.get("academy_next", state["next_lesson"]) - 1

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

def head(title, desc, noindex=False, path=None):
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
    <meta property="og:type" content="website">
    <meta property="og:image" content="https://openfraudlabs.com/assets/og-academy.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:card" content="summary_large_image">
    {f'<link rel="canonical" href="https://openfraudlabs.com/{path}/"><meta property="og:url" content="https://openfraudlabs.com/{path}/">' if path and not noindex else ''}
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
                <p class="ac-muted">Free, practical data courses from Open Fraud Labs in Lagos, Nigeria. Video lessons, coding practice in the browser, quizzes and verifiable certificates.</p>
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
                    <li><a href="/careers/">Careers</a></li>
                    <li><a href="mailto:academy@openfraudlabs.com">academy@openfraudlabs.com</a></li>
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

PUBLIC_PAGES = []
def page(path, title, desc, main, script="", active="", noindex=False, extra=""):
    if not noindex: PUBLIC_PAGES.append(path)
    html = head(title, desc, noindex, path) + header(active) + f'    <main id="main">\n{main}\n    </main>\n' + FOOTER + SCRIPTS + extra
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
    """Server-rendered outline (works without JS; replaced with live state when signed in)."""
    out = [f'<div class="ac-ledger__head"><strong>{esc(title)}</strong><span class="num">{len(curriculum)} lessons and projects</span></div>']
    groups = []
    for l in (rows[:limit] if limit else rows):
        m = module_of(l["n"])
        if not groups or groups[-1][0] != m:
            groups.append((m, []))
        groups[-1][1].append(l)
    for gi, (m, ls) in enumerate(groups):
        name = re.sub(r"^Module \d+:\s*", "", m)
        out.append(f'<details class="ac-mod"{" open" if gi == 0 else ""}><summary class="ac-mod__sum"><span class="ac-mod__name">{esc(name)}</span>'
                   f'<span class="ac-mod__meta num">{len(ls)} {"lesson" if len(ls) == 1 else "lessons"}</span></summary><ol>')
        for l in ls:
            st = "preview" if l["n"] <= released_n else "soon"
            label = "" if st == "preview" else "Coming soon"
            out.append(f'<li><div class="ac-row is-{st}"><span class="ac-row__n">{l["n"]:02d}</span><span class="ac-row__t">{esc(l["title"])}</span><span class="ac-row__s">{label}</span></div></li>')
        out.append("</ol></details>")
    return "\n".join(out)

# ============================================================== Academy home
COMING = [("Data Analysis", "Spreadsheets, SQL and dashboards that turn raw data into clear business answers."),
          ("Data Engineering", "Pipelines, warehouses and data models: how reliable data reaches analysts and models."),
          ("Machine Learning", "Build, evaluate and explain models, from regression to gradient boosting."),
          ("Financial Analysis", "Financial statements, ratios, forecasting and valuation for better decisions."),
          ("Live classes", "Live sessions with Q&A for the Academy community.")]
coming_html = "\n".join(f'<li><strong>{esc(t)}</strong><span>{esc(d)}</span><em>In preparation</em></li>' for t, d in COMING)

home_main = f"""        <a class="ap-banner" id="ap-banner" href="/academy/apply/" hidden><span class="ap-banner__tag">Pre-launch</span><span id="ap-banner-text">Applications are open for the free Founding Cohort</span><span aria-hidden="true">&rarr;</span></a>
        <section class="lp-hero">
            <div class="ac-wrap lp-hero__grid">
                <div class="lp-hero__copy">
                    <h1>Practical data skills, one lesson at a time.</h1>
                    <p class="lp-hero__lead">Short video lessons built on real code and real data. Practise in your browser, build a portfolio, and earn a certificate anyone can verify.</p>
                    <div class="lp-hero__actions">
                        <a class="ac-btn ac-btn--primary lp-btn-lg" href="#courses" id="hero-cta">Browse courses</a>
                        <a class="ac-btn lp-btn-ghost lp-btn-lg" href="#inside">See inside a lesson</a>
                    </div>
                    <dl class="lp-facts">
                        <div><dt>Lessons and project parts</dt><dd class="num">39</dd></div>
                        <div><dt>Hours of video</dt><dd class="num">6.6</dd></div>
                        <div><dt>Coding exercises</dt><dd class="num">117</dd></div>
                    </dl>
                </div>
                <div class="lp-stage" aria-hidden="true">
                    <div class="lp-window">
                        <div class="lp-window__bar"><i></i><i></i><i></i><span>Lesson 25 · Feature engineering</span></div>
                        <img src="/assets/academy/lesson-frame.jpg" width="1280" height="720" alt="">
                    </div>
                    <div class="lp-cell" id="lp-cell">
                        <div class="lp-cell__in"><span class="lp-cell__p">In [3]</span><code id="lp-code">subs.groupby("contract")["churned"].mean().round(3)</code></div>
                        <div class="lp-cell__out" id="lp-out"><span class="lp-cell__p">Out</span><pre>contract
Annual     0.076
Monthly    0.250</pre></div>
                    </div>
                    <div class="lp-badge"><span class="ac-tick">{TICK}</span>Correct! Well done.</div>
                </div>
            </div>
        </section>

        <section class="lp-section" id="inside">
            <div class="ac-wrap">
                <div class="lp-head">
                    <h2>Inside every lesson</h2>
                    <p>The same four steps every time. Each one unlocks the next, so finishing a lesson means you really did the work.</p>
                </div>
                <ol class="lp-steps">
                    <li>
                        <div class="lp-mock lp-mock--video"><img src="/assets/academy/lesson-frame.jpg" alt="" loading="lazy"><div class="lp-mock__play"></div><div class="lp-mock__meter"><span style="width:64%"></span></div></div>
                        <h3>Watch</h3><p>A 10-minute video with worked examples in Python, explained line by line.</p>
                    </li>
                    <li>
                        <div class="lp-mock lp-mock--notes"><b>Mean or median?</b><table><tr><th>Measure</th><th>Outliers?</th></tr><tr><td>Mean</td><td>Pulled a lot</td></tr><tr><td>Median</td><td>Barely moves</td></tr></table></div>
                        <h3>Read</h3><p>Study notes with the code, key terms and common mistakes, ready to revisit.</p>
                    </li>
                    <li>
                        <div class="lp-mock lp-mock--code"><code>median_income = income.median()</code><div class="lp-mock__ok"><span class="ac-tick">{TICK}</span>Correct! Well done.</div></div>
                        <h3>Practise</h3><p>Three coding exercises that run in your browser. Nothing to install.</p>
                    </li>
                    <li>
                        <div class="lp-mock lp-mock--quiz"><b>Which average suits skewed incomes?</b><span>The mean</span><span class="is-picked">The median</span><span>The range</span></div>
                        <h3>Quiz</h3><p>A short quiz to check you understood. Score 70% to complete the lesson.</p>
                    </li>
                </ol>
            </div>
        </section>

        <section class="lp-section lp-section--white">
            <div class="ac-wrap">
                <div class="lp-head">
                    <h2>Finish with a portfolio, not just a certificate</h2>
                    <p>Three guided projects in different industries: the kind of problems working data scientists are asked to solve. Each one is peer reviewed against a published rubric.</p>
                </div>
                <div class="lp-projects">
                    <article class="lp-project">
                        <span class="lp-project__field">Finance</span>
                        <h3>Credit risk</h3>
                        <p>Which loan applications are likely to default, and where should a lender set its approval cut-off?</p>
                        <p class="lp-project__out">You deliver a default model, a costed approval policy and a write-up.</p>
                    </article>
                    <article class="lp-project">
                        <span class="lp-project__field">Health</span>
                        <h3>Clinic no-shows</h3>
                        <p>Who is likely to miss an appointment, and which patients should get a reminder call?</p>
                        <p class="lp-project__out">You deliver a risk model and a reminder plan the clinic could run.</p>
                    </article>
                    <article class="lp-project">
                        <span class="lp-project__field">Real estate</span>
                        <h3>City rents</h3>
                        <p>What drives rent across a city, and what should a new listing be priced at?</p>
                        <p class="lp-project__out">You deliver a price model, error analysis and a valuation tool.</p>
                    </article>
                </div>
            </div>
        </section>

        <section class="lp-section" id="courses">
            <div class="ac-wrap">
                <div class="lp-head">
                    <h2>Courses</h2>
                    <p>Start with Data Science from Scratch. More tracks open as they're ready.</p>
                </div>
                <article class="lp-course">
                    <div class="lp-course__body">
                        <span class="ac-status ac-status--live" id="home-ds-status">Open for enrolment</span>
                        <h3>Data Science from Scratch</h3>
                        <p>From &ldquo;what is data science?&rdquo; to building and explaining your first models, with examples from retail, health, transport, media and finance.</p>
                        <ul class="ac-outcomes">
                            <li>Describe and clean real datasets with confidence</li>
                            <li>Understand the statistics behind everyday analysis</li>
                            <li>Train, evaluate and explain machine learning models</li>
                            <li>Build three portfolio projects in finance, health and real estate</li>
                        </ul>
                        <a class="ac-btn ac-btn--primary" href="/academy/courses/data-science/">View course and enrol</a>
                    </div>
                    <dl class="lp-course__facts">
                        <div><dt>Format</dt><dd>30 video lessons and 3 portfolio projects</dd></div>
                        <div><dt>Each lesson</dt><dd>Video, study notes, coding practice, quiz</dd></div>
                        <div><dt>Level</dt><dd>Beginner, no experience needed</dd></div>
                        <div><dt>Final step</dt><dd>Peer-reviewed capstone project</dd></div>
                        <div><dt>Certificate</dt><dd>Yes, with public verification</dd></div>
                    </dl>
                </article>
                <div class="lp-more" id="more-courses" hidden></div>
                <div class="ac-coming">
                    <h3>Coming to the Academy</h3>
                    <ul id="coming-list">
{coming_html}
                    </ul>
                </div>
            </div>
        </section>

        <section class="lp-section lp-section--white" id="how">
            <div class="ac-wrap lp-cert">
                <div>
                    <h2>A certificate that means something</h2>
                    <p>Pass every lesson and project, get your capstone approved by your peers, and claim a certificate with your registered name and a unique ID. Anyone can check it on our verification page, so it holds up on a CV or LinkedIn.</p>
                    <a class="ac-btn ac-btn--secondary" href="/verify/">How verification works</a>
                </div>
                <div class="lp-cert__card" aria-hidden="true">
                    <small>Certificate of completion</small>
                    <b>Your name here</b>
                    <span>Data Science from Scratch</span>
                    <em>ID OFL-XXXX-XXXX · verify at openfraudlabs.com/verify</em>
                </div>
            </div>
        </section>

        <section class="ac-section--tight">
            <div class="ac-wrap">
                <div class="ac-social">
                    <div>
                        <h2>New lessons on TikTok</h2>
                        <p>Follow @_drhola for short lessons, then like, share and comment. Your questions shape what we teach next.</p>
                    </div>
                    <a class="ac-btn ac-btn--primary" href="{TT}" target="_blank" rel="noopener noreferrer">Follow @_drhola</a>
                </div>
            </div>
        </section>

        <section class="ac-section">
            <div class="ac-narrow ac-faq">
                <h2>Questions</h2>
                <details><summary>Do I need any experience?</summary><p>No. Data Science from Scratch starts from zero. You'll see real Python from Lesson 1, explained line by line, and practise it in your browser. There's nothing to install.</p></details>
                <details><summary>How long does a course take?</summary><p>Plan for about 30 minutes per lesson: a 10-minute video, the study notes, a few practice exercises and the quiz. You can stop and pick up where you left off at any time.</p></details>
                <details><summary>How much does it cost?</summary><p>Creating an account is free, and every released lesson is open during early access. If parts of a course become paid, the Plans page will show exactly what's included before you pay.</p></details>
                <details><summary>Is the certificate accredited?</summary><p>It's a certificate of course completion from Open Fraud Labs, not an accredited academic qualification. Each one has a unique ID that anyone can check on our <a href="/verify/">verification page</a>.</p></details>
                <details><summary>How is my data used?</summary><p>Only to run your account and track your learning. Read the <a href="/privacy/">Privacy Policy</a>.</p></details>
            </div>
        </section>"""

home_script = r"""        (function () {
            var cell = document.getElementById('lp-cell'); if (!cell) return;
            if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
            var code = document.getElementById('lp-code'), full = code.textContent, i = 0;
            cell.classList.add('is-typing'); code.textContent = '';
            setTimeout(function tick() {
                code.textContent = full.slice(0, ++i);
                if (i < full.length) setTimeout(tick, 28); else setTimeout(function () { cell.classList.remove('is-typing'); cell.classList.add('is-done'); }, 260);
            }, 700);
        })();
        (async function cohort() {
            var c = (await OFL.sb.rpc('cohort_public', { p_slug: null })).data;
            if (!c || c.status !== 'open') return;
            var b = document.getElementById('ap-banner'); b.href = '/academy/apply/?c=' + encodeURIComponent(c.slug);
            var hs = document.getElementById('home-ds-status'); if (hs && c.course === 'data-science') { hs.textContent = 'Pre-launch: applications open'; var hl = hs.parentNode.querySelector('a.ac-btn'); if (hl) { hl.textContent = 'View course and apply'; } }
            document.getElementById('ap-banner-text').textContent = 'Applications are open for the free ' + c.title + (c.places_left > 0 ? ': ' + c.places_left + ' places left' : ': waitlist open');
            b.hidden = false;
        })();
        (async function courses() {
            var r = await OFL.sb.from('courses').select('slug, title, description, level, status, access, total_lessons, sort').neq('status', 'hidden').order('sort');
            if (r.error || !r.data) return;
            var el = OFL.el, more = document.getElementById('more-courses'), ul = document.getElementById('coming-list');
            var live = r.data.filter(function (c) { return c.status === 'live' && c.slug !== 'data-science'; });
            more.textContent = '';
            live.forEach(function (c) {
                more.appendChild(el('article', { class: 'lp-more__card' }, el('span', { class: 'ac-status ac-status--live', text: 'Open for enrolment' }),
                    el('h3', { text: c.title }), c.description ? el('p', { text: c.description }) : null,
                    el('small', { class: 'ac-muted', text: [c.level, c.total_lessons ? c.total_lessons + ' lessons' : null, c.access === 'paid' ? 'Paid' : 'Free'].filter(Boolean).join(' · ') }),
                    el('a', { class: 'ac-btn ac-btn--secondary ac-btn--sm', href: '/academy/courses/?c=' + encodeURIComponent(c.slug), text: 'View course and enrol' })));
            });
            more.hidden = !live.length;
            var soon = r.data.filter(function (c) { return c.status === 'coming_soon'; });
            var keep = Array.prototype.filter.call(ul.children, function (li) { return /Live classes/.test(li.textContent); });
            ul.textContent = '';
            soon.forEach(function (c) { ul.appendChild(el('li', {}, el('strong', { text: c.title }), el('span', { text: c.description || '' }), el('em', { text: 'In preparation' }))); });
            keep.forEach(function (li) { ul.appendChild(li); });
        })();
        (async function () {
            var user = await OFL.getUser();
            if (!user) return;
            var st = await ACADEMY.courseState('data-science');
            var cta = document.getElementById('hero-cta');
            if (!st.enrolled) { cta.textContent = 'Choose a course'; cta.href = '#courses'; return; }
            if (st.next) { cta.textContent = 'Continue: Lesson ' + st.next.n; cta.href = '/academy/lesson/?course=data-science&n=' + st.next.n; }
            else if (st.done) { cta.textContent = 'Go to my learning'; cta.href = '/academy/dashboard/'; }
        })();"""

page("academy", "Open Fraud Labs Academy: free practical data courses",
     "Free, beginner-friendly data courses from Open Fraud Labs: video lessons with real Python, study notes, in-browser coding practice, quizzes and verifiable certificates.",
     home_main, home_script, active="courses")

# ============================================================== Course overview
course_main = f"""        <section class="cp-hero">
            <div class="ac-wrap cp-layout">
                <div class="cp-hero__copy">
                    <nav class="cp-crumbs" aria-label="Breadcrumb"><a href="/academy/">Academy</a><span aria-hidden="true">/</span><a href="/academy/#courses">Courses</a><span aria-hidden="true">/</span><span>Data Science from Scratch</span></nav>
                    <h1>Data Science from Scratch</h1>
                    <p class="cp-hero__lead">Learn how data becomes decisions: describing and cleaning data, the statistics behind it, and building and explaining machine learning models, with examples from retail, health, transport, media and finance.</p>
                    <ul class="cp-meta">
                        <li><b>Beginner</b>No experience needed</li>
                        <li><b class="num">6.6 hours</b>of video</li>
                        <li><b class="num">39</b>lessons and project parts</li>
                        <li><b>Certificate</b>with public verification</li>
                    </ul>
                    <p class="cp-by">Taught by <strong>Ayodele Odugbile</strong>, data and analytics professional and founder of Open Fraud Labs</p>
                </div>
            </div>
        </section>

        <div class="ac-wrap cp-layout cp-body">
            <aside class="cp-aside">
                <div class="cp-card">
                    <div class="cp-card__media"><img src="/assets/academy/lesson-frame.jpg" width="1280" height="720" alt="A frame from Lesson 25: Python code and the chart it produces."></div>
                    <div class="cp-card__body">
                        <span class="ac-status ac-status--live" id="cp-status">Open for enrolment</span>
                        <p class="cp-card__price">Free during early access</p>
                        <a class="ac-btn ac-btn--primary cp-card__cta" id="start-btn" href="/account/?next=/academy/courses/data-science/">Sign up free to enrol</a>
                        <p class="cp-card__note" id="start-note">Browse the outline freely. Enrol to open the lessons.</p>
                        <h3>This course includes</h3>
                        <ul class="cp-includes">
                            <li>30 video lessons, about 10 minutes each</li>
                            <li>3 portfolio projects in 9 guided parts</li>
                            <li class="num">117 coding exercises that run in your browser</li>
                            <li>A quiz for every lesson and project part</li>
                            <li>Downloadable notebooks for Colab or Jupyter</li>
                            <li>Peer-reviewed projects and capstone</li>
                            <li>Certificate with a public verification ID</li>
                        </ul>
                        <a class="cp-card__link" href="{TT}" target="_blank" rel="noopener noreferrer">Follow new lessons on TikTok</a>
                    </div>
                </div>
            </aside>

            <div class="cp-main">
                <section class="cp-sec cp-learn">
                    <h2>What you'll learn</h2>
                    <ul class="cp-checks">
                        <li>Explain what data science is and how a project runs from question to answer</li>
                        <li>Read a dataset's structure and identify data types correctly</li>
                        <li>Summarise data with averages, spread and distributions</li>
                        <li>Find outliers, handle missing data and clean messy datasets</li>
                        <li>Choose the right chart and avoid common statistical traps</li>
                        <li>Query data with SQL and work fluently with pandas</li>
                        <li>Train, test and fairly evaluate machine learning models</li>
                        <li>Explain model decisions and check them for bias</li>
                    </ul>
                </section>

                <section class="cp-sec">
                    <h2>Skills you'll practise</h2>
                    <ul class="cp-tags">
                        <li>Python</li><li>pandas</li><li>Statistics</li><li>Data cleaning</li><li>Data visualisation</li><li>SQL</li>
                        <li>scikit-learn</li><li>Model evaluation</li><li>Imbalanced data</li><li>Explainable AI</li><li>Data ethics</li>
                    </ul>
                </section>

                <section class="cp-sec">
                    <div class="cp-sec__head">
                        <h2>Course outline</h2>
                        <p>Six modules. Lessons unlock in order: watch the video, read the notes, solve the practice and pass the quiz to complete each one.</p>
                    </div>
                    <div class="ac-ledger" id="ledger">
{static_ledger(curriculum, "Data Science from Scratch")}
                    </div>
                </section>

                <section class="cp-sec">
                    <h2>Portfolio projects</h2>
                    <p class="cp-sec__intro">Three guided projects in different industries, each peer reviewed against a published rubric. You finish with work you can show employers.</p>
                    <div class="cp-projects">
                        <div><span>Finance</span><h3>Credit risk</h3><p>Predict loan default and set a costed approval cut-off.</p></div>
                        <div><span>Health</span><h3>Clinic no-shows</h3><p>Find who is likely to miss appointments and target reminders.</p></div>
                        <div><span>Real estate</span><h3>City rents</h3><p>Model rents across a city and price new listings.</p></div>
                    </div>
                </section>

                <section class="cp-sec">
                    <h2>How you earn the certificate</h2>
                    <ol class="cp-path">
                        <li><b>Complete every lesson</b><span>Watch, read, practise and pass the quiz for all 30 lessons.</span></li>
                        <li><b>Finish the three projects</b><span>Follow each one through its three parts and pass the quizzes.</span></li>
                        <li><b>Pass your capstone</b><span>Analyse a dataset of your choice; three learners review it with the rubric.</span></li>
                        <li><b>Claim your certificate</b><span>It shows your registered name and an ID anyone can verify.</span></li>
                    </ol>
                    <div class="cp-certrow">
                        <div class="ac-mini-cert"><small>Certificate of Completion</small><b>Your name here</b><small>Data Science from Scratch</small></div>
                        <p><a href="/academy/capstone/?course=data-science">Read the capstone brief</a><br><a href="/verify/">See how verification works</a></p>
                    </div>
                </section>

                <section class="cp-sec cp-instructor">
                    <h2>Your instructor</h2>
                    <div class="cp-instructor__row">
                        <img src="/assets/logo.png" alt="" width="64" height="64">
                        <div>
                            <h3>Ayodele Odugbile</h3>
                            <p>Data and analytics professional and founder of Open Fraud Labs. Every lesson is built on real code and checked numbers, so what you see on screen is exactly what you'll get when you run it.</p>
                        </div>
                    </div>
                </section>
            </div>
        </div>"""

course_script = r"""        (async function () {
            var st = await ACADEMY.courseState('data-science');
            if (!st.lessons.length) return;
            ACADEMY.renderLedger(document.getElementById('ledger'), st, { course: 'data-science' });
            var rel = st.lessons.filter(function (l) { return l.released; }).length;
            document.querySelectorAll('[data-released]').forEach(function (e) { e.textContent = rel; });
            var btn = document.getElementById('start-btn'), note = document.getElementById('start-note');
            if (!st.enrolled && st.course && st.course.enrol_mode === 'application') {
                btn.textContent = 'Apply for the Founding Cohort'; btn.href = '/academy/apply/';
                var cps = document.getElementById('cp-status'); if (cps) cps.textContent = 'Pre-launch: applications open';
                note.textContent = 'Pre-launch: places are free and limited. Browse the outline, then apply.';
                return;
            }
            if (!st.user) return;
            if (!st.enrolled) {
                var b2 = OFL.el('button', { class: 'ac-btn ac-btn--primary cp-card__cta', type: 'button', id: 'start-btn', text: 'Enrol for free' });
                btn.replaceWith(b2);
                note.textContent = 'Enrolling adds the course to My learning and opens Lesson 1.';
                b2.addEventListener('click', async function () {
                    b2.disabled = true;
                    var r = await OFL.sb.rpc('enroll', { p_course: 'data-science' });
                    if (r.error) { b2.disabled = false; note.textContent = OFL.friendlyError(r.error); if (/Terms of Service/.test(r.error.message)) location.href = '/account/?next=/academy/courses/data-science/'; return; }
                    location.href = '/academy/lesson/?course=data-science&n=1&enrolled=1';
                });
                return;
            }
            note.textContent = st.done + ' of ' + st.total + ' lessons complete';
            if (st.next) { btn.textContent = st.done ? 'Continue: Lesson ' + st.next.n : 'Start Lesson 1'; btn.href = '/academy/lesson/?course=data-science&n=' + st.next.n; }
            else { btn.textContent = 'Go to my learning'; btn.href = '/academy/dashboard/'; note.textContent = 'You’re up to date. The next lesson is released soon.'; }
        })();"""

COURSE_LD = '''    <script type="application/ld+json">
    {"@context": "https://schema.org", "@type": "Course", "name": "Data Science from Scratch",
     "description": "A beginner course: 30 video lessons, 3 portfolio projects in finance, health and real estate, in-browser coding practice, quizzes, a peer-reviewed capstone and a verifiable certificate.",
     "url": "https://openfraudlabs.com/academy/courses/data-science/", "inLanguage": "en",
     "provider": {"@type": "Organization", "name": "Open Fraud Labs", "sameAs": "https://openfraudlabs.com/"},
     "instructor": {"@type": "Person", "name": "Ayodele Odugbile"},
     "educationalLevel": "Beginner", "isAccessibleForFree": true,
     "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "online", "courseWorkload": "PT20H"}}
    </script>
'''
page("academy/courses/data-science", "Data Science from Scratch | Open Fraud Labs Academy",
     "A free beginner course: 30 video lessons, 3 portfolio projects in finance, health and real estate, in-browser coding practice, quizzes, a capstone project and a verifiable certificate.",
     course_main, course_script, active="courses", extra=COURSE_LD)

# ============================================================== Generic course page (courses added from the staff dashboard)
gc_main = """        <section class="cp-hero">
            <div class="ac-wrap cp-layout">
                <div class="cp-hero__copy">
                    <nav class="cp-crumbs" aria-label="Breadcrumb"><a href="/academy/">Academy</a><span aria-hidden="true">/</span><a href="/academy/courses/">Courses</a><span aria-hidden="true" id="gc-crumb-sep" hidden>/</span><span id="gc-crumb"></span></nav>
                    <p class="ac-eyebrow" id="gc-eyebrow">Courses</p>
                    <h1 id="gc-title">All courses</h1>
                    <p class="cp-hero__lead" id="gc-lead">Everything in Open Fraud Labs Academy, open now and in preparation.</p>
                    <div id="msg"></div>
                </div>
                <aside class="cp-card" id="gc-card" hidden>
                    <div class="cp-card__body">
                        <dl class="gc-facts" id="gc-facts"></dl>
                        <a class="ac-btn ac-btn--primary cp-card__cta" id="gc-cta" href="/account/">Create a free account</a>
                        <p class="cp-card__note" id="gc-note"></p>
                    </div>
                </aside>
            </div>
        </section>
        <section class="ac-section">
            <div class="ac-wrap">
                <div class="lp-more" id="gc-catalog"></div>
                <div id="gc-outline" hidden><h2>Lessons</h2><ol class="gc-lessons" id="gc-lessons"></ol></div>
            </div>
        </section>"""

gc_script = r"""        (async function () {
            var sb = OFL.sb, el = OFL.el, slug = OFL.qs('c');
            if (slug === 'data-science') { location.replace('/academy/courses/data-science/'); return; }
            function link(c) { return c.slug === 'data-science' ? '/academy/courses/data-science/' : '/academy/courses/?c=' + encodeURIComponent(c.slug); }
            if (!slug) {
                var r = await sb.from('courses').select('slug, title, description, level, status, access, total_lessons, sort').neq('status', 'hidden').order('sort');
                var box = document.getElementById('gc-catalog');
                (r.data || []).forEach(function (c) {
                    box.appendChild(el('article', { class: 'lp-more__card' },
                        el('span', { class: 'ac-status ac-status--' + (c.status === 'live' ? 'live' : 'soon'), text: c.status === 'live' ? 'Open for enrolment' : 'In preparation' }),
                        el('h3', { text: c.title }), c.description ? el('p', { text: c.description }) : null,
                        el('small', { class: 'ac-muted', text: [c.level, c.total_lessons ? c.total_lessons + ' lessons' : null, c.access === 'paid' ? 'Paid' : 'Free'].filter(Boolean).join(' · ') }),
                        c.status === 'live' ? el('a', { class: 'ac-btn ac-btn--secondary ac-btn--sm', href: link(c), text: 'View course' }) : null));
                });
                return;
            }
            var st = await ACADEMY.courseState(slug), c = st.course;
            if (!c) {
                document.getElementById('gc-title').textContent = 'Course not found';
                document.getElementById('gc-lead').textContent = 'This course doesn’t exist or isn’t available yet.';
                document.getElementById('gc-catalog').appendChild(el('a', { class: 'ac-btn ac-btn--secondary', href: '/academy/courses/', text: 'See all courses' }));
                return;
            }
            document.title = c.title + ' | Open Fraud Labs Academy';
            document.getElementById('gc-crumb').textContent = c.title; document.getElementById('gc-crumb-sep').hidden = false;
            document.getElementById('gc-eyebrow').textContent = c.status === 'live' ? 'Open for enrolment' : c.status === 'coming_soon' ? 'In preparation' : 'Hidden: staff preview';
            document.getElementById('gc-title').textContent = c.title;
            document.getElementById('gc-lead').textContent = c.description || '';
            var released = st.lessons.filter(function (l) { return l.released; }).length;
            var facts = document.getElementById('gc-facts');
            [['Level', c.level || '—'], ['Lessons', released + ' released' + (st.lessons.length > released ? ' of ' + st.lessons.length : '')], ['Access', c.access === 'paid' ? 'Paid pass' : 'Free']]
                .forEach(function (f) { facts.appendChild(el('div', {}, el('dt', { text: f[0] }), el('dd', { text: f[1] }))); });
            document.getElementById('gc-card').hidden = false;
            var ol = document.getElementById('gc-lessons');
            st.lessons.forEach(function (l) {
                var s = ACADEMY.rowState(l, st), done = s === 'done';
                var t = (s === 'open' || s === 'current' || done) ? el('a', { href: '/academy/lesson/?course=' + encodeURIComponent(slug) + '&n=' + l.n, text: l.title }) : el('span', { text: l.title });
                ol.appendChild(el('li', {}, el('span', { text: String(l.n).padStart(2, '0') }), t, el('em', { text: !l.released ? 'Coming soon' : done ? 'Done' : '' })));
            });
            document.getElementById('gc-outline').hidden = !st.lessons.length;
            var cta = document.getElementById('gc-cta'), note = document.getElementById('gc-note');
            if (c.status !== 'live') { cta.replaceWith(el('span', { class: 'ac-btn ac-btn--secondary cp-card__cta', 'aria-disabled': 'true', text: c.status === 'coming_soon' ? 'In preparation' : 'Not published' })); note.textContent = c.status === 'coming_soon' ? 'Enrolment opens when the first lessons are ready.' : 'Only staff who manage content can see this page.'; return; }
            if (!st.enrolled && c.enrol_mode === 'application') { cta.href = '/academy/apply/'; cta.textContent = 'Apply for a place'; note.textContent = 'Pre-launch: places are limited and shortlisted from applications.'; return; }
            if (!st.user) { cta.href = '/account/?next=' + encodeURIComponent(location.pathname + location.search); cta.textContent = 'Create a free account to enrol'; return; }
            if (!st.enrolled) {
                var b = el('button', { class: 'ac-btn ac-btn--primary cp-card__cta', type: 'button', text: c.access === 'paid' ? 'Enrol' : 'Enrol for free' });
                cta.replaceWith(b); note.textContent = 'Enrolling adds the course to My learning and opens Lesson 1.';
                b.addEventListener('click', async function () {
                    b.disabled = true;
                    var r = await sb.rpc('enroll', { p_course: slug });
                    if (r.error) { b.disabled = false; note.textContent = OFL.friendlyError(r.error); if (/Terms of Service/.test(r.error.message)) location.href = '/account/?next=' + encodeURIComponent(location.pathname + location.search); return; }
                    location.href = '/academy/lesson/?course=' + encodeURIComponent(slug) + '&n=1&enrolled=1';
                });
                return;
            }
            note.textContent = st.done + ' of ' + st.total + ' lessons complete';
            if (st.next) { cta.textContent = st.done ? 'Continue: Lesson ' + st.next.n : 'Start Lesson 1'; cta.href = '/academy/lesson/?course=' + encodeURIComponent(slug) + '&n=' + st.next.n; }
            else { cta.textContent = 'Go to my learning'; cta.href = '/academy/dashboard/'; }
        })();"""

page("academy/courses", "Courses | Open Fraud Labs Academy", "All Open Fraud Labs Academy courses: open for enrolment and in preparation.",
     gc_main, gc_script, active="courses")

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
                    <button class="ac-tab ac-tab--lab" role="tab" data-step="lab" aria-selected="false" hidden><i>3</i><span>Practice<small id="tab-lab-sub">Code lab</small></span></button>
                    <button class="ac-tab" role="tab" data-step="quiz" aria-selected="false"><i id="tab-quiz-num">3</i><span>Quiz<small id="tab-quiz-sub">Pass mark 70%</small></span></button>
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
                <div class="ac-panel" data-panel="lab" hidden><div id="colab"></div><div id="lab"></div></div>
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
            var fullTitle = /^Project \d/.test(lesson.title) ? lesson.title : 'Lesson ' + n + ': ' + lesson.title;
            titleEl.textContent = fullTitle;
            document.title = fullTitle + ' | Open Fraud Labs Academy';
            if (!st.enrolled) {
                return lockedPanel('Enrol to start this course', 'You can browse the course outline, but lessons open once you enrol. It\u2019s free.',
                    '/academy/courses/' + course + '/', 'Go to the course and enrol');
            }
            if (n > 1 && !st.unlockAll && !((n - 1) in st.passed)) {
                return lockedPanel('Lesson ' + n + ' is locked', 'Lessons unlock in order. Complete Lesson ' + (st.next ? st.next.n : n - 1) + ' first.',
                    '/academy/lesson/?course=' + course + '&n=' + (st.next ? st.next.n : n - 1), 'Go to Lesson ' + (st.next ? st.next.n : n - 1));
            }

            if (OFL.qs('enrolled')) {
                msg.appendChild(el('div', { class: 'ofl-notice ofl-notice--success', text: 'You\u2019re enrolled in ' + (st.course ? st.course.title : 'the course') + '. Welcome! You\u2019ll find a confirmation under the bell at the top. Start here with Lesson 1.' }));
                history.replaceState(null, '', location.pathname + '?course=' + course + '&n=' + n);
            }
            OFL.track('lesson_open', course, n);
            var act = (await sb.from('lesson_activity').select('*').eq('course_slug', course).eq('lesson_n', n).maybeSingle()).data || {};
            var passed = n in st.passed;
            var tabs = document.getElementById('tabs'); tabs.hidden = false;
            // Long-form lessons (spec in longform/) add rich reading and a code lab.
            var nn = (n < 10 ? '0' : '') + n, labDone = false;
            var long = null;
            // Notes and exercises come from the server, only for learners allowed to open this lesson.
            var lc = await sb.rpc('get_lesson_content', { p_course: course, p_lesson: n });
            if (lc.error) {
                tabs.hidden = true;
                if (/PAID:/.test(lc.error.message || '')) return lockedPanel(fullTitle, 'This lesson is part of the full course. A pass unlocks every lesson, practice exercise, project and certificate.', '/academy/pricing/', 'See plans');
                return OFL.notice(msg, OFL.friendlyError(lc.error), 'error');
            }
            long = lc.data;
            var tabEls = {}; tabs.querySelectorAll('.ac-tab').forEach(function (t) { tabEls[t.getAttribute('data-step')] = t; });
            var panels = {}; document.querySelectorAll('[data-panel]').forEach(function (p) { panels[p.getAttribute('data-panel')] = p; });

            var hasLab = !!(long && (long.exercises || long.practice));
            function unlocked(step) {
                if (step === 'watch' || st.isAdmin) return true;   // admins can preview every step
                if (step === 'read') return !!act.video_completed_at || passed;
                if (step === 'lab') return !!act.notes_completed_at || passed;
                return passed || (!!act.notes_completed_at && (!hasLab || labDone));   // quiz: practice first
            }
            function refreshTabs() {
                tabEls.watch.classList.toggle('is-done', !!act.video_completed_at || passed);
                tabEls.read.classList.toggle('is-done', !!act.notes_completed_at || passed);
                tabEls.quiz.classList.toggle('is-done', passed);
                tabEls.lab.classList.toggle('is-done', !!labDone);
                ['read', 'lab', 'quiz'].forEach(function (s) { tabEls[s].disabled = !unlocked(s); });
                document.getElementById('tab-quiz-sub').textContent = passed ? 'Passed' : (hasLab && !labDone ? 'After practice' : 'Pass mark 70%');
            }
            function show(step) {
                if (!unlocked(step)) return;
                Object.keys(panels).forEach(function (k) { panels[k].hidden = k !== step; tabEls[k].setAttribute('aria-selected', String(k === step)); });
                if (step === 'read') openNotes();
                if (step === 'quiz') loadQuiz();
                if (step === 'lab') openLab();
            }
            if (hasLab) { tabEls.lab.hidden = false; tabs.classList.add('ac-tabs--4'); document.getElementById('tab-quiz-num').textContent = '4'; }
            Object.keys(tabEls).forEach(function (k) { tabEls[k].addEventListener('click', function () { show(k); }); });
            if (st.isAdmin) msg.appendChild(el('div', { class: 'ofl-notice', text: 'Admin preview: every lesson and step is open to you, and you can take any quiz without the practice or cooldown rules. Learners still follow the normal order.' }));
            refreshTabs();

            // ---------------- Watch ----------------
            var video = document.getElementById('video'), meter = document.getElementById('meter'), meterText = document.getElementById('meter-text');
            // Videos are private: each learner gets a short-lived signed link, renewed if it expires.
            async function signVideo() {
                if (!lesson.video_path) { video.src = lesson.video_url || ''; return; }
                var sv = await sb.storage.from('lesson-videos').createSignedUrl(lesson.video_path, 4 * 3600);
                if (sv.error || !sv.data) return OFL.notice(msg, 'The video could not be loaded. Please refresh the page.', 'error');
                var at = video.currentTime || 0, wasPlaying = !video.paused;
                video.src = sv.data.signedUrl;
                if (at) video.addEventListener('loadedmetadata', function once() { video.removeEventListener('loadedmetadata', once); video.currentTime = at; if (wasPlaying) video.play(); });
            }
            var resigned = 0;
            video.addEventListener('error', function () { if (lesson.video_path && resigned++ < 3) signVideo(); });
            await signVideo();
            if (long && long.captions) {
                // Captions travel with the protected lesson content; the CC button in the player turns them on.
                var trk = document.createElement('track');
                trk.kind = 'captions'; trk.srclang = 'en'; trk.label = 'English';
                trk.src = URL.createObjectURL(new Blob([long.captions], { type: 'text/vtt' }));
                video.appendChild(trk);
            }
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
                if (hasLab && window.CODELAB) CODELAB.preload(exercisesOf(long));
                if (!notesLoaded) {
                    notesLoaded = true;
                    try {
                        if (long && long.reading) renderReading(long);
                        else document.getElementById('notes').textContent = 'The notes for this lesson are not available yet.';
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
                else hint.textContent = 'Done reading? Continue to the practice.';
                readBtn.disabled = !(sawEnd && left <= 0);
                if (left > 0 || !sawEnd) timer = setTimeout(tick, 1000);
            }
            new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting && notesLoaded) { sawEnd = true; if (openedAt) tick(); } }); })
                .observe(document.getElementById('notes-end'));
            readBtn.addEventListener('click', async function () {
                readBtn.disabled = true;
                var r = await sb.rpc('complete_notes', { p_course: course, p_lesson: n });
                if (r.error) { readBtn.disabled = false; return OFL.notice(msg, OFL.friendlyError(r.error), 'error'); }
                act.notes_completed_at = new Date().toISOString(); refreshTabs(); show(hasLab && !labDone ? 'lab' : 'quiz');
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
                var peerKey = { 33: 'project-credit', 36: 'project-clinic', 39: 'project-rent' }[n];
                if (peerKey && course === 'data-science') box.appendChild(el('p', { class: 'ac-callout' }, 'Finished the project? ',
                    el('a', { href: '/academy/review/?course=' + course + '&a=' + peerKey, text: 'Share it for peer review' }),
                    ': three learners score it with a rubric, you review three in return, and you get a reviewed portfolio piece.'));
                if (exercisesOf(spec).length) box.appendChild(el('p', { class: 'ac-callout' }, 'Practise in your browser: the ', el('strong', { text: 'Practice' }), ' tab has ' + exercisesOf(spec).length + ' short coding exercises on this lesson. Python runs right in the page, nothing to install.'));
                var d = el('details', {}, el('summary', { text: 'Full transcript' }));
                (spec.transcript || []).forEach(function (c) {
                    d.appendChild(el('h3', { text: c.title }));
                    (c.paragraphs || []).forEach(function (t) { if (t) d.appendChild(el('p', { text: t })); });
                });
                box.appendChild(d);
            }
            var labMounted = false;
            function exercisesOf(spec) { return spec.exercises || (spec.practice ? [spec.practice] : []); }
            function labSub(done, total) {
                document.getElementById('tab-lab-sub').textContent = done ? done + ' of ' + total + ' solved' : total + (total === 1 ? ' exercise' : ' exercises');
                var was = labDone; labDone = done === total; refreshTabs();
                if (labDone && !was && !passed && document.getElementById('lab-next') === null && labMounted) {
                    var box = document.getElementById('lab');
                    box.insertBefore(el('div', { class: 'ofl-notice ofl-notice--success', id: 'lab-next' }, 'All practice exercises solved. The quiz is unlocked. ',
                        el('button', { class: 'ac-btn ac-btn--primary ac-btn--sm', type: 'button', text: 'Go to the quiz', onclick: function () { show('quiz'); } })), box.firstChild);
                }
            }
            // Practise in Google Colab: a public, practice-only notebook that reports passing checks with the learner's key.
            var labCtl = null, pollTimer = null;
            async function syncSolved() {
                var ev2 = (await sb.from('learner_events').select('detail').eq('event', 'practice_solved').eq('course_slug', course).eq('lesson_n', n)).data || [];
                var got = {}; ev2.forEach(function (e) { if (e.detail && e.detail.exercise) got[e.detail.exercise] = true; });
                Object.keys(got).forEach(function (k) { try { localStorage.setItem('ofl-lab-done:' + course + ':' + n + ':' + (k - 1), '1'); } catch (e) {} });
                if (labCtl && labCtl.refresh) labCtl.refresh();
                labSub(Object.keys(got).length, exercisesOf(long).length);
                return Object.keys(got).length;
            }
            function startPolling() {
                if (pollTimer) return;
                var until = Date.now() + 45 * 60 * 1000;
                pollTimer = setInterval(async function () {
                    if (document.hidden) return;
                    var c = await syncSolved();
                    if (c >= exercisesOf(long).length || Date.now() > until) { clearInterval(pollTimer); pollTimer = null; }
                }, 8000);
            }
            async function renderColab() {
                var box = document.getElementById('colab'); if (box.dataset.done) return; box.dataset.done = '1';
                var url = 'https://colab.research.google.com/github/OpenFraudLabs/lab-docs/blob/main/practice/ds' + nn + '.ipynb';
                var open = el('a', { class: 'ac-btn ac-btn--primary', href: url, target: '_blank', rel: 'noopener noreferrer', text: 'Open in Google Colab' });
                var status = el('p', { class: 'cl-status', role: 'status' });
                box.appendChild(el('div', { class: 'cl' },
                    el('div', { class: 'cl-head' }, el('h2', { text: 'Practise in Google Colab' }),
                        el('p', { text: 'Run the exercises in a real notebook. Every check that passes in Colab is saved here automatically, and the quiz unlocks when all three are solved.' })),
                    el('ol', { class: 'cl-steps' },
                        el('li', {}, el('span', { text: 'Copy your practice key' }), await keyBlock()),
                        el('li', {}, el('span', { text: 'Open the notebook, paste the key into the first cell and run it' }), open),
                        el('li', {}, el('span', { text: 'Solve each exercise and run its check. Progress appears here within a few seconds.' }), status)),
                    el('p', { class: 'cl-alt', text: 'Or practise right here on the page below: both count the same.' })));
                open.addEventListener('click', function () { OFL.track('practice_run', course, n, { via: 'colab' }); status.textContent = 'Watching for your progress from Colab\u2026'; startPolling(); });
                document.addEventListener('visibilitychange', function () { if (!document.hidden && pollTimer) syncSolved(); });
            }
            function openLab() {
                renderColab();
                if (labMounted || !long) return; labMounted = true;
                labCtl = CODELAB.mountSet(document.getElementById('lab'), exercisesOf(long), { course: course, lesson: n, onProgress: labSub,
                    onEvent: function (ev, ex) { return OFL.track(ev, course, n, { exercise: ex }); },
                    getSolution: async function (ex) {
                        var r = await sb.rpc('get_exercise_solution', { p_course: course, p_lesson: n, p_exercise: ex });
                        if (r.error) throw new Error(OFL.friendlyError(r.error));
                        return r.data || '';
                    },
                    getNotebook: null });
            }
            if (hasLab) {
                // Practice progress is saved on the server (so it counts on any device); this device's record fills any gaps.
                var exs = exercisesOf(long), solved = {};
                var ev = (await sb.from('learner_events').select('detail').eq('event', 'practice_solved').eq('course_slug', course).eq('lesson_n', n)).data || [];
                ev.forEach(function (e) { if (e.detail && e.detail.exercise) solved[e.detail.exercise] = true; });
                for (var xi = 0; xi < exs.length; xi++) {
                    var key = 'ofl-lab-done:' + course + ':' + n + ':' + xi, local = false;
                    try { local = localStorage.getItem(key) === '1'; } catch (e) {}
                    if (solved[xi + 1]) { try { localStorage.setItem(key, '1'); } catch (e) {} }
                    else if (local) { await OFL.track('practice_solved', course, n, { exercise: xi + 1 }); solved[xi + 1] = true; }
                }
                labSub(Object.keys(solved).length, exs.length);
            }
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
                if (passed) {
                    var best = (await sb.from('quiz_attempts').select('score, answers, results, created_at').eq('course_slug', course).eq('lesson_n', n)
                        .eq('passed', true).order('score', { ascending: false }).order('created_at', { ascending: false }).limit(1)).data;
                    return showPassed(best && best[0]);
                }
                var last = (await sb.from('quiz_attempts').select('passed, created_at').eq('course_slug', course).eq('lesson_n', n).order('created_at', { ascending: false }).limit(1)).data;
                if (last && last[0] && !last[0].passed) {
                    var left = 600 - (Date.now() - new Date(last[0].created_at).getTime()) / 1000;
                    if (left > 0 && !st.isAdmin) return cooldown(left);
                }
                buildQuiz();
            }
            // A passed quiz stays on record: show the learner's best passing attempt, answer by answer.
            // Worked solutions in Colab: unlocked after the quiz is passed. The public notebook holds no answers;
            // it fetches the full lesson code and exercise solutions with the learner's practice key.
            var practiceKey = null;
            async function keyBlock() {
                var keyEl = el('code', { class: 'cl-key__val', text: practiceKey || 'Loading\u2026' });
                var copy = el('button', { class: 'ac-btn ac-btn--secondary ac-btn--sm', type: 'button', text: 'Copy key' });
                copy.addEventListener('click', async function () {
                    try { await navigator.clipboard.writeText(keyEl.textContent); copy.textContent = 'Copied'; setTimeout(function () { copy.textContent = 'Copy key'; }, 2000); }
                    catch (e) { var r = document.createRange(); r.selectNodeContents(keyEl); var sel = getSelection(); sel.removeAllRanges(); sel.addRange(r); }
                });
                if (!practiceKey) { var k = await sb.rpc('my_practice_key'); practiceKey = k.error ? null : k.data; keyEl.textContent = practiceKey || 'Could not load your key. Refresh the page.'; }
                return el('div', { class: 'cl-key' }, keyEl, copy);
            }
            async function solutionsCard() {
                var url = 'https://colab.research.google.com/github/OpenFraudLabs/lab-docs/blob/main/practice/ds' + nn + '-solutions.ipynb';
                return el('div', { class: 'cl cl--solutions' },
                    el('div', { class: 'cl-head' }, el('h2', { text: 'Worked solutions in Google Colab' }),
                        el('p', { text: 'See the full solution for this lesson: every code example from the video and the answers to all three practice exercises, running live with their outputs and charts.' })),
                    el('ol', { class: 'cl-steps' },
                        el('li', {}, el('span', { text: 'Copy your practice key' }), await keyBlock()),
                        el('li', {}, el('span', { text: 'Open the worked solutions, paste the key into the cell and run it' }),
                            el('a', { class: 'ac-btn ac-btn--primary', href: url, target: '_blank', rel: 'noopener noreferrer', text: 'Open worked solutions in Colab' }))));
            }
            function showPassed(att) {
                form.hidden = true; form.textContent = ''; result.textContent = ''; waitBox.textContent = '';
                var box = el('div', { class: 'ac-review' });
                var pct = att ? Math.round(att.score * 100) : Math.round((st.passed[n] || 0) * 100);
                var res = att && att.results ? att.results : null;
                var right = res ? res.filter(function (x) { return x.correct; }).length : null;
                box.appendChild(el('div', { class: 'ac-result is-pass' },
                    el('h3', { text: 'Passed: ' + pct + '%' + (res ? ' (' + right + ' of ' + res.length + ')' : '') }),
                    el('p', { text: (att ? 'Your best result, saved on ' + OFL.formatDate(att.created_at) + '. ' : '') + 'This lesson is complete and stays complete.' })));
                if (res) {
                    var byPos = {}; qs.forEach(function (q) { byPos[q.position] = q; });
                    res.forEach(function (x, k) {
                        var q = byPos[x.position]; if (!q) return;
                        var fs = el('div', { class: 'ac-q is-locked ' + (x.correct ? 'is-right' : 'is-wrong') }, el('p', { class: 'ac-q__title', text: (k + 1) + '. ' + q.question }));
                        q.options.forEach(function (opt, j) {
                            var cls = 'ac-opt is-static' + (j === x.answer ? ' is-chosen' : '') + (j === x.correct_index ? ' is-answer' : '');
                            fs.appendChild(el('div', { class: cls }, el('span', { class: 'ac-opt__mark', 'aria-hidden': 'true', text: j === x.correct_index ? '✓' : (j === x.answer ? '✕' : '') }),
                                el('span', { text: opt + (j === x.answer ? '  (your answer)' : '') })));
                        });
                        if (x.explanation) fs.appendChild(el('p', { class: 'ac-q__fb', text: (x.correct ? 'Correct. ' : 'The answer is “' + q.options[x.correct_index] + '”. ') + x.explanation }));
                        box.appendChild(fs);
                    });
                }
                var actions = el('div', { class: 'ofl-actions' });
                actions.appendChild(el('button', { class: 'ac-btn ac-btn--secondary', type: 'button', text: 'Practise the quiz again', onclick: function () { result.textContent = ''; buildQuiz(); } }));
                var nl = st.lessons.find(function (l) { return l.n === n + 1; });
                if (nl && nl.released) actions.appendChild(el('a', { class: 'ac-btn ac-btn--primary', href: '/academy/lesson/?course=' + course + '&n=' + (n + 1), text: 'Go to Lesson ' + (n + 1) }));
                box.appendChild(actions);
                result.appendChild(box);
                if (long) solutionsCard().then(function (c) { box.insertBefore(c, box.children[1] || null); });
            }
            function buildQuiz() {
                form.textContent = ''; result.textContent = '';
                if (passed) form.appendChild(el('p', { class: 'ofl-notice ofl-notice--info', text: 'Practice attempt: your lesson is already passed, and this attempt can’t undo that. Your best result stays saved.' }));
                order = shuffle(qs.map(function (_, i) { return i; }));
                order.forEach(function (qi, k) {
                    var item = qs[qi], fs = el('fieldset', { class: 'ac-q', 'data-q': qi }, el('legend', { text: (k + 1) + '. ' + item.question }));
                    shuffle(item.options.map(function (_, j) { return j; })).forEach(function (j) {
                        fs.appendChild(el('label', { class: 'ac-opt' }, el('input', { type: 'radio', name: 'q' + qi, value: j, required: true }), el('span', { text: item.options[j] })));
                    });
                    fs.setAttribute('data-pos', item.position);
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
                    var fs = form.querySelector('[data-pos="' + (x.position != null ? x.position : qs[i].position) + '"]') || form.querySelector('[data-q="' + i + '"]'), fb = fs.querySelector('.ac-q__fb');
                    fs.classList.add(x.correct ? 'is-right' : 'is-wrong'); fb.hidden = false;
                    fb.textContent = x.correct ? 'Correct. ' + (x.explanation || '') :
                        (res.passed ? 'The answer is “' + qs[i].options[x.correct_index] + '”. ' + (x.explanation || '') : 'Not quite.');
                });
                var actions = el('div', { class: 'ofl-actions' });
                var wasPassed = passed;
                if (res.passed) {
                    passed = true; st.passed[n] = Math.max(st.passed[n] || 0, res.score); st.done = Object.keys(st.passed).length; refreshTabs();
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
                    el('h3', { text: (res.passed ? (wasPassed ? 'Practice result: ' : 'Lesson complete: ') : (wasPassed ? 'Practice result: ' : 'Not passed yet: ')) + pct + '% (' + res.correct + ' of ' + res.total + ')' }),
                    el('p', { text: wasPassed ? 'Your lesson stays passed, and your best result is saved.'
                        : res.passed ? (next ? 'Your result is saved. Lesson ' + (n + 1) + ' is released soon. Follow @_drhola on TikTok to catch it.' : 'Your result and answers are saved. Nice work.')
                        : 'You need 70% to pass. Answers are shown once you pass. You can try again in 10 minutes.' }), actions));
                if (res.passed && long) solutionsCard().then(function (c) { result.appendChild(c); });
                if (!res.passed && !wasPassed && !st.isAdmin) cooldown(600, true);
                result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            });

            // Start on the first unfinished step.
            // Passed lessons open on the saved quiz result; otherwise on the first unfinished step.
            show(passed ? 'quiz' : (!act.video_completed_at ? 'watch' : (!act.notes_completed_at ? 'read' : (hasLab && !labDone ? 'lab' : 'quiz'))));
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
            var bg = (await sb.from('learner_background').select('completed_at, skipped_at').eq('user_id', user.id).maybeSingle()).data;
            if (!bg) { location.replace('/academy/welcome/?next=/academy/dashboard/'); return; }
            if (OFL.qs('welcome')) OFL.notice(msg, 'Thank you! Your answers are saved. You can change them any time from your account page.', 'success');
            else if (!bg.completed_at) msg.appendChild(el('div', { class: 'ofl-notice ac-nudge' }, 'Help us build better lessons: ', el('a', { href: '/academy/welcome/?next=/academy/dashboard/', text: 'tell us a little about you' }), ' (about a minute).'));
            var course = 'data-science';
            var acc = (await sb.rpc('my_access')).data || {}, live = ((await sb.from('courses').select('slug, title, description, status').eq('status', 'live').order('sort')).data || []);
            var titles = {}; live.forEach(function (c) { titles[c.slug] = c.title; });
            (acc.scholarships || []).forEach(function (x) {
                msg.appendChild(el('div', { class: 'ac-sch-banner' }, '\uD83C\uDF93 Scholarship: full access to ' + (x.course ? (titles[x.course] || x.course) : 'every Academy course') +
                    (x.until ? ' until ' + new Date(new Date(x.until).getTime() - 1000).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' }) : '') + '.'));
            });
            var mine = ((await sb.from('enrollments').select('course_slug').eq('user_id', user.id)).data || []).map(function (e) { return e.course_slug; });
            var others = live.filter(function (c) { return c.slug !== course; });
            function otherCourses(box, heading) {
                if (!others.length) return;
                var wrap = el('div', { class: 'lp-more' });
                others.forEach(function (c) { var on = mine.indexOf(c.slug) >= 0;
                    wrap.appendChild(el('article', { class: 'lp-more__card' }, el('h3', { text: c.title }), c.description ? el('p', { text: c.description }) : null,
                        el('a', { class: 'ac-btn ac-btn--' + (on ? 'primary' : 'secondary') + ' ac-btn--sm', href: '/academy/courses/?c=' + encodeURIComponent(c.slug), text: on ? 'Continue' : 'View course and enrol' }))); });
                box.appendChild(el('div', { class: 'ac-panel' }, el('h2', { text: heading }), wrap));
            }
            var st = await A.courseState(course);
            if (!st.enrolled) {
                document.getElementById('hello').textContent = prof.full_name ? 'Welcome, ' + prof.full_name.split(' ')[0] : 'Welcome';
                document.querySelector('.ac-two').hidden = true;
                document.getElementById('next').appendChild(el('div', { class: 'ac-panel' },
                    el('h2', { text: 'Choose your first course' }),
                    el('p', { class: 'ac-muted', text: 'Look through what each course covers, then enrol in the one you want. Your progress, projects and certificates will appear here.' }),
                    el('div', { class: 'ac-choose' },
                        el('img', { src: '/assets/academy/lesson-frame.jpg', alt: '', width: '320', height: '180', loading: 'lazy' }),
                        el('div', {}, el('h3', { text: 'Data Science from Scratch' }),
                            el('p', { class: 'ac-muted', text: 'From your first dataset to machine learning models you can explain. ' + st.total + ' lessons and projects for beginners, with a certificate.' }),
                            el('a', { class: 'ac-btn ac-btn--primary', href: st.course && st.course.enrol_mode === 'application' ? '/academy/apply/' : '/academy/courses/data-science/', text: st.course && st.course.enrol_mode === 'application' ? 'Apply for the Founding Cohort' : 'View course and enrol' }))),
                    el('p', { class: 'ac-muted ac-small' }, others.length ? '' : 'More courses are on the way, starting with Data Analysis. ', el('a', { href: '/academy/courses/', text: 'See all courses' }))));
                otherCourses(document.getElementById('next'), mine.length ? 'Your other courses' : 'Also open for enrolment');
                return;
            }
            A.renderLedger(document.getElementById('ledger'), st, { course: course, title: false });
            var cap = ((await sb.from('capstone_submissions').select('status, feedback, submitted_at').eq('course_slug', course).eq('assignment', 'capstone').order('submitted_at', { ascending: false }).limit(1)).data || [])[0];
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

            otherCourses(next, 'More courses');
            var list = document.getElementById('checklist');
            function item(isDone, text, link) {
                list.appendChild(el('li', { class: isDone ? 'is-done' : '' }, el('span', { class: 'ac-dot' }), el('span', { text: text }), link || el('span')));
            }
            item(st.done >= st.total, 'Complete all ' + st.total + ' lessons and projects (' + st.done + ' done, ' + released + ' released)');
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

PORT_FIX = [("select('repo_url, status, feedback, submitted_at, reviewed_at').eq('course_slug', course)",
             "select('repo_url, status, feedback, submitted_at, reviewed_at').eq('course_slug', course).eq('assignment', 'capstone')"),
("<p>Each submission is reviewed by Open Fraud Labs. You’ll see the result here and in My Learning: <em>Approved</em>, or <em>Changes requested</em> with feedback. You can resubmit as many times as you need.</p>",
             "<p>Your capstone is <strong>peer reviewed</strong>: three other learners score it with a published rubric, and you review three capstones in return on the <a href=\"/academy/review/?course=data-science&amp;a=capstone\">peer review page</a>. The middle score counts and the pass mark is 70%. Open Fraud Labs can review any project. If changes are requested, improve it and resubmit as many times as you need.</p>"),
            ("OFL.notice(msg, 'Submitted! You’ll see the review result here and in My Learning.', 'success');",
             "OFL.notice(msg, 'Submitted! Now review three other capstones on the peer review page to receive your grade.', 'success');"),
("'/my-learning/'", "'/academy/dashboard/'"), ('"/my-learning/"', '"/academy/dashboard/"'), ("/my-learning/", "/academy/dashboard/"),
            ("/learn/capstone/", "/academy/capstone/"), ("OFL.requireUser('/admin/')", "OFL.requireUser('/academy/admin/')"),
            ("'/learn/' + c.slug + '/'", "'/academy/courses/' + c.slug + '/'"),
            # Verify page: sample preview, awarded certificates and revocation
            ('<div class="ofl-cert" id="cert">', '<div class="ofl-cert" id="cert"><div class="ofl-cert__sample" id="c-sample" hidden aria-hidden="true">SAMPLE</div>'),
            ('<p class="ofl-cert__desc">including all lesson quizzes and an approved capstone project.</p>', '<p class="ofl-cert__desc" id="c-desc">including all lesson quizzes and an approved capstone project.</p>'),
            ("""                if (!r.data) return OFL.notice(msg, 'No certificate found with ID “' + id + '”. Check the ID and try again.', 'error');""",
             """                if (!r.data) return OFL.notice(msg, 'No certificate found with ID “' + id + '”. Check the ID and try again.', 'error');
                if (r.data.revoked_at) return OFL.notice(msg, 'Certificate ' + r.data.id + ' was issued to ' + r.data.full_name + ' but was revoked on ' + OFL.formatDate(r.data.revoked_at) + '. It is no longer valid.', 'error');
                document.getElementById('c-sample').hidden = true;
                document.getElementById('c-desc').textContent = r.data.award_type === 'awarded' ? 'awarded by Open Fraud Labs in recognition of completing this programme.' : 'including all lesson quizzes and an approved capstone project.';"""),
            ("""            var id = OFL.qs('id');
            if (id) { form.id.value = id; check(id); }""",
             """            var id = OFL.qs('id');
            if (OFL.qs('sample')) {
                // Design preview only: clearly marked, never verifiable.
                var who = 'Your Name Here', u = await OFL.getUser();
                if (u) { var pr = (await sb.from('profiles').select('full_name').eq('id', u.id).maybeSingle()).data; if (pr && pr.full_name) who = pr.full_name; }
                document.getElementById('c-name').textContent = who;
                document.getElementById('c-course').textContent = 'Data Science from Scratch';
                document.getElementById('c-date').textContent = OFL.formatDate(new Date().toISOString());
                document.getElementById('c-id').textContent = 'OFL-SAMPLE';
                document.getElementById('c-sample').hidden = false;
                document.getElementById('copy-link').hidden = true;
                OFL.notice(msg, 'This is a sample to preview the certificate design. It is not a certificate and cannot be verified.', 'info');
                wrap.hidden = false;
            } else if (id) { form.id.value = id; check(id); }""")]

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
# ============================================================== Account (sign up, log in, reset, terms, profile)
account_main = """        <div class="au">
            <aside class="au-side" aria-hidden="true">
                <div class="au-side__inner">
                    <p class="au-side__brand">Open Fraud Labs Academy</p>
                    <h2>Learn data science by doing it.</h2>
                    <ul class="au-side__list">
                        <li>Short video lessons built on real code and data</li>
                        <li>Practice that runs in your browser, nothing to install</li>
                        <li>Portfolio projects reviewed by other learners</li>
                        <li>A certificate anyone can verify</li>
                    </ul>
                    <div class="au-side__shot"><img src="/assets/academy/lesson-frame.jpg" width="1280" height="720" alt=""></div>
                </div>
            </aside>
            <section class="au-main">
                <div class="au-panel">
                    <div id="msg"></div>
                    <div id="auth-box" hidden>
                        <h1 id="au-title">Create your free account</h1>
                        <p class="au-sub" id="au-sub">Save your progress, practise in your browser and earn certificates.</p>
                        <div class="au-switch" role="tablist" aria-label="Account">
                            <button type="button" class="au-switch__btn is-active" data-tab="signup" role="tab" aria-selected="true">Create account</button>
                            <button type="button" class="au-switch__btn" data-tab="login" role="tab" aria-selected="false">Log in</button>
                        </div>
                        <form id="signup-form" class="au-form" data-panel="signup" novalidate>
                            <label class="au-field"><span>Full name</span>
                                <input name="full_name" required maxlength="120" autocomplete="name" placeholder="As it should appear on your certificate"></label>
                            <label class="au-field"><span>Email</span>
                                <input name="email" type="email" required autocomplete="email" inputmode="email" placeholder="you@example.com"></label>
                            <label class="au-field"><span>Password</span>
                                <span class="au-pw"><input name="password" type="password" required minlength="8" autocomplete="new-password" placeholder="At least 8 characters"><button type="button" class="au-pw__toggle" aria-label="Show password">Show</button></span></label>
                            <fieldset class="au-sign">
                                <legend>Sign the Terms of Service</legend>
                                <p>Read the <a href="/terms/" target="_blank" rel="noopener">Terms of Service</a> and <a href="/privacy/" target="_blank" rel="noopener">Privacy Policy</a>, then type your full name exactly as above to sign.</p>
                                <label class="au-field"><span class="u-sr-only">Signature (your full name)</span>
                                    <input name="signature" required maxlength="120" autocomplete="off" class="ofl-sign__input au-sign__input" placeholder="Type your full name"></label>
                                <p class="ofl-sign__status" aria-live="polite"></p>
                                <label class="au-check"><input type="checkbox" name="agree" required>
                                    <span>I agree to the Terms of Service and Privacy Policy, and I'm at least 18 or have a parent or guardian's permission.</span></label>
                            </fieldset>
                            <button class="ac-btn ac-btn--primary au-submit" type="submit">Create free account</button>
                        </form>
                        <form id="login-form" class="au-form" data-panel="login" hidden novalidate>
                            <label class="au-field"><span>Email</span>
                                <input name="email" type="email" required autocomplete="email" inputmode="email" placeholder="you@example.com"></label>
                            <label class="au-field"><span class="au-field__row">Password <button class="au-link" type="button" id="forgot">Forgot password?</button></span>
                                <span class="au-pw"><input name="password" type="password" required autocomplete="current-password"><button type="button" class="au-pw__toggle" aria-label="Show password">Show</button></span></label>
                            <button class="ac-btn ac-btn--primary au-submit" type="submit">Log in</button>
                        </form>
                        <form id="forgot-form" class="au-form" data-panel="forgot" hidden novalidate>
                            <label class="au-field"><span>Email</span>
                                <input name="email" type="email" required autocomplete="email" inputmode="email" placeholder="you@example.com"></label>
                            <button class="ac-btn ac-btn--primary au-submit" type="submit">Send reset link</button>
                            <button class="au-link au-back" type="button" data-back>Back to log in</button>
                        </form>
                    </div>
                    <form id="reset-form" class="au-form" hidden novalidate>
                        <h1>Set a new password</h1>
                        <p class="au-sub">Choose a password with at least 8 characters.</p>
                        <label class="au-field"><span>New password</span>
                            <span class="au-pw"><input name="password" type="password" required minlength="8" autocomplete="new-password"><button type="button" class="au-pw__toggle" aria-label="Show password">Show</button></span></label>
                        <button class="ac-btn ac-btn--primary au-submit" type="submit">Save new password</button>
                    </form>
                    <form id="terms-form" class="au-form au-block" hidden novalidate>
                        <h2>One more step: sign the Terms of Service</h2>
                        <p class="au-sub">Before taking quizzes or sharing projects, read the <a href="/terms/" target="_blank" rel="noopener">Terms of Service</a> and sign by typing your registered full name: <strong id="terms-name"></strong></p>
                        <label class="au-field"><span class="u-sr-only">Signature (your full name)</span><input name="signature" required maxlength="120" autocomplete="off" class="ofl-sign__input au-sign__input" placeholder="Type your full name"></label>
                        <p class="ofl-sign__status" aria-live="polite"></p>
                        <label class="au-check"><input type="checkbox" name="agree" required><span>I have read and agree to the Terms of Service and Privacy Policy.</span></label>
                        <button class="ac-btn ac-btn--primary au-submit" type="submit">Sign and continue</button>
                    </form>
                    <div id="profile-box" hidden>
                        <div class="au-me"><span class="au-me__avatar" id="me-initials"></span><div><h1 id="me-name">Your account</h1><p class="au-sub" id="me-email"></p></div></div>
                        <div class="au-actions">
                            <a class="ac-btn ac-btn--primary" href="/academy/dashboard/">Go to My learning</a>
                            <a class="ac-btn ac-btn--secondary" href="/academy/#courses">Browse courses</a>
                        </div>
                        <form id="profile-form" class="au-form au-block">
                            <h2>Name on your certificates</h2>
                            <label class="au-field"><span class="u-sr-only">Full name</span><input name="full_name" required maxlength="120" autocomplete="name"></label>
                            <button class="ac-btn ac-btn--secondary" type="submit">Save name</button>
                        </form>
                        <p class="au-edit-bg"><a href="/academy/welcome/?next=/account/">Edit your background and goals</a></p>
                        <button class="au-link au-logout" type="button" id="logout">Log out</button>
                    </div>
                </div>
            </section>
        </div>"""

account_script = r"""        (async function () {
            var sb = OFL.sb, msg = document.getElementById('msg');
            var next = OFL.qs('next') || '/academy/dashboard/';
            if (!next.startsWith('/') || next.startsWith('//')) next = '/academy/dashboard/';
            var authBox = document.getElementById('auth-box'), profileBox = document.getElementById('profile-box'), resetForm = document.getElementById('reset-form');
            var title = document.getElementById('au-title'), sub = document.getElementById('au-sub'), sw = document.querySelector('.au-switch');
            var COPY = {
                signup: ['Create your free account', 'Save your progress, practise in your browser and earn certificates.'],
                login: ['Welcome back', 'Log in to continue where you left off.'],
                forgot: ['Reset your password', 'Enter your email and we’ll send you a link to set a new password.']
            };
            function show(tab) {
                document.querySelectorAll('[data-panel]').forEach(function (p) { p.hidden = p.getAttribute('data-panel') !== tab; });
                document.querySelectorAll('.au-switch__btn').forEach(function (t) { var on = t.getAttribute('data-tab') === tab; t.classList.toggle('is-active', on); t.setAttribute('aria-selected', String(on)); });
                title.textContent = COPY[tab][0]; sub.textContent = COPY[tab][1];
                sw.hidden = tab === 'forgot';
                var first = document.querySelector('[data-panel="' + tab + '"] input'); if (first && window.innerWidth > 700) first.focus();
            }
            document.querySelectorAll('.au-switch__btn').forEach(function (t) { t.addEventListener('click', function () { msg.textContent = ''; show(t.getAttribute('data-tab')); }); });
            document.getElementById('forgot').addEventListener('click', function () { msg.textContent = ''; show('forgot'); });
            document.querySelector('[data-back]').addEventListener('click', function () { msg.textContent = ''; show('login'); });
            document.querySelectorAll('.au-pw__toggle').forEach(function (b) {
                b.addEventListener('click', function () {
                    var i = b.previousElementSibling, vis = i.type === 'password';
                    i.type = vis ? 'text' : 'password'; b.textContent = vis ? 'Hide' : 'Show'; b.setAttribute('aria-label', vis ? 'Hide password' : 'Show password');
                });
            });
            // Clear messages and invalid styles as people fix their input.
            document.querySelectorAll('.au-form input').forEach(function (i) { i.addEventListener('input', function () { i.classList.remove('is-invalid'); }); });
            function valid(form) {
                var bad = Array.prototype.filter.call(form.querySelectorAll('input[required]'), function (i) { return !i.checkValidity(); });
                bad.forEach(function (i) { i.classList.add('is-invalid'); });
                if (!bad.length) return true;
                var i = bad[0], t = i.type === 'checkbox' ? 'Please tick the box to agree to the terms.' : i.name === 'email' ? 'Please enter a valid email address.' : i.name === 'password' ? 'Your password needs at least 8 characters.' : i.name === 'signature' ? 'Type your full name to sign.' : 'Please fill in every field.';
                OFL.notice(msg, t, 'error'); i.focus();
                return false;
            }
            async function renderProfile(user) {
                authBox.hidden = true; profileBox.hidden = false;
                document.getElementById('me-email').textContent = user.email;
                var res = await sb.from('profiles').select('full_name, terms_accepted_at').eq('id', user.id).maybeSingle();
                registeredName = (res.data && res.data.full_name) || '';
                document.querySelector('#profile-form [name=full_name]').value = registeredName;
                document.getElementById('me-name').textContent = registeredName || 'Your account';
                document.getElementById('me-initials').textContent = (registeredName || user.email).split(/\s+/).map(function (w) { return w[0]; }).join('').slice(0, 2).toUpperCase();
                document.getElementById('terms-name').textContent = registeredName || '(add your name below first)';
                document.getElementById('terms-form').hidden = !!(res.data && res.data.terms_accepted_at);
                return res.data;
            }
            var TERMS_VERSION = '2026-10-01';
            function norm(t) { return (t || '').trim().replace(/\s+/g, ' ').toLowerCase(); }
            function wireSignature(form, getName) {
                var input = form.querySelector('.ofl-sign__input'), status = form.querySelector('.ofl-sign__status');
                function check() {
                    var ok = norm(input.value) !== '' && norm(input.value) === norm(getName());
                    input.setCustomValidity(ok || !input.value ? '' : 'Your signature must match your full name exactly.');
                    status.textContent = !input.value ? '' : ok ? '✓ Signature matches your name' : 'Must match your full name exactly';
                    status.className = 'ofl-sign__status ' + (!input.value ? '' : ok ? 'is-ok' : 'is-bad');
                    return ok;
                }
                input.addEventListener('input', check);
                form.addEventListener('input', function (e) { if (e.target !== input && input.value) check(); });
                return check;
            }
            var signupCheck = wireSignature(document.getElementById('signup-form'), function () { return document.querySelector('#signup-form [name=full_name]').value; });
            var registeredName = '';
            var termsCheck = wireSignature(document.getElementById('terms-form'), function () { return registeredName; });

            var recovering = /type=recovery/.test(location.hash) || OFL.qs('reset') === '1';
            sb.auth.onAuthStateChange(function (event) {
                if (event === 'PASSWORD_RECOVERY') { recovering = true; authBox.hidden = true; profileBox.hidden = true; resetForm.hidden = false; }
            });
            var user = await OFL.getUser();
            if (recovering && user) { resetForm.hidden = false; }
            else if (user) {
                var prof = await renderProfile(user);
                if (OFL.qs('next') && prof && prof.terms_accepted_at) { location.href = next; return; }
            } else {
                authBox.hidden = false;
                var wantsLogin = OFL.qs('mode') === 'login' || /^\/academy\/(admin|dashboard)/.test(OFL.qs('next') || '');
                var remembered = null; try { remembered = localStorage.getItem('ofl-has-account'); } catch (e) {}
                show(wantsLogin || (remembered && OFL.qs('mode') !== 'signup') ? 'login' : 'signup');
            }
            async function busy(btn, on, label) { btn.disabled = on; if (on) { btn.dataset.label = btn.textContent; btn.textContent = label; } else if (btn.dataset.label) btn.textContent = btn.dataset.label; }

            document.getElementById('signup-form').addEventListener('submit', async function (e) {
                e.preventDefault();
                var f = e.target; if (!valid(f)) return;
                if (!signupCheck()) { f.signature.classList.add('is-invalid'); return OFL.notice(msg, 'Your signature must match your full name exactly.', 'error'); }
                var btn = f.querySelector('button[type=submit]'); busy(btn, true, 'Creating your account…');
                var res = await sb.auth.signUp({
                    email: f.email.value.trim(), password: f.password.value,
                    options: { data: { full_name: f.full_name.value.trim(), terms_signature: f.signature.value.trim(), terms_version: TERMS_VERSION }, emailRedirectTo: location.origin + '/account/?next=' + encodeURIComponent(next) }
                });
                busy(btn, false);
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                try { localStorage.setItem('ofl-has-account', '1'); } catch (x) {}
                if (res.data.session) { location.href = next; return; }
                var email = f.email.value.trim(); f.reset();
                document.getElementById('signup-form').hidden = true; sw.hidden = true;
                title.textContent = 'Check your email';
                sub.textContent = 'We’ve sent a confirmation link to ' + email + '. Click it to activate your account. If it isn’t in your inbox within a few minutes, check your spam folder.';
            });
            document.getElementById('login-form').addEventListener('submit', async function (e) {
                e.preventDefault();
                var f = e.target; if (!valid(f)) return;
                var btn = f.querySelector('button[type=submit]'); busy(btn, true, 'Logging in…');
                var res = await sb.auth.signInWithPassword({ email: f.email.value.trim(), password: f.password.value });
                busy(btn, false);
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                try { localStorage.setItem('ofl-has-account', '1'); } catch (x) {}
                location.href = next;
            });
            document.getElementById('forgot-form').addEventListener('submit', async function (e) {
                e.preventDefault();
                var f = e.target; if (!valid(f)) return;
                var btn = f.querySelector('button[type=submit]'); busy(btn, true, 'Sending…');
                var res = await sb.auth.resetPasswordForEmail(f.email.value.trim(), { redirectTo: location.origin + '/account/?reset=1' });
                busy(btn, false);
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                OFL.notice(msg, 'If an account exists for that email, a reset link is on its way.', 'success');
            });
            resetForm.addEventListener('submit', async function (e) {
                e.preventDefault(); if (!valid(resetForm)) return;
                var res = await sb.auth.updateUser({ password: resetForm.password.value });
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                resetForm.hidden = true;
                OFL.notice(msg, 'Your password has been updated.', 'success');
                renderProfile((await sb.auth.getUser()).data.user);
            });
            document.getElementById('terms-form').addEventListener('submit', async function (e) {
                e.preventDefault(); if (!valid(e.target)) return;
                if (!termsCheck()) return OFL.notice(msg, 'Your signature must match your registered full name exactly.', 'error');
                var res = await sb.rpc('accept_terms', { p_version: TERMS_VERSION, p_signature: e.target.signature.value.trim() });
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                e.target.hidden = true;
                OFL.notice(msg, 'Thank you. Your signed acceptance has been recorded.', 'success');
                if (OFL.qs('next')) location.href = next;
            });
            document.getElementById('profile-form').addEventListener('submit', async function (e) {
                e.preventDefault();
                var u = await OFL.getUser();
                var res = await sb.from('profiles').update({ full_name: e.target.full_name.value.trim() }).eq('id', u.id);
                OFL.notice(msg, res.error ? OFL.friendlyError(res.error) : 'Name saved.', res.error ? 'error' : 'success');
                if (!res.error) { registeredName = e.target.full_name.value.trim(); document.getElementById('me-name').textContent = registeredName; }
            });
            document.getElementById('logout').addEventListener('click', async function () { await sb.auth.signOut(); location.href = '/academy/'; });
        })();"""

page("account", "Your account | Open Fraud Labs Academy", "Create a free Academy account or log in.", account_main, account_script, noindex=True)
port("verify", "verify", "Verify a certificate | Open Fraud Labs Academy", "Check that an Open Fraud Labs Academy certificate is genuine.", active="verify")
json.dump(PORTED, open(CACHE, "w"))

# ============================================================== Admin (reports + capstone review)
admin_main = """        <div class="ac-wrap ac-admin">
            <div class="ac-dash-head">
                <h1>Academy admin</h1>
                <p class="ac-muted" id="admin-sub">Live figures from the learning database. <a href="/verify/?sample=1" target="_blank" rel="noopener">Preview the certificate design</a></p>
                <div id="msg"></div>
            </div>
            <div id="admin-body" hidden>
                <div class="ac-kpis" id="kpis"></div>
                <section class="ac-admin__sec" data-cap="manage_applications" id="app-sec">
                    <div class="ac-admin__head"><h2>Applications</h2><p class="ac-muted" id="app-sub">Cohort applications, scored against the published criteria. Shortlisting, the trial deadline, reminders and waitlist moves run by themselves every hour; you can step in at any time.</p>
                        <div class="ac-admin__tools"><select id="app-cohort" aria-label="Cohort"></select>
                            <button class="ac-btn ac-btn--secondary ac-btn--sm" type="button" id="app-settings">Cohort settings</button>
                            <button class="ac-btn ac-btn--secondary ac-btn--sm" type="button" id="app-fill">Fill open places now</button>
                            <button class="ac-btn ac-btn--secondary ac-btn--sm" type="button" id="app-csv">Download CSV</button></div></div>
                    <p class="app-line" id="app-line"></p>
                    <div class="ac-kpis ac-kpis--sm" id="app-kpis"></div>
                    <div class="app-filter"><div class="ofl-tabs" id="app-tabs">
                        <button type="button" class="ofl-tab is-active" data-f="all">All</button>
                        <button type="button" class="ofl-tab" data-f="check">To check</button>
                        <button type="button" class="ofl-tab" data-f="shortlisted">Offered</button>
                        <button type="button" class="ofl-tab" data-f="completed">Confirmed</button>
                        <button type="button" class="ofl-tab" data-f="waitlisted">Waitlist</button>
                        <button type="button" class="ofl-tab" data-f="missed">Missed</button>
                        <button type="button" class="ofl-tab" data-f="rejected">Rejected</button>
                    </div><input type="search" id="app-q" placeholder="Search name or email" aria-label="Search applications"></div>
                    <div class="ac-table-wrap"><table class="ac-table" id="app-table"></table></div>
                </section>
                <dialog class="ac-dialog ac-dialog--wide" id="app-dlg" aria-labelledby="app-dlg-title">
                    <div class="ac-dialog__head"><h2 id="app-dlg-title">Application</h2><button class="ac-btn ac-btn--ghost ac-btn--sm" type="button" data-close aria-label="Close">Close</button></div>
                    <div id="app-dlg-msg"></div>
                    <div id="app-dlg-body"></div>
                </dialog>
                <dialog class="ac-dialog" id="cohort-dlg" aria-labelledby="cohort-dlg-title">
                    <div class="ac-dialog__head"><h2 id="cohort-dlg-title">Cohort settings</h2><button class="ac-btn ac-btn--ghost ac-btn--sm" type="button" data-close aria-label="Close">Close</button></div>
                    <div id="cohort-msg"></div>
                    <form id="cohort-form" class="ac-form" novalidate>
                        <label>Name<input id="co-title" maxlength="80" placeholder="e.g. Founding Cohort"></label>
                        <label>Link name<input id="co-slug" maxlength="40" placeholder="founding-2026"><small class="ac-muted">Used in the apply link. Can't be changed later.</small></label>
                        <label>Course<select id="co-course"></select></label>
                        <fieldset class="cf-status"><legend>Applications</legend>
                            <label><input type="radio" name="co-status" value="draft"> <b>Draft</b><span>Not visible to learners yet.</span></label>
                            <label><input type="radio" name="co-status" value="open"> <b>Open</b><span>Anyone can apply on the careers and apply pages.</span></label>
                            <label><input type="radio" name="co-status" value="closed"> <b>Closed</b><span>No new applications. Trials and the waitlist keep running.</span></label>
                        </fieldset>
                        <div class="cf-row">
                            <label>Places<input id="co-capacity" type="number" min="1" max="100000"></label>
                            <label>Minimum score (0–100)<input id="co-min" type="number" min="0" max="100"></label>
                        </div>
                        <div class="cf-row">
                            <label>Trial lesson<input id="co-lesson" type="number" min="1"></label>
                            <label>Days to finish it<input id="co-days" type="number" min="1" max="90"></label>
                        </div>
                        <fieldset class="cf-status"><legend>Shortlisting</legend>
                            <label><input type="radio" name="co-mode" value="rolling"> <b>Automatic, as places open</b><span>Highest score first. Applicants below the minimum wait for you to decide.</span></label>
                            <label><input type="radio" name="co-mode" value="batch"> <b>Once, when applications close</b><span>Everyone waits until the closing date, then the top applicants are shortlisted.</span></label>
                        </fieldset>
                        <label>Applications close <em class="ac-muted">(optional, Lagos time)</em><input id="co-closes" type="datetime-local"></label>
                        <fieldset class="co-cond"><legend>Conditions</legend>
                            <label class="ap-check"><input type="checkbox" id="co-c-laptop"> Applicants must have their own laptop or desktop</label>
                            <label class="ap-check"><input type="checkbox" id="co-c-proofs"> Applicants must give a LinkedIn profile and upload screenshots showing they follow @_drhola on TikTok, the founder and the Open Fraud Labs page on LinkedIn. Staff check them before anyone is offered a place.</label>
                            <label class="ap-check"><input type="checkbox" id="co-c-post"> To accept an offer, post about it on LinkedIn tagging the founder and the page</label>
                            <label class="ap-check"><input type="checkbox" id="co-c-wa"> To accept an offer, join the cohort WhatsApp group</label>
                        </fieldset>
                        <label>Founder's LinkedIn profile<input id="co-founder" type="url" maxlength="200" placeholder="https://www.linkedin.com/in/..."><small class="ac-muted">Linked from the apply page so applicants follow the right person.</small></label>
                        <label>WhatsApp group invite link<input id="co-wa" type="url" maxlength="300" placeholder="https://chat.whatsapp.com/..."><small class="ac-muted">Shown only to applicants with an offer or a confirmed place.</small></label>
                        <label class="ap-check"><input type="checkbox" id="co-require"> Only shortlisted applicants (plus staff and scholarship holders) can enrol in this course. Learners already enrolled keep their place.</label>
                        <div class="ofl-actions"><button class="ac-btn ac-btn--primary" type="submit">Save settings</button><button class="ac-btn ac-btn--ghost" type="button" data-close>Cancel</button></div>
                        <p class="ac-muted ac-small">Screenshots are only needed to check eligibility. <button type="button" class="au-link" id="co-del-proofs">Delete all screenshots for this cohort</button> once you've finished checking.</p>
                    </form>
                </dialog>
                <section class="ac-admin__sec" data-cap="view_people">
                    <div class="ac-admin__head"><h2>Learners</h2><div class="ac-admin__tools"><input type="search" id="q" placeholder="Search name or email" aria-label="Search learners"><button class="ac-btn ac-btn--secondary ac-btn--sm" type="button" id="csv">Download CSV</button></div></div>
                    <div class="ac-table-wrap"><table class="ac-table" id="learners"></table></div>
                </section>
                <dialog class="ac-dialog" id="manage" aria-labelledby="manage-title">
                    <div class="ac-dialog__head"><h2 id="manage-title">Manage learner</h2><button class="ac-btn ac-btn--ghost ac-btn--sm" type="button" id="manage-close" aria-label="Close">Close</button></div>
                    <div id="manage-msg"></div>
                    <div id="manage-body"></div>
                </dialog>
                <section class="ac-admin__sec" data-cap="manage_applications" id="roles-sec">
                    <div class="ac-admin__head"><h2>Internship applications</h2><p class="ac-muted">Applications for roles on the careers page. Move each person through the stages; they're told on the site and by email at every step except notes.</p>
                        <div class="ac-admin__tools"><select id="role-pick" aria-label="Role"></select><select id="role-status" aria-label="Role status"><option value="open">Open (rolling)</option><option value="filled">Filled</option><option value="closed">Closed</option><option value="draft">Hidden</option></select>
                            <button class="ac-btn ac-btn--secondary ac-btn--sm" type="button" id="role-csv">Download CSV</button></div></div>
                    <p class="app-line" id="role-line"></p>
                    <div class="ac-table-wrap"><table class="ac-table" id="role-table"></table></div>
                </section>
                <dialog class="ac-dialog ac-dialog--wide" id="role-dlg" aria-labelledby="role-dlg-title">
                    <div class="ac-dialog__head"><h2 id="role-dlg-title">Applicant</h2><button class="ac-btn ac-btn--ghost ac-btn--sm" type="button" data-close aria-label="Close">Close</button></div>
                    <div id="role-dlg-msg"></div>
                    <div id="role-dlg-body"></div>
                </dialog>
                <section class="ac-admin__sec" data-cap="manage_scholarships" id="sch-sec">
                    <div class="ac-admin__head"><h2>Scholarships</h2><p class="ac-muted">Full access to a course, or every course, without paying. Each scholarship records how long it lasts and why it was given. The learner is told on the site and by email.</p>
                        <button class="ac-btn ac-btn--primary ac-btn--sm" type="button" id="sch-new">Give a scholarship</button></div>
                    <div class="ac-kpis ac-kpis--sm" id="sch-kpis"></div>
                    <div class="ofl-tabs" id="sch-tabs">
                        <button type="button" class="ofl-tab is-active" data-f="active">Active</button>
                        <button type="button" class="ofl-tab" data-f="ended">Ended</button>
                        <button type="button" class="ofl-tab" data-f="all">All</button>
                    </div>
                    <div class="ac-table-wrap"><table class="ac-table" id="sch-table"></table></div>
                </section>
                <dialog class="ac-dialog" id="sch-dlg" aria-labelledby="sch-title">
                    <div class="ac-dialog__head"><h2 id="sch-title">Give a scholarship</h2><button class="ac-btn ac-btn--ghost ac-btn--sm" type="button" data-close aria-label="Close">Close</button></div>
                    <div id="sch-msg"></div>
                    <form id="sch-form" class="ac-form sch-form" novalidate>
                        <fieldset class="sch-step">
                            <legend>1. Learner</legend>
                            <div id="sch-who"></div>
                            <div id="sch-find"><input type="search" id="sch-q" placeholder="Search by name or email (at least 3 letters)" aria-label="Find a learner" autocomplete="off">
                                <ul class="sch-results" id="sch-results"></ul></div>
                        </fieldset>
                        <fieldset class="sch-step">
                            <legend>2. Course</legend>
                            <select id="sch-course" aria-label="Course"></select>
                        </fieldset>
                        <fieldset class="sch-step">
                            <legend>3. Duration</legend>
                            <div class="sch-chips" id="sch-dur" role="radiogroup" aria-label="Duration"></div>
                            <label class="sch-until" id="sch-until-wrap" hidden>Ends on <input type="date" id="sch-until"></label>
                        </fieldset>
                        <fieldset class="sch-step">
                            <legend>4. Why</legend>
                            <textarea id="sch-reason" rows="3" maxlength="500" placeholder="e.g. Winner of the 2026 women in data essay competition; partner programme with ABC University; financial hardship application approved"></textarea>
                            <small class="ac-muted">Kept in the scholarship record and the staff log. The learner doesn't see this.</small>
                        </fieldset>
                        <p class="sch-summary" id="sch-summary"></p>
                        <div class="ofl-actions"><button class="ac-btn ac-btn--primary" type="submit" id="sch-save">Give scholarship</button><button class="ac-btn ac-btn--ghost" type="button" data-close>Cancel</button></div>
                    </form>
                </dialog>
                <section class="ac-admin__sec" data-cap="manage_content" id="courses-sec">
                    <div class="ac-admin__head"><h2>Courses</h2><p class="ac-muted">Add a course, edit what learners see, and choose whether it's live, coming soon or hidden. Hidden courses are visible only to staff who manage content.</p>
                        <button class="ac-btn ac-btn--primary ac-btn--sm" type="button" id="course-new">Add a course</button></div>
                    <div class="cm-list" id="cm-list"><p class="ac-muted">Loading…</p></div>
                </section>
                <dialog class="ac-dialog" id="course-dlg" aria-labelledby="course-title">
                    <div class="ac-dialog__head"><h2 id="course-title">Add a course</h2><button class="ac-btn ac-btn--ghost ac-btn--sm" type="button" data-close aria-label="Close">Close</button></div>
                    <div id="course-msg"></div>
                    <form id="course-form" class="ac-form" novalidate>
                        <label>Title<input id="cf-title" maxlength="80" required placeholder="e.g. Data Analysis"></label>
                        <label>Course link<span class="cf-slug"><span class="ac-muted">/academy/courses/?c=</span><input id="cf-slug" maxlength="40" pattern="[a-z0-9-]+" placeholder="data-analysis"></span>
                            <small class="ac-muted">Lowercase letters, numbers and dashes. Can't be changed later.</small></label>
                        <label>Short description<textarea id="cf-desc" rows="3" maxlength="400" placeholder="One or two sentences on what learners will be able to do."></textarea></label>
                        <div class="cf-row">
                            <label>Level<select id="cf-level"><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></label>
                            <label>Access<select id="cf-access"><option value="free">Free</option><option value="paid">Paid (needs a pass)</option></select></label>
                        </div>
                        <fieldset class="cf-status"><legend>Status</legend>
                            <label><input type="radio" name="cf-status" value="live"> <b>Live</b><span>Listed and open for enrolment.</span></label>
                            <label><input type="radio" name="cf-status" value="coming_soon"> <b>Coming soon</b><span>Listed as in preparation; nobody can enrol yet.</span></label>
                            <label><input type="radio" name="cf-status" value="hidden"> <b>Hidden</b><span>Not listed anywhere. Only content staff can see it, to build and check lessons.</span></label>
                        </fieldset>
                        <div class="ofl-actions"><button class="ac-btn ac-btn--primary" type="submit">Save course</button><button class="ac-btn ac-btn--ghost" type="button" data-close>Cancel</button></div>
                    </form>
                </dialog>
                <dialog class="ac-dialog ac-dialog--wide" id="lessons-dlg" aria-labelledby="lessons-title">
                    <div class="ac-dialog__head"><h2 id="lessons-title">Lessons</h2><button class="ac-btn ac-btn--ghost ac-btn--sm" type="button" data-close aria-label="Close">Close</button></div>
                    <div id="lessons-msg"></div>
                    <p class="ac-muted ac-small">Rename lessons, add new ones, and release or hide them. A hidden lesson stays in the outline as &ldquo;Coming soon&rdquo; and can't be opened. Notes, quiz and video for each lesson are uploaded with the content import tool.</p>
                    <div class="ac-table-wrap"><table class="ac-table cm-lessons" id="lessons-table"></table></div>
                </dialog>
                <section class="ac-admin__sec" data-cap="view_stats">
                    <div class="ac-admin__head"><h2>Lesson funnel: Data Science from Scratch</h2></div>
                    <p class="ac-muted">Learners at each step of every released lesson. Video and notes counts start from 1 October 2026, when the step-by-step rules began.</p>
                    <div class="ac-table-wrap"><table class="ac-table" id="funnel"></table></div>
                </section>
                <section class="ac-admin__sec" data-cap="view_stats">
                    <div class="ac-admin__head"><h2>Who's learning</h2><p class="ac-muted" id="bg-note">Answers from the About you step. Totals only; use the download for your own analysis.</p>
                        <button class="ac-btn ac-btn--secondary ac-btn--sm" type="button" id="bg-csv">Download answers (CSV)</button></div>
                    <div class="bg-grid" id="bg-grid"><p class="ac-muted">Loading…</p></div>
                </section>
                <section class="ac-admin__sec" data-cap="view_people">
                    <div class="ac-admin__head"><h2>Recent activity</h2><p class="ac-muted">Enrolments, completed courses, certificates and project results, newest first. Learners get the same messages on the site and by email.</p></div>
                    <ul class="ac-activity" id="activity"><li class="ac-muted">Loading…</li></ul>
                </section>
                <section class="ac-admin__sec" data-cap="view_finance" id="finance-sec">
                    <div class="ac-admin__head"><h2>Finance</h2><p class="ac-muted">Paystack payments and passes. Amounts are what learners paid, before Paystack's fees.</p></div>
                    <div class="ac-kpis" id="fin-kpis"></div>
                    <h3 class="ac-admin__sub">Plans and prices</h3>
                    <div class="ac-table-wrap"><table class="ac-table" id="plans-table"></table></div>
                    <h3 class="ac-admin__sub">Recent payments</h3>
                    <div class="ac-table-wrap"><table class="ac-table" id="payments-table"></table></div>
                </section>
                <section class="ac-admin__sec" data-cap="view_staff">
                    <div class="ac-admin__head"><h2>Staff and roles</h2><p class="ac-muted" id="staff-note">Who can use this page and what they can do. Only the owner can give or remove roles, and nobody can change the owner.</p></div>
                    <div class="ac-table-wrap"><table class="ac-table" id="staff-table"></table></div>
                    <details class="ac-roles"><summary>What each role can do</summary>
                        <ul>
                            <li><b>Owner</b>: everything, including giving and removing roles. Can't be removed from the website.</li>
                            <li><b>Admin</b>: manage learners (suspend, unlock, certificates), applications, scholarships, courses and lessons, grade projects, see learners and stats. Can't change roles or other staff.</li>
                            <li><b>Reviewer</b>: grade projects and capstones, see learners and stats.</li>
                            <li><b>Finance</b> (CFO, account officer): payments, passes, plans and prices, and stats.</li>
                            <li><b>HR</b>: run cohort applications (settings, shortlist, waitlist, reject), see learners, the staff list and stats. Can't change learner accounts or roles.</li>
                            <li><b>Scholarship officer</b>: give and end scholarships (course, duration and reason), and see stats. Can find a learner by name or email to do this, but can't change their account.</li>
                            <li><b>Instructor</b> (content editor): add and edit courses and lessons, release or hide them, open any lesson without studying, grade projects, and see stats. Can't take a course off live once learners are enrolled, or make it paid; the owner or an admin does that.</li>
                            <li><b>Analyst</b>: stats, the lesson funnel and learner totals only; no names or emails.</li>
                        </ul>
                    </details>
                </section>
                <section class="ac-admin__sec" data-cap="review">
                    <div class="ac-admin__head"><h2>Project and capstone reviews</h2><p class="ac-muted">Peer review grades these automatically; approve or request changes here to step in at any time.</p></div>
                    <div class="ofl-tabs" id="filters">
                        <button type="button" class="ofl-tab is-active" data-status="submitted">Waiting for review</button>
                        <button type="button" class="ofl-tab" data-status="changes_requested">Changes requested</button>
                        <button type="button" class="ofl-tab" data-status="approved">Approved</button>
                    </div>
                    <div id="subs"></div>
                </section>
            </div>
        </div>"""

admin_script = r"""        (async function () {
            var sb = OFL.sb, el = OFL.el, msg = document.getElementById('msg');
            (async function background() {
                var grid = document.getElementById('bg-grid');
                var r = await sb.rpc('admin_background_summary');
                if (r.error || !r.data) { grid.textContent = ''; return; }
                var d = r.data, regionName = null; try { regionName = new Intl.DisplayNames(['en'], { type: 'region' }); } catch (e) {}
                document.getElementById('bg-note').textContent = d.answered + ' of ' + d.learners + ' learners have answered. Totals only; use the download for your own analysis.';
                var L = { woman: 'Woman', man: 'Man', another: 'Another gender', prefer_not: 'Prefer not to say', under_18: 'Under 18', '18_24': '18–24', '25_34': '25–34', '35_44': '35–44', '45_54': '45–54', '55_plus': '55+',
                    student: 'Student', employed_full: 'Employed full-time', employed_part: 'Employed part-time', self_employed: 'Self-employed', looking: 'Looking for work', not_working: 'Not working', other: 'Other',
                    secondary: 'Secondary', diploma: 'Diploma, OND or HND', bachelors: 'Bachelor’s', masters: 'Master’s', doctorate: 'Doctorate',
                    none: 'None', beginner: 'Tried a little', some: 'Some', confident: 'Regular user', work: 'At work',
                    first_job: 'First data job', switch_career: 'Switch careers', upskill: 'Upskill in current job', study: 'Support studies', business: 'Own business', curious: 'Curiosity',
                    tiktok: 'TikTok', linkedin: 'LinkedIn', friend: 'Friend or colleague', search: 'Search', school: 'School or employer', XX: 'Prefer not to say', '?': 'No answer' };
                var T = [['country', 'Country'], ['gender', 'Gender'], ['age_range', 'Age'], ['employment', 'Doing now'], ['education', 'Education'], ['python_level', 'Python'], ['data_level', 'Data analysis'], ['goal', 'Goal'], ['heard_from', 'Heard about us']];
                grid.textContent = '';
                if (!d.answered) return grid.appendChild(el('p', { class: 'ac-muted', text: 'No answers yet. New learners see the questions after they sign up.' }));
                T.forEach(function (t) {
                    var obj = d[t[0]] || {}, rows = Object.keys(obj).map(function (k) { return [k, obj[k]]; }).sort(function (a, b) { return b[1] - a[1]; }).slice(0, 8);
                    var box = el('div', { class: 'bg-card' }, el('h3', { text: t[1] }));
                    rows.forEach(function (x) {
                        var label = t[0] === 'country' && x[0].length === 2 && x[0] !== 'XX' && regionName ? regionName.of(x[0]) : (L[x[0]] || x[0]);
                        var pct = Math.round(100 * x[1] / d.answered);
                        box.appendChild(el('div', { class: 'bg-bar' }, el('span', { class: 'bg-bar__l', text: label }), el('span', { class: 'bg-bar__n num', text: x[1] + ' · ' + pct + '%' }),
                            el('i', { style: 'width:' + pct + '%' })));
                    });
                    grid.appendChild(box);
                });
            })();
            document.getElementById('bg-csv').addEventListener('click', async function () {
                var r = await sb.from('learner_background').select('*').not('completed_at', 'is', null);
                var who = {}; ((await sb.rpc('admin_learners')).data || []).forEach(function (x) { who[x.user_id] = x; });
                var cols = ['country', 'city', 'gender', 'age_range', 'employment', 'industry', 'education', 'python_level', 'data_level', 'goal', 'heard_from', 'completed_at'];
                var lines = [['name', 'email'].concat(cols).join(',')];
                (r.data || []).forEach(function (x) {
                    var w = who[x.user_id] || {};
                    lines.push([w.full_name || '', w.email || ''].concat(cols.map(function (c) { return x[c] == null ? '' : x[c]; })).map(function (v) { return '"' + String(v).replace(/"/g, '""') + '"'; }).join(','));
                });
                var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/csv' }));
                a.download = 'learner-background.csv'; document.body.appendChild(a); a.click(); a.remove();
            });
            (async function activity() {
                var ul = document.getElementById('activity');
                var r = await sb.from('notifications').select('user_id, kind, title, created_at, email_status').neq('kind', 'welcome').order('created_at', { ascending: false }).limit(40);
                var who = {}; ((await sb.rpc('admin_learners')).data || []).forEach(function (x) { who[x.user_id] = x.full_name || x.email; });
                ul.textContent = '';
                if (!r.data || !r.data.length) return ul.appendChild(el('li', { class: 'ac-muted', text: 'No activity yet.' }));
                var tag = { enrolled: 'Enrolled', course_complete: 'Completed', certificate: 'Certificate', project_reviewed: 'Project' };
                r.data.forEach(function (x) {
                    ul.appendChild(el('li', {}, el('span', { class: 'ac-activity__tag ac-activity__tag--' + x.kind, text: tag[x.kind] || x.kind }),
                        el('span', {}, el('strong', { text: (who[x.user_id] || 'Learner') + ': ' }), x.title),
                        el('small', { text: OFL.formatDate(x.created_at) + (x.email_status === 'sent' ? ' · emailed' : x.email_status === 'skipped' ? ' · email not set up' : '') })));
                });
            })();
            var user = await OFL.requireUser('/academy/admin/'); if (!user) return;
            var role = (await sb.rpc('my_staff_role')).data;
            if (!role) return OFL.notice(msg, 'This page is only for Open Fraud Labs staff.', 'error');
            var CAPS = { manage_roles: ['owner'], manage_learners: ['owner', 'admin'], review: ['owner', 'admin', 'reviewer', 'instructor'],
                view_people: ['owner', 'admin', 'reviewer', 'hr'], view_staff: ['owner', 'admin', 'hr'], view_finance: ['owner', 'finance'],
                manage_plans: ['owner', 'finance'], manage_scholarships: ['owner', 'admin', 'scholarship'], manage_content: ['owner', 'admin', 'instructor'], manage_applications: ['owner', 'admin', 'hr'],
                view_stats: ['owner', 'admin', 'reviewer', 'analyst', 'finance', 'hr', 'scholarship', 'instructor'] };
            function can(c) { return (CAPS[c] || []).indexOf(role) >= 0; }
            var ROLE_NAME = { owner: 'Owner', admin: 'Admin', reviewer: 'Reviewer', analyst: 'Analyst', finance: 'Finance', hr: 'HR', scholarship: 'Scholarship officer', instructor: 'Instructor' };
            var ROLE_OPTS = [['admin', 'Admin'], ['instructor', 'Instructor'], ['reviewer', 'Reviewer'], ['scholarship', 'Scholarship officer'], ['finance', 'Finance'], ['hr', 'HR'], ['analyst', 'Analyst']];
            document.querySelectorAll('[data-cap]').forEach(function (sec) { sec.hidden = !can(sec.getAttribute('data-cap')); });
            if (!can('view_people')) document.getElementById('bg-csv').hidden = true;
            document.getElementById('admin-sub').prepend(el('span', { class: 'ac-rolebadge', text: 'Your role: ' + ROLE_NAME[role] }), ' ');
            document.getElementById('admin-body').hidden = false;
            document.querySelectorAll('dialog [data-close]').forEach(function (b) { b.addEventListener('click', function () { b.closest('dialog').close(); }); });
            function dOnly(v) { return v ? new Date(v).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : ''; }
            function schUntil(x) { return x.ends_at ? 'until ' + dOnly(new Date(new Date(x.ends_at).getTime() - 1000)) : 'with no end date'; }
            var allCourses = [];
            async function loadCourses() { allCourses = (await sb.from('courses').select('slug, title, status, access, sort').order('sort')).data || []; }

            // ---- Scholarships
            var schRows = [], schFilter = 'active', schPick = null, schDur = '90';
            async function loadScholarships() {
                if (!can('manage_scholarships')) return;
                var r = await sb.rpc('scholarship_list');
                if (r.error) return OFL.notice(msg, OFL.friendlyError(r.error), 'error');
                schRows = r.data || []; drawScholarships();
            }
            function drawScholarships() {
                var active = schRows.filter(function (x) { return x.status === 'active'; });
                var soon = active.filter(function (x) { return x.ends_at && new Date(x.ends_at) - Date.now() < 14 * 864e5; });
                var k = document.getElementById('sch-kpis'); k.textContent = '';
                [['Active', active.length], ['Ending in the next 14 days', soon.length], ['Given in total', schRows.length]]
                    .forEach(function (x) { k.appendChild(el('div', { class: 'ac-kpi' }, el('strong', { class: 'num', text: String(x[1]) }), el('span', { text: x[0] }))); });
                var t = document.getElementById('sch-table'); t.textContent = '';
                var hr = el('tr'); ['Learner', 'Course', 'Duration', 'Why', 'Given by', 'Status', ''].forEach(function (h) { hr.appendChild(el('th', { text: h })); });
                t.appendChild(el('thead', {}, hr));
                var tb = el('tbody'); t.appendChild(tb);
                var list = schRows.filter(function (x) { return schFilter === 'all' || (schFilter === 'active' ? x.status === 'active' : x.status !== 'active'); });
                if (!list.length) tb.appendChild(el('tr', {}, el('td', { colspan: '7', class: 'ac-muted', text: schFilter === 'active' ? 'No active scholarships. Use “Give a scholarship” to add one.' : 'Nothing here yet.' })));
                list.forEach(function (x) {
                    var left = x.ends_at && x.status === 'active' ? Math.ceil((new Date(x.ends_at) - Date.now()) / 864e5) : null;
                    var dur = el('td', {}, el('div', { text: dOnly(x.starts_at) + ' → ' + (x.ends_at ? dOnly(new Date(new Date(x.ends_at).getTime() - 1000)) : 'no end date') }),
                        left != null ? el('small', { class: 'ac-muted', text: left + (left === 1 ? ' day' : ' days') + ' left' }) : null);
                    var st = el('td', {}, el('span', { class: 'sch-status sch-status--' + x.status, text: x.status === 'active' ? 'Active' : x.status === 'expired' ? 'Ended' : 'Ended early' }),
                        x.revoke_reason ? el('small', { class: 'ac-muted', text: x.revoke_reason }) : null);
                    var end = x.status === 'active' ? el('button', { class: 'ac-btn ac-btn--secondary ac-btn--sm', type: 'button', text: 'End', onclick: async function () {
                        var why = window.prompt('End the scholarship for ' + (x.full_name || x.email) + '? Give a reason (kept in the record):', ''); if (!why) return;
                        var res = await sb.rpc('scholarship_revoke', { p_id: x.id, p_reason: why });
                        if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                        OFL.notice(msg, 'Scholarship ended for ' + (x.full_name || x.email) + '.', 'success'); loadScholarships();
                    } }) : null;
                    tb.appendChild(el('tr', {}, el('td', {}, el('div', { text: x.full_name || '(no name)' }), el('small', { class: 'ac-muted', text: x.email })),
                        el('td', { text: x.course_title }), dur, el('td', { class: 'sch-why', text: x.reason }),
                        el('td', {}, el('div', { text: x.granted_by_name || x.granted_by_email || '—' }), el('small', { class: 'ac-muted', text: dOnly(x.granted_at) })), st, el('td', {}, end)));
                });
            }
            document.querySelectorAll('#sch-tabs .ofl-tab').forEach(function (b) { b.addEventListener('click', function () {
                document.querySelectorAll('#sch-tabs .ofl-tab').forEach(function (o) { o.classList.toggle('is-active', o === b); }); schFilter = b.dataset.f; drawScholarships(); }); });
            var schDlg = document.getElementById('sch-dlg');
            var DUR = [['30', '30 days'], ['90', '3 months'], ['180', '6 months'], ['365', '1 year'], ['date', 'Until a date'], ['none', 'No end date']];
            function schEnd() {
                if (schDur === 'none') return null;
                if (schDur === 'date') { var v = document.getElementById('sch-until').value; return v ? new Date(v + 'T00:00:00') : undefined; }
                return new Date(Date.now() + (+schDur) * 864e5);
            }
            function schSummary() {
                var c = document.getElementById('sch-course'), end = schEnd(), s = document.getElementById('sch-summary');
                if (!schPick) { s.textContent = 'Choose a learner to continue.'; return; }
                s.textContent = (schPick.full_name || schPick.email) + ' will get full access to ' + c.options[c.selectedIndex].text +
                    (end === null ? ' with no end date.' : end ? ' until ' + dOnly(end) + '.' : ' until the date you choose.') + ' They’ll get a message on the site and by email' + (c.value !== 'all' ? ', and be enrolled in the course if it’s live.' : '.');
            }
            function schSetWho(p) {
                schPick = p; var who = document.getElementById('sch-who'); who.textContent = '';
                document.getElementById('sch-find').hidden = !!p;
                if (p) who.appendChild(el('div', { class: 'sch-picked' }, el('span', {}, el('strong', { text: p.full_name || '(no name)' }), ' ', el('span', { class: 'ac-muted', text: p.email })),
                    el('button', { class: 'ac-btn ac-btn--ghost ac-btn--sm', type: 'button', text: 'Change', onclick: function () { schSetWho(null); document.getElementById('sch-q').focus(); } })));
                schSummary();
            }
            function openScholarship(person) {
                document.getElementById('sch-msg').textContent = '';
                document.getElementById('sch-form').reset(); document.getElementById('sch-results').textContent = '';
                var c = document.getElementById('sch-course'); c.textContent = '';
                c.appendChild(el('option', { value: 'all', text: 'All courses' }));
                allCourses.forEach(function (x) { c.appendChild(el('option', { value: x.slug, text: x.title + (x.status === 'live' ? '' : x.status === 'coming_soon' ? ' (coming soon)' : ' (hidden)') })); });
                schDur = '90'; drawDur(); schSetWho(person || null);
                schDlg.showModal(); if (!person) document.getElementById('sch-q').focus();
            }
            function drawDur() {
                var box = document.getElementById('sch-dur'); box.textContent = '';
                DUR.forEach(function (d) { box.appendChild(el('button', { type: 'button', role: 'radio', 'aria-checked': String(d[0] === schDur), class: 'sch-chip' + (d[0] === schDur ? ' is-on' : ''), text: d[1],
                    onclick: function () { schDur = d[0]; drawDur(); if (d[0] === 'date') document.getElementById('sch-until').focus(); } })); });
                document.getElementById('sch-until-wrap').hidden = schDur !== 'date';
                document.getElementById('sch-until').min = new Date(Date.now() + 864e5).toISOString().slice(0, 10);
                schSummary();
            }
            document.getElementById('sch-new').addEventListener('click', function () { openScholarship(null); });
            document.getElementById('sch-course').addEventListener('change', schSummary);
            document.getElementById('sch-until').addEventListener('input', schSummary);
            var schTimer;
            document.getElementById('sch-q').addEventListener('input', function (e) {
                clearTimeout(schTimer); var q = e.target.value.trim(), ul = document.getElementById('sch-results');
                if (q.length < 3) { ul.textContent = ''; return; }
                schTimer = setTimeout(async function () {
                    var r = await sb.rpc('scholarship_find_learner', { p_q: q }); ul.textContent = '';
                    if (r.error) return OFL.notice(document.getElementById('sch-msg'), OFL.friendlyError(r.error), 'error');
                    if (!(r.data || []).length) return ul.appendChild(el('li', { class: 'ac-muted', text: 'No learner matches. They need an Academy account first.' }));
                    r.data.forEach(function (p) { ul.appendChild(el('li', {}, el('button', { type: 'button', onclick: function () { schSetWho(p); } },
                        el('strong', { text: p.full_name || '(no name)' }), el('span', { class: 'ac-muted', text: p.email + ' · ' + p.courses + (p.courses == 1 ? ' course' : ' courses') })))); });
                }, 250);
            });
            document.getElementById('sch-form').addEventListener('submit', async function (e) {
                e.preventDefault(); var m = document.getElementById('sch-msg');
                if (!schPick) return OFL.notice(m, 'Choose the learner first.', 'error');
                var end = schEnd(); if (end === undefined) return OFL.notice(m, 'Choose the end date.', 'error');
                var reason = document.getElementById('sch-reason').value.trim();
                if (reason.length < 5) { document.getElementById('sch-reason').focus(); return OFL.notice(m, 'Say why this scholarship is being given.', 'error'); }
                var btnS = document.getElementById('sch-save'); btnS.disabled = true;
                var res = await sb.rpc('scholarship_grant', { p_user: schPick.id, p_course: document.getElementById('sch-course').value,
                    p_days: /^\d+$/.test(schDur) ? +schDur : null, p_until: schDur === 'date' ? document.getElementById('sch-until').value : null, p_reason: reason });
                btnS.disabled = false;
                if (res.error) return OFL.notice(m, OFL.friendlyError(res.error), 'error');
                schDlg.close(); OFL.notice(msg, 'Scholarship given to ' + (schPick.full_name || schPick.email) + '.', 'success'); loadScholarships();
            });

            // ---- Courses and lessons
            var cmData = [], cmEdit = null;
            var STATUS = { live: ['Live', 'live'], coming_soon: ['Coming soon', 'soon'], hidden: ['Hidden', 'hidden'] };
            async function loadContent() {
                if (!can('manage_content')) return;
                var r = await sb.rpc('content_courses');
                if (r.error) return OFL.notice(msg, OFL.friendlyError(r.error), 'error');
                cmData = r.data || []; drawContent();
                if (lessonsCourse) drawLessons(lessonsCourse);
            }
            function drawContent() {
                var box = document.getElementById('cm-list'); box.textContent = '';
                cmData.forEach(function (c) {
                    var rel = c.lessons.filter(function (l) { return l.released; }).length;
                    box.appendChild(el('article', { class: 'cm-card' },
                        el('div', { class: 'cm-card__main' },
                            el('div', { class: 'cm-card__top' }, el('span', { class: 'cm-status cm-status--' + STATUS[c.status][1], text: STATUS[c.status][0] }),
                                el('span', { class: 'ac-muted ac-small', text: (c.access === 'paid' ? 'Paid' : 'Free') + (c.level ? ' · ' + c.level : '') })),
                            el('h3', { text: c.title }), c.description ? el('p', { class: 'ac-muted', text: c.description }) : null,
                            el('p', { class: 'cm-card__facts num' }, rel + ' of ' + c.lessons.length + ' lessons released · ' + c.enrolled + ' enrolled')),
                        el('div', { class: 'cm-card__actions' },
                            el('button', { class: 'ac-btn ac-btn--secondary ac-btn--sm', type: 'button', text: 'Edit', onclick: function () { openCourse(c); } }),
                            el('button', { class: 'ac-btn ac-btn--secondary ac-btn--sm', type: 'button', text: 'Lessons', onclick: function () { openLessons(c.slug); } }),
                            el('a', { class: 'ac-btn ac-btn--ghost ac-btn--sm', href: c.slug === 'data-science' ? '/academy/courses/data-science/' : '/academy/courses/?c=' + c.slug, target: '_blank', rel: 'noopener', text: 'View page' }))));
                });
            }
            var courseDlg = document.getElementById('course-dlg');
            function slugify(t) { return t.toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 40); }
            function openCourse(c) {
                cmEdit = c || null; document.getElementById('course-msg').textContent = '';
                var f = document.getElementById('course-form'); f.reset();
                document.getElementById('course-title').textContent = c ? 'Edit ' + c.title : 'Add a course';
                document.getElementById('cf-title').value = c ? c.title : '';
                var sl = document.getElementById('cf-slug'); sl.value = c ? c.slug : ''; sl.readOnly = !!c; sl.dataset.auto = c ? '' : '1';
                document.getElementById('cf-desc').value = c && c.description || '';
                document.getElementById('cf-level').value = c && c.level || 'Beginner';
                var acc = document.getElementById('cf-access'); acc.value = c ? c.access : 'free'; acc.disabled = !can('manage_learners');
                f.querySelector('input[name="cf-status"][value="' + (c ? c.status : 'hidden') + '"]').checked = true;
                courseDlg.showModal(); document.getElementById('cf-title').focus();
            }
            document.getElementById('cf-title').addEventListener('input', function (e) { var sl = document.getElementById('cf-slug'); if (sl.dataset.auto) sl.value = slugify(e.target.value); });
            document.getElementById('cf-slug').addEventListener('input', function (e) { e.target.dataset.auto = ''; });
            document.getElementById('course-new').addEventListener('click', function () { openCourse(null); });
            document.getElementById('course-form').addEventListener('submit', async function (e) {
                e.preventDefault(); var m = document.getElementById('course-msg');
                var status = (e.target.querySelector('input[name="cf-status"]:checked') || {}).value;
                if (cmEdit && cmEdit.status === 'live' && status !== 'live' && cmEdit.enrolled > 0 &&
                    !window.confirm(cmEdit.enrolled + ' learners are enrolled. Taking the course off live stops them opening lessons until it’s live again. Continue?')) return;
                if (status === 'live' && !(cmEdit && cmEdit.lessons.some(function (l) { return l.released; })) &&
                    !window.confirm('This course has no released lessons yet. Learners will be able to enrol but won’t find anything to open. Make it live anyway?')) return;
                var res = await sb.rpc('content_save_course', { p_slug: document.getElementById('cf-slug').value, p_title: document.getElementById('cf-title').value,
                    p_description: document.getElementById('cf-desc').value, p_level: document.getElementById('cf-level').value,
                    p_access: document.getElementById('cf-access').value, p_status: status, p_sort: null });
                if (res.error) return OFL.notice(m, OFL.friendlyError(res.error), 'error');
                courseDlg.close(); OFL.notice(msg, (cmEdit ? 'Saved ' : 'Added ') + document.getElementById('cf-title').value.trim() + '.', 'success');
                await loadCourses(); loadContent();
                if (!cmEdit) openLessons(res.data.slug);
            });
            var lessonsDlg = document.getElementById('lessons-dlg'), lessonsCourse = null;
            function openLessons(slug) { lessonsCourse = slug; document.getElementById('lessons-msg').textContent = ''; drawLessons(slug); if (!lessonsDlg.open) lessonsDlg.showModal(); }
            lessonsDlg.addEventListener('close', function () { lessonsCourse = null; });
            function drawLessons(slug) {
                var c = cmData.filter(function (x) { return x.slug === slug; })[0]; if (!c) return;
                document.getElementById('lessons-title').textContent = 'Lessons: ' + c.title;
                var t = document.getElementById('lessons-table'); t.textContent = '';
                var hr = el('tr'); ['#', 'Title', 'Released', c.access === 'paid' ? 'Free preview' : '', 'Content', ''].forEach(function (h) { hr.appendChild(el('th', { text: h })); });
                t.appendChild(el('thead', {}, hr)); var tb = el('tbody'); t.appendChild(tb);
                function row(l, isNew) {
                    var title = el('input', { value: l.title || '', 'aria-label': 'Lesson title', placeholder: isNew ? 'Title of the new lesson' : '', maxlength: '120' });
                    var rel = el('input', { type: 'checkbox', 'aria-label': 'Released' }); rel.checked = !!l.released;
                    var fp = el('input', { type: 'checkbox', 'aria-label': 'Free preview' }); fp.checked = !!l.free_preview;
                    var content = isNew ? el('span', { class: 'ac-muted', text: '—' }) : el('span', { class: 'cm-content' + (l.has_content ? ' is-ok' : ''), text: l.has_content ? 'Notes' + (l.has_video ? ' + video' : '') : 'Not uploaded' });
                    var save = el('button', { class: 'ac-btn ac-btn--' + (isNew ? 'primary' : 'secondary') + ' ac-btn--sm', type: 'button', text: isNew ? 'Add lesson' : 'Save' });
                    function dirty() { save.classList.toggle('is-dirty', title.value !== (l.title || '') || rel.checked !== !!l.released || fp.checked !== !!l.free_preview); }
                    [title, rel, fp].forEach(function (i) { i.addEventListener('input', dirty); i.addEventListener('change', dirty); });
                    save.addEventListener('click', async function () {
                        if (!title.value.trim()) { title.focus(); return OFL.notice(document.getElementById('lessons-msg'), 'Give the lesson a title.', 'error'); }
                        if (rel.checked && !l.released && !l.has_content && !window.confirm('Lesson ' + (l.n || 'new') + ' has no notes or quiz uploaded yet. Learners will see “not available” if they open it. Release anyway?')) return;
                        save.disabled = true;
                        var res = await sb.rpc('content_save_lesson', { p_course: slug, p_n: isNew ? null : l.n, p_title: title.value, p_released: rel.checked, p_free_preview: fp.checked });
                        save.disabled = false;
                        if (res.error) return OFL.notice(document.getElementById('lessons-msg'), OFL.friendlyError(res.error), 'error');
                        OFL.notice(document.getElementById('lessons-msg'), isNew ? 'Lesson ' + res.data.n + ' added.' : 'Lesson ' + l.n + ' saved.', 'success');
                        loadContent();
                    });
                    tb.appendChild(el('tr', { class: isNew ? 'cm-new' : (l.released ? '' : 'is-hidden') }, el('td', { class: 'num', text: isNew ? '+' : String(l.n) }), el('td', {}, title), el('td', {}, rel),
                        el('td', {}, c.access === 'paid' ? fp : null), el('td', {}, content), el('td', {}, save)));
                }
                c.lessons.forEach(function (l) { row(l, false); }); row({}, true);
            }

            // ---- Cohort applications
            var cohorts = [], cohortId = null, apps = [], appFilter = 'all';
            var APP_STATUS = { shortlisted: ['In trial', 'go'], completed: ['Confirmed', 'done'], waitlisted: ['Waitlist', 'wait'], missed: ['Missed deadline', 'end'], rejected: ['Rejected', 'end'], withdrawn: ['Withdrawn', 'end'] };
            var A_LABEL = { hours: { '1-2': '1–2 h', '3-5': '3–5 h', '6-10': '6–10 h', '10+': '10+ h' },
                device: { laptop: 'Own laptop/desktop', shared: 'Shared computer', phone: 'Phone only' }, internet: { reliable: 'Reliable', sometimes: 'Sometimes unreliable', poor: 'Often poor' },
                career_goal: { first_job: 'First data job', switch: 'Switch careers', upskill: 'Upskill in current job', freelance: 'Freelance', business: 'Own business', study: 'Further study' },
                can_afford: { '0': 'Nothing right now', lt5k: 'Under ₦5,000', '5-15k': '₦5,000–15,000', '15-30k': '₦15,000–30,000', '30k+': 'Over ₦30,000' } };
            var PART = { hours: ['Weekly study time', 30], motivation: ['Why they want to join', 30], problem: ['Problem to solve', 25], about_you: ['About-you profile', 15] };
            var PROOF = { pending: ['To check', 'wait'], ok: ['Eligible', 'done'], fix: ['Asked to fix', 'end'] };
            var KINDS = [['tiktok', 'TikTok: @_drhola'], ['linkedin-founder', 'LinkedIn: founder'], ['linkedin-page', 'LinkedIn: Open Fraud Labs']];
            async function loadCohorts(keep) {
                if (!can('manage_applications')) return;
                cohorts = (await sb.from('cohorts').select('*').order('created_at', { ascending: false })).data || [];
                var sel = document.getElementById('app-cohort'); sel.textContent = '';
                cohorts.forEach(function (c) { sel.appendChild(el('option', { value: c.id, text: c.title })); });
                sel.appendChild(el('option', { value: 'new', text: '+ New cohort' }));
                cohortId = keep && cohorts.some(function (c) { return c.id == keep; }) ? keep : (cohorts[0] || {}).id;
                if (cohortId) sel.value = cohortId;
                loadApps();
            }
            function cur() { return cohorts.filter(function (c) { return c.id == cohortId; })[0]; }
            document.getElementById('app-cohort').addEventListener('change', function (e) {
                if (e.target.value === 'new') { e.target.value = cohortId || ''; return openCohort(null); }
                cohortId = e.target.value; loadApps();
            });
            async function loadApps() {
                var c = cur(); if (!c) { document.getElementById('app-line').textContent = 'No cohorts yet. Choose “+ New cohort” to create one.'; return; }
                var r = await sb.rpc('applications_admin', { p_cohort: c.id });
                if (r.error) return OFL.notice(msg, OFL.friendlyError(r.error), 'error');
                apps = r.data || [];
                var course = allCourses.filter(function (x) { return x.slug === c.course_slug; })[0] || {};
                var gate = (await sb.from('courses').select('enrol_mode').eq('slug', c.course_slug).maybeSingle()).data || {};
                c._require = gate.enrol_mode === 'application';
                var line = document.getElementById('app-line'); line.textContent = '';
                line.append(el('span', { class: 'cm-status cm-status--' + (c.status === 'open' ? 'live' : c.status === 'draft' ? 'hidden' : 'soon'), text: c.status === 'open' ? 'Open' : c.status === 'draft' ? 'Draft' : 'Closed' }), ' ',
                    (course.title || c.course_slug) + ' · ' + c.capacity + ' places · trial: Lesson ' + c.trial_lesson + ' in ' + c.trial_days + ' days · minimum score ' + c.min_score + ' · ' +
                    (c.mode === 'rolling' ? 'automatic shortlisting' : 'shortlist when applications close') + (c.closes_at ? ' · closes ' + dt(c.closes_at) : '') +
                    ' · enrolment ' + (c._require ? 'by application only' : 'open to everyone') + ' · ',
                    el('a', { href: '/academy/apply/?c=' + c.slug, target: '_blank', rel: 'noopener', text: 'Apply page' }));
                var n = function (s) { return apps.filter(function (a) { return a.status === s; }).length; };
                var trialsEnded = n('completed') + n('missed');
                var k = document.getElementById('app-kpis'); k.textContent = '';
                [['Applied', apps.length], ['To check', apps.filter(function (a) { return a.status === 'waitlisted' && a.proof_status === 'pending'; }).length], ['Offered', n('shortlisted')], ['Confirmed', n('completed')], ['Missed deadline', n('missed')], ['Waitlist', n('waitlisted')],
                 ['Places left', Math.max(0, c.capacity - n('shortlisted') - n('completed'))], ['Offers accepted', trialsEnded ? Math.round(100 * n('completed') / trialsEnded) + '%' : '—']]
                    .forEach(function (x) { k.appendChild(el('div', { class: 'ac-kpi' }, el('strong', { class: 'num', text: String(x[1]) }), el('span', { text: x[0] }))); });
                drawApps();
            }
            function drawApps() {
                var q = document.getElementById('app-q').value.trim().toLowerCase(), t = document.getElementById('app-table'); t.textContent = '';
                var hr = el('tr'); ['', 'Applicant', 'Score', 'Study time', 'Eligibility', 'Status', 'Lessons passed', 'Applied', ''].forEach(function (h) { hr.appendChild(el('th', { text: h })); });
                t.appendChild(el('thead', {}, hr)); var tb = el('tbody'); t.appendChild(tb);
                var wl = 0, list = apps.filter(function (a) { return (appFilter === 'all' || (appFilter === 'check' ? a.status === 'waitlisted' && a.proof_status === 'pending' : a.status === appFilter)) && (!q || ((a.full_name || '') + ' ' + a.email).toLowerCase().indexOf(q) >= 0); });
                if (!list.length) tb.appendChild(el('tr', {}, el('td', { colspan: '9', class: 'ac-muted', text: apps.length ? 'No applications match.' : 'No applications yet. Share the apply link to get started.' })));
                list.forEach(function (a) {
                    var st = APP_STATUS[a.status] || [a.status, 'end'], c = cur();
                    var stCell = el('td', {}, el('span', { class: 'app-st app-st--' + st[1], text: st[0] }));
                    if (a.status === 'shortlisted' && a.deadline_at) { var left = new Date(a.deadline_at) - Date.now(); stCell.appendChild(el('small', { class: left < 2 * 864e5 ? 'app-warn' : 'ac-muted', text: left > 0 ? Math.floor(left / 864e5) + 'd ' + Math.floor(left % 864e5 / 36e5) + 'h left' : 'deadline passed' })); }
                    if (a.status === 'waitlisted') stCell.appendChild(el('small', { class: 'ac-muted', text: a.score >= c.min_score ? '#' + (++wl) + ' in line' : 'below minimum score' }));
                    var ans = a.answers || {}, pr = PROOF[a.proof_status] || ['—', 'end'], follows = el('td', { class: 'app-follows' }, el('span', { class: 'app-st app-st--' + pr[1], text: pr[0] }));
                    if (ans.tiktok_handle) follows.appendChild(el('a', { href: 'https://www.tiktok.com/' + encodeURIComponent(ans.tiktok_handle), target: '_blank', rel: 'noopener noreferrer', text: ans.tiktok_handle }));
                    if (a.status === 'shortlisted') stCell.appendChild(el('small', { class: 'app-steps', text: (c.require_post ? (a.post_url ? 'Post \u2713 ' : 'Post \u2717 ') : '') + (c.require_whatsapp ? (a.whatsapp_joined_at ? 'WhatsApp \u2713 ' : 'WhatsApp \u2717 ') : '') + (a.trial_done ? 'Lesson \u2713' : 'Lesson \u2717') }));
                    var actions = el('td', { class: 'app-actions' }, el('button', { class: 'ac-btn ac-btn--secondary ac-btn--sm', type: 'button', text: 'View', onclick: function () { openApp(a); } }));
                    if (a.status === 'waitlisted' && a.proof_status === 'pending') actions.appendChild(el('button', { class: 'ac-btn ac-btn--primary ac-btn--sm', type: 'button', text: 'Check', onclick: function () { openApp(a); } }));
                    tb.appendChild(el('tr', {}, el('td', { class: 'num ac-muted', text: String(list.indexOf(a) + 1) }),
                        el('td', {}, el('div', { text: a.full_name || '(no name)' }), el('small', { class: 'ac-muted', text: a.email })),
                        el('td', {}, el('b', { class: 'app-score num', text: String(a.score) })),
                        el('td', { text: A_LABEL.hours[ans.hours] || '—' }), follows, stCell,
                        el('td', { class: 'num', text: a.lessons_done ? String(a.lessons_done) : '0' }),
                        el('td', { text: dOnly(a.applied_at) }), actions));
                });
            }
            document.querySelectorAll('#app-tabs .ofl-tab').forEach(function (b) { b.addEventListener('click', function () {
                document.querySelectorAll('#app-tabs .ofl-tab').forEach(function (o) { o.classList.toggle('is-active', o === b); }); appFilter = b.dataset.f; drawApps(); }); });
            document.getElementById('app-q').addEventListener('input', drawApps);
            async function decide(a, action, note) {
                var text = { shortlist: 'Offer ' + (a.full_name || a.email) + ' a place now' + (a.proof_status !== 'ok' ? ', even though their screenshots aren\u2019t confirmed' : '') + '? They\u2019ll be enrolled, told on the site and by email, and get ' + cur().trial_days + ' days to complete the offer steps.',
                    waitlist: 'Move ' + (a.full_name || a.email) + ' back to the waitlist? If they’re in a trial, they lose course access.', reject: 'Reject ' + (a.full_name || a.email) + '? They’ll see “not offered a place” on the apply page. No email is sent.' }[action];
                if (text && !window.confirm(text)) return false;
                var res = await sb.rpc('application_decide', { p_id: a.id, p_action: action, p_note: note == null ? null : note });
                if (res.error) { OFL.notice(document.getElementById('app-dlg').open ? document.getElementById('app-dlg-msg') : msg, OFL.friendlyError(res.error), 'error'); return false; }
                OFL.notice(msg, action === 'note' ? 'Note saved.' : 'Done: ' + action + ' for ' + (a.full_name || a.email) + '.', 'success');
                appDlg.close(); loadApps(); return true;
            }
            var appDlg = document.getElementById('app-dlg');
            async function review(a, ok, note) {
                var r = await sb.rpc('application_proof_review', { p_id: a.id, p_ok: ok, p_note: note || null });
                if (r.error) return OFL.notice(document.getElementById('app-dlg-msg'), OFL.friendlyError(r.error), 'error');
                appDlg.close();
                OFL.notice(msg, ok ? ((a.full_name || a.email) + ' is eligible' + (r.data.shortlisted ? '. Offers sent automatically: ' + r.data.shortlisted + '.' : ' and on the waitlist.')) : 'Asked ' + (a.full_name || a.email) + ' to fix their screenshots. They\u2019ve been told on the site and by email.', 'success');
                loadApps();
            }
            function openApp(a) {
                var b = document.getElementById('app-dlg-body'); b.textContent = ''; document.getElementById('app-dlg-msg').textContent = '';
                document.getElementById('app-dlg-title').textContent = (a.full_name || '(no name)') + ' · ' + (APP_STATUS[a.status] || [a.status])[0];
                var ans = a.answers || {}, bgr = a.background || {};
                b.appendChild(el('p', { class: 'ac-muted', text: a.email + ' · applied ' + dt(a.applied_at) + (a.deadline_at ? ' · trial deadline ' + dt(a.deadline_at) : '') + (a.completed_at ? ' · trial completed ' + dt(a.completed_at) : '') }));
                var c0 = cur();
                if (c0.require_proofs) {
                    var pf = el('div', { class: 'app-card app-proofcard' }, el('h3', {}, 'Eligibility screenshots ', el('span', { class: 'app-st app-st--' + (PROOF[a.proof_status] || ['', 'end'])[1], text: (PROOF[a.proof_status] || ['—'])[0] })));
                    var shots = el('div', { class: 'app-shots' }); pf.appendChild(shots);
                    KINDS.forEach(function (k) {
                        var fig = el('figure', {}, el('div', { class: 'app-shot__img', text: 'Loading\u2026' }), el('figcaption', { text: k[1] })); shots.appendChild(fig);
                        sb.storage.from('application-proofs').createSignedUrl(a.user_id + '/' + a.cohort_slug + '/' + k[0] + '.jpg', 600).then(function (r) {
                            var box = fig.firstChild; box.textContent = '';
                            if (r.error || !r.data) { box.textContent = 'Not uploaded'; return; }
                            box.appendChild(el('a', { href: r.data.signedUrl, target: '_blank', rel: 'noopener' }, el('img', { src: r.data.signedUrl, alt: k[1] + ' screenshot' })));
                        });
                    });
                    pf.appendChild(el('p', { class: 'ac-muted ac-small' }, 'Check each shows the right profile and \u201cFollowing\u201d. Click to enlarge. ',
                        ans.tiktok_handle ? el('a', { href: 'https://www.tiktok.com/' + encodeURIComponent(ans.tiktok_handle), target: '_blank', rel: 'noopener noreferrer', text: 'Their TikTok' }) : null, ans.tiktok_handle ? ' \u00b7 ' : null,
                        ans.linkedin_url ? el('a', { href: ans.linkedin_url, target: '_blank', rel: 'noopener noreferrer', text: 'Their LinkedIn' }) : null));
                    if (a.proof_note) pf.appendChild(el('p', { class: 'app-warn', text: 'Asked to fix: ' + a.proof_note }));
                    if (a.status === 'waitlisted' || a.status === 'rejected') pf.appendChild(el('div', { class: 'ofl-actions' },
                        a.proof_status !== 'ok' ? el('button', { class: 'ac-btn ac-btn--primary ac-btn--sm', type: 'button', text: 'Screenshots OK', onclick: function () { review(a, true); } }) : null,
                        el('button', { class: 'ac-btn ac-btn--secondary ac-btn--sm', type: 'button', text: 'Ask to fix', onclick: function () {
                            var why = window.prompt('What should they fix? They\u2019ll see this message, e.g. \u201cThe LinkedIn page screenshot doesn\u2019t show Following.\u201d', ''); if (why) review(a, false, why); } })));
                    b.appendChild(pf);
                }
                if (a.status === 'shortlisted' || a.status === 'completed' || a.status === 'missed') {
                    var os = el('div', { class: 'app-card' }, el('h3', { text: 'Offer steps' }));
                    if (c0.require_post) os.appendChild(el('div', { class: 'app-kv' }, el('span', { text: 'LinkedIn post' }), a.post_url ? el('a', { href: a.post_url, target: '_blank', rel: 'noopener noreferrer', text: 'Open post' }) : el('b', { text: 'Not yet' })));
                    if (c0.require_whatsapp) os.appendChild(el('div', { class: 'app-kv' }, el('span', { text: 'WhatsApp group' }), el('b', { text: a.whatsapp_joined_at ? 'Says they joined ' + dOnly(a.whatsapp_joined_at) : 'Not yet' })));
                    os.appendChild(el('div', { class: 'app-kv' }, el('span', { text: 'Lesson ' + c0.trial_lesson }), el('b', { text: a.trial_done ? 'Passed' : 'Not yet' })));
                    b.appendChild(os);
                }
                var grid = el('div', { class: 'app-detail' });
                var sc = el('div', { class: 'app-card' }, el('h3', {}, 'Score ', el('b', { class: 'num', text: a.score + ' / 100' })));
                Object.keys(PART).forEach(function (k) { var got = (a.score_detail || {})[k] || 0; sc.appendChild(el('div', { class: 'app-part' }, el('span', { text: PART[k][0] }), el('span', { class: 'num', text: got + ' / ' + PART[k][1] }), el('i', { style: 'width:' + Math.round(100 * got / PART[k][1]) + '%' }))); });
                sc.appendChild(el('p', { class: 'ac-muted ac-small', text: 'Ranks eligible applicants. Longer answers score higher, so read the text too.' }));
                var info = el('div', { class: 'app-card' }, el('h3', { text: 'Answers' }));
                function row(label, v) { if (v) info.appendChild(el('div', { class: 'app-kv' }, el('span', { text: label }), typeof v === 'string' ? el('b', { text: v }) : v)); }
                row('Study time', A_LABEL.hours[ans.hours]); row('Learns on', A_LABEL.device[ans.device]); row('Internet', A_LABEL.internet[ans.internet]);
                row('Wants to', A_LABEL.career_goal[ans.career_goal]); row('Could pay after launch', A_LABEL.can_afford[ans.can_afford]);
                row('TikTok', ans.tiktok_handle ? el('a', { href: 'https://www.tiktok.com/' + encodeURIComponent(ans.tiktok_handle), target: '_blank', rel: 'noopener noreferrer', text: ans.tiktok_handle + (ans.follows_tiktok ? ' (says they follow)' : '') }) : (ans.follows_tiktok ? 'Says they follow' : 'No'));
                row('Follows founder', ans.follows_founder ? 'Says yes' : 'No'); row('Follows page', ans.follows_linkedin ? 'Says yes' : 'No');
                row('LinkedIn profile', ans.linkedin_url ? el('a', { href: ans.linkedin_url, target: '_blank', rel: 'noopener noreferrer', text: 'Open profile' }) : null);
                if (a.cv_path) { var cvA = el('a', { href: '#', text: 'Open CV' }); cvA.addEventListener('click', async function (e) { e.preventDefault(); var r = await sb.storage.from('cvs').createSignedUrl(a.cv_path, 600); if (r.data) window.open(r.data.signedUrl, '_blank', 'noopener'); }); row('CV', cvA); }
                row('Consent: funder reports', ans.consent_reports ? 'Yes, without name' : 'No'); row('Consent: job alerts', ans.consent_jobs ? 'Yes' : 'No');
                grid.append(sc, info); b.appendChild(grid);
                b.appendChild(el('div', { class: 'app-card' }, el('h3', { text: 'Why they want to join' }), el('p', { class: 'app-text', text: ans.motivation || '—' }),
                    el('h3', { text: 'A problem they’d like to solve with data' }), el('p', { class: 'app-text', text: ans.problem || '—' })));
                if (bgr.completed_at) b.appendChild(el('p', { class: 'ac-muted ac-small', text: 'About you: ' + [bgr.city, bgr.country, bgr.employment, bgr.education, 'Python: ' + bgr.python_level, 'data: ' + bgr.data_level].filter(Boolean).join(' · ') + '. (Shown for context; never part of the score.)' }));
                var note = el('textarea', { rows: '2', maxlength: '1000', placeholder: 'Private staff note (optional)', class: 'app-note' }); note.value = a.staff_note || '';
                b.appendChild(el('label', { class: 'app-note-wrap' }, el('span', { text: 'Staff note' }), note));
                var acts = el('div', { class: 'ofl-actions' });
                if (a.status !== 'shortlisted' && a.status !== 'completed') acts.appendChild(el('button', { class: 'ac-btn ac-btn--primary ac-btn--sm', type: 'button', text: 'Offer a place', onclick: function () { decide(a, 'shortlist', note.value || null); } }));
                if (a.status === 'shortlisted' || a.status === 'missed' || a.status === 'rejected') acts.appendChild(el('button', { class: 'ac-btn ac-btn--secondary ac-btn--sm', type: 'button', text: 'Move to waitlist', onclick: function () { decide(a, 'waitlist', note.value || null); } }));
                if (a.status !== 'rejected' && a.status !== 'completed') acts.appendChild(el('button', { class: 'ac-btn ac-btn--danger ac-btn--sm', type: 'button', text: 'Reject', onclick: function () { decide(a, 'reject', note.value || null); } }));
                acts.appendChild(el('button', { class: 'ac-btn ac-btn--ghost ac-btn--sm', type: 'button', text: 'Save note', onclick: function () { decide(a, 'note', note.value); } }));
                b.appendChild(acts);
                appDlg.showModal();
            }
            document.getElementById('app-fill').addEventListener('click', async function () {
                var c = cur(); if (!c) return;
                if (!window.confirm('Shortlist the highest-scoring waitlisted applicants (at or above the minimum score) into any open places now?')) return;
                var r = await sb.rpc('cohort_fill_now', { p_cohort: c.id });
                if (r.error) return OFL.notice(msg, OFL.friendlyError(r.error), 'error');
                OFL.notice(msg, r.data.shortlisted ? r.data.shortlisted + ' applicant' + (r.data.shortlisted === 1 ? '' : 's') + ' shortlisted and notified.' : 'No one to shortlist: either no places are open or nobody waiting meets the minimum score.', 'success'); loadApps();
            });
            document.getElementById('app-csv').addEventListener('click', function () {
                var c = cur(); if (!c) return;
                var keys = ['full_name', 'email', 'status', 'proof_status', 'score', 'applied_at', 'shortlisted_at', 'deadline_at', 'completed_at', 'post_url', 'whatsapp_joined_at', 'trial_done', 'lessons_done'];
                var ak = ['hours', 'device', 'internet', 'career_goal', 'can_afford', 'follows_tiktok', 'tiktok_handle', 'follows_founder', 'follows_linkedin', 'linkedin_url', 'motivation', 'problem', 'consent_reports', 'consent_jobs'];
                var bk = ['country', 'city', 'gender', 'age_range', 'employment', 'industry', 'education', 'python_level', 'data_level', 'goal', 'heard_from'];
                var pk = Object.keys(PART);
                function esc(v) { v = v == null ? '' : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
                var lines = [keys.concat(ak, pk.map(function (k) { return 'score_' + k; }), bk, ['staff_note']).join(',')];
                apps.forEach(function (a) { lines.push(keys.map(function (k) { return esc(a[k]); }).concat(ak.map(function (k) { return esc((a.answers || {})[k]); }), pk.map(function (k) { return esc((a.score_detail || {})[k]); }), bk.map(function (k) { return esc((a.background || {})[k]); }), [esc(a.staff_note)]).join(',')); });
                var x = el('a', { href: URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/csv' })), download: c.slug + '-applications-' + new Date().toISOString().slice(0, 10) + '.csv' });
                document.body.appendChild(x); x.click(); x.remove();
            });
            var cohortDlg = document.getElementById('cohort-dlg'), coEdit = null;
            function localInput(v) { if (!v) return ''; var d = new Date(new Date(v).getTime() + 3600e3); return d.toISOString().slice(0, 16); }
            function openCohort(c) {
                coEdit = c; document.getElementById('cohort-msg').textContent = '';
                document.getElementById('cohort-dlg-title').textContent = c ? 'Settings: ' + c.title : 'New cohort';
                document.getElementById('co-title').value = c ? c.title : '';
                var sl = document.getElementById('co-slug'); sl.value = c ? c.slug : ''; sl.readOnly = !!c;
                var cs = document.getElementById('co-course'); cs.textContent = '';
                allCourses.forEach(function (x) { cs.appendChild(el('option', { value: x.slug, text: x.title })); }); cs.value = c ? c.course_slug : 'data-science';
                document.querySelector('input[name="co-status"][value="' + (c ? c.status : 'draft') + '"]').checked = true;
                document.querySelector('input[name="co-mode"][value="' + (c ? c.mode : 'rolling') + '"]').checked = true;
                document.getElementById('co-capacity').value = c ? c.capacity : 40; document.getElementById('co-min').value = c ? c.min_score : 40;
                document.getElementById('co-lesson').value = c ? c.trial_lesson : 1; document.getElementById('co-days').value = c ? c.trial_days : 7;
                document.getElementById('co-closes').value = c ? localInput(c.closes_at) : '';
                document.getElementById('co-require').checked = c ? !!c._require : true;
                document.getElementById('co-c-laptop').checked = c ? c.require_laptop !== false : true; document.getElementById('co-c-proofs').checked = c ? c.require_proofs !== false : true;
                document.getElementById('co-c-post').checked = c ? c.require_post !== false : true; document.getElementById('co-c-wa').checked = c ? c.require_whatsapp !== false : true;
                document.getElementById('co-founder').value = c && c.founder_linkedin_url || ''; document.getElementById('co-wa').value = c && c.whatsapp_url || '';
                document.getElementById('co-del-proofs').hidden = !c;
                cohortDlg.showModal();
            }
            document.getElementById('app-settings').addEventListener('click', function () { openCohort(cur() || null); });
            document.getElementById('co-del-proofs').addEventListener('click', async function () {
                var c = cur(); if (!c) return;
                if (!window.confirm('Delete every eligibility screenshot for ' + c.title + '? Do this only after you\u2019ve finished checking. Applicants keep their status.')) return;
                var paths = []; apps.forEach(function (a) { KINDS.forEach(function (k) { paths.push(a.user_id + '/' + c.slug + '/' + k[0] + '.jpg'); }); });
                var r = paths.length ? await sb.storage.from('application-proofs').remove(paths) : { data: [] };
                if (r.error) return OFL.notice(document.getElementById('cohort-msg'), OFL.friendlyError(r.error), 'error');
                OFL.notice(document.getElementById('cohort-msg'), 'Deleted ' + (r.data || []).length + ' screenshots.', 'success');
            });
            document.getElementById('cohort-form').addEventListener('submit', async function (e) {
                e.preventDefault(); var m = document.getElementById('cohort-msg');
                var title = document.getElementById('co-title').value.trim(), slug = document.getElementById('co-slug').value.trim().toLowerCase();
                if (!title || !/^[a-z0-9][a-z0-9-]{2,39}$/.test(slug)) return OFL.notice(m, 'Give the cohort a name and a link name of 3–40 lowercase letters, numbers or dashes.', 'error');
                var closes = document.getElementById('co-closes').value;
                var status = document.querySelector('input[name="co-status"]:checked').value, require = document.getElementById('co-require').checked;
                if (status === 'open' && require && !(coEdit && coEdit.status === 'open') && !window.confirm('Open applications now? New learners will need to apply and be shortlisted before they can enrol in this course.')) return;
                var res = await sb.rpc('cohort_save', { p_slug: slug, p_title: title, p_course: document.getElementById('co-course').value, p_status: status,
                    p_capacity: +document.getElementById('co-capacity').value, p_trial_lesson: +document.getElementById('co-lesson').value, p_trial_days: +document.getElementById('co-days').value,
                    p_min_score: +document.getElementById('co-min').value, p_mode: document.querySelector('input[name="co-mode"]:checked').value,
                    p_closes_at: closes ? closes + ':00+01:00' : null, p_require_application: require });
                if (res.error) return OFL.notice(m, OFL.friendlyError(res.error), 'error');
                var r2 = await sb.rpc('cohort_save_conditions', { p_cohort: res.data.id, p_founder_linkedin: document.getElementById('co-founder').value, p_whatsapp: document.getElementById('co-wa').value,
                    p_laptop: document.getElementById('co-c-laptop').checked, p_proofs: document.getElementById('co-c-proofs').checked, p_post: document.getElementById('co-c-post').checked, p_whatsapp_required: document.getElementById('co-c-wa').checked });
                if (r2.error) return OFL.notice(m, OFL.friendlyError(r2.error), 'error');
                cohortDlg.close(); OFL.notice(msg, 'Cohort settings saved.', 'success'); loadCohorts(res.data.id);
            });

            // ---- Internship / job applications
            var roles = [], roleId = null, roleApps = [];
            var RSTAGE = { new: ['New', 'wait'], shortlisted: ['Shortlisted', 'go'], interview: ['Interview', 'go'], offered: ['Offered', 'done'], hired: ['Hired', 'done'], not_progressed: ['Not progressed', 'end'], withdrawn: ['Withdrawn', 'end'] };
            var RL = { stage: { student: 'Student', graduate: 'Recent graduate', corps: 'NYSC corps member', other: 'Other' }, hours: { '3-5': '3–5 h', '6-8': '6–8 h', '9-12': '9–12 h', '12+': '12+ h' } };
            async function loadRoles(keep) {
                if (!can('manage_applications')) return;
                roles = (await sb.from('roles').select('*').order('sort')).data || [];
                var sel = document.getElementById('role-pick'); sel.textContent = '';
                roles.forEach(function (r) { sel.appendChild(el('option', { value: r.id, text: r.title })); });
                roleId = keep || (roles[0] || {}).id; if (roleId) sel.value = roleId;
                loadRoleApps();
            }
            function curRole() { return roles.filter(function (r) { return r.id == roleId; })[0]; }
            document.getElementById('role-pick').addEventListener('change', function (e) { roleId = e.target.value; loadRoleApps(); });
            document.getElementById('role-status').addEventListener('change', async function (e) {
                var r = curRole(); if (!r) return;
                var labels = { open: 'Open this role for rolling applications?', filled: 'Mark this role as filled? It stays on the careers page as Filled and stops taking applications.', closed: 'Close this role? It stops taking applications.', draft: 'Hide this role from the careers page?' };
                if (!window.confirm(labels[e.target.value])) { e.target.value = r.status; return; }
                var res = await sb.rpc('role_set_status', { p_role: r.id, p_status: e.target.value });
                if (res.error) { e.target.value = r.status; return OFL.notice(msg, OFL.friendlyError(res.error), 'error'); }
                OFL.notice(msg, 'Role updated.', 'success'); loadRoles(r.id);
            });
            async function loadRoleApps() {
                var r = curRole(); if (!r) { document.getElementById('role-line').textContent = 'No roles yet.'; return; }
                document.getElementById('role-status').value = r.status;
                var res = await sb.rpc('role_applications_admin', { p_role: r.id });
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                roleApps = res.data || [];
                var n = function (st) { return roleApps.filter(function (a) { return a.status === st; }).length; };
                var line = document.getElementById('role-line'); line.textContent = '';
                line.append(roleApps.length + ' applications · ' + n('new') + ' new · ' + (n('shortlisted') + n('interview')) + ' in progress · ' + n('hired') + ' hired · ', el('a', { href: '/careers/role/?r=' + r.slug, target: '_blank', rel: 'noopener', text: 'Role page' }));
                var t = document.getElementById('role-table'); t.textContent = '';
                var hr = el('tr'); ['Applicant', 'Now', 'Location', 'Hours', 'Stage', 'Applied', ''].forEach(function (h) { hr.appendChild(el('th', { text: h })); });
                t.appendChild(el('thead', {}, hr)); var tb = el('tbody'); t.appendChild(tb);
                if (!roleApps.length) tb.appendChild(el('tr', {}, el('td', { colspan: '7', class: 'ac-muted', text: 'No applications yet.' })));
                roleApps.forEach(function (a) {
                    var an = a.answers || {}, st = RSTAGE[a.status] || [a.status, 'end'];
                    tb.appendChild(el('tr', {}, el('td', {}, el('div', { text: a.full_name || '(no name)' }), el('small', { class: 'ac-muted', text: a.email })),
                        el('td', {}, el('div', { text: RL.stage[an.stage] || '—' }), el('small', { class: 'ac-muted', text: an.institution || '' })),
                        el('td', {}, el('div', { text: [an.city, an.country].filter(Boolean).join(', ') || '—' }), el('small', { class: 'ac-muted', text: an.timezone || '' })),
                        el('td', { text: RL.hours[an.hours] || '—' }), el('td', {}, el('span', { class: 'app-st app-st--' + st[1], text: st[0] })),
                        el('td', { text: dOnly(a.applied_at) }), el('td', {}, el('button', { class: 'ac-btn ac-btn--' + (a.status === 'new' ? 'primary' : 'secondary') + ' ac-btn--sm', type: 'button', text: a.status === 'new' ? 'Review' : 'View', onclick: function () { openRoleApp(a); } }))));
                });
            }
            var roleDlg = document.getElementById('role-dlg');
            function openRoleApp(a) {
                var r = curRole(), an = a.answers || {}, b = document.getElementById('role-dlg-body'); b.textContent = ''; document.getElementById('role-dlg-msg').textContent = '';
                document.getElementById('role-dlg-title').textContent = (a.full_name || '(no name)') + ' · ' + (RSTAGE[a.status] || [a.status])[0];
                b.appendChild(el('p', { class: 'ac-muted', text: a.email + ' · ' + r.title + ' · applied ' + dt(a.applied_at) }));
                var info = el('div', { class: 'app-card' }, el('h3', { text: 'Details' }));
                function row(label, v) { if (v) info.appendChild(el('div', { class: 'app-kv' }, el('span', { text: label }), typeof v === 'string' ? el('b', { text: v }) : v)); }
                var cv = el('a', { href: '#', class: 'ac-btn ac-btn--primary ac-btn--sm', text: 'Open CV' });
                cv.addEventListener('click', async function (e) { e.preventDefault(); var s2 = await sb.storage.from('cvs').createSignedUrl(a.cv_path, 600); if (s2.error) return OFL.notice(document.getElementById('role-dlg-msg'), 'CV not found.', 'error'); window.open(s2.data.signedUrl, '_blank', 'noopener'); });
                row('CV', a.cv_path ? cv : null); row('Now', RL.stage[an.stage]); row('Institution', an.institution); row('Course', an.course); row('Graduation', an.grad_year);
                row('Location', [an.city, an.country].filter(Boolean).join(', ')); row('Time zone', an.timezone); row('Hours a week', RL.hours[an.hours]); row('Can start', an.start_date);
                row('WhatsApp', an.phone ? el('a', { href: 'https://wa.me/' + an.phone.replace(/\D/g, ''), target: '_blank', rel: 'noopener noreferrer', text: an.phone }) : null);
                row('LinkedIn', an.linkedin_url ? el('a', { href: an.linkedin_url, target: '_blank', rel: 'noopener noreferrer', text: 'Open profile' }) : null);
                row('Portfolio', an.portfolio_url ? el('a', { href: an.portfolio_url, target: '_blank', rel: 'noopener noreferrer', text: 'Open link' }) : null);
                row('Keep for future roles', an.consent_keep ? 'Yes' : 'No');
                b.appendChild(info);
                b.appendChild(el('div', { class: 'app-card' }, el('h3', { text: 'Why this role' }), el('p', { class: 'app-text', text: an.why || '—' }), el('h3', { text: 'Relevant experience' }), el('p', { class: 'app-text', text: an.experience || '—' })));
                var note = el('textarea', { rows: '2', maxlength: '2000', placeholder: 'Private staff note (interview notes, impressions)', class: 'app-note' }); note.value = a.staff_note || '';
                b.appendChild(el('label', { class: 'app-note-wrap' }, el('span', { text: 'Staff note' }), note));
                var msgBox = el('textarea', { rows: '2', maxlength: '1000', placeholder: 'Optional personal message to the applicant (replaces the standard text in their email)', class: 'app-note' });
                b.appendChild(el('label', { class: 'app-note-wrap' }, el('span', { text: 'Message with the next step (optional)' }), msgBox));
                var acts = el('div', { class: 'ofl-actions' });
                [['shortlisted', 'Shortlist', 'primary'], ['interview', 'Invite to interview', 'secondary'], ['offered', 'Make offer', 'secondary'], ['hired', 'Mark hired', 'secondary'], ['not_progressed', 'Not progressing', 'danger']].forEach(function (x) {
                    if (a.status === x[0]) return;
                    acts.appendChild(el('button', { class: 'ac-btn ac-btn--' + x[2] + ' ac-btn--sm', type: 'button', text: x[1], onclick: function () { roleDecide(a, x[0], note.value || null, msgBox.value || null); } }));
                });
                acts.appendChild(el('button', { class: 'ac-btn ac-btn--ghost ac-btn--sm', type: 'button', text: 'Save note', onclick: function () { roleDecide(a, 'note', note.value, null); } }));
                b.appendChild(acts);
                if (a.status === 'hired') b.appendChild(el('p', { class: 'ac-muted ac-small', text: 'To give them dashboard access, the owner sets their staff role in Staff and roles (HR for the coordinator; the communications intern usually needs no dashboard access).' }));
                roleDlg.showModal();
            }
            async function roleDecide(a, status, note, message) {
                var names = { shortlisted: 'shortlist', interview: 'invite to interview', offered: 'make an offer to', hired: 'mark as hired', not_progressed: 'tell they are not progressing' };
                if (status !== 'note' && !window.confirm('This will ' + names[status] + ' ' + (a.full_name || a.email) + ' and email them. Continue?')) return;
                var res = await sb.rpc('role_application_decide', { p_id: a.id, p_status: status, p_note: note, p_message: message });
                if (res.error) return OFL.notice(document.getElementById('role-dlg-msg'), OFL.friendlyError(res.error), 'error');
                roleDlg.close(); OFL.notice(msg, status === 'note' ? 'Note saved.' : 'Updated and emailed.', 'success'); loadRoleApps();
            }
            document.getElementById('role-csv').addEventListener('click', function () {
                var r = curRole(); if (!r) return;
                var keys = ['stage', 'institution', 'course', 'grad_year', 'city', 'country', 'timezone', 'phone', 'linkedin_url', 'portfolio_url', 'hours', 'start_date', 'why', 'experience', 'consent_keep'];
                function esc(v) { v = v == null ? '' : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
                var lines = [['full_name', 'email', 'status', 'applied_at'].concat(keys, ['staff_note']).join(',')];
                roleApps.forEach(function (a) { lines.push([a.full_name, a.email, a.status, a.applied_at].map(esc).concat(keys.map(function (k) { return esc((a.answers || {})[k]); }), [esc(a.staff_note)]).join(',')); });
                var x = el('a', { href: URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/csv' })), download: r.slug + '-applications-' + new Date().toISOString().slice(0, 10) + '.csv' });
                document.body.appendChild(x); x.click(); x.remove();
            });
            await loadCourses(); loadScholarships(); loadContent(); loadCohorts(); loadRoles();
            var staffRoles = {};
            if (can('view_staff')) (async function staff() {
                var r = await sb.rpc('admin_staff'), t = document.getElementById('staff-table');
                t.textContent = '';
                t.appendChild(el('thead', {}, el('tr', {}, el('th', { text: 'Name' }), el('th', { text: 'Email' }), el('th', { text: 'Role' }))));
                var tb = el('tbody'); t.appendChild(tb);
                (r.data || []).forEach(function (x) {
                    staffRoles[x.user_id] = x.staff_role;
                    var cell = el('td');
                    if (can('manage_roles') && x.staff_role !== 'owner') {
                        var sel = el('select', { 'aria-label': 'Role for ' + (x.full_name || x.email) });
                        ROLE_OPTS.concat([['none', 'Remove role']]).forEach(function (o) { sel.appendChild(el('option', { value: o[0], text: o[1], selected: o[0] === x.staff_role ? 'selected' : null })); });
                        sel.addEventListener('change', async function () {
                            if (!window.confirm((sel.value === 'none' ? 'Remove the staff role from ' : 'Change the role of ') + (x.full_name || x.email) + (sel.value === 'none' ? '?' : ' to ' + ROLE_NAME[sel.value] + '?'))) { sel.value = x.staff_role; return; }
                            var res = await sb.rpc('admin_manage_user', { p_user: x.user_id, p_action: 'set_role', p_value: sel.value });
                            if (res.error) { sel.value = x.staff_role; return OFL.notice(msg, OFL.friendlyError(res.error), 'error'); }
                            OFL.notice(msg, 'Role updated for ' + (x.full_name || x.email) + '.', 'success'); staff();
                        });
                        cell.appendChild(sel);
                    } else cell.appendChild(el('span', { class: 'ac-rolebadge' + (x.staff_role === 'owner' ? ' is-owner' : ''), text: ROLE_NAME[x.staff_role] || x.staff_role }));
                    tb.appendChild(el('tr', {}, el('td', { text: x.full_name || '—' }), el('td', { text: x.email }), cell));
                });
            })();
            if (can('view_finance')) (async function finance() {
                var f = (await sb.rpc('admin_finance_summary')).data || {};
                function money(minor, cur) { try { return new Intl.NumberFormat(cur === 'NGN' ? 'en-NG' : undefined, { style: 'currency', currency: cur, currencyDisplay: 'narrowSymbol', maximumFractionDigits: 0 }).format(minor / 100); } catch (e) { return cur + ' ' + minor / 100; } }
                function sum(o) { var k = Object.keys(o || {}); return k.length ? k.map(function (c) { return money(o[c], c); }).join(' + ') : '—'; }
                var fk = document.getElementById('fin-kpis'); fk.textContent = '';
                [['Revenue, all time', sum(f.revenue)], ['Revenue, last 30 days', sum(f.revenue_30d)], ['Successful payments', f.payments || 0], ['Failed or abandoned', f.failed || 0], ['Active paid passes', f.active_passes || 0], ['Free access (complimentary)', f.complimentary || 0]]
                    .forEach(function (x) { fk.appendChild(el('div', { class: 'ac-kpi' }, el('strong', { class: 'num', text: String(x[1]) }), el('span', { text: x[0] }))); });
                var pt = document.getElementById('payments-table'); pt.textContent = '';
                function head(t, cols) { var tr = el('tr'); cols.forEach(function (h) { tr.appendChild(el('th', { text: h })); }); t.appendChild(el('thead', {}, tr)); }
                head(pt, ['Date', 'Learner', 'Plan', 'Amount', 'Status', 'Reference']);
                var pb = el('tbody'); pt.appendChild(pb);
                if (!(f.recent || []).length) pb.appendChild(el('tr', {}, el('td', { colspan: '6', class: 'ac-muted', text: 'No payments yet.' })));
                (f.recent || []).forEach(function (x) { pb.appendChild(el('tr', {}, el('td', { text: dt(x.paid_at || x.created_at) }), el('td', { text: x.email }), el('td', { text: x.plan_id }), el('td', { class: 'num', text: money(x.amount_minor, x.currency) }), el('td', { text: x.status }), el('td', { text: x.reference }))); });
                async function drawPlans() {
                    var plans = (await sb.from('plans').select('*').order('sort')).data || [];
                    var t = document.getElementById('plans-table'); t.textContent = '';
                    head(t, ['Plan', 'Months', 'Price', 'Currency', 'Shown to learners', '']);
                    var tb = el('tbody'); t.appendChild(tb);
                    function row(p, isNew) {
                        var name = el('input', { value: p.name || '', 'aria-label': 'Plan name', placeholder: 'e.g. 3 months' });
                        var months = el('input', { type: 'number', min: '1', value: p.months || 1, 'aria-label': 'Months', style: 'width:5rem' });
                        var price = el('input', { type: 'number', min: '1', step: '1', value: p.amount_minor ? p.amount_minor / 100 : '', 'aria-label': 'Price', style: 'width:8rem', placeholder: 'e.g. 15000' });
                        var cur = el('select', { 'aria-label': 'Currency' }); ['NGN', 'USD'].forEach(function (c) { cur.appendChild(el('option', { value: c, text: c, selected: c === (p.currency || 'NGN') ? 'selected' : null })); });
                        var active = el('input', { type: 'checkbox', 'aria-label': 'Shown to learners' }); active.checked = !!p.active;
                        var save = el('button', { class: 'ac-btn ac-btn--' + (isNew ? 'primary' : 'secondary') + ' ac-btn--sm', type: 'button', text: isNew ? 'Add plan' : 'Save' });
                        if (!can('manage_plans')) [name, months, price, cur, active].forEach(function (i) { i.disabled = true; }), save.hidden = true;
                        save.addEventListener('click', async function () {
                            var amount = Math.round(parseFloat(price.value) * 100);
                            if (!name.value.trim() || !(amount > 0) || !(+months.value > 0)) return OFL.notice(msg, 'Give the plan a name, a number of months and a price.', 'error');
                            var data = { name: name.value.trim(), months: +months.value, amount_minor: amount, currency: cur.value, active: active.checked };
                            var res = isNew ? await sb.from('plans').insert(Object.assign({ id: 'p' + Date.now().toString(36), sort: plans.length + 1 }, data)) : await sb.from('plans').update(data).eq('id', p.id);
                            if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                            OFL.notice(msg, isNew ? 'Plan added.' : 'Plan saved.', 'success'); drawPlans();
                        });
                        tb.appendChild(el('tr', {}, el('td', {}, name), el('td', {}, months), el('td', {}, price), el('td', {}, cur), el('td', {}, active), el('td', {}, save)));
                    }
                    plans.forEach(function (p) { row(p, false); });
                    if (can('manage_plans')) row({}, true);
                }
                drawPlans();
            })();
            function dt(v) { if (!v) return '—'; var d = new Date(v); return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) + ' ' + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }); }
            function pct(v) { return v == null ? '—' : Math.round(v * 100) + '%'; }

            var ov = await sb.rpc('admin_overview');
            if (ov.error) return OFL.notice(msg, OFL.friendlyError(ov.error), 'error');
            var o = ov.data, k = document.getElementById('kpis');
            [['Registered', o.registered, o.confirmed + ' confirmed email'], ['Signed terms', o.signed_terms, ''], ['Enrolled', o.enrolled, 'opened a lesson'],
             ['Active, last 7 days', o.active_7d, o.logins_7d + ' log-ins'], ['Lessons passed', o.lessons_passed, ''], ['Quiz attempts', o.quiz_attempts, pct(o.quiz_pass_rate) + ' passed'],
             ['Practice exercises solved', o.practice_solved, ''], ['Capstones waiting', o.capstones_waiting, ''], ['Certificates', o.certificates, '']]
              .forEach(function (x) { k.appendChild(el('div', { class: 'ac-kpi' }, el('strong', { class: 'num', text: String(x[1] == null ? 0 : x[1]) }), el('span', { text: x[0] }), x[2] ? el('small', { text: x[2] }) : null)); });

            var lr = await sb.rpc('admin_learners'), rows = lr.data || [];
            var cr = await sb.rpc('admin_learner_certs'), certs = {};
            (cr.data || []).forEach(function (c) { if (!c.revoked_at && !certs[c.user_id]) certs[c.user_id] = c; });
            var fl = await sb.rpc('admin_learner_flags'), flags = {};
            (fl.data || []).forEach(function (x) { flags[x.user_id] = x; });
            rows.forEach(function (r) { var x = flags[r.user_id] || {}; r.is_admin = x.is_admin; r.suspended_at = x.suspended_at; r.unlock_all = x.unlock_all; r.access_until = x.access_until; });
            var cols = [['full_name', 'Name'], ['email', 'Email'], ['registered_at', 'Registered'], ['last_sign_in_at', 'Last log-in'], ['enrolled_courses', 'Enrolled'],
                        ['lessons_passed', 'Lessons passed'], ['avg_best_score', 'Avg quiz score'], ['quiz_attempts', 'Quiz attempts'], ['practice_solved', 'Practice solved'],
                        ['last_activity_at', 'Last activity'], ['certificates', 'Certificates'], ['status', 'Status']];
            function cell(r, c) {
                var v = r[c];
                if (/_at$/.test(c)) return dt(v);
                if (c === 'avg_best_score') return pct(v);
                if (c === 'status') {
                    var tags = [];
                    if (r.suspended_at) tags.push('Suspended'); if (staffRoles[r.user_id]) tags.push(ROLE_NAME[staffRoles[r.user_id]]); else if (r.is_admin) tags.push('Admin');
                    if (r.unlock_all) tags.push('All lessons unlocked'); if (r.access_until) tags.push('Free access (' + r.access_until + ')');
                    return tags.join(' · ') || 'Active';
                }
                if (c === 'full_name') return (v || '(no name)') + (r.terms_signed ? '' : ' · terms not signed') + (r.email_confirmed ? '' : ' · email not confirmed');
                return v == null || v === '' ? '—' : String(v);
            }
            function drawLearners() {
                var q = document.getElementById('q').value.trim().toLowerCase(), t = document.getElementById('learners'); t.textContent = '';
                var hr = el('tr', {}, el('th', { text: '' })); cols.forEach(function (c) { hr.appendChild(el('th', { text: c[1] })); }); t.appendChild(el('thead', {}, hr));
                var tb = el('tbody');
                rows.filter(function (r) { return !q || ((r.full_name || '') + ' ' + (r.email || '')).toLowerCase().indexOf(q) >= 0; })
                    .forEach(function (r) {
                        var tr = el('tr', { class: r.suspended_at ? 'is-suspended' : '' });
                        tr.appendChild(el('td', {}, can('manage_learners') ? el('button', { class: 'ac-btn ac-btn--secondary ac-btn--sm', type: 'button', text: 'Manage', onclick: function () { manage(r); } }) : null));
                        cols.forEach(function (c) { tr.appendChild(el('td', { text: cell(r, c[0]) })); }); tb.appendChild(tr);
                    });
                if (!tb.children.length) tb.appendChild(el('tr', {}, el('td', { colspan: String(cols.length), text: 'No learners match.' })));
                t.appendChild(tb);
            }
            document.getElementById('q').addEventListener('input', drawLearners); drawLearners();

            // ---- Manage one learner: suspend, special rights, admin role
            var dlg = document.getElementById('manage');
            function manage(r) {
                var body = document.getElementById('manage-body'); body.textContent = '';
                document.getElementById('manage-title').textContent = (r.full_name || r.email);
                body.appendChild(el('p', { class: 'ac-muted', text: r.email + ' · registered ' + dt(r.registered_at) + ' · ' + r.lessons_passed + ' lessons passed' }));
                var self = r.user_id === user.id, targetRole = staffRoles[r.user_id] || (r.is_admin ? 'admin' : null);
                if (targetRole === 'owner' || (targetRole && !can('manage_roles'))) {
                    body.appendChild(el('p', { class: 'ofl-notice', text: targetRole === 'owner' ? 'This is the owner\u2019s account. It can\u2019t be changed from the admin page.' : 'This person is staff (' + ROLE_NAME[targetRole] + '). Only the owner can change staff accounts.' }));
                    document.getElementById('manage-msg').textContent = ''; dlg.showModal(); return;
                }
                function act(action, value, confirmText) {
                    return async function () {
                        if (confirmText && !window.confirm(confirmText)) return;
                        var res = await sb.rpc('admin_manage_user', { p_user: r.user_id, p_action: action, p_value: value == null ? null : String(value) });
                        if (res.error) return OFL.notice(document.getElementById('manage-msg'), OFL.friendlyError(res.error), 'error');
                        dlg.close(); OFL.notice(msg, 'Done: ' + action.replace('_', ' ') + ' for ' + (r.full_name || r.email) + '.', 'success');
                        var f2 = await sb.rpc('admin_learner_flags'); (f2.data || []).forEach(function (x) { flags[x.user_id] = x; });
                        var c2 = await sb.rpc('admin_learner_certs'); certs = {}; (c2.data || []).forEach(function (c) { if (!c.revoked_at && !certs[c.user_id]) certs[c.user_id] = c; });
                        rows.forEach(function (q) { var x = flags[q.user_id] || {}; q.is_admin = x.is_admin; q.suspended_at = x.suspended_at; q.unlock_all = x.unlock_all; q.access_until = x.access_until; });
                        drawLearners();
                    };
                }
                function group(title, text, buttons) {
                    var g = el('div', { class: 'ac-manage__group' }, el('h3', { text: title }), el('p', { class: 'ac-muted', text: text }));
                    var row = el('div', { class: 'ofl-actions' }); buttons.forEach(function (b) { if (b) row.appendChild(b); }); g.appendChild(row); body.appendChild(g);
                }
                function btn(label, kind, fn, disabled) { return el('button', { class: 'ac-btn ac-btn--' + kind + ' ac-btn--sm', type: 'button', text: label, onclick: fn, disabled: disabled ? 'disabled' : null }); }
                group('Account', r.suspended_at ? 'Suspended on ' + dt(r.suspended_at) + '. They can’t log in, open lessons or take quizzes.' : 'Suspending blocks log-in and all learning. Their records are kept, and you can reactivate them at any time.',
                    [r.suspended_at ? btn('Reactivate', 'primary', act('reactivate')) : btn('Suspend account', 'danger', function () { var why = window.prompt('Reason for suspending (kept in the admin log):', ''); if (why === null) return; act('suspend', why)(); }, self)]);
                group('Unlock all lessons', r.unlock_all ? 'This learner can open any released lesson in any order.' : 'Let this learner open released lessons in any order, without passing the previous lesson first. Video, notes and quiz rules still apply.',
                    [r.unlock_all ? btn('Lock again', 'secondary', act('relock')) : btn('Unlock all lessons', 'primary', act('unlock_all'))]);
                var mine = schRows.filter(function (x) { return x.user_id === r.user_id && x.status === 'active'; });
                group('Scholarship', mine.length ? 'Active: ' + mine.map(function (x) { return x.course_title + ' ' + schUntil(x); }).join('; ') + '.' : 'Full access to a course, or every course, for a set time, with the reason recorded.',
                    [can('manage_scholarships') ? btn(mine.length ? 'Give another scholarship' : 'Give a scholarship', 'primary', function () { dlg.close(); openScholarship({ id: r.user_id, email: r.email, full_name: r.full_name }); }) : null]);
                if (r.access_until) group('Older free access', 'Given before scholarships existed: free access ' + (r.access_until === 'no end date' ? 'with no end date' : 'until ' + r.access_until) + '.', [btn('Remove free access', 'secondary', act('revoke_access'))]);
                if (can('manage_roles') && !self) {
                    var roleSel = el('select', { 'aria-label': 'Staff role' });
                    [['none', 'No staff role']].concat(ROLE_OPTS).forEach(function (o) { roleSel.appendChild(el('option', { value: o[0], text: o[1], selected: o[0] === (targetRole || 'none') ? 'selected' : null })); });
                    group('Staff role', targetRole ? 'Currently ' + ROLE_NAME[targetRole] + '.' : 'Give this person a staff role only if they work with Open Fraud Labs. See \u201cWhat each role can do\u201d in Staff and roles.',
                        [roleSel, btn('Save role', 'secondary', function () { act('set_role', roleSel.value, roleSel.value === 'none' ? 'Remove the staff role from ' + r.email + '?' : 'Make ' + r.email + ' ' + ROLE_NAME[roleSel.value] + '?')(); })]);
                }
                var cert = certs[r.user_id];
                group('Certificate', cert ? 'Valid certificate ' + cert.id + (cert.award_type === 'awarded' ? ' (awarded by an admin)' : ' (earned by completing the course)') + ', issued ' + dt(cert.issued_at) + '.'
                        : 'Learners normally earn the certificate by passing every lesson and an approved capstone. You can award one directly for exceptional cases, such as a live cohort. The public verification page will say it was awarded by Open Fraud Labs, not earned through the course.',
                    cert ? [el('a', { class: 'ac-btn ac-btn--secondary ac-btn--sm', href: '/verify/?id=' + cert.id, target: '_blank', rel: 'noopener', text: 'View certificate' }),
                            btn('Revoke certificate', 'danger', function () { var why = window.prompt('Reason for revoking (kept in the admin log):', ''); if (!why) return; act('revoke_certificate', why)(); })]
                         : [btn('Award certificate', 'primary', function () { var why = window.prompt('Reason for awarding this certificate (kept in the admin log), e.g. "Completed the live cohort":', ''); if (!why) return; act('issue_certificate', why)(); })]);
                group('Delete account', 'Not switched on yet. Permanent deletion would also remove their progress, quiz history and any certificates, so for now suspend the account instead. It can be enabled later.', []);
                document.getElementById('manage-msg').textContent = '';
                dlg.showModal();
            }
            document.getElementById('manage-close').addEventListener('click', function () { dlg.close(); });
            document.getElementById('csv').addEventListener('click', function () {
                function esc(v) { v = v == null ? '' : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
                var keys = ['full_name', 'email', 'registered_at', 'email_confirmed', 'terms_signed', 'last_sign_in_at', 'enrolled_courses', 'lessons_passed', 'avg_best_score', 'quiz_attempts', 'practice_solved', 'last_activity_at', 'certificates'];
                var csv = [keys.join(',')].concat(rows.map(function (r) { return keys.map(function (c) { return esc(r[c]); }).join(','); })).join('\n');
                var a = el('a', { href: URL.createObjectURL(new Blob([csv], { type: 'text/csv' })), download: 'academy-learners-' + new Date().toISOString().slice(0, 10) + '.csv' });
                document.body.appendChild(a); a.click(); a.remove();
            });

            var fr = await sb.rpc('admin_lesson_funnel', { p_course: 'data-science' }), f = document.getElementById('funnel');
            var fh = ['Lesson', 'Opened', 'Watched video', 'Read notes', 'Took quiz', 'Passed', 'Avg best score', 'Solved practice'];
            var hr2 = el('tr'); fh.forEach(function (h) { hr2.appendChild(el('th', { text: h })); }); f.appendChild(el('thead', {}, hr2));
            var fb = el('tbody');
            (fr.data || []).filter(function (r) { return r.released; }).forEach(function (r) {
                var tr = el('tr'); [r.lesson_n + '. ' + r.title, r.opened, r.video_done, r.notes_done, r.quiz_attempted, r.passed, pct(r.avg_best_score), r.practice_solvers]
                    .forEach(function (v) { tr.appendChild(el('td', { text: String(v) })); }); fb.appendChild(tr);
            });
            f.appendChild(fb);

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
                var names = {}; rows.forEach(function (x) { names[x.user_id] = x.full_name || x.email; });
                box.textContent = '';
                if (!r.data.length) return box.appendChild(el('p', { class: 'ac-muted', text: 'Nothing here.' }));
                r.data.forEach(function (s) {
                    var fbx = el('textarea', { rows: 3, placeholder: 'Feedback for the learner (required when requesting changes)' }); fbx.value = s.feedback || '';
                    async function review(newStatus) {
                        if (newStatus === 'changes_requested' && !fbx.value.trim()) return OFL.notice(msg, 'Please add feedback explaining what to change.', 'error');
                        var u = await sb.from('capstone_submissions').update({ status: newStatus, feedback: fbx.value.trim(), reviewed_at: new Date().toISOString() }).eq('id', s.id);
                        if (u.error) return OFL.notice(msg, OFL.friendlyError(u.error), 'error');
                        OFL.notice(msg, 'Saved: ' + (names[s.user_id] || 'learner') + ' → ' + newStatus.replace('_', ' '), 'success'); load();
                    }
                    box.appendChild(el('article', { class: 'ofl-card card ofl-sub' },
                        el('h3', { text: (names[s.user_id] || 'Learner') + ' · ' + ({ capstone: 'Capstone', 'project-credit': 'Project 1: Credit risk', 'project-clinic': 'Project 2: Clinic no-shows', 'project-rent': 'Project 3: City rents' }[s.assignment] || s.assignment) }),
                        s.peer_score != null ? el('p', { class: 'ac-muted', text: 'Peer score (median): ' + Math.round(100 * s.peer_score) + '%' }) : null,
                        el('p', { class: 'ac-muted', text: 'Submitted ' + OFL.formatDate(s.submitted_at) + (s.reviewed_at ? ' · reviewed ' + OFL.formatDate(s.reviewed_at) : '') }),
                        el('p', {}, el('a', { href: s.repo_url, target: '_blank', rel: 'noopener noreferrer', text: s.repo_url })),
                        el('p', { class: 'ofl-writeup', text: s.writeup }), fbx,
                        el('div', { class: 'ofl-actions' },
                            el('button', { class: 'ac-btn ac-btn--primary', type: 'button', text: 'Approve', onclick: function () { review('approved'); } }),
                            el('button', { class: 'ac-btn ac-btn--secondary', type: 'button', text: 'Request changes', onclick: function () { review('changes_requested'); } }))));
                });
            }
            load();
        })();"""

# ============================================================== Peer review (projects and capstone)
review_main = """        <div class="ac-wrap">
            <div class="ac-dash-head">
                <h1 id="rv-title">Peer review</h1>
                <p class="ac-muted">Your project is graded by three other learners using the rubric below, and you review three projects in return. The middle of the three scores counts, so one harsh or generous reviewer can't decide your grade. Open Fraud Labs can step in and review any project.</p>
                <div id="msg"></div>
            </div>
            <div class="ac-two">
                <div>
                    <div id="mine"></div>
                    <form id="sub-form" class="ac-panel ofl-form" hidden>
                        <h2>Share your project</h2>
                        <p class="ac-muted">Push your notebook and a README to a public GitHub repository, then share it here. Your reviewers see the link and your summary, not your name.</p>
                        <label>GitHub repository link <input name="repo_url" type="url" required placeholder="https://github.com/you/your-project"></label>
                        <label>Summary <small>(the problem, what you did and what you found)</small>
                            <textarea name="writeup" rows="6" required minlength="50" maxlength="5000"></textarea></label>
                        <div class="ofl-sign">
                            <p class="ofl-sign__title">Declaration of own work</p>
                            <p class="ofl-muted">I confirm this project is my own work and that I have credited any code, data or ideas from others. Sign by typing your registered full name: <strong id="sub-name"></strong></p>
                            <label>Signature (your full name) <input name="signature" required maxlength="120" autocomplete="off" class="ofl-sign__input"></label>
                            <p class="ofl-sign__status" aria-live="polite"></p>
                        </div>
                        <button class="ac-btn ac-btn--primary" type="submit">Sign &amp; share for peer review</button>
                    </form>
                    <div id="review"></div>
                    <div id="feedback"></div>
                </div>
                <div>
                    <div class="ac-aside-card"><h3>The rubric</h3><ol class="rv-rubric" id="rubric"></ol><p class="ac-small ac-muted" id="rv-pass"></p></div>
                    <div class="ac-aside-card"><h3>Reviewing well</h3><p>Be specific and kind: say what works, then the one or two changes that would most improve the project. Score what's in the repository, not what you think the author meant. Reviews are anonymous and each one is due within 48 hours.</p></div>
                </div>
            </div>
        </div>"""
review_script = r"""        (async function () {
            var sb = OFL.sb, el = OFL.el, msg = document.getElementById('msg');
            var course = OFL.qs('course') || 'data-science', key = OFL.qs('a') || 'capstone';
            var user = await OFL.requireUser(location.pathname + location.search); if (!user) return;
            var prof = (await sb.from('profiles').select('full_name, terms_accepted_at').eq('id', user.id).maybeSingle()).data || {};
            if (!prof.terms_accepted_at) { location.href = '/account/?next=' + encodeURIComponent(location.pathname + location.search); return; }
            var LABELS = ['Missing', 'Weak', 'Partly there', 'Good', 'Excellent'];
            function pct(x) { return Math.round(100 * x) + '%'; }
            async function load() {
                var r = await sb.rpc('peer_status', { p_course: course, p_assignment: key });
                if (r.error || !r.data || !r.data.title) return OFL.notice(msg, r.error ? OFL.friendlyError(r.error) : 'Unknown project.', 'error');
                var st = r.data;
                document.getElementById('rv-title').textContent = st.title;
                document.title = st.title + ': peer review | Open Fraud Labs Academy';
                var rub = document.getElementById('rubric'); rub.textContent = '';
                (st.rubric || []).forEach(function (it) { rub.appendChild(el('li', {}, el('strong', { text: it.title + ' (0–' + it.max + ')' }), el('p', { class: 'ac-small', text: it.guide }))); });
                document.getElementById('rv-pass').textContent = 'Pass mark: ' + pct(st.pass_ratio) + ' of the total.';
                renderMine(st); renderFeedback(st);
                var rv = document.getElementById('review'); rv.textContent = '';
                if (st.submission || key === 'capstone') rv.appendChild(reviewCard(st));
            }
            function renderMine(st) {
                var box = document.getElementById('mine'); box.textContent = '';
                var form = document.getElementById('sub-form'), s = st.submission;
                if (!s) {
                    if (key === 'capstone') {
                        box.appendChild(el('div', { class: 'ac-panel' }, el('h2', { text: 'Submit your capstone first' }),
                            el('p', { text: 'Read the brief and submit your capstone, then come back here to review other learners.' }),
                            el('a', { class: 'ac-btn ac-btn--primary', href: '/academy/capstone/?course=' + course, text: 'Go to the capstone' })));
                    } else form.hidden = false;
                    return;
                }
                var label = { submitted: 'Waiting for peer reviews', approved: 'Approved', changes_requested: 'Changes requested' }[s.status];
                var card = el('div', { class: 'ac-panel' }, el('h2', { text: 'Your project' }),
                    el('p', {}, el('span', { class: 'ofl-badge ofl-badge--' + s.status, text: label }), ' shared ' + OFL.formatDate(s.submitted_at)),
                    el('p', {}, el('a', { href: s.repo_url, target: '_blank', rel: 'noopener noreferrer', text: s.repo_url })));
                if (s.status === 'submitted') {
                    card.appendChild(el('p', { text: 'Reviews received: ' + s.received + ' of ' + st.needed + '. Reviews you have given: ' + Math.min(st.given, st.needed) + ' of ' + st.needed + '.' }));
                    if (st.given < st.needed) card.appendChild(el('p', { class: 'ac-muted', text: 'Your grade is released once you have reviewed ' + st.needed + ' projects (or there are none left for you to review) and three learners have reviewed yours.' }));
                }
                if (s.feedback) card.appendChild(el('blockquote', { class: 'ofl-feedback-box', text: s.feedback }));
                box.appendChild(card);
                form.hidden = s.status !== 'changes_requested' || key === 'capstone';
                if (!form.hidden) form.querySelector('h2').textContent = 'Share your improved project';
            }
            function renderFeedback(st) {
                var box = document.getElementById('feedback'); box.textContent = '';
                if (!st.reviews || !st.reviews.length) return;
                var wrap = el('div', { class: 'ac-panel' }, el('h2', { text: 'What your reviewers said' }));
                st.reviews.forEach(function (rv, i) {
                    var ul = el('ul', { class: 'rv-scores' });
                    (st.rubric || []).forEach(function (it) { ul.appendChild(el('li', {}, el('span', { text: it.title }), el('b', { text: (rv.scores || {})[it.key] + ' / ' + it.max }))); });
                    wrap.appendChild(el('div', { class: 'rv-feedback' }, el('h3', { text: 'Reviewer ' + (i + 1) + ' · ' + rv.total + ' / ' + rv.max }), ul, el('p', { text: rv.comment })));
                });
                box.appendChild(wrap);
            }
            function reviewCard(st) {
                var card = el('div', { class: 'ac-panel' }, el('h2', { text: 'Review a peer' }));
                var body = el('div');
                var btn = el('button', { class: 'ac-btn ac-btn--primary', type: 'button', text: st.open_review ? 'Continue your review' : 'Get a project to review' });
                btn.addEventListener('click', async function () {
                    btn.disabled = true; msg.textContent = '';
                    var r = await sb.rpc('peer_next_review', { p_course: course, p_assignment: key });
                    btn.disabled = false;
                    if (r.error) return OFL.notice(msg, OFL.friendlyError(r.error), 'error');
                    if (r.data.none) { body.textContent = ''; body.appendChild(el('p', { class: 'ac-muted', text: 'There are no projects waiting for review right now. Check back later; your own grade isn’t held up by this.' })); return load(); }
                    btn.hidden = true; body.textContent = ''; body.appendChild(reviewForm(r.data));
                });
                card.appendChild(el('p', { class: 'ac-muted', text: 'You have reviewed ' + st.given + ' project' + (st.given === 1 ? '' : 's') + ' for ' + st.title + '.' }));
                card.appendChild(btn); card.appendChild(body);
                return card;
            }
            function reviewForm(d) {
                var f = el('form', { class: 'ofl-form rv-form' });
                f.appendChild(el('p', {}, el('strong', { text: 'Project: ' }), el('a', { href: d.repo_url, target: '_blank', rel: 'noopener noreferrer', text: d.repo_url })));
                f.appendChild(el('blockquote', { class: 'ofl-feedback-box', text: d.writeup }));
                f.appendChild(el('p', { class: 'ac-small ac-muted', text: 'Due ' + OFL.formatDate(d.due) + '. Open the repository, read the README and notebook, then score each part.' }));
                (d.rubric || []).forEach(function (it) {
                    var fs = el('fieldset', { class: 'rv-item' }, el('legend', { text: it.title }), el('p', { class: 'ac-small ac-muted', text: it.guide }));
                    var row = el('div', { class: 'rv-choices' });
                    for (var v = 0; v <= it.max; v++) {
                        row.appendChild(el('label', { class: 'rv-choice' }, el('input', { type: 'radio', name: it.key, value: String(v), required: 'required' }),
                            el('span', { text: v + (it.max === 4 ? ' · ' + LABELS[v] : '') })));
                    }
                    fs.appendChild(row); f.appendChild(fs);
                });
                var ta = el('textarea', { name: 'comment', rows: '5', required: 'required', minlength: '40', maxlength: '4000', placeholder: 'What works well, and the one or two changes that would most improve this project.' });
                f.appendChild(el('label', {}, 'Your feedback', ta));
                var sub = el('button', { class: 'ac-btn ac-btn--primary', type: 'submit', text: 'Submit review' });
                f.appendChild(sub);
                f.addEventListener('submit', async function (e) {
                    e.preventDefault(); sub.disabled = true;
                    var scores = {}; (d.rubric || []).forEach(function (it) { var c = f.querySelector('input[name="' + it.key + '"]:checked'); if (c) scores[it.key] = +c.value; });
                    var r = await sb.rpc('peer_submit_review', { p_review: d.review_id, p_scores: scores, p_comment: ta.value });
                    sub.disabled = false;
                    if (r.error) return OFL.notice(msg, OFL.friendlyError(r.error), 'error');
                    OFL.notice(msg, 'Thank you! Your review has been sent anonymously.', 'success');
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                    load();
                });
                return f;
            }
            // Sharing a project (portfolio projects; the capstone uses its own page)
            var form = document.getElementById('sub-form');
            document.getElementById('sub-name').textContent = prof.full_name || '';
            function norm(t) { return (t || '').trim().replace(/\s+/g, ' ').toLowerCase(); }
            var sigIn = form.signature, sigStatus = form.querySelector('.ofl-sign__status');
            function sigOk() {
                var ok = norm(sigIn.value) !== '' && norm(sigIn.value) === norm(prof.full_name);
                sigStatus.textContent = !sigIn.value ? '' : ok ? '\u2713 Signature matches your registered name' : 'Signature must match your registered name exactly';
                sigStatus.className = 'ofl-sign__status ' + (!sigIn.value ? '' : ok ? 'is-ok' : 'is-bad');
                return ok;
            }
            sigIn.addEventListener('input', sigOk);
            form.addEventListener('submit', async function (e) {
                e.preventDefault();
                if (!sigOk()) return OFL.notice(msg, 'Your signature must match your registered full name exactly.', 'error');
                var b = form.querySelector('button[type=submit]'); b.disabled = true;
                var res = await sb.from('capstone_submissions').insert({ user_id: user.id, course_slug: course, assignment: key, repo_url: form.repo_url.value.trim(), writeup: form.writeup.value.trim(), integrity_signature: sigIn.value.trim() });
                b.disabled = false;
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                form.reset(); form.hidden = true;
                OFL.notice(msg, 'Shared! Now review three other projects to receive your grade.', 'success');
                load();
            });
            load();
        })();"""

page("academy/review", "Peer review | Open Fraud Labs Academy", "Share your project and review other learners' work with a rubric.",
     review_main, review_script, active="dashboard", noindex=True)

# ============================================================== Welcome: learner background (after sign-up)
COUNTRY_CODES = "AF AX AL DZ AS AD AO AI AQ AG AR AM AW AU AT AZ BS BH BD BB BY BE BZ BJ BM BT BO BQ BA BW BR IO BN BG BF BI CV KH CM CA KY CF TD CL CN CX CC CO KM CG CD CK CR CI HR CU CW CY CZ DK DJ DM DO EC EG SV GQ ER EE SZ ET FK FO FJ FI FR GF PF GA GM GE DE GH GI GR GL GD GP GU GT GG GN GW GY HT VA HN HK HU IS IN ID IR IQ IE IM IL IT JM JP JE JO KZ KE KI KP KR KW KG LA LV LB LS LR LY LI LT LU MO MG MW MY MV ML MT MH MQ MR MU YT MX FM MD MC MN ME MS MA MZ MM NA NR NP NL NC NZ NI NE NG NU NF MK MP NO OM PK PW PS PA PG PY PE PH PN PL PT PR QA RE RO RU RW BL SH KN LC MF PM VC WS SM ST SA SN RS SC SL SG SX SK SI SB SO ZA GS SS ES LK SD SR SJ SE CH SY TW TJ TZ TH TL TG TK TO TT TN TR TM TC TV UG UA AE GB US UM UY UZ VU VE VN VG VI WF EH YE ZM ZW XK"
welcome_main = """        <div class="ac-narrow wb">
            <div class="wb-head">
                <h1>Tell us a little about you</h1>
                <p>It takes about a minute. Your answers help us shape lessons for learners like you, and the totals (never your individual answers) help us report our reach when we apply for funding and partnerships. Personal questions are optional.</p>
            </div>
            <div id="msg"></div>
            <form id="wb-form" class="wb-form" novalidate>
                <fieldset class="wb-group">
                    <legend>Where you are</legend>
                    <div class="wb-row">
                        <label class="au-field"><span>Country</span><select name="country" required><option value="">Choose your country</option></select></label>
                        <label class="au-field"><span>City or town <em>(optional)</em></span><input name="city" maxlength="80" autocomplete="address-level2" placeholder="e.g. Lagos, Nairobi, London"></label>
                    </div>
                </fieldset>
                <fieldset class="wb-group">
                    <legend>About you <em>(optional)</em></legend>
                    <div class="wb-q"><span class="wb-q__label" id="q-gender">Gender</span>
                        <div class="wb-chips" role="radiogroup" aria-labelledby="q-gender" data-name="gender"></div></div>
                    <div class="wb-q"><span class="wb-q__label" id="q-age">Age</span>
                        <div class="wb-chips" role="radiogroup" aria-labelledby="q-age" data-name="age_range"></div></div>
                </fieldset>
                <fieldset class="wb-group">
                    <legend>Your background</legend>
                    <div class="wb-row">
                        <label class="au-field"><span>What do you do now?</span><select name="employment" required><option value="">Choose one</option></select></label>
                        <label class="au-field"><span>Highest education</span><select name="education" required><option value="">Choose one</option></select></label>
                    </div>
                    <label class="au-field"><span>Industry or field <em>(optional)</em></span><input name="industry" maxlength="80" placeholder="e.g. banking, health, retail, engineering student"></label>
                    <div class="wb-q"><span class="wb-q__label" id="q-py">Experience with Python</span>
                        <div class="wb-chips" role="radiogroup" aria-labelledby="q-py" data-name="python_level" data-required></div></div>
                    <div class="wb-q"><span class="wb-q__label" id="q-data">Experience analysing data (Excel, SQL, dashboards)</span>
                        <div class="wb-chips" role="radiogroup" aria-labelledby="q-data" data-name="data_level" data-required></div></div>
                </fieldset>
                <fieldset class="wb-group">
                    <legend>Your goal</legend>
                    <div class="wb-q"><span class="wb-q__label" id="q-goal">What do you most want from the Academy?</span>
                        <div class="wb-chips" role="radiogroup" aria-labelledby="q-goal" data-name="goal" data-required></div></div>
                    <label class="au-field"><span>How did you hear about us?</span><select name="heard_from" required><option value="">Choose one</option></select></label>
                </fieldset>
                <div class="wb-actions">
                    <button class="ac-btn ac-btn--primary au-submit" type="submit">Save and continue</button>
                    <button class="au-link" type="button" id="wb-skip">Skip for now</button>
                </div>
                <p class="wb-privacy">You can change these answers any time from your account page. See how we use them in our <a href="/privacy/">Privacy Policy</a>.</p>
            </form>
        </div>"""

welcome_script = r"""        (async function () {
            var sb = OFL.sb, el = OFL.el, msg = document.getElementById('msg'), form = document.getElementById('wb-form');
            var next = OFL.qs('next') || '/academy/dashboard/'; if (!next.startsWith('/') || next.startsWith('//')) next = '/academy/dashboard/';
            var user = await OFL.requireUser(location.pathname + location.search); if (!user) return;
            var OPTS = {
                gender: [['woman', 'Woman'], ['man', 'Man'], ['another', 'Another gender'], ['prefer_not', 'Prefer not to say']],
                age_range: [['under_18', 'Under 18'], ['18_24', '18–24'], ['25_34', '25–34'], ['35_44', '35–44'], ['45_54', '45–54'], ['55_plus', '55+'], ['prefer_not', 'Prefer not to say']],
                employment: [['student', 'Student'], ['employed_full', 'Employed full-time'], ['employed_part', 'Employed part-time'], ['self_employed', 'Self-employed or business owner'], ['looking', 'Looking for work'], ['not_working', 'Not working'], ['other', 'Other']],
                education: [['secondary', 'Secondary school'], ['diploma', 'Diploma, OND or HND'], ['bachelors', 'Bachelor’s degree'], ['masters', 'Master’s degree'], ['doctorate', 'Doctorate'], ['other', 'Other'], ['prefer_not', 'Prefer not to say']],
                python_level: [['none', 'Never used it'], ['beginner', 'Tried a little'], ['some', 'Written some code'], ['confident', 'Use it regularly']],
                data_level: [['none', 'None yet'], ['some', 'Some, on my own'], ['work', 'Part of my work']],
                goal: [['first_job', 'Get my first data job'], ['switch_career', 'Switch careers into data'], ['upskill', 'Get better at my current job'], ['study', 'Support my studies'], ['business', 'Use data in my own business'], ['curious', 'Learn out of curiosity']],
                heard_from: [['tiktok', 'TikTok'], ['linkedin', 'LinkedIn'], ['friend', 'A friend or colleague'], ['search', 'Google or another search'], ['school', 'School, university or employer'], ['other', 'Somewhere else']]
            };
            // Countries named in the learner's language by the browser; Nigeria, Ghana, Kenya and South Africa first.
            var names = null; try { names = new Intl.DisplayNames([navigator.language || 'en', 'en'], { type: 'region' }); } catch (e) {}
            var codes = '__CODES__'.split(' ').map(function (c) { return [c, names ? names.of(c) : c]; }).sort(function (a, b) { return a[1].localeCompare(b[1]); });
            var top = ['NG', 'GH', 'KE', 'ZA', 'GB', 'US'];
            var sel = form.country, g1 = el('optgroup', { label: 'Common' }), g2 = el('optgroup', { label: 'All countries' });
            top.forEach(function (c) { var f = codes.find(function (x) { return x[0] === c; }); if (f) g1.appendChild(el('option', { value: f[0], text: f[1] })); });
            codes.forEach(function (x) { g2.appendChild(el('option', { value: x[0], text: x[1] })); });
            sel.appendChild(g1); sel.appendChild(g2); sel.appendChild(el('option', { value: 'XX', text: 'Prefer not to say' }));
            ['employment', 'education', 'heard_from'].forEach(function (k) { OPTS[k].forEach(function (o) { form[k].appendChild(el('option', { value: o[0], text: o[1] })); }); });
            document.querySelectorAll('.wb-chips').forEach(function (g) {
                var name = g.getAttribute('data-name');
                OPTS[name].forEach(function (o) {
                    g.appendChild(el('label', { class: 'wb-chip' }, el('input', { type: 'radio', name: name, value: o[0] }), el('span', { text: o[1] })));
                });
            });
            var cur = (await sb.from('learner_background').select('*').eq('user_id', user.id).maybeSingle()).data;
            if (cur) Object.keys(cur).forEach(function (k) {
                var f = form.elements[k]; if (!f || cur[k] == null) return;
                if (f instanceof RadioNodeList) { Array.prototype.forEach.call(f, function (r) { r.checked = r.value === cur[k]; }); }
                else f.value = cur[k];
            });
            function val(n) { var f = form.elements[n]; return f ? (f.value || null) : null; }
            async function save(row) {
                row.user_id = user.id; row.updated_at = new Date().toISOString();
                return sb.from('learner_background').upsert(row, { onConflict: 'user_id' });
            }
            form.addEventListener('submit', async function (e) {
                e.preventDefault();
                var missing = [];
                ['country', 'employment', 'education', 'heard_from'].forEach(function (n) { if (!val(n)) { missing.push(n); form[n].classList.add('is-invalid'); } });
                document.querySelectorAll('.wb-chips[data-required]').forEach(function (g) { var n = g.getAttribute('data-name'); if (!val(n)) { missing.push(n); g.classList.add('is-invalid'); } });
                if (missing.length) { OFL.notice(msg, 'Please answer the highlighted questions, or choose Skip for now.', 'error'); window.scrollTo({ top: 0, behavior: 'smooth' }); return; }
                var b = form.querySelector('button[type=submit]'); b.disabled = true;
                var row = {}; ['country', 'city', 'gender', 'age_range', 'employment', 'industry', 'education', 'python_level', 'data_level', 'goal', 'heard_from'].forEach(function (n) { var v = val(n); row[n] = v ? String(v).trim() || null : null; });
                row.completed_at = new Date().toISOString();
                var r = await save(row);
                b.disabled = false;
                if (r.error) return OFL.notice(msg, OFL.friendlyError(r.error), 'error');
                location.href = next + (next.indexOf('?') < 0 ? '?' : '&') + 'welcome=1';
            });
            form.addEventListener('change', function (e) { e.target.classList.remove('is-invalid'); var g = e.target.closest('.wb-chips'); if (g) g.classList.remove('is-invalid'); });
            document.getElementById('wb-skip').addEventListener('click', async function () {
                if (!cur || !cur.completed_at) await save({ skipped_at: new Date().toISOString() });
                location.href = next;
            });
        })();""".replace('__CODES__', COUNTRY_CODES)

page("academy/welcome", "Tell us about you | Open Fraud Labs Academy", "A few quick questions about you and your goals.", welcome_main, welcome_script, active="dashboard", noindex=True)

# ---- shared CV uploader (used by the cohort and role application forms)
CV_JS = r"""
            function cvUploader(box, uid, context, onDone) {
                box.textContent = '';
                var input = OFL.el('input', { type: 'file', accept: '.pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document', class: 'ap-file', 'aria-label': 'Upload your CV' });
                var state = OFL.el('span', { class: 'ap-up-state', text: 'PDF or Word, up to 2 MB' });
                var pick = OFL.el('button', { type: 'button', class: 'ac-btn ac-btn--secondary ac-btn--sm', text: 'Upload CV', onclick: function () { input.click(); } });
                input.addEventListener('change', async function () {
                    var f = input.files[0]; if (!f) return;
                    var ext = (f.name.split('.').pop() || '').toLowerCase();
                    if (['pdf', 'doc', 'docx'].indexOf(ext) < 0) { state.textContent = 'Use a PDF or Word file.'; state.className = 'ap-up-state is-err'; return; }
                    if (f.size > 2097152) { state.textContent = 'That file is over 2 MB. Save it as a smaller PDF and try again.'; state.className = 'ap-up-state is-err'; return; }
                    state.textContent = 'Uploading…'; state.className = 'ap-up-state'; pick.disabled = true;
                    var types = { pdf: 'application/pdf', doc: 'application/msword', docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' };
                    var r = await OFL.sb.storage.from('cvs').upload(uid + '/' + context + '/cv.' + ext, f, { upsert: true, contentType: types[ext] });
                    pick.disabled = false; input.value = '';
                    if (r.error) { state.textContent = r.error.message || 'Upload failed. Try again.'; state.className = 'ap-up-state is-err'; return; }
                    state.textContent = f.name + ' uploaded'; state.className = 'ap-up-state is-ok'; pick.textContent = 'Replace CV';
                    onDone(true);
                });
                box.append(OFL.el('div', { class: 'ap-up-row' }, pick, state), input);
            }
"""

# ============================================================== Founding cohort: careers listing + application
LI = "https://www.linkedin.com/company/open-fraud-labs/"
apply_main = f"""        <section class="cp-hero ap-hero">
            <div class="ac-wrap">
                <nav class="cp-crumbs" aria-label="Breadcrumb"><a href="/careers/">Careers</a><span aria-hidden="true">/</span><span>Founding Cohort</span></nav>
                <p class="ac-eyebrow" id="ap-eyebrow">Pre-launch · Free learning internship</p>
                <h1 id="ap-title">Join the Academy's Founding Cohort</h1>
                <p class="cp-hero__lead">Before the Academy opens to everyone, we're taking a small group of learners through <b>Data Science from Scratch</b> for free. Places are limited, so we shortlist from applications and keep a waitlist.</p>
                <ul class="ap-facts" id="ap-facts">
                    <li><b>Free</b><span>No fees during pre-launch</span></li>
                    <li><b id="ap-span">Online</b><span id="ap-span-sub">Learn at your own pace, from anywhere</span></li>
                    <li><b id="ap-trial">7-day trial</b><span>Finish Lesson 1 in time to keep your place</span></li>
                    <li><b id="ap-places">Limited places</b><span id="ap-places-sub">Shortlisted from applications</span></li>
                </ul>
            </div>
        </section>
        <section class="ac-section">
            <div class="ac-narrow">
                <div id="msg"></div>
                <div id="ap-status"></div>
                <div class="ap-how" id="ap-how">
                    <div id="ap-dates-wrap" hidden><h2>Key dates</h2><ol class="ap-dates" id="ap-dates"></ol></div>
                    <h2>How it works</h2>
                    <ol class="ap-steps">
                        <li><b>Apply</b><span>Create a free account, answer a few questions and upload three screenshots showing you follow us (about 10 minutes).</span></li>
                        <li><b>We check and rank</b><span>We check your screenshots, usually within two days. Eligible applicants are ranked and offered places in order as they open; everyone else waits on the waitlist.</span></li>
                        <li><b>Accept your offer</b><span id="ap-step3">You'll get the offer by email and on this page. Within 7 days: post about it on LinkedIn and tag Ayodele Odugbile and Open Fraud Labs, join the cohort WhatsApp group, and complete Lesson 1 (video, notes, practice and quiz).</span></li>
                        <li><b>Carry on as a founding learner</b><span>Work through the course and projects, earn a verifiable certificate, and help shape the Academy with your feedback.</span></li>
                    </ol>
                    <h3>Who can apply</h3>
                    <ul class="ac-outcomes" id="ap-reqs">
                        <li data-req="laptop">You have your own laptop or desktop computer</li>
                        <li data-req="proofs">You have a LinkedIn account and follow <a href="{TT}" target="_blank" rel="noopener noreferrer">@_drhola on TikTok</a>, <a class="ap-founder-link" href="https://www.linkedin.com/search/results/people/?keywords=Ayodele%20Odugbile" target="_blank" rel="noopener noreferrer">Ayodele Odugbile</a> and <a href="{LI}" target="_blank" rel="noopener noreferrer">Open Fraud Labs</a> on LinkedIn, with a screenshot of each</li>
                        <li data-req="cv">You attach your CV (PDF or Word)</li>
                        <li data-req="post">If offered a place, you're happy to post about it on LinkedIn and tag us</li>
                        <li>You can finish the offer steps within 7 days</li>
                    </ul>
                    <h3>How we rank eligible applicants</h3>
                    <ul class="ac-outcomes">
                        <li>The time you can give the course each week</li>
                        <li>A clear reason for joining and a problem you'd like to solve with data</li>
                        <li>A completed About-you profile</li>
                    </ul>
                    <p class="ac-muted ac-small">Your country, gender, age and other About-you answers are never used to decide who gets a place. This is a free learning programme, not a paid job.</p>
                </div>
                <div id="ap-cta"></div>
                <form id="ap-form" class="wb-form" novalidate hidden>
                    <fieldset class="wb-group" id="ap-follow-group">
                        <legend>1. Follow us and show us</legend>
                        <p class="ac-muted ap-help">Follow all three, then upload a screenshot of each profile showing &ldquo;Following&rdquo;. Screenshots are private: only the Open Fraud Labs team checking applications can see them.</p>
                        <div class="ap-proofs">
                            <div class="ap-proof" data-kind="tiktok">
                                <div class="ap-proof__head"><b>TikTok: @_drhola</b><a class="ac-btn ac-btn--secondary ac-btn--sm" href="{TT}" target="_blank" rel="noopener noreferrer">Open</a></div>
                                <label class="ap-check"><input type="checkbox" name="follows_tiktok"> I follow @_drhola</label>
                                <label class="au-field"><span>Your TikTok username</span><input name="tiktok_handle" maxlength="40" placeholder="@yourname" autocomplete="off"></label>
                                <div class="ap-upload"></div>
                            </div>
                            <div class="ap-proof" data-kind="linkedin-founder">
                                <div class="ap-proof__head"><b>LinkedIn: Ayodele Odugbile</b><a class="ac-btn ac-btn--secondary ac-btn--sm ap-founder-link" href="https://www.linkedin.com/search/results/people/?keywords=Ayodele%20Odugbile" target="_blank" rel="noopener noreferrer">Open</a></div>
                                <label class="ap-check"><input type="checkbox" name="follows_founder"> I follow Ayodele Odugbile (founder)</label>
                                <div class="ap-upload"></div>
                            </div>
                            <div class="ap-proof" data-kind="linkedin-page">
                                <div class="ap-proof__head"><b>LinkedIn: Open Fraud Labs</b><a class="ac-btn ac-btn--secondary ac-btn--sm" href="{LI}" target="_blank" rel="noopener noreferrer">Open</a></div>
                                <label class="ap-check"><input type="checkbox" name="follows_linkedin"> I follow the Open Fraud Labs page</label>
                                <div class="ap-upload"></div>
                            </div>
                        </div>
                        <label class="au-field"><span>Your LinkedIn profile link</span><input name="linkedin_url" type="url" maxlength="200" placeholder="https://www.linkedin.com/in/yourname"></label>
                        <div class="au-field" id="ap-cv-field" hidden><span>Your CV <em>(PDF or Word)</em></span><div class="ap-upload" id="ap-cv"></div></div>
                    </fieldset>
                    <fieldset class="wb-group">
                        <legend>2. Your time and setup</legend>
                        <div class="wb-q"><span class="wb-q__label" id="q-hours">How many hours a week can you study?</span>
                            <div class="wb-chips" role="radiogroup" aria-labelledby="q-hours" data-name="hours" data-required></div></div>
                        <div class="wb-q"><span class="wb-q__label" id="q-device">What will you mostly learn on?</span>
                            <div class="wb-chips" role="radiogroup" aria-labelledby="q-device" data-name="device"></div></div>
                        <div class="wb-q"><span class="wb-q__label" id="q-net">How reliable is your internet?</span>
                            <div class="wb-chips" role="radiogroup" aria-labelledby="q-net" data-name="internet"></div></div>
                    </fieldset>
                    <fieldset class="wb-group">
                        <legend>3. Your goals</legend>
                        <div class="wb-q"><span class="wb-q__label" id="q-career">Where do you want this course to take you?</span>
                            <div class="wb-chips" role="radiogroup" aria-labelledby="q-career" data-name="career_goal"></div></div>
                        <label class="au-field"><span>Why do you want to join the Founding Cohort?</span>
                            <textarea name="motivation" rows="5" maxlength="1500" placeholder="Tell us where you are now, what you want to do next, and how this course fits in. Specific answers stand out."></textarea>
                            <small class="ap-count" data-for="motivation"></small></label>
                        <label class="au-field"><span>A problem you'd like to solve with data <em>(at work, in your community or anywhere)</em></span>
                            <textarea name="problem" rows="3" maxlength="1000" placeholder="e.g. spotting fake loan applications, reducing clinic no-shows, pricing farm produce fairly"></textarea>
                            <small class="ap-count" data-for="problem"></small></label>
                    </fieldset>
                    <fieldset class="wb-group">
                        <legend>4. After launch <em>(not used for selection)</em></legend>
                        <div class="wb-q"><span class="wb-q__label" id="q-afford">If the full course had a fee after launch, what could you pay per month?</span>
                            <div class="wb-chips" role="radiogroup" aria-labelledby="q-afford" data-name="can_afford"></div></div>
                    </fieldset>
                    <fieldset class="wb-group">
                        <legend>5. Commitment</legend>
                        <label class="ap-check ap-check--req"><input type="checkbox" name="commit_deadline"> <span id="ap-commit">If I'm offered a place, I'll complete the offer steps within 7 days.</span></label>
                        <label class="ap-check"><input type="checkbox" name="consent_reports"> You can include my answers, without my name, in reports to funders and partners.</label>
                        <label class="ap-check"><input type="checkbox" name="consent_jobs"> Tell me about internships and job opportunities that match my profile.</label>
                    </fieldset>
                    <div class="wb-actions">
                        <button class="ac-btn ac-btn--primary au-submit" type="submit" id="ap-submit">Submit application</button>
                    </div>
                    <p class="wb-privacy">One application per person. You can't edit it after you submit, except to replace screenshots if we ask. See how we use your answers in our <a href="/privacy/">Privacy Policy</a>.</p>
                </form>
            </div>
        </section>"""

apply_script = r"""        (async function () {
            var sb = OFL.sb, el = OFL.el, msg = document.getElementById('msg');
""" + CV_JS + r"""
            var info = (await sb.rpc('cohort_public', { p_slug: OFL.qs('c') || null })).data;
            var cta = document.getElementById('ap-cta'), form = document.getElementById('ap-form'), status = document.getElementById('ap-status');
            var KINDS = [['tiktok', 'TikTok: @_drhola'], ['linkedin-founder', 'LinkedIn: Ayodele Odugbile'], ['linkedin-page', 'LinkedIn: Open Fraud Labs']];
            if (!info || info.status !== 'open') {
                document.getElementById('ap-places').textContent = 'Applications closed';
                document.getElementById('ap-places-sub').textContent = 'Follow us to hear about the next cohort';
                cta.appendChild(el('div', { class: 'ac-panel' }, el('h2', { text: 'Applications aren’t open right now' }),
                    el('p', { class: 'ac-muted', text: 'Follow Open Fraud Labs on TikTok and LinkedIn to hear when the next cohort opens.' })));
            }
            if (info) {
                document.getElementById('ap-title').textContent = 'Join the Academy’s ' + info.title;
                document.getElementById('ap-trial').textContent = info.trial_days + '-day offer window';
                document.querySelector('#ap-facts li:nth-child(3) span').textContent = 'Accept your offer and finish Lesson ' + info.trial_lesson + ' in time';
                var steps = [];
                if (info.require_post) steps.push('post about it on LinkedIn and tag Ayodele Odugbile and Open Fraud Labs');
                if (info.require_whatsapp) steps.push('join the cohort WhatsApp group');
                steps.push('complete Lesson ' + info.trial_lesson + ' (video, notes, practice and quiz)');
                document.getElementById('ap-step3').textContent = 'You’ll get the offer by email and on this page. Within ' + info.trial_days + ' days: ' + steps.join(', ').replace(/, ([^,]*)$/, ', and $1') + '.';
                document.getElementById('ap-commit').textContent = 'If I’m offered a place, I’ll ' + steps.join(', ').replace(/, ([^,]*)$/, ' and $1') + ' within ' + info.trial_days + ' days.';
                document.querySelectorAll('#ap-reqs [data-req]').forEach(function (li) { li.hidden = !info['require_' + li.getAttribute('data-req')]; });
                if (info.founder_linkedin_url) document.querySelectorAll('.ap-founder-link').forEach(function (a) { a.href = info.founder_linkedin_url; });
                (function dates() {
                    function dd(v, time) { var d = new Date(v.length === 10 ? v + 'T12:00:00+01:00' : v); return d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', timeZone: 'Africa/Lagos' }) + (time ? ', ' + d.toLocaleTimeString('en-GB', { hour: 'numeric', minute: '2-digit', hour12: true, timeZone: 'Africa/Lagos' }).replace(':00', '') : ''); }
                    if (info.starts_on && info.ends_on) { document.getElementById('ap-span').textContent = dd(info.starts_on).replace(/^\w+, /, '') + ' \u2013 ' + dd(info.ends_on).replace(/^\w+, /, ''); document.getElementById('ap-span-sub').textContent = 'Online, at your own pace within the weekly plan'; }
                    var rows = [];
                    if (info.closes_at) rows.push([dd(info.closes_at, true), 'Applications close']);
                    if (info.offers_at) rows.push([dd(info.offers_at), 'Offers sent to eligible applicants, by email and on this page']);
                    if (info.orientation_at) rows.push([dd(info.orientation_at, true), 'Online orientation (link shared in the cohort WhatsApp group)']);
                    if (info.offers_at) rows.push([dd(new Date(new Date(info.offers_at).getTime() + info.trial_days * 864e5).toISOString()), 'Accept your offer by this date (' + info.trial_days + ' days after it arrives)']);
                    if (info.starts_on) rows.splice(info.offers_at ? 2 : rows.length, 0, [dd(info.starts_on), 'Learning starts: a weekly plan of lessons, then three portfolio projects and a capstone']);
                    if (info.ends_on) rows.push([dd(info.ends_on), 'Final deadline: lessons, projects and capstone all complete']);
                    if (!rows.length) return;
                    var ol = document.getElementById('ap-dates');
                    rows.forEach(function (r) { ol.appendChild(OFL.el('li', {}, OFL.el('b', { text: r[0] }), OFL.el('span', { text: r[1] }))); });
                    document.getElementById('ap-dates-wrap').hidden = false;
                })();
                if (info.status === 'open') {
                    document.getElementById('ap-places').textContent = info.places_left > 0 ? info.places_left + ' of ' + info.capacity + ' places open' : 'All ' + info.capacity + ' places taken';
                    document.getElementById('ap-places-sub').textContent = info.places_left > 0 ? 'Offered to eligible applicants in order' : 'Apply to join the waitlist';
                }
            }
            var user = await OFL.getUser();
            if (!info || info.status !== 'open') { if (user && info) { var m0 = (await sb.rpc('application_mine', { p_slug: info.slug })).data; if (m0) drawStatus(m0); } return; }
            var next = '/academy/apply/' + (OFL.qs('c') ? '?c=' + encodeURIComponent(OFL.qs('c')) : '');
            if (!user) {
                cta.appendChild(el('div', { class: 'ap-cta' }, el('a', { class: 'ac-btn ac-btn--primary', href: '/account/?next=' + encodeURIComponent(next), text: 'Create a free account to apply' }),
                    el('p', { class: 'ac-muted ac-small' }, 'Already have an account? ', el('a', { href: '/account/?next=' + encodeURIComponent(next), text: 'Log in' }))));
                return;
            }
            var prof = (await sb.from('profiles').select('terms_accepted_at').eq('id', user.id).maybeSingle()).data || {};
            if (!prof.terms_accepted_at) { location.href = '/account/?next=' + encodeURIComponent(next); return; }

            // ---- screenshot uploads: resized and compressed in the browser, stored privately
            var uploaded = {};
            function path(kind) { return user.id + '/' + info.slug + '/' + kind + '.jpg'; }
            function compress(file) {
                return new Promise(function (resolve, reject) {
                    var img = new Image(), url = URL.createObjectURL(file);
                    img.onload = function () {
                        var max = 1280, w = img.naturalWidth, h = img.naturalHeight, k = Math.min(1, max / Math.max(w, h));
                        var cv = document.createElement('canvas'); cv.width = Math.round(w * k); cv.height = Math.round(h * k);
                        cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height); URL.revokeObjectURL(url);
                        (function tryQ(q) { cv.toBlob(function (b) { if (!b) return reject(new Error('Could not read that image')); if (b.size > 450000 && q > 0.4) return tryQ(q - 0.15); resolve(b); }, 'image/jpeg', q); })(0.75);
                    };
                    img.onerror = function () { URL.revokeObjectURL(url); reject(new Error('That file isn’t an image we can read. Use a PNG or JPG screenshot.')); };
                    img.src = url;
                });
            }
            function uploader(box, kind, label) {
                box.textContent = '';
                var input = el('input', { type: 'file', accept: 'image/*', class: 'ap-file', 'aria-label': 'Screenshot for ' + label });
                var thumb = el('div', { class: 'ap-thumb' }), state = el('span', { class: 'ap-up-state', text: 'No screenshot yet' });
                var pick = el('button', { type: 'button', class: 'ac-btn ac-btn--secondary ac-btn--sm', text: 'Upload screenshot', onclick: function () { input.click(); } });
                input.addEventListener('change', async function () {
                    var f = input.files[0]; if (!f) return;
                    state.textContent = 'Uploading…'; state.className = 'ap-up-state'; pick.disabled = true;
                    try {
                        var blob = await compress(f);
                        var r = await sb.storage.from('application-proofs').upload(path(kind), blob, { upsert: true, contentType: 'image/jpeg' });
                        if (r.error) throw r.error;
                        uploaded[kind] = true; thumb.textContent = ''; thumb.appendChild(el('img', { src: URL.createObjectURL(blob), alt: 'Your ' + label + ' screenshot' }));
                        state.textContent = 'Uploaded'; state.className = 'ap-up-state is-ok'; pick.textContent = 'Replace';
                    } catch (e) { state.textContent = e.message || 'Upload failed. Try again.'; state.className = 'ap-up-state is-err'; }
                    pick.disabled = false; input.value = '';
                });
                box.append(thumb, el('div', { class: 'ap-up-row' }, pick, state), input);
            }

            var mine = (await sb.rpc('application_mine', { p_slug: info.slug })).data;
            if (mine) return drawStatus(mine);
            var bg = (await sb.from('learner_background').select('completed_at').eq('user_id', user.id).maybeSingle()).data;
            if (!bg || !bg.completed_at) cta.appendChild(el('div', { class: 'ofl-notice ac-nudge' }, 'Tip: ', el('a', { href: '/academy/welcome/?next=' + encodeURIComponent(next), text: 'complete your About-you profile' }), ' before you apply. It’s one of the things we look at.'));
            var OPTS = { hours: [['1-2', '1–2 hours'], ['3-5', '3–5 hours'], ['6-10', '6–10 hours'], ['10+', 'More than 10']],
                device: [['laptop', 'My own laptop or desktop'], ['shared', 'A shared or public computer'], ['phone', 'Phone only']],
                internet: [['reliable', 'Reliable'], ['sometimes', 'Sometimes unreliable'], ['poor', 'Often poor']],
                career_goal: [['first_job', 'My first data job'], ['switch', 'Switch careers'], ['upskill', 'Do my current job better'], ['freelance', 'Freelance work'], ['business', 'My own business'], ['study', 'Further study']],
                can_afford: [['0', 'Nothing right now'], ['lt5k', 'Under ₦5,000'], ['5-15k', '₦5,000–15,000'], ['15-30k', '₦15,000–30,000'], ['30k+', 'Over ₦30,000']] };
            document.querySelectorAll('#ap-form .wb-chips').forEach(function (g) {
                var name = g.getAttribute('data-name');
                (OPTS[name] || []).forEach(function (o) { g.appendChild(el('label', { class: 'wb-chip' }, el('input', { type: 'radio', name: name, value: o[0] }), el('span', { text: o[1] }))); });
            });
            if (info.require_laptop) document.querySelector('[data-name="device"]').before(el('p', { class: 'ap-help ac-muted', text: 'This cohort needs your own laptop or desktop computer.' }));
            if (info.require_proofs) document.querySelectorAll('#ap-follow-group .ap-proof').forEach(function (p) { var k = p.getAttribute('data-kind'); uploader(p.querySelector('.ap-upload'), k, KINDS.filter(function (x) { return x[0] === k; })[0][1]); });
            else document.querySelectorAll('#ap-follow-group .ap-proof .ap-upload').forEach(function (u) { u.hidden = true; });
            var hasCv = false;
            if (info.require_cv) { document.getElementById('ap-cv-field').hidden = false; cvUploader(document.getElementById('ap-cv'), user.id, 'cohort-' + info.slug, function () { hasCv = true; }); }
            document.querySelectorAll('.ap-count').forEach(function (c) {
                var t = form[c.getAttribute('data-for')], min = c.getAttribute('data-for') === 'motivation' ? 30 : 0;
                function upd() { var n = t.value.trim().length; c.textContent = n + ' characters' + (min && n < min ? ' (at least ' + min + ')' : ''); c.classList.toggle('is-short', !!min && n < min); }
                t.addEventListener('input', upd); upd();
            });
            form.hidden = false;
            form.addEventListener('submit', async function (e) {
                e.preventDefault();
                var f = form, val = function (n) { var x = f.querySelector('input[name="' + n + '"]:checked'); return x ? x.value : null; };
                function stop(target, text) { if (target && target.scrollIntoView) target.scrollIntoView({ block: 'center' }); if (target && target.focus) target.focus(); return OFL.notice(msg, text, 'error'); }
                document.querySelectorAll('#ap-form .wb-chips').forEach(function (g) { g.classList.remove('is-invalid'); });
                if (info.require_proofs) {
                    if (!f.follows_tiktok.checked || !f.follows_founder.checked || !f.follows_linkedin.checked) return stop(f.follows_tiktok, 'Follow all three and tick each box.');
                    if (f.tiktok_handle.value.replace(/^@/, '').trim().length < 2) return stop(f.tiktok_handle, 'Add your TikTok username.');
                    var missing = KINDS.filter(function (k) { return !uploaded[k[0]]; });
                    if (missing.length) return stop(document.getElementById('ap-follow-group'), 'Upload a screenshot for: ' + missing.map(function (k) { return k[1]; }).join(', ') + '.');
                    if (!/^https?:\/\/([a-z]+\.)?linkedin\.com\/in\/\S+/i.test(f.linkedin_url.value.trim())) return stop(f.linkedin_url, 'Add your LinkedIn profile link. It starts with https://www.linkedin.com/in/');
                }
                if (info.require_cv && !hasCv) return stop(document.getElementById('ap-cv-field'), 'Upload your CV.');
                if (!val('hours')) { var g = f.querySelector('[data-name="hours"]'); g.classList.add('is-invalid'); return stop(g, 'Tell us how many hours a week you can study.'); }
                if (info.require_laptop && val('device') !== 'laptop') { var gd = f.querySelector('[data-name="device"]'); gd.classList.add('is-invalid'); return stop(gd, 'This cohort needs your own laptop or desktop computer.'); }
                if (f.motivation.value.trim().length < 30) return stop(f.motivation, 'Tell us a little more about why you want to join (at least 30 characters).');
                if (!f.commit_deadline.checked) return stop(f.commit_deadline, 'Please confirm you can complete the offer steps in time.');
                var btn = document.getElementById('ap-submit'); btn.disabled = true; btn.textContent = 'Submitting…';
                var res = await sb.rpc('application_submit', { p_slug: info.slug, p_answers: {
                    follows_tiktok: f.follows_tiktok.checked, tiktok_handle: f.tiktok_handle.value, follows_founder: f.follows_founder.checked, follows_linkedin: f.follows_linkedin.checked, linkedin_url: f.linkedin_url.value,
                    hours: val('hours'), device: val('device'), internet: val('internet'), career_goal: val('career_goal'), can_afford: val('can_afford'),
                    motivation: f.motivation.value, problem: f.problem.value,
                    commit_deadline: f.commit_deadline.checked, consent_reports: f.consent_reports.checked, consent_jobs: f.consent_jobs.checked } });
                btn.disabled = false; btn.textContent = 'Submit application';
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                form.hidden = true; cta.textContent = ''; msg.textContent = ''; window.scrollTo({ top: 0, behavior: 'smooth' });
                drawStatus(res.data, true);
            });

            function when(v) { return new Date(v).toLocaleString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }); }
            function copyBtn(text) {
                var b = el('button', { type: 'button', class: 'ac-btn ac-btn--secondary ac-btn--sm', text: 'Copy post text' });
                b.addEventListener('click', function () { (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).then(function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy post text'; }, 1800); }, function () { window.prompt('Copy this text:', text); }); });
                return b;
            }
            async function step(name, value) {
                var r = await sb.rpc('application_offer_step', { p_slug: info.slug, p_step: name, p_value: value || null });
                if (r.error) return OFL.notice(msg, OFL.friendlyError(r.error), 'error');
                msg.textContent = ''; drawStatus(r.data);
            }
            function drawStatus(m, fresh) {
                document.getElementById('ap-how').hidden = !(m.status === 'waitlisted' && m.proof_status === 'ok');
                document.getElementById('ap-facts').hidden = true; document.querySelector('.ap-hero .cp-hero__lead').hidden = true;
                var lesson = '/academy/lesson/?course=' + info.course + '&n=' + info.trial_lesson, box;
                if (m.status === 'shortlisted') {
                    var left = Math.max(0, new Date(m.deadline_at) - Date.now()), d = Math.floor(left / 864e5), h = Math.floor(left % 864e5 / 36e5);
                    var list = el('ol', { class: 'ap-offer' });
                    function item(done, title, body) { list.appendChild(el('li', { class: done ? 'is-done' : '' }, el('span', { class: 'ap-offer__dot', 'aria-hidden': 'true', text: done ? '✓' : '' }), el('div', {}, el('b', { text: title + (done ? ' (done)' : '') }), body))); }
                    if (info.require_post) {
                        var post = 'I’ve been offered a place in the Founding Cohort of Open Fraud Labs Academy.\n\nOver the coming weeks I’ll be learning Data Science from Scratch: Python, statistics and machine learning, with hands-on projects.\n\nThank you @Ayodele Odugbile and @Open Fraud Labs for the opportunity. If you’re curious about data, take a look: openfraudlabs.com/academy\n\n#OpenFraudLabsAcademy #DataScience';
                        var url = el('input', { type: 'url', placeholder: 'https://www.linkedin.com/posts/…', value: m.post_url || '', 'aria-label': 'Link to your LinkedIn post' });
                        item(!!m.post_url, 'Post your offer on LinkedIn', el('div', { class: 'ap-offer__body' },
                            el('p', { text: 'Share the news and tag Ayodele Odugbile and Open Fraud Labs. You can use this text. When you paste it into LinkedIn, type @ and pick both names from the list so the tags work.' }),
                            el('pre', { class: 'ap-post', text: post }),
                            el('div', { class: 'ap-up-row' }, copyBtn(post), el('a', { class: 'ac-btn ac-btn--secondary ac-btn--sm', href: 'https://www.linkedin.com/feed/', target: '_blank', rel: 'noopener noreferrer', text: 'Open LinkedIn' })),
                            el('label', { class: 'au-field' }, el('span', { text: 'Then paste the link to your post (on the post, choose … then “Copy link to post”)' }), url),
                            el('button', { type: 'button', class: 'ac-btn ac-btn--primary ac-btn--sm', text: m.post_url ? 'Update link' : 'Save link', onclick: function () { step('post', url.value); } })));
                    }
                    if (info.require_whatsapp) {
                        item(!!m.whatsapp_joined, 'Join the cohort WhatsApp group', el('div', { class: 'ap-offer__body' },
                            m.whatsapp_url ? el('p', { text: 'Updates, reminders and questions go here. Please don’t share the link outside the cohort.' }) : el('p', { text: 'The group link will appear here shortly. Check back soon; your deadline already allows for this.' }),
                            m.whatsapp_url ? el('div', { class: 'ap-up-row' }, el('a', { class: 'ac-btn ac-btn--secondary ac-btn--sm', href: m.whatsapp_url, target: '_blank', rel: 'noopener noreferrer', text: 'Open WhatsApp group' }),
                                m.whatsapp_joined ? null : el('button', { type: 'button', class: 'ac-btn ac-btn--primary ac-btn--sm', text: 'I’ve joined', onclick: function () { step('whatsapp'); } })) : null));
                    }
                    item(!!m.trial_done, 'Complete Lesson ' + info.trial_lesson, el('div', { class: 'ap-offer__body' },
                        el('p', { text: 'Watch the video, read the notes, try the practice and pass the quiz.' }),
                        m.trial_done ? null : el('a', { class: 'ac-btn ac-btn--primary ac-btn--sm', href: lesson, text: 'Start Lesson ' + info.trial_lesson })));
                    box = el('div', { class: 'ap-state ap-state--go' }, el('span', { class: 'ap-state__tag', text: 'Offer' }),
                        el('h2', { text: 'You’ve been offered a place' }),
                        el('p', { text: 'Finish every step below by ' + when(m.deadline_at) + ' to accept it. If they aren’t all done in time, the place goes to the next person on the waitlist.' }),
                        el('div', { class: 'ap-countdown' }, el('b', { class: 'num', text: d + 'd ' + h + 'h' }), el('span', { text: 'left' })), list);
                } else if (m.status === 'completed') {
                    box = el('div', { class: 'ap-state ap-state--done' }, el('span', { class: 'ap-state__tag', text: 'Place confirmed' }),
                        el('h2', { text: 'Welcome to the ' + info.title }), el('p', { text: 'You completed every step in time. Carry on with the course whenever you’re ready.' }),
                        el('div', { class: 'ap-up-row' }, el('a', { class: 'ac-btn ac-btn--primary', href: '/academy/dashboard/', text: 'Go to my learning' }),
                            m.whatsapp_url ? el('a', { class: 'ac-btn ac-btn--secondary', href: m.whatsapp_url, target: '_blank', rel: 'noopener noreferrer', text: 'Cohort WhatsApp group' }) : null));
                } else if (m.status === 'waitlisted' && m.proof_status === 'fix') {
                    var ups = el('div', { class: 'ap-proofs' });
                    KINDS.forEach(function (k) { var b = el('div', { class: 'ap-proof' }, el('div', { class: 'ap-proof__head' }, el('b', { text: k[1] })), el('div', { class: 'ap-upload' })); ups.appendChild(b); uploader(b.querySelector('.ap-upload'), k[0], k[1]); });
                    box = el('div', { class: 'ap-state ap-state--fix' }, el('span', { class: 'ap-state__tag', text: 'Action needed' }),
                        el('h2', { text: 'Please update your screenshots' }), el('p', { class: 'ap-note', text: m.proof_note || 'One or more screenshots didn’t show what we need.' }),
                        el('p', { class: 'ac-muted ac-small', text: 'Upload new screenshots for the ones that need fixing (each should show the profile name and “Following”), then send them.' }), ups,
                        el('button', { type: 'button', class: 'ac-btn ac-btn--primary', text: 'Send new screenshots', onclick: async function () {
                            var r = await sb.rpc('application_proofs_resubmit', { p_slug: info.slug });
                            if (r.error) return OFL.notice(msg, OFL.friendlyError(r.error), 'error');
                            OFL.notice(msg, 'Thank you. We’ll check them again soon.', 'success'); drawStatus(r.data);
                        } }));
                } else if (m.status === 'waitlisted' && m.proof_status === 'pending') {
                    box = el('div', { class: 'ap-state' }, el('span', { class: 'ap-state__tag', text: fresh ? 'Application received' : 'Checking your screenshots' }),
                        el('h2', { text: fresh ? 'Thank you for applying' : 'We’re checking your application' }),
                        el('p', { text: 'We check screenshots by hand, usually within two days. You’ll hear from us here and by email.' }),
                        el('p', { class: 'ac-muted ac-small', text: 'While you wait, follow @_drhola on TikTok for free short lessons.' }));
                } else if (m.status === 'waitlisted') {
                    box = el('div', { class: 'ap-state' }, el('span', { class: 'ap-state__tag', text: 'On the waitlist' }),
                        el('h2', { text: 'You’re eligible and on the waitlist' }),
                        el('p', { text: m.meets_min ? 'You’re number ' + m.position + ' in line. Places open when offers aren’t accepted in time, and we offer the next place automatically.'
                                                   : 'Our team will review your application. We’ll tell you here and by email if a place opens for you.' }));
                } else if (m.status === 'missed') {
                    box = el('div', { class: 'ap-state ap-state--end' }, el('span', { class: 'ap-state__tag', text: 'Offer expired' }),
                        el('h2', { text: 'Your offer has expired' }), el('p', { text: 'The offer steps weren’t all completed by the deadline, so the place went to the next person on the waitlist. You’re welcome to apply for a future cohort.' }));
                } else {
                    box = el('div', { class: 'ap-state ap-state--end' }, el('span', { class: 'ap-state__tag', text: 'Application closed' }),
                        el('h2', { text: 'Thank you for applying' }), el('p', { text: 'We weren’t able to offer you a place in this cohort. You’re welcome to apply for a future one.' }));
                }
                status.textContent = ''; status.appendChild(box);
            }
        })();"""


page("academy/apply", "Founding Cohort: apply | Open Fraud Labs Academy",
     "Apply for a free place in the Open Fraud Labs Academy Founding Cohort: Data Science from Scratch, shortlisted from applications with a 7-day trial.",
     apply_main, apply_script, active="courses")

careers_main = f"""        <section class="cp-hero">
            <div class="ac-wrap">
                <p class="ac-eyebrow">Careers</p>
                <h1>Work and learn with Open Fraud Labs</h1>
                <p class="cp-hero__lead">Open Fraud Labs builds practical, trustworthy data and AI skills for Africa and beyond. Join us as a learner or as part of the team that runs the Academy.</p>
            </div>
        </section>
        <section class="ac-section">
            <div class="ac-narrow">
                <h2 class="cr-h">Internships</h2>
                <div id="cr-roles"><p class="ac-muted">Loading&hellip;</p></div>
                <h2 class="cr-h">Programmes</h2>
                <article class="cr-job" id="cr-cohort">
                    <div>
                        <span class="ac-status ac-status--soon" id="cr-state">Loading</span>
                        <h3>Academy Founding Cohort: free learning internship</h3>
                        <p class="ac-muted">Learn Data Science from Scratch for free before the Academy launches. For people with their own laptop who follow Open Fraud Labs on TikTok and LinkedIn. Offers go to eligible applicants in ranked order.</p>
                        <p class="cr-meta" id="cr-meta">Online · Free · Unpaid</p>
                    </div>
                    <a class="ac-btn ac-btn--primary" href="/academy/apply/" id="cr-apply">See details and apply</a>
                </article>
                <h2 class="cr-h">Paid roles</h2>
                <p class="ac-muted">No paid roles are open right now. Follow Open Fraud Labs on <a href="{LI}" target="_blank" rel="noopener noreferrer">LinkedIn</a> to hear when they are. Questions about careers: <a href="mailto:careers@openfraudlabs.com">careers@openfraudlabs.com</a>.</p>
            </div>
        </section>"""

careers_script = r"""        (async function () {
            var el = OFL.el, box = document.getElementById('cr-roles');
            var roles = ((await OFL.sb.from('roles').select('slug, title, summary, paid, kind, location, commitment, duration, status, rolling').in('status', ['open', 'filled']).order('sort')).data || []);
            box.textContent = '';
            if (!roles.length) box.appendChild(el('p', { class: 'ac-muted', text: 'No internships are open right now.' }));
            roles.forEach(function (r) {
                var open = r.status === 'open';
                box.appendChild(el('article', { class: 'cr-job' }, el('div', {},
                    el('span', { class: 'ac-status ' + (open ? 'ac-status--live' : 'ac-status--soon'), text: open ? (r.rolling ? 'Open: rolling applications' : 'Open') : 'Filled' }),
                    el('h3', { text: r.title }), el('p', { class: 'ac-muted', text: r.summary }),
                    el('p', { class: 'cr-meta', text: [r.paid ? 'Paid' : 'Unpaid', r.location, r.commitment].filter(Boolean).join(' · ') })),
                    el('a', { class: 'ac-btn ac-btn--' + (open ? 'primary' : 'secondary'), href: '/careers/role/?r=' + encodeURIComponent(r.slug), text: open ? 'See role and apply' : 'See role' })));
            });
        })();
        (async function () {
            var info = (await OFL.sb.rpc('cohort_public', { p_slug: null })).data;
            var s = document.getElementById('cr-state'), meta = document.getElementById('cr-meta'), a = document.getElementById('cr-apply');
            if (!info || info.status !== 'open') { s.textContent = 'Closed'; a.textContent = 'See details'; return; }
            s.textContent = 'Applications open'; s.className = 'ac-status ac-status--live';
            meta.textContent = 'Online · Free · Unpaid · ' + (info.places_left > 0 ? info.places_left + ' of ' + info.capacity + ' places open' : 'Places full: waitlist open');
            a.href = '/academy/apply/?c=' + encodeURIComponent(info.slug);
        })();"""

page("careers", "Careers | Open Fraud Labs", "Internships, programmes and roles at Open Fraud Labs, including the free Academy Founding Cohort.",
     careers_main, careers_script)

# ============================================================== Role page (internships, jobs)
role_main = """        <section class="cp-hero ap-hero">
            <div class="ac-wrap">
                <nav class="cp-crumbs" aria-label="Breadcrumb"><a href="/careers/">Careers</a><span aria-hidden="true">/</span><span id="rl-crumb">Role</span></nav>
                <p class="ac-eyebrow" id="rl-eyebrow">Internship</p>
                <h1 id="rl-title">Loading&hellip;</h1>
                <p class="cp-hero__lead" id="rl-summary"></p>
                <ul class="ap-facts" id="rl-facts"></ul>
            </div>
        </section>
        <section class="ac-section">
            <div class="ac-narrow">
                <div id="msg"></div>
                <div id="rl-status"></div>
                <div id="rl-body" class="rl-body"></div>
                <div id="rl-cta"></div>
                <form id="rl-form" class="wb-form" novalidate hidden>
                    <fieldset class="wb-group">
                        <legend>1. About you</legend>
                        <div class="wb-q"><span class="wb-q__label" id="q-stage">Where are you now?</span>
                            <div class="wb-chips" role="radiogroup" aria-labelledby="q-stage" data-name="stage"></div></div>
                        <div class="wb-row">
                            <label class="au-field"><span>Institution <em>(or where you studied)</em></span><input name="institution" maxlength="160" placeholder="e.g. University of Lagos"></label>
                            <label class="au-field"><span>Course of study</span><input name="course" maxlength="160" placeholder="e.g. Economics"></label>
                        </div>
                        <div class="wb-row">
                            <label class="au-field"><span>Year of graduation <em>(or expected)</em></span><input name="grad_year" maxlength="10" inputmode="numeric" placeholder="e.g. 2025"></label>
                            <label class="au-field"><span>Earliest start date</span><input name="start_date" type="date"></label>
                        </div>
                        <div class="wb-row">
                            <label class="au-field"><span>City</span><input name="city" maxlength="80" autocomplete="address-level2"></label>
                            <label class="au-field"><span>Country</span><input name="country" maxlength="80" autocomplete="country-name"></label>
                        </div>
                        <label class="au-field"><span>Your time zone</span><input name="timezone" maxlength="60"></label>
                    </fieldset>
                    <fieldset class="wb-group">
                        <legend>2. Contact and profile</legend>
                        <label class="au-field"><span>WhatsApp number <em>(with country code)</em></span><input name="phone" type="tel" maxlength="30" placeholder="+234 801 234 5678" autocomplete="tel"></label>
                        <label class="au-field"><span>Your LinkedIn profile link</span><input name="linkedin_url" type="url" maxlength="200" placeholder="https://www.linkedin.com/in/yourname"></label>
                        <label class="au-field"><span>Portfolio or work sample <em>(optional)</em></span><input name="portfolio_url" type="url" maxlength="300" placeholder="A link to anything you've made, organised or written"></label>
                        <div class="au-field"><span>Your CV</span><div class="ap-upload" id="rl-cv"></div></div>
                    </fieldset>
                    <fieldset class="wb-group">
                        <legend>3. Time and motivation</legend>
                        <div class="wb-q"><span class="wb-q__label" id="q-rhours">How many hours a week can you give?</span>
                            <div class="wb-chips" role="radiogroup" aria-labelledby="q-rhours" data-name="hours"></div></div>
                        <label class="au-field"><span>Why do you want this role?</span>
                            <textarea name="why" rows="5" maxlength="2000" placeholder="What draws you to it, and what do you hope to learn?"></textarea><small class="ap-count" data-for="why"></small></label>
                        <label class="au-field"><span>Relevant experience <em>(student groups, volunteering, NYSC CDS, work, anything counts)</em></span>
                            <textarea name="experience" rows="4" maxlength="2000"></textarea></label>
                    </fieldset>
                    <fieldset class="wb-group">
                        <legend>4. Confirm</legend>
                        <label class="ap-check ap-check--req"><input type="checkbox" name="unpaid_ok"> <span id="rl-unpaid">I understand this is an unpaid internship.</span></label>
                        <label class="ap-check"><input type="checkbox" name="consent_keep"> If I'm not selected, you can keep my application for future roles.</label>
                    </fieldset>
                    <div class="wb-actions"><button class="ac-btn ac-btn--primary au-submit" type="submit" id="rl-submit">Submit application</button></div>
                    <p class="wb-privacy">One application per role. Only the Open Fraud Labs team handling applications sees your CV. See our <a href="/privacy/">Privacy Policy</a>.</p>
                </form>
            </div>
        </section>"""

role_script = r"""        (async function () {
            var sb = OFL.sb, el = OFL.el, msg = document.getElementById('msg'), slug = OFL.qs('r');
""" + CV_JS + r"""
            var r = slug ? (await sb.from('roles').select('*').eq('slug', slug).maybeSingle()).data : null;
            if (!r) { document.getElementById('rl-title').textContent = 'Role not found'; document.getElementById('rl-summary').textContent = 'This role may have closed.'; document.getElementById('rl-cta').appendChild(el('a', { class: 'ac-btn ac-btn--secondary', href: '/careers/', text: 'See all roles' })); return; }
            document.title = r.title + ' | Careers | Open Fraud Labs';
            document.getElementById('rl-crumb').textContent = r.title;
            document.getElementById('rl-title').textContent = r.title;
            document.getElementById('rl-summary').textContent = r.summary;
            document.getElementById('rl-eyebrow').textContent = (r.paid ? 'Paid ' : 'Unpaid ') + r.kind + (r.team ? ' · ' + r.team : '');
            var facts = document.getElementById('rl-facts');
            [[r.paid ? 'Paid' : 'Unpaid', r.paid ? '' : 'Experience and a recommendation letter'], [r.location, 'Work from anywhere'], [r.commitment, 'Around your studies or NYSC'], [r.status === 'open' ? (r.rolling ? 'Rolling' : 'Open') : 'Filled', r.status === 'open' ? 'Reviewed as applications arrive' : 'Not taking applications']]
                .forEach(function (f) { if (f[0]) facts.appendChild(el('li', {}, el('b', { text: f[0] }), el('span', { text: f[1] }))); });
            var body = document.getElementById('rl-body');
            function list(title, items) { if (!items || !items.length) return; var ul = el('ul', { class: 'ac-outcomes' }); items.forEach(function (t) { ul.appendChild(el('li', { text: t })); }); body.append(el('h2', { text: title }), ul); }
            list('What you’ll do', r.responsibilities); list('Who we’re looking for', r.requirements); list('What you’ll get', r.benefits);
            body.appendChild(el('p', { class: 'ac-muted ac-small', text: (r.duration ? r.duration + '. ' : '') + (r.paid ? '' : 'This is an unpaid internship: no salary or allowance. ') + (r.rolling ? 'We review applications as they arrive and close the role once it’s filled.' : '') }));
            var user = await OFL.getUser(), next = '/careers/role/?r=' + encodeURIComponent(slug), cta = document.getElementById('rl-cta');
            if (user) {
                var mine = (await sb.rpc('role_application_mine', { p_slug: slug })).data;
                if (mine) return drawStatus(mine);
            }
            if (r.status !== 'open') { cta.appendChild(el('div', { class: 'ac-panel' }, el('h2', { text: 'This role isn’t taking applications' }), el('a', { href: '/careers/', text: 'See other roles' }))); return; }
            if (!user) {
                cta.appendChild(el('div', { class: 'ap-cta' }, el('h2', { text: 'Apply' }), el('p', { class: 'ac-muted', text: 'Create a free Open Fraud Labs account, then fill in the form and attach your CV (about 10 minutes).' }),
                    el('a', { class: 'ac-btn ac-btn--primary', href: '/account/?next=' + encodeURIComponent(next), text: 'Create an account to apply' }),
                    el('p', { class: 'ac-muted ac-small' }, 'Already have one? ', el('a', { href: '/account/?next=' + encodeURIComponent(next), text: 'Log in' }))));
                return;
            }
            var prof = (await sb.from('profiles').select('terms_accepted_at').eq('id', user.id).maybeSingle()).data || {};
            if (!prof.terms_accepted_at) { location.href = '/account/?next=' + encodeURIComponent(next); return; }
            var form = document.getElementById('rl-form'), hasCv = false;
            cta.appendChild(el('h2', { class: 'rl-apply-h', text: 'Apply for this role' }));
            var OPTS = { stage: [['student', 'Student (university or polytechnic)'], ['graduate', 'Recent graduate'], ['corps', 'NYSC corps member'], ['other', 'Other']],
                hours: [['3-5', '3–5 hours'], ['6-8', '6–8 hours'], ['9-12', '9–12 hours'], ['12+', 'More than 12']] };
            form.querySelectorAll('.wb-chips').forEach(function (g) { var n = g.getAttribute('data-name'); (OPTS[n] || []).forEach(function (o) { g.appendChild(el('label', { class: 'wb-chip' }, el('input', { type: 'radio', name: n, value: o[0] }), el('span', { text: o[1] }))); }); });
            try { form.timezone.value = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
            if (r.paid) document.getElementById('rl-unpaid').textContent = 'I’ve read the role details.';
            cvUploader(document.getElementById('rl-cv'), user.id, 'role-' + slug, function () { hasCv = true; });
            var cnt = form.querySelector('.ap-count'); function upd() { var n = form.why.value.trim().length; cnt.textContent = n + ' characters' + (n < 50 ? ' (at least 50)' : ''); cnt.classList.toggle('is-short', n < 50); } form.why.addEventListener('input', upd); upd();
            form.hidden = false;
            form.addEventListener('submit', async function (e) {
                e.preventDefault();
                var f = form, val = function (n) { var x = f.querySelector('input[name="' + n + '"]:checked'); return x ? x.value : null; };
                function stop(t, text) { if (t && t.scrollIntoView) t.scrollIntoView({ block: 'center' }); if (t && t.focus) t.focus(); return OFL.notice(msg, text, 'error'); }
                if (!val('stage')) return stop(f.querySelector('[data-name="stage"]'), 'Tell us where you are now.');
                if (f.phone.value.replace(/\D/g, '').length < 7) return stop(f.phone, 'Add a WhatsApp number we can reach you on.');
                if (!/^https?:\/\/([a-z]+\.)?linkedin\.com\/in\/\S+/i.test(f.linkedin_url.value.trim())) return stop(f.linkedin_url, 'Add your LinkedIn profile link. It starts with https://www.linkedin.com/in/');
                if (!hasCv) return stop(document.getElementById('rl-cv'), 'Upload your CV.');
                if (!val('hours')) return stop(f.querySelector('[data-name="hours"]'), 'Tell us how many hours a week you can give.');
                if (f.why.value.trim().length < 50) return stop(f.why, 'Tell us a little more about why you want this role (at least 50 characters).');
                if (!f.unpaid_ok.checked) return stop(f.unpaid_ok, 'Please confirm before you submit.');
                var b = document.getElementById('rl-submit'); b.disabled = true; b.textContent = 'Submitting…';
                var res = await sb.rpc('role_apply', { p_slug: slug, p_answers: { stage: val('stage'), institution: f.institution.value, course: f.course.value, grad_year: f.grad_year.value, start_date: f.start_date.value || null,
                    city: f.city.value, country: f.country.value, timezone: f.timezone.value, phone: f.phone.value, linkedin_url: f.linkedin_url.value, portfolio_url: f.portfolio_url.value,
                    hours: val('hours'), why: f.why.value, experience: f.experience.value, unpaid_ok: f.unpaid_ok.checked, consent_keep: f.consent_keep.checked } });
                b.disabled = false; b.textContent = 'Submit application';
                if (res.error) return OFL.notice(msg, OFL.friendlyError(res.error), 'error');
                form.hidden = true; cta.textContent = ''; msg.textContent = ''; window.scrollTo({ top: 0, behavior: 'smooth' }); drawStatus(res.data, true);
            });
            function drawStatus(m, fresh) {
                var T = { new: ['Application received', fresh ? 'Thank you for applying' : 'We’re reviewing your application', 'We review applications as they arrive. You’ll hear from us here, by email and possibly on WhatsApp.'],
                    shortlisted: ['Shortlisted', 'You’re shortlisted', 'We’ll be in touch soon about the next step.'],
                    interview: ['Interview', 'We’d like to talk with you', 'We’ll contact you on WhatsApp or by email to agree a time.'],
                    offered: ['Offer', 'We’d like to offer you this role', 'Check your email for the details.'],
                    hired: ['Welcome', 'You’re on the team', 'We’ll share onboarding details with you directly.'],
                    not_progressed: ['Application closed', 'Thank you for applying', 'We won’t be taking your application further for this role, but we’d be glad to see you apply again.'],
                    withdrawn: ['Withdrawn', 'Application withdrawn', ''] }[m.status] || ['Application', 'Your application', ''];
                var box = document.getElementById('rl-status'); box.textContent = '';
                box.appendChild(el('div', { class: 'ap-state' + (m.status === 'hired' || m.status === 'offered' ? ' ap-state--done' : m.status === 'not_progressed' ? ' ap-state--end' : '') },
                    el('span', { class: 'ap-state__tag', text: T[0] }), el('h2', { text: T[1] }), el('p', { text: T[2] })));
            }
        })();"""

page("careers/role", "Role | Careers | Open Fraud Labs", "An open role at Open Fraud Labs.", role_main, role_script, noindex=True)

# ============================================================== Pricing (Paystack passes)
pricing_main = """        <div class="ac-wrap">
            <div class="ac-dash-head">
                <h1>Plans</h1>
                <p class="ac-muted">A pass unlocks every lesson, practice exercise, project and certificate across all Academy courses for the time you choose. Pay once by card, bank transfer or USSD through Paystack. Passes don't renew automatically.</p>
                <div id="msg"></div>
            </div>
            <div id="access"></div>
            <div class="ac-plans" id="plans"><p class="ac-muted">Loading plans…</p></div>
            <p class="ac-muted ac-small">Payments are processed securely by Paystack; Open Fraud Labs never sees your card details. Questions or refunds: academy@openfraudlabs.com.</p>
        </div>"""
pricing_script = """        (async function () {
            var sb = OFL.sb, el = OFL.el, msg = document.getElementById('msg');
            var user = await OFL.getUser();
            var params = new URLSearchParams(location.search), ref = params.get('reference') || params.get('trxref');
            function money(minor, cur) {
                try { return new Intl.NumberFormat(cur === 'NGN' ? 'en-NG' : undefined, { style: 'currency', currency: cur, currencyDisplay: 'narrowSymbol', maximumFractionDigits: 0 }).format(minor / 100); }
                catch (e) { return cur + ' ' + (minor / 100).toLocaleString(); }
            }
            async function call(body) {
                var s = (await sb.auth.getSession()).data.session;
                var r = await sb.functions.invoke('paystack-checkout', { body: body, headers: s ? { Authorization: 'Bearer ' + s.access_token } : {} });
                if (r.error) {
                    var m = 'Something went wrong. Please try again.';
                    try { var j = await r.error.context.json(); if (j && j.error) m = j.error; } catch (e) {}
                    throw new Error(m);
                }
                return r.data;
            }
            async function showAccess() {
                var box = document.getElementById('access'); box.textContent = '';
                if (!user) return;
                var a = (await sb.rpc('my_access')).data || {};
                if (a.active) box.appendChild(el('div', { class: 'ofl-notice ofl-notice--success', text: 'Your pass is active' + (a.until ? ' until ' + OFL.formatDate(a.until) : '') + '. Buying another pass adds time to it.' }));
            }
            if (ref && user) {
                OFL.notice(msg, 'Confirming your payment…', 'info');
                try {
                    var v = await call({ action: 'verify', reference: ref });
                    msg.textContent = '';
                    if (v.status === 'success') OFL.notice(msg, 'Payment received. Thank you! Your access is now active.', 'success');
                    else if (v.status === 'abandoned' || v.status === 'failed') OFL.notice(msg, 'The payment was not completed. You have not been charged.', 'error');
                    else OFL.notice(msg, 'Your payment is still processing. Refresh this page in a minute.', 'info');
                } catch (e) { msg.textContent = ''; OFL.notice(msg, e.message, 'error'); }
                history.replaceState(null, '', location.pathname);
            }
            await showAccess();
            var plans = (await sb.from('plans').select('*').eq('active', true).order('sort')).data || [];
            var box = document.getElementById('plans'); box.textContent = '';
            if (!plans.length) { box.appendChild(el('div', { class: 'ac-panel' }, el('h2', { text: 'Early access: everything is free' }), el('p', { text: 'Plans will appear here soon. For now, every released lesson is open to anyone with a free account.' }), el('a', { class: 'ac-btn ac-btn--primary', href: '/academy/courses/data-science/', text: 'Browse the course' }))); return; }
            var featured = plans.length === 3 ? 1 : -1;
            plans.forEach(function (p, pi) {
                var btn = el('button', { class: 'ac-btn ' + (featured === -1 || pi === featured ? 'ac-btn--primary' : 'ac-btn--secondary'), type: 'button', text: user ? 'Choose ' + p.name : 'Log in to choose' });
                btn.addEventListener('click', async function () {
                    if (!user) { location.href = '/account/?next=' + encodeURIComponent('/academy/pricing/'); return; }
                    btn.disabled = true; msg.textContent = '';
                    try { var r = await call({ action: 'start', plan_id: p.id }); location.href = r.url; }
                    catch (e) { btn.disabled = false; OFL.notice(msg, e.message, 'error'); }
                });
                box.appendChild(el('div', { class: 'ac-plan' + (pi === featured ? ' is-featured' : '') },
                    el('h2', { text: p.name }),
                    el('p', { class: 'ac-plan__price', text: money(p.amount_minor, p.currency) }),
                    el('p', { class: 'ac-muted', text: p.months + (p.months === 1 ? ' month' : ' months') + ' of full access' }),
                    p.blurb ? el('p', { text: p.blurb }) : null,
                    btn));
            });
        })();"""

page("academy/pricing", "Plans | Open Fraud Labs Academy", "Choose an Academy pass to unlock every lesson, project and certificate.",
     pricing_main, pricing_script, noindex=True)

page("academy/admin", "Admin | Open Fraud Labs Academy", "Academy admin.", admin_main, admin_script, noindex=True)


# ============================================================== Redirects from old URLs
redirect("learn/data-science", "location.replace('/academy/courses/data-science/');")
redirect("learn/quiz", "var p=new URLSearchParams(location.search);location.replace('/academy/lesson/?course='+(p.get('course')||'data-science')+'&n='+(p.get('lesson')||'1'));")
redirect("learn/capstone", "location.replace('/academy/capstone/'+location.search);")
redirect("my-learning", "location.replace('/academy/dashboard/');")
redirect("admin", "location.replace('/academy/admin/');")


# ============================================================== Sitemap
import datetime as _dt
_today = _dt.date.today().isoformat()
_main = [("", "1.0", "monthly")]
_urls = "".join(f"  <url><loc>https://openfraudlabs.com/{u}</loc><lastmod>{_today}</lastmod><changefreq>{c}</changefreq><priority>{pr}</priority></url>\n" for u, pr, c in _main)
for pth in PUBLIC_PAGES:
    pr = "0.9" if pth in ("academy", "academy/courses/data-science") else "0.6"
    _urls += f"  <url><loc>https://openfraudlabs.com/{pth}/</loc><lastmod>{_today}</lastmod><changefreq>weekly</changefreq><priority>{pr}</priority></url>\n"
for extra_path in ("privacy", "terms"):
    if os.path.exists(os.path.join(extra_path, "index.html")):
        _urls += f"  <url><loc>https://openfraudlabs.com/{extra_path}/</loc><lastmod>{_today}</lastmod><changefreq>yearly</changefreq><priority>0.3</priority></url>\n"
open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + _urls + "</urlset>\n")
print("wrote sitemap.xml with", _urls.count("<url>"), "urls")
