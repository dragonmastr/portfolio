# hardikmurdiac20.com

Personal site for Hardik Murdia — Site Reliability Engineer and Technical Lead.

A single static page. No build step, no dependencies, no framework. Every image is
inlined as a data URI, so `index.html` renders correctly on its own if you open it
straight from disk.

## Layout

```
index.html                    the entire site — markup, CSS and JS in one file
404.html                      styled not-found page
favicon.svg
og-image.png                  link preview card for LinkedIn, Slack, WhatsApp
CNAME                         custom domain for GitHub Pages — do not delete
robots.txt
sitemap.xml
scripts/check.py              pre-deploy validation, runs in CI
.github/workflows/deploy.yml  builds and deploys on every push to main
```

## Working on it

Open `index.html` in a browser. That's the whole loop — edit, save, refresh.

If you want a local server (so root-relative paths like `/favicon.svg` resolve
the way they will in production):

```sh
python3 -m http.server 8000
```

Then visit http://localhost:8000.

Before pushing, run the same checks CI runs:

```sh
python3 scripts/check.py
```

It verifies tags are balanced, CSS braces match, every class in the markup has a
rule behind it, every tab points at a panel that exists, and every in-page anchor
has a target. It exits non-zero on failure, so a broken page never deploys.

## Deploying

Deployment is automatic. Push to `main` and the workflow validates the page and
publishes it. A deploy takes roughly a minute; watch it under the repo's **Actions**
tab.

```sh
git add -A
git commit -m "Update the Storm case study"
git push
```

Nothing else to run. No manual build, no upload step.

## First-time setup

### 1. Create the repository

```sh
git init
git add -A
git commit -m "Initial commit"
git branch -M main
git remote add origin git@github.com:<your-username>/<repo-name>.git
git push -u origin main
```

The repo must be **public** on a free GitHub plan. Pages is private-repo-capable
only on Pro and above.

### 2. Turn on Pages

Repo → **Settings** → **Pages** → under **Build and deployment**, set **Source**
to **GitHub Actions**. Not "Deploy from a branch" — the workflow in this repo
handles it.

Push once after this. The first run creates the `github-pages` environment.

### 3. Point the domain

At your registrar's DNS panel, for `hardikmurdiac20.com`:

| Type  | Name | Value                       |
|-------|------|-----------------------------|
| A     | @    | 185.199.108.153             |
| A     | @    | 185.199.109.153             |
| A     | @    | 185.199.110.153             |
| A     | @    | 185.199.111.153             |
| AAAA  | @    | 2606:50c0:8000::153         |
| AAAA  | @    | 2606:50c0:8001::153         |
| AAAA  | @    | 2606:50c0:8002::153         |
| AAAA  | @    | 2606:50c0:8003::153         |
| CNAME | www  | `<your-username>.github.io` |

Delete any existing `@` A record or parking-page record the registrar added by
default, or it will fight these.

The four A records are IPv4 and the four AAAA are IPv6. Add both — GitHub
recommends keeping A records alongside AAAA because IPv6 adoption is still uneven.

### 4. Attach the domain in GitHub

Repo → **Settings** → **Pages** → **Custom domain** → enter `hardikmurdiac20.com`
→ **Save**. GitHub reads the `CNAME` file in this repo, so the value should
already match.

Wait for the DNS check to pass, then tick **Enforce HTTPS**. The certificate is
issued by Let's Encrypt automatically and can take up to an hour on first setup.
It's normal to see a certificate warning during that window.

### 5. Verify

```sh
dig hardikmurdiac20.com +noall +answer -t A
dig www.hardikmurdiac20.com +noall +answer -t CNAME
curl -sI https://hardikmurdiac20.com | head -1
```

The A records should list the four GitHub IPs, and the curl should return `200`.

DNS propagation is usually minutes but can take up to 48 hours depending on the
registrar's TTL.

## If something goes wrong

**Actions run is green but the site is stale.** Hard-refresh (Cmd/Ctrl + Shift + R).
GitHub Pages sets a 10-minute cache on HTML.

**"Domain does not resolve to the GitHub Pages server."** DNS hasn't propagated, or
an old A record is still present. Check with `dig` and remove any conflicting
records.

**The custom domain resets itself after a deploy.** The `CNAME` file was deleted.
It must stay in the repo root — the workflow publishes the whole directory, so
losing that file unsets the domain.

**HTTPS is greyed out.** GitHub needs the DNS check to pass first. Wait, then
revisit Settings → Pages.

**Workflow fails at "Validate markup".** Run `python3 scripts/check.py` locally to
see the same output. It prints the line and column of the problem.

## Alternative: Cloudflare Pages

If you'd rather not manage apex A records, Cloudflare Pages handles the root
domain via CNAME flattening.

1. **Workers & Pages** → **Create** → **Pages** → **Connect to Git**, pick this repo.
2. Framework preset **None**, build command empty, output directory `/`.
3. **Custom domains** → add `hardikmurdiac20.com` and `www.hardikmurdiac20.com`.
4. Move your nameservers to Cloudflare when prompted.

Same push-to-deploy behaviour. Delete `.github/workflows/deploy.yml` if you go
this route so the two don't both publish.

## Notes

- Indentation is tabs. `.editorconfig` enforces it.
- Fonts load from Google Fonts. Everything else is self-contained.
- The `og-image.png` reference is absolute, so link previews resolve correctly.
  If the domain ever changes, update the `og:` and `twitter:` meta tags,
  `CNAME`, `robots.txt`, `sitemap.xml`, and the status bar text in `index.html`.
