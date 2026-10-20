# imavelo.com

Static site for Imavelo and its apps: ParkLast's privacy policy, terms of service and support pages, in English and
Hebrew. Served by GitHub Pages from the repository root. No scripts, no cookies, no analytics, no external fonts or
assets; one stylesheet (`assets/site.css`).

| Page | English | Hebrew |
|---|---|---|
| Imavelo | `/` | `/he/` |
| ParkLast | `/parklast/` | `/parklast/he/` |
| Privacy Policy | `/parklast/privacy/` | `/parklast/privacy/he/` |
| Terms of Service | `/parklast/terms/` | `/parklast/terms/he/` |
| Support | `/parklast/support/` | `/parklast/support/he/` |

## Operator details
`site.json` holds the public operator details:
- trade name, legal form, legal name;
- privacy and support e-mail addresses;
- minimum age.

The effective date is the real publication day. It is given at publish time:
`EFFECTIVE_DATE=YYYY-MM-DD python3 tools/build.py`.

**The operator's private postal address is never added here.** The pages say it is available on request by e-mail,
and `tools/check_site.py` fails on address-like text or an address field.

## Editing
- **Sources:** page content lives in `src/<page>.en.html` and `src/<page>.he.html` (body only).
- **Build:** `python3 tools/build.py` adds the shared header, footer, language switch and metadata, and writes the
  `index.html` files.
- **Check:** `python3 tools/check_site.py` verifies the language and direction, mobile viewport, links, that nothing
  external is loaded, and that there are no secret- or personal-data-like strings. It also lists the placeholders
  (`class="todo"`). Before publishing, run `EFFECTIVE_DATE=YYYY-MM-DD python3 tools/build.py && python3 tools/check_site.py --publish`;
  it fails while any placeholder is left.
- **Accuracy:** the texts describe ParkLast 1.1.0 as implemented. Change them only together with the app.

## Publishing (needs the owner's approval; nothing here is live yet)
1. **Make the repository public.** GitHub Pages on a free account serves public repositories only. Only these
   pages are in it: no secrets, no user data.
2. **Turn on Pages.** Settings → Pages → Build and deployment:
   - Source: Deploy from a branch, `main`, `/ (root)`.
   - Custom domain: `imavelo.com` (the `CNAME` file already says so).
3. **Verify the domain against takeover.** Account Settings → Pages → Add a verified domain → `imavelo.com`. GitHub
   shows a TXT record to add (step 4).
4. **Add DNS records at box.co.il** (the domain's DNS host):

   | Type | Host / name | Value |
   |---|---|---|
   | A | `@` | `185.199.108.153` |
   | A | `@` | `185.199.109.153` |
   | A | `@` | `185.199.110.153` |
   | A | `@` | `185.199.111.153` |
   | AAAA (optional) | `@` | `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153` |
   | CNAME | `www` | `raanan-netizen.github.io.` |
   | TXT | `_github-pages-challenge-raanan-netizen` | the value GitHub shows in step 3 |

   **Do not change** the existing records:
   - MX `@` → `1 smtp.google.com.` (e-mail);
   - TXT `@` → `google-site-verification=…`;
   - the NS records.
5. **Enable HTTPS.** Once Pages shows the domain as verified and the certificate is ready (minutes to a day), tick
   **Enforce HTTPS**.
6. **Check.** `https://imavelo.com/parklast/privacy/` answers 200 without login, `http://` redirects to `https://`,
   and the page reads well on a phone.
7. **Point the app and Play at it:**
   - **ParkLast repository variables:** `PARKLAST_PRIVACY_POLICY_URL=https://imavelo.com/parklast/privacy/` and
     `PARKLAST_TERMS_URL=https://imavelo.com/parklast/terms/`.
   - **Play Console:** Privacy policy URL, plus Support website `https://imavelo.com/parklast/support/`.
