# henok-tasissa.github.io

Privacy policies and terms for my apps, one folder per project. Published with
GitHub Pages from the `main` branch.

```
index.html                     # hub listing every project
app-ads.txt                    # AdMob authorised sellers (root of the domain, shared by all apps)
projects/<slug>/index.html     # app page: description, support, legal links
projects/<slug>/privacy.html
projects/<slug>/terms.html
projects.json                  # the source of truth
templates/                     # base layout + one template per page type
build.py                       # projects.json + templates → HTML
```

## Adding a project

1. Add an entry to `projects.json` (`slug`, `name`, `tagline`, `language`,
   `description`, `bundleId`, `color`, `updated`, and optionally `latinName`).
2. `python3 build.py`
3. Commit and push. The pages appear at
   `https://henok-tasissa.github.io/projects/<slug>/privacy.html` and `.../terms.html`.

The privacy and terms templates describe a free app with AdMob ads, store
purchases through RevenueCat, no accounts and progress stored on the device.
Set `"crash_reports": true` on a project that ships Sentry; the policy then
names it. Never hand-edit the built HTML: `build.py` overwrites it.
Edit `templates/privacy.html` / `templates/terms.html` if a project differs,
or add a per-project template and point `build.py` at it.
