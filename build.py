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


# Wording that differs between word games and other games. Existing projects keep these defaults.
DEFAULTS = {
    "progress_items": "collected letter tiles",
    "notifications_text": "If you allow reminders, they are scheduled on your device and nothing about them leaves it",
    "content_assets": "word selections",
    "items_list": "Coins, hints, letter tiles, stickers, costumes",
    "content_title": "Word content",
    "content_text": "The app's word lists are built from public dictionaries and other sources, and are filtered to remove offensive words. The filtering is automated and imperfect. If a word slips through or a valid word is missing, email us and we will review it. We do not guarantee that every word in the game is appropriate, correct or accepted in every region, dialect or spelling.",
    "purchases_list": "coin packs, the Starter Pack and Remove Ads",
    "support_prompt": "Questions, bugs or a word that should be accepted?",
    "achievements_clause": "achievements, ",
    "ad_kinds": "rewarded videos you choose to watch and occasional interstitial ads between levels",
    "remove_ads_effect": "interstitial ads",
    "second_event": "a timed challenge was failed",
    "terms_other_ads": "others appear between levels",
    "terms_remove_ads": "the ads between levels",
    # Used only by the "_free" templates (apps with ads but nothing to buy).
    "stored_items": "the level you are on and your best scores",
    "first_event": "a level was completed",
    "privacy_options_where": 'with "Ad privacy choices" in the Settings of the app',
    "terms_ads_text": "Some ads are optional rewarded videos you choose to watch; others are a small banner on the game screen.",
}

# Projects with "crash_reports": true send crash reports to Sentry; the policy must say so (never hand-edit the built
# HTML for this, a rebuild would drop it).
CRASH_ITEM = (
    '\n    <li>If the app crashes, a crash report is sent to <a href="https://sentry.io/privacy/">Sentry</a>. It contains '
    "technical details only (device model, operating system and app version, and the error), with no name, account or "
    "screenshots. We ask Sentry not to store IP addresses, and reports are used only to fix bugs</li>"
)
SERVICES = {
    False: ("Google, RevenueCat, PostHog, Apple and Expo", "Google, RevenueCat, PostHog, Apple"),
    True: ("Google, RevenueCat, PostHog, Sentry, Apple and Expo", "Google, RevenueCat, PostHog, Sentry, Apple"),
}
# A project with "purchases": false sells nothing: it has no RevenueCat, no Remove Ads and no shop, so it is built
# from the "_free" templates, which say so instead of describing purchases that do not exist.
SERVICES_FREE = {
    False: ("Google, PostHog, Apple and Expo", "Google, PostHog, Apple"),
    True: ("Google, PostHog, Sentry, Apple and Expo", "Google, PostHog, Sentry, Apple"),
}

cards = []
for p in cfg["projects"]:
    out = ROOT / "projects" / p["slug"]
    out.mkdir(parents=True, exist_ok=True)
    latin = f" ({p['latinName']})" if p.get("latinName") else ""
    vars = {k: p[k] for k in ("name", "tagline", "description", "updated")} | {"latin": latin}
    for k, default in DEFAULTS.items():
        vars[k] = p.get(k, default)
    crash = bool(p.get("crash_reports"))
    vars["crash_item"] = CRASH_ITEM if crash else ""
    free = p.get("purchases", True) is False
    kind = "_free" if free else ""
    vars["services_connect"], vars["services_transfer"] = (SERVICES_FREE if free else SERVICES)[crash]
    initial = p.get("latinName", p["name"])[0].upper()
    common_kw = dict(color=p["color"], initial=initial, root="../../")
    footer = f' · <a href="privacy.html">Privacy</a> · <a href="terms.html">Terms</a>'
    (out / "index.html").write_text(page("project" + kind, title=p["name"], meta=p["description"], footer_links=footer, **common_kw, **vars))
    (out / "privacy.html").write_text(page("privacy" + kind, title=f"{p['name']} Privacy Policy", meta=f"Privacy policy for {p['name']}{latin}.", footer_links=footer, **common_kw, **vars))
    (out / "terms.html").write_text(page("terms" + kind, title=f"{p['name']} Terms and Conditions", meta=f"Terms and conditions for {p['name']}{latin}.", footer_links=footer, **common_kw, **vars))
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
