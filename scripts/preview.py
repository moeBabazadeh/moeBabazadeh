#!/usr/bin/env python3
"""Preview the profile README locally, laid out like a GitHub profile page.

    python3 scripts/preview.py [--port 8000] [--no-open]

Each page load renders README.md through GitHub's Markdown API (via `gh`), so
the HTML is sanitised exactly as it will be on the real profile. That call
only renders; nothing is saved or published. Without `gh`, the page falls
back to rendering the Markdown in the browser.
"""

import argparse
import json
import subprocess
import webbrowser
from functools import partial
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGIN = ROOT.name  # a profile repo is named after its account

CDN = "https://cdnjs.cloudflare.com/ajax/libs"


def gh(*args, body=None):
    try:
        out = subprocess.run(["gh", "api", *args], input=body, capture_output=True,
                             text=True, check=True, timeout=20)
        return out.stdout
    except (OSError, subprocess.SubprocessError):
        return None


def render_markdown(markdown):
    body = json.dumps({"text": markdown, "mode": "gfm", "context": f"{LOGIN}/{LOGIN}"})
    return gh("markdown", "--input", "-", body=body)


def profile():
    data = gh(f"users/{LOGIN}")
    return json.loads(data) if data else {"login": LOGIN}


def page():
    markdown = (ROOT / "README.md").read_text()
    html = render_markdown(markdown)
    user = profile()
    blog = user.get("blog") or ""
    sidebar = "".join(
        f'<div class="meta">{escape(item)}</div>'
        for item in (
            user.get("company"),
            blog,
            f"{user['followers']} followers · {user['following']} following" if "followers" in user else None,
        )
        if item
    )
    return TEMPLATE.format(
        cdn=CDN,
        login=escape(user["login"]),
        name=escape(user.get("name") or ""),
        bio=escape(user.get("bio") or ""),
        avatar=escape(user.get("avatar_url") or ""),
        sidebar=sidebar,
        rendered=html or "",
        source=json.dumps(markdown if html is None else "").replace("<", "\\u003c"),
        renderer="GitHub API" if html is not None else "offline fallback (marked)",
    )


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{login} · profile preview</title>
<link id="md-light" rel="stylesheet" href="{cdn}/github-markdown-css/5.8.1/github-markdown-light.min.css">
<link id="md-dark" rel="stylesheet" href="{cdn}/github-markdown-css/5.8.1/github-markdown-dark.min.css" disabled>
<style>
  :root {{ --bg: #ffffff; --fg: #1f2328; --muted: #59636e; --border: #d0d7de; --bar: #f6f8fa; --btn: #ffffff; --on: #0969da; }}
  :root[data-theme="dark"] {{ --bg: #0d1117; --fg: #e6edf3; --muted: #9198a1; --border: #3d444d; --bar: #010409; --btn: #212830; --on: #4493f8; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--fg); font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif; }}
  .bar {{ position: sticky; top: 0; z-index: 2; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; padding: 10px 16px; background: var(--bar); border-bottom: 1px solid var(--border); }}
  .bar strong {{ margin-right: auto; }}
  .bar .note {{ color: var(--muted); font-size: 12px; }}
  .seg {{ display: inline-flex; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }}
  .seg button {{ border: 0; background: var(--btn); color: var(--fg); padding: 5px 12px; font: inherit; cursor: pointer; }}
  .seg button + button {{ border-left: 1px solid var(--border); }}
  .seg button[aria-pressed="true"] {{ color: var(--on); font-weight: 600; box-shadow: inset 0 -2px 0 var(--on); }}
  .page {{ display: flex; gap: 24px; max-width: 1280px; margin: 0 auto; padding: 24px 32px; }}
  .side {{ width: 296px; flex: none; }}
  .side img {{ width: 100%; border-radius: 50%; border: 1px solid var(--border); }}
  .side h1 {{ margin: 16px 0 0; font-size: 24px; line-height: 1.25; }}
  .side .login {{ color: var(--muted); font-size: 20px; font-weight: 300; }}
  .side .bio {{ margin: 12px 0; }}
  .side .meta {{ color: var(--muted); margin-top: 6px; }}
  .main {{ flex: 1; min-width: 0; }}
  .box {{ border: 1px solid var(--border); border-radius: 6px; padding: 24px; }}
  .box .path {{ font: 12px ui-monospace, SFMono-Regular, Menlo, monospace; color: var(--muted); margin-bottom: 16px; }}
  .markdown-body {{ background: transparent; }}
  .mobile .page {{ flex-direction: column; max-width: 390px; padding: 16px; border-inline: 1px dashed var(--border); }}
  .mobile .side {{ width: auto; display: grid; grid-template-columns: 64px 1fr; column-gap: 12px; align-items: center; }}
  .mobile .side img {{ grid-row: span 2; }}
  .mobile .side h1 {{ margin: 0; font-size: 20px; }}
  .mobile .side .bio, .mobile .side .meta {{ grid-column: 1 / -1; }}
  .mobile .box {{ padding: 16px; }}
</style>
</head>
<body>
<div class="bar">
  <strong>Local preview · not published</strong>
  <span class="note">rendered by {renderer}</span>
  <div class="seg" id="theme">
    <button data-v="system">System</button><button data-v="light">Light</button><button data-v="dark">Dark</button>
  </div>
  <div class="seg" id="width">
    <button data-v="desktop">Desktop</button><button data-v="mobile">Mobile</button>
  </div>
</div>
<div class="page">
  <aside class="side">
    <img src="{avatar}" alt="">
    <h1>{name}</h1>
    <div class="login">{login}</div>
    <div class="bio">{bio}</div>
    {sidebar}
  </aside>
  <main class="main">
    <div class="box">
      <div class="path">{login} / README.md</div>
      <article class="markdown-body" id="readme">{rendered}</article>
    </div>
  </main>
</div>
<script type="application/json" id="source">{source}</script>
<script>
  const readme = document.getElementById("readme");
  const source = JSON.parse(document.getElementById("source").textContent);
  const system = matchMedia("(prefers-color-scheme: dark)");

  function store(key, value) {{ try {{ localStorage.setItem(key, value); }} catch {{}} }}
  function load(key, fallback) {{ try {{ return localStorage.getItem(key) || fallback; }} catch {{ return fallback; }} }}

  function press(group, value) {{
    document.querySelectorAll(`#${{group}} button`).forEach(b => b.setAttribute("aria-pressed", b.dataset.v === value));
  }}

  // GitHub picks <picture> sources by the viewer's theme; mirror that for the chosen one.
  function applyTheme(choice) {{
    const dark = choice === "dark" || (choice === "system" && system.matches);
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    document.getElementById("md-light").disabled = dark;
    document.getElementById("md-dark").disabled = !dark;
    readme.querySelectorAll("picture source[media]").forEach(s => {{
      s.dataset.media ??= s.getAttribute("media");
      const scheme = s.dataset.media.match(/prefers-color-scheme:\\s*(dark|light)/);
      if (scheme) s.media = (scheme[1] === "dark") === dark ? "all" : "not all";
    }});
    press("theme", choice);
    store("theme", choice);
  }}

  function applyWidth(choice) {{
    document.body.classList.toggle("mobile", choice === "mobile");
    press("width", choice);
    store("width", choice);
  }}

  async function boot() {{
    if (!readme.innerHTML.trim() && source.trim()) {{
      await new Promise((ok, fail) => {{
        const s = Object.assign(document.createElement("script"), {{ src: "{cdn}/marked/12.0.2/marked.min.js", onload: ok, onerror: fail }});
        document.head.append(s);
      }});
      readme.innerHTML = marked.parse(source);
    }}
    const params = new URLSearchParams(location.search);
    applyTheme(params.get("theme") || load("theme", "system"));
    applyWidth(params.get("width") || load("width", "desktop"));
    system.addEventListener("change", () => applyTheme(load("theme", "system")));
    document.querySelectorAll("#theme button").forEach(b => b.onclick = () => applyTheme(b.dataset.v));
    document.querySelectorAll("#width button").forEach(b => b.onclick = () => applyWidth(b.dataset.v));
  }}
  boot();
</script>
</body>
</html>
"""


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] not in ("/", "/index.html"):
            return super().do_GET()
        content = page().encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-open", action="store_true", help="don't open a browser")
    args = parser.parse_args()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(ROOT)))
    url = f"http://localhost:{args.port}"
    print(f"Previewing {LOGIN}/README.md at {url}  (Ctrl+C to stop)")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
