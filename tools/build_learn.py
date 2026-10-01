"""Rebuild the homepage Learn section as a course catalog and create the Data Science course page.

Run from the lab-docs repo root: python3 <this file>
"""
import json, re, urllib.request

TT = "https://www.tiktok.com/@_drhola"
REPO = "https://github.com/Odugbile1993/openfraudlab-tiktok"
RAW = "https://raw.githubusercontent.com/Odugbile1993/openfraudlab-tiktok/main/"
CSSV = "20261001c"

curriculum = json.load(urllib.request.urlopen(RAW + "curriculum.json"))["lessons"]
state = json.load(urllib.request.urlopen(RAW + "state.json"))
NEXT = state["next_lesson"]
released = [l for l in curriculum if l["n"] < NEXT]

MODULES = [(1, 3, "Module 1 · Foundations"), (4, 14, "Module 2 · Statistics & Exploring Data"),
           (15, 17, "Module 3 · Tools of the Trade"), (18, 27, "Module 4 · Machine Learning Essentials"),
           (28, 30, "Module 5 · Responsible Data Science & Next Steps")]

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

ICONS = {
    "follow": '<circle cx="9" cy="8" r="4"></circle><path d="M2 20c0-3.3 3.1-6 7-6s7 2.7 7 6"></path><path d="M19 8v6"></path><path d="M16 11h6"></path>',
    "like": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"></path>',
    "share": '<circle cx="18" cy="5" r="2.5"></circle><circle cx="6" cy="12" r="2.5"></circle><circle cx="18" cy="19" r="2.5"></circle><path d="m8.2 10.8 7.6-4.4"></path><path d="m8.2 13.2 7.6 4.4"></path>',
    "comment": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"></path>',
    "ds": '<path d="M4 19V5"></path><path d="M4 19h16"></path><circle cx="9" cy="13" r="1.4"></circle><circle cx="13" cy="10" r="1.4"></circle><circle cx="17" cy="7" r="1.4"></circle>',
    "da": '<path d="M5 19V11"></path><path d="M12 19V5"></path><path d="M19 19v-7"></path><path d="M3 19h18"></path>',
    "de": '<ellipse cx="12" cy="6" rx="7" ry="2.5"></ellipse><path d="M5 6v6c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V6"></path><path d="M5 12v6c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5v-6"></path>',
    "ml": '<circle cx="6" cy="7" r="2"></circle><circle cx="6" cy="17" r="2"></circle><circle cx="18" cy="12" r="2"></circle><path d="m8 7.8 8 3.4"></path><path d="m8 16.2 8-3.4"></path>',
    "fa": '<path d="M12 3 5 6v5c0 4.4 3 8.3 7 10 4-1.7 7-5.6 7-10V6z"></path><path d="m9 12 2 2 4-4"></path>',
    "live": '<rect x="3" y="6" width="13" height="12" rx="2"></rect><path d="m16 10 5-3v10l-5-3"></path>',
}

def svg(k):
    return f'<svg viewBox="0 0 24 24">{ICONS[k]}</svg>'

STEPS = [("follow", "Follow", "Follow @_drhola so you never miss a lesson"),
         ("like", "Like", "Like each video to help it reach more learners"),
         ("share", "Share", "Share with a friend who wants to learn data science"),
         ("comment", "Comment", "Ask questions in the comments. They shape future lessons")]

def steps_html(indent):
    out = []
    for i, (k, label, body) in enumerate(STEPS, 1):
        out.append(f'''{indent}<a class="learn-step card card--interactive" href="{TT}" target="_blank" rel="noopener noreferrer">
{indent}    <span class="service-card__icon" aria-hidden="true">{svg(k)}</span>
{indent}    <strong>{i}. {label}</strong>
{indent}    <span>{body}</span>
{indent}</a>''')
    return "\n".join(out)

COMING = [("da", "Data Analysis", "Spreadsheets, SQL and dashboards that turn raw data into clear business answers."),
          ("de", "Data Engineering", "Pipelines, warehouses and data modelling: how reliable data reaches analysts and models."),
          ("ml", "Machine Learning", "Build, evaluate and explain models, from regression to gradient boosting."),
          ("fa", "Fraud Analytics", "Detect, investigate and prevent fraud with data, rules and machine learning."),
          ("live", "Live Classes", "Interactive live sessions with Q&amp;A for the Open Fraud Labs learning community.")]

coming_cards = "\n".join(f'''                    <article class="course-card course-card--soon card">
                        <span class="course-card__badge course-card__badge--soon">Coming soon</span>
                        <span class="service-card__icon" aria-hidden="true">{svg(k)}</span>
                        <h3>{t}</h3>
                        <p>{d}</p>
                    </article>''' for k, t, d in COMING)

home_section = f'''        <section id="learn" class="section learn-section" aria-labelledby="learn-heading">
            <div class="container">
                <div class="section-header section-heading">
                    <p class="section-kicker">Learn with Open Fraud Labs</p>
                    <h2 id="learn-heading">Free courses for the next generation of data talent</h2>
                    <p>Short, beginner-friendly video lessons by Ayodele Odugbile, released daily on TikTok. Start with Data Science from Scratch; more tracks are on the way.</p>
                </div>

                <div class="learn-strip card">
                    <p><strong>New here?</strong> Follow <strong>@_drhola</strong> on TikTok, then like, share and comment on each lesson.</p>
                    <a class="btn btn-primary" href="{TT}" target="_blank" rel="noopener noreferrer">Follow on TikTok</a>
                </div>

                <div class="course-grid">
                    <a class="course-card course-card--live card card--interactive" href="/learn/data-science/">
                        <span class="course-card__badge">Available now</span>
                        <span class="service-card__icon" aria-hidden="true">{svg("ds")}</span>
                        <h3>Data Science from Scratch</h3>
                        <p>Data, statistics and machine learning basics, one 90-second lesson at a time.</p>
                        <span class="course-card__meta" data-course-count>{len(released)} of {len(curriculum)} lessons released</span>
                        <span class="service-card__link">Start learning <span aria-hidden="true">→</span></span>
                    </a>
{coming_cards}
                </div>
            </div>
        </section>

'''

LOADER = f'''    <script>
        // Keeps lesson counts and lists current from the course outline (new lessons are added daily).
        (function () {{
            var RAW = '{RAW}';
            if (!window.fetch) return;
            Promise.all([
                fetch(RAW + 'curriculum.json', {{ cache: 'no-cache' }}).then(function (r) {{ return r.json(); }}),
                fetch(RAW + 'state.json', {{ cache: 'no-cache' }}).then(function (r) {{ return r.json(); }})
            ]).then(function (res) {{
                var all = res[0].lessons || [];
                var next = res[1].next_lesson;
                var released = all.filter(function (l) {{ return l.n < next; }}).length;
                document.querySelectorAll('[data-course-count]').forEach(function (el) {{
                    el.textContent = released + ' of ' + Math.max(all.length, released) + ' lessons released';
                }});
                if (window.renderLessons) window.renderLessons(all, next);
            }}).catch(function () {{ /* keep the built-in content */ }});
        }})();
    </script>
'''

# ---------------- homepage ----------------
p = "index.html"
s = open(p).read()
s = re.sub(r'        <section id="learn".*?</section>\n\n', lambda m: home_section, s, count=1, flags=re.S)
s = re.sub(r'    <script>\n        // Keep "Latest lessons" current.*?</script>\n', lambda m: LOADER, s, count=1, flags=re.S)
s = re.sub(r'assets/css/style\.css\?v=\w+', f'assets/css/style.css?v={CSSV}', s)
open(p, "w").write(s)

# ---------------- course page ----------------
head_end = s.index("</head>")
head = s[:head_end]
head = re.sub(r"<title>.*?</title>", "<title>Data Science from Scratch | Open Fraud Labs</title>", head, flags=re.S)
head = re.sub(r'<meta name="description" content="[^"]*">',
              '<meta name="description" content="A free, beginner-friendly data science course by Ayodele Odugbile: 90-second video lessons on TikTok, with study notes and practice exercises.">', head)
head = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Data Science from Scratch | Open Fraud Labs">', head)
head = re.sub(r'<meta property="og:description" content="[^"]*">',
              '<meta property="og:description" content="Free 90-second data science lessons, released daily on TikTok, with study notes and exercises.">', head)
head = re.sub(r'<meta name="keywords" content="[^"]*">',
              '<meta name="keywords" content="data science course, learn data science, free data science lessons, machine learning, statistics, Open Fraud Labs">', head)
head = head.replace(f'href="assets/css/style.css?v={CSSV}"', f'href="/assets/css/style.css?v={CSSV}"')

body_start = s.index("<body>")
header_end = s.index("</header>") + len("</header>")
header = s[body_start:header_end]
header = header.replace('src="assets/logo.png"', 'src="/assets/logo.png"')
for a in ["services", "approach", "learn", "contact"]:
    header = header.replace(f'href="#{a}"', f'href="/#{a}"')

foot_start = s.index('    <script>\n        const navToggle')
footer = s[foot_start:]
footer = footer.replace(LOADER, "")
footer = footer.replace('src="assets/logo.png"', 'src="/assets/logo.png"')
for a in ["services", "approach", "learn", "contact"]:
    footer = footer.replace(f'href="#{a}"', f'href="/#{a}"')

def module_of(n):
    for lo, hi, name in MODULES:
        if lo <= n <= hi:
            return name
    return "Module 6 · Going Further"

def lesson_row(l):
    n, t = l["n"], esc(l["title"])
    if n < NEXT:
        return f'''                            <li class="lesson-row" data-lesson="{n}">
                                <span class="lesson-row__num">{n:02d}</span>
                                <span class="lesson-row__title">{t}</span>
                                <span class="lesson-row__actions">
                                    <a class="lesson-row__watch" href="{TT}" target="_blank" rel="noopener noreferrer">Watch on TikTok</a>
                                    <a class="lesson-row__quiz" href="/learn/quiz/?course=data-science&amp;lesson={n}">Quiz</a>
                                    <a class="lesson-row__notes" href="{REPO}/blob/main/notes/lesson-{n:02d}.md" target="_blank" rel="noopener noreferrer">Notes</a>
                                </span>
                            </li>'''
    return f'''                            <li class="lesson-row lesson-row--soon">
                                <span class="lesson-row__num">{n:02d}</span>
                                <span class="lesson-row__title">{t}</span>
                                <span class="lesson-row__actions"><span class="lesson-row__soon">Coming soon</span></span>
                            </li>'''

groups, order = {}, []
for l in curriculum:
    m = module_of(l["n"])
    if m not in groups:
        groups[m] = []; order.append(m)
    groups[m].append(l)
modules_html = "\n".join(f'''                    <div class="lesson-module">
                        <h3>{esc(m)}</h3>
                        <ol class="lesson-list">
{chr(10).join(lesson_row(l) for l in groups[m])}
                        </ol>
                    </div>''' for m in order)

RENDER = f'''    <script>
        // Rebuilds the lesson list from the live course outline.
        window.renderLessons = function (all, next) {{
            var TIKTOK = '{TT}', NOTES = '{REPO}/blob/main/notes/lesson-';
            var MODULES = {json.dumps([[a, b, c] for a, b, c in MODULES])};
            var box = document.getElementById('lesson-modules');
            if (!box || !all.length) return;
            function mod(n) {{ for (var i = 0; i < MODULES.length; i++) if (n >= MODULES[i][0] && n <= MODULES[i][1]) return MODULES[i][2]; return 'Module 6 · Going Further'; }}
            function el(tag, cls, text) {{ var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }}
            function link(cls, href, text) {{ var a = el('a', cls, text); a.href = href; a.target = '_blank'; a.rel = 'noopener noreferrer'; return a; }}
            box.textContent = '';
            var current = null, list = null;
            all.forEach(function (l) {{
                var m = mod(l.n);
                if (m !== current) {{
                    current = m;
                    var wrap = el('div', 'lesson-module');
                    wrap.appendChild(el('h3', '', m));
                    list = el('ol', 'lesson-list');
                    wrap.appendChild(list);
                    box.appendChild(wrap);
                }}
                var nn = (l.n < 10 ? '0' : '') + l.n;
                var row = el('li', 'lesson-row' + (l.n < next ? '' : ' lesson-row--soon'));
                row.setAttribute('data-lesson', l.n);
                row.appendChild(el('span', 'lesson-row__num', nn));
                row.appendChild(el('span', 'lesson-row__title', l.title));
                var act = el('span', 'lesson-row__actions');
                if (l.n < next) {{
                    act.appendChild(link('lesson-row__watch', TIKTOK, 'Watch on TikTok'));
                    var qz = el('a', 'lesson-row__quiz', 'Quiz'); qz.href = '/learn/quiz/?course=data-science&lesson=' + l.n; act.appendChild(qz);
                    act.appendChild(link('lesson-row__notes', NOTES + nn + '.md', 'Notes'));
                }} else {{
                    act.appendChild(el('span', 'lesson-row__soon', 'Coming soon'));
                }}
                row.appendChild(act);
                list.appendChild(row);
            }});
            if (window.markProgress) window.markProgress();
        }};
    </script>
'''

course_main = f'''    <main id="main-content">
        <section class="section course-hero">
            <div class="container">
                <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/#learn">Learn</a> <span aria-hidden="true">/</span> Data Science from Scratch</nav>
                <div class="section-header section-heading">
                    <p class="section-kicker">Free course · Beginner</p>
                    <h1>Data Science from Scratch</h1>
                    <p>One idea per lesson, explained in plain language in about 90 seconds, by Ayodele Odugbile. New lessons are released every day on TikTok, each with study notes and a short exercise.</p>
                    <p class="course-hero__meta" data-course-count>{len(released)} of {len(curriculum)} lessons released</p>
                </div>

                <div class="ofl-card card ofl-course-progress" id="my-progress">
                    <div>
                        <h2>Track your progress &amp; earn a certificate</h2>
                        <p>Create a free account, pass the quiz after each lesson, complete the capstone project, and claim your Open Fraud Labs certificate of completion.</p>
                    </div>
                    <div class="ofl-actions">
                        <a class="btn btn-primary" href="/account/?next=/learn/data-science/">Create free account</a>
                        <a class="btn btn-secondary" href="/account/?mode=login&amp;next=/learn/data-science/">Log in</a>
                    </div>
                </div>

                <div class="learn-cta card">
                    <p class="learn-cta__title">Before you watch, join the community on TikTok:</p>
                    <div class="learn-steps">
{steps_html("                        ")}
                    </div>
                    <div class="learn-cta__actions">
                        <a class="btn btn-primary" href="{TT}" target="_blank" rel="noopener noreferrer">Follow &amp; Watch on TikTok</a>
                        <a class="btn btn-secondary" href="{REPO}" target="_blank" rel="noopener noreferrer">Study Notes on GitHub →</a>
                    </div>
                </div>
            </div>
        </section>

        <section class="section course-lessons" aria-labelledby="lessons-heading">
            <div class="container">
                <div class="section-header section-heading">
                    <p class="section-kicker">Course map</p>
                    <h2 id="lessons-heading">All lessons</h2>
                    <p>Work through the lessons in order. Each one builds on the last.</p>
                </div>
                <div id="lesson-modules">
{modules_html}
                </div>

                <div class="ofl-card card ofl-capstone-card">
                    <p class="section-kicker">Final step</p>
                    <h3>Capstone project</h3>
                    <p>Bring the course together in one small, real analysis of a public dataset. Once it&rsquo;s approved and every lesson quiz is passed, you can claim your certificate.</p>
                    <a class="btn btn-secondary" href="/learn/capstone/?course=data-science">Read the capstone brief</a>
                </div>

                <div class="course-next card">
                    <h3>Coming next</h3>
                    <p>Full lesson videos right here on openfraudlabs.com, and live classes with Q&amp;A. Follow <a href="{TT}" target="_blank" rel="noopener noreferrer">@_drhola on TikTok</a> to hear first.</p>
                </div>
            </div>
        </section>
    </main>

'''

PROGRESS = '''    <script src="/assets/js/vendor/supabase-2.117.2.js"></script>
    <script src="/assets/js/learn.js?v=''' + CSSV + '''"></script>
    <script>
        // Logged-in learners: show progress and tick passed lessons.
        window.markProgress = async function () {
            if (!window.OFL) return;
            var user = await OFL.getUser(); if (!user) return;
            var r = await OFL.sb.from('lesson_progress').select('lesson_n').eq('course_slug', 'data-science');
            var done = {}; (r.data || []).forEach(function (x) { done[x.lesson_n] = true; });
            document.querySelectorAll('.lesson-row[data-lesson]').forEach(function (row) {
                var n = +row.getAttribute('data-lesson');
                if (done[n]) { row.classList.add('is-done'); var q = row.querySelector('.lesson-row__quiz'); if (q) q.textContent = '\u2713 Passed'; }
            });
            var count = Object.keys(done).length, box = document.getElementById('my-progress');
            var pct = Math.round(100 * count / 30);
            box.textContent = '';
            box.appendChild(OFL.el('div', {}, OFL.el('h2', { text: 'Your progress: ' + count + ' of 30 lessons' }),
                OFL.el('div', { class: 'ofl-progress' }, OFL.el('span', { style: 'width:' + pct + '%' }))));
            box.appendChild(OFL.el('div', { class: 'ofl-actions' }, OFL.el('a', { class: 'btn btn-primary', href: '/my-learning/', text: 'My Learning' })));
        };
        markProgress();
    </script>
'''
page = head + "</head>\n" + header + "\n\n" + course_main + RENDER + PROGRESS + LOADER + footer
import os
os.makedirs("learn/data-science", exist_ok=True)
open("learn/data-science/index.html", "w").write(page)
print("released", len(released), "of", len(curriculum))
