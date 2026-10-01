/* Open Fraud Labs Academy: in-browser Python code lab (Pyodide). Nothing is installed on the learner's device. */
(function () {
    'use strict';

    var PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.29.5/full/';
    var DATA_URL = 'https://raw.githubusercontent.com/Odugbile1993/openfraudlab-tiktok/main/data/loans.csv';
    var COLAB = 'https://colab.research.google.com/github/Odugbile1993/openfraudlab-tiktok/blob/main/notebooks/';

    // Runs learner code like a notebook cell: prints go to the output, and the last line's value is shown.
    var HARNESS = [
        'import ast, io, sys, contextlib, traceback',
        'import pandas as pd',
        'import pyodide.http',
        'if not getattr(pd.read_csv, "_ofl", False):',
        '    _orig_read_csv = pd.read_csv',
        '    def _ofl_read_csv(f, *a, **k):',
        '        if isinstance(f, str) and f.startswith(("http://", "https://")):',
        '            f = pyodide.http.open_url(f)',
        '        return _orig_read_csv(f, *a, **k)',
        '    _ofl_read_csv._ofl = True',
        '    pd.read_csv = _ofl_read_csv',
        'def _ofl_html(v):',
        '    if isinstance(v, pd.DataFrame): return v.to_html(max_rows=20, max_cols=12, border=0, classes="lab-df")',
        '    if isinstance(v, pd.Series): return v.to_frame().to_html(max_rows=20, border=0, classes="lab-df")',
        '    return None',
        'def _ofl_err(e):',
        '    tb = traceback.extract_tb(e.__traceback__)',
        '    lines = [f.lineno for f in tb if f.filename == "<lab>"]',
        '    where = f" (line {lines[-1]})" if lines else ""',
        '    return f"{type(e).__name__}{where}: {e}"',
        'def _ofl_run(src, ns):',
        '    out, html, err = io.StringIO(), None, None',
        '    try:',
        '        tree = ast.parse(src, "<lab>")',
        '        last = None',
        '        if tree.body and isinstance(tree.body[-1], ast.Expr):',
        '            last = ast.Expression(tree.body.pop().value)',
        '        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):',
        '            exec(compile(tree, "<lab>", "exec"), ns)',
        '            if last is not None:',
        '                v = eval(compile(last, "<lab>", "eval"), ns)',
        '                if v is not None:',
        '                    html = _ofl_html(v)',
        '                    if html is None:',
        '                        if hasattr(v, "item") and getattr(v, "ndim", 1) == 0: v = v.item()',
        '                        print(repr(v))',
        '    except SyntaxError as e:',
        '        err = f"SyntaxError (line {e.lineno}): {e.msg}"',
        '    except Exception as e:',
        '        err = _ofl_err(e)',
        '    return out.getvalue(), html, err',
        'def _ofl_ns():',
        '    return {"DATA_URL": DATA_URL}',
        'def _ofl_check(src, check):',
        '    ns = {"DATA_URL": DATA_URL}',
        '    out, html, err = _ofl_run(src, ns)',
        '    if err: return False, "Your code stopped with an error: " + err',
        '    try:',
        '        exec(compile(check, "<check>", "exec"), ns)',
        '        return True, "Correct! Well done."',
        '    except AssertionError as e:',
        '        return False, str(e) or "Not quite yet. Read the task again and compare your output."',
        '    except NameError as e:',
        '        return False, "Something the task asks for is missing: " + str(e)',
        '    except Exception as e:',
        '        return False, "Not quite yet: " + _ofl_err(e)'
    ].join('\n');

    var loading = null;
    function loadPython(status) {
        if (loading) return loading;
        loading = new Promise(function (resolve, reject) {
            status('Loading Python in your browser. The first time takes a few seconds…');
            var s = document.createElement('script');
            s.src = PYODIDE + 'pyodide.js';
            s.onload = async function () {
                try {
                    var py = await window.loadPyodide({ indexURL: PYODIDE });
                    status('Loading pandas…');
                    await py.loadPackage(['pandas']);
                    py.globals.set('DATA_URL', DATA_URL);
                    await py.runPythonAsync(HARNESS);
                    resolve(py);
                } catch (e) { loading = null; reject(e); }
            };
            s.onerror = function () { loading = null; reject(new Error('Python could not be loaded. Check your connection and try again.')); };
            document.head.appendChild(s);
        });
        return loading;
    }

    function store(key, val) {
        try { if (val === undefined) return localStorage.getItem(key); localStorage.setItem(key, val); } catch (e) { return null; }
    }

    function mount(box, practice, opts) {
        var el = window.OFL.el;
        var key = 'ofl-lab:' + opts.course + ':' + opts.lesson + (opts.ex ? ':' + opts.ex : '');
        var ns = null, running = false;
        box.textContent = '';

        var task = el('div', { class: 'lab-task' },
            el('span', { class: 'lab-eyebrow', text: opts.label || 'Practice · not graded' }),
            el('h2', { text: practice.title }),
            el('p', { text: practice.prompt }));
        var ed = el('textarea', { class: 'lab-editor', spellcheck: 'false', autocapitalize: 'off', autocomplete: 'off', 'aria-label': 'Python code editor', rows: '14' });
        ed.value = store(key) || practice.starter;
        var runBtn = el('button', { class: 'ac-btn ac-btn--primary ac-btn--sm', type: 'button', text: 'Run code' });
        var chkBtn = el('button', { class: 'ac-btn ac-btn--secondary ac-btn--sm', type: 'button', text: 'Check my answer' });
        var hintBtn = el('button', { class: 'ac-btn ac-btn--ghost ac-btn--sm', type: 'button', text: 'Hint' });
        var solBtn = el('button', { class: 'ac-btn ac-btn--ghost ac-btn--sm', type: 'button', text: 'Show a solution', hidden: true });
        var resetBtn = el('button', { class: 'ac-btn ac-btn--ghost ac-btn--sm', type: 'button', text: 'Reset' });
        var colab = el('a', { class: 'ac-btn ac-btn--ghost ac-btn--sm', href: COLAB + 'lesson-' + ('0' + opts.lesson).slice(-2) + '.ipynb', target: '_blank', rel: 'noopener noreferrer', text: 'Open in Colab' });
        var status = el('p', { class: 'lab-status', role: 'status' });
        var out = el('div', { class: 'lab-out', 'aria-live': 'polite' });
        var verdict = el('div', { class: 'lab-verdict' });
        box.appendChild(task);
        box.appendChild(el('div', { class: 'lab-shell' },
            el('div', { class: 'lab-bar' }, el('span', { text: 'lesson.py' }), el('small', { text: 'Ctrl + Enter to run' })),
            ed));
        box.appendChild(el('div', { class: 'lab-actions' }, runBtn, chkBtn, hintBtn, solBtn, resetBtn, colab));
        box.appendChild(status);
        box.appendChild(verdict);
        box.appendChild(out);
        box.appendChild(el('p', { class: 'ac-muted lab-note', text: 'Your code runs privately in your browser, and is saved on this device. DATA_URL is the address of the practice loans dataset.' }));

        function say(t) { status.textContent = t || ''; }
        function busy(b) { running = b; runBtn.disabled = chkBtn.disabled = b; }

        ed.addEventListener('input', function () { store(key, ed.value); });
        ed.addEventListener('keydown', function (e) {
            if (e.key === 'Tab' && !e.shiftKey) {
                e.preventDefault();
                var s = ed.selectionStart, t = ed.selectionEnd;
                ed.value = ed.value.slice(0, s) + '    ' + ed.value.slice(t);
                ed.selectionStart = ed.selectionEnd = s + 4; store(key, ed.value);
            } else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); run(); }
        });

        async function ready() {
            var py = await loadPython(say);
            if (!ns) ns = py.globals.get('_ofl_ns')();
            return py;
        }
        async function run() {
            if (running) return; busy(true); verdict.textContent = '';
            try {
                var py = await ready();
                say('Running…');
                var res = py.globals.get('_ofl_run')(ed.value, ns).toJs();
                out.textContent = '';
                if (res[0]) out.appendChild(el('pre', { class: 'lab-stdout', text: res[0] }));
                if (res[1]) { var d = el('div', { class: 'lab-table' }); d.innerHTML = res[1]; out.appendChild(d); }
                if (res[2]) out.appendChild(el('pre', { class: 'lab-err', text: res[2] }));
                if (!res[0] && !res[1] && !res[2]) out.appendChild(el('p', { class: 'ac-muted', text: 'Ran with no output. Add print(...) or put a value on the last line to see it.' }));
                say('');
            } catch (e) { say(e.message || String(e)); }
            busy(false);
        }
        async function check() {
            if (running) return; busy(true);
            try {
                var py = await ready();
                say('Checking…');
                var r = py.globals.get('_ofl_check')(ed.value, practice.check).toJs();
                verdict.textContent = '';
                verdict.appendChild(el('div', { class: 'ofl-notice ofl-notice--' + (r[0] ? 'success' : 'info'), text: r[1] }));
                if (r[0] && opts.onPass) opts.onPass();
                if (!r[0]) solBtn.hidden = false;
                say('');
            } catch (e) { say(e.message || String(e)); }
            busy(false);
        }
        runBtn.addEventListener('click', run);
        chkBtn.addEventListener('click', check);
        hintBtn.addEventListener('click', function () { verdict.textContent = ''; verdict.appendChild(el('div', { class: 'ofl-notice ofl-notice--info', text: practice.hint })); });
        solBtn.addEventListener('click', function () {
            verdict.textContent = '';
            verdict.appendChild(el('div', { class: 'lab-solution' },
                el('p', { text: 'One way to solve it. Try typing it yourself rather than copying, then run it and check again.' }),
                el('pre', { text: practice.solution })));
        });
        resetBtn.addEventListener('click', function () {
            if (ed.value !== practice.starter && !window.confirm('Reset the editor to the starter code? Your changes will be lost.')) return;
            ed.value = practice.starter; store(key, ed.value); out.textContent = ''; verdict.textContent = ''; ns = null;
        });
    }

    // Several exercises per lesson, with a switcher and progress kept on this device.
    function mountSet(box, exercises, opts) {
        var el = window.OFL.el, base = 'ofl-lab-done:' + opts.course + ':' + opts.lesson + ':';
        box.textContent = '';
        var bar = el('div', { class: 'lab-switch', role: 'tablist', 'aria-label': 'Exercises' });
        var inner = el('div');
        box.appendChild(bar); box.appendChild(inner);
        function solved(i) { return store(base + i) === '1'; }
        function count() { var c = 0; exercises.forEach(function (_, i) { if (solved(i)) c++; }); return c; }
        var btns = [];
        function paint(cur) {
            btns.forEach(function (b, i) {
                b.setAttribute('aria-selected', String(i === cur));
                b.classList.toggle('is-done', solved(i));
            });
            if (opts.onProgress) opts.onProgress(count(), exercises.length);
        }
        function open(i) {
            mount(inner, exercises[i], { course: opts.course, lesson: opts.lesson, ex: i ? String(i + 1) : '',
                label: 'Exercise ' + (i + 1) + ' of ' + exercises.length + ' · practice, not graded',
                onPass: function () { store(base + i, '1'); paint(i); } });
            paint(i);
        }
        exercises.forEach(function (ex, i) {
            var b = el('button', { class: 'lab-pill', type: 'button', role: 'tab' }, el('b', { text: String(i + 1) }), el('span', { text: ex.title }));
            b.addEventListener('click', function () { open(i); });
            btns.push(b); bar.appendChild(b);
        });
        var first = 0; while (first < exercises.length - 1 && solved(first)) first++;
        open(first);
        return { solved: count, total: exercises.length };
    }

    window.CODELAB = { mount: mount, mountSet: mountSet, DATA_URL: DATA_URL };
})();
