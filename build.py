#!/usr/bin/env python3
"""Builds the static site from projects.json and templates/.

Add a project to projects.json and run `python3 build.py`. Each project gets
projects/<slug>/index.html, privacy.html and terms.html; the root index.html
lists them all. Everything else at the root (app-ads.txt, .nojekyll) is kept.
"""
import json
import pathlib
import urllib.parse

ROOT = pathlib.Path(__file__).parent
T = {p.stem: (ROOT / "templates" / p.name).read_text() for p in (ROOT / "templates").glob("*.html")}
cfg = json.loads((ROOT / "projects.json").read_text())
common = {"owner": cfg["owner"], "email": cfg["email"]}


def page(template, *, title, meta, color, initial, root, footer_links="", **vars):
    body = T[template].format(**common, **vars, initial=initial)
    return T["base"].format(
        title=title, meta=meta, color=color, color_enc=urllib.parse.quote(color),
        initial=initial, root=root, body=body, footer_links=footer_links, **common,
    )


cards = []
for p in cfg["projects"]:
    out = ROOT / "projects" / p["slug"]
    out.mkdir(parents=True, exist_ok=True)
    latin = f" ({p['latinName']})" if p.get("latinName") else ""
    vars = {k: p[k] for k in ("name", "tagline", "description", "updated")} | {"latin": latin}
    initial = p.get("latinName", p["name"])[0].upper()
    common_kw = dict(color=p["color"], initial=initial, root="../../")
    footer = f' · <a href="privacy.html">Privacy</a> · <a href="terms.html">Terms</a>'
    (out / "index.html").write_text(page("project", title=p["name"], meta=p["description"], footer_links=footer, **common_kw, **vars))
    (out / "privacy.html").write_text(page("privacy", title=f"{p['name']} Privacy Policy", meta=f"Privacy policy for {p['name']}{latin}.", footer_links=footer, **common_kw, **vars))
    (out / "terms.html").write_text(page("terms", title=f"{p['name']} Terms and Conditions", meta=f"Terms and conditions for {p['name']}{latin}.", footer_links=footer, **common_kw, **vars))
    cards.append(
        f'    <a class="card" href="projects/{p["slug"]}/index.html"><h3>{p["name"]}{latin}</h3>'
        f'<p>{p["language"]} · {p["tagline"]}</p>'
        f'<p class="links"><span>Privacy</span><span>Terms</span></p></a>'
    )

(ROOT / "index.html").write_text(page(
    "hub", title=f"{cfg['owner']} · Projects", meta="Privacy policies and terms for apps by " + cfg["owner"],
    color=cfg["projects"][0]["color"], initial=cfg["owner"][0], root="", cards="\n".join(cards),
))
print(f"built {len(cfg['projects'])} projects")
