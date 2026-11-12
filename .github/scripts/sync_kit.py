#!/usr/bin/env python3
"""Turn public Kit broadcasts into short Jekyll teaser posts.

Needs the KIT_API_KEY environment variable (a GitHub Actions secret).
Only broadcasts that are public on the web (they have a public_url) are used.
A broadcast that already has a post (matched by kit_id) is skipped.
"""
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

API = "https://api.kit.com/v4/broadcasts"
POSTS_DIR = Path("_posts")


def fetch(url, key):
    req = urllib.request.Request(
        url, headers={"X-Kit-Api-Key": key, "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def all_broadcasts(key):
    url, out = API, []
    while True:
        data = fetch(url, key)
        out += data.get("broadcasts", [])
        page = data.get("pagination") or {}
        if not page.get("has_next_page"):
            return out
        url = API + "?" + urllib.parse.urlencode({"after": page["end_cursor"]})


def existing_ids():
    ids = set()
    for p in POSTS_DIR.glob("*.md"):
        m = re.search(r'^kit_id:\s*"?(\d+)"?\s*$', p.read_text(encoding="utf-8"), re.M)
        if m:
            ids.add(m.group(1))
    return ids


def plain_text(raw_html):
    t = re.sub(r"(?is)<(script|style|head).*?</\1>", " ", raw_html or "")
    t = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</h\d>|</li>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"[ \t\xa0]+", " ", re.sub(r"\n\s*\n+", "\n\n", t)).strip()


def teaser(b, limit=320):
    text = plain_text(b.get("content")) or (b.get("description") or "")
    text = re.sub(r"[{}]", "", text)
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
    return text


def slugify(text, fallback):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60].strip("-") or fallback


def build_post(b):
    title = (b.get("subject") or b.get("description") or f"Newsletter {b['id']}").strip()
    when = b.get("published_at") or b.get("send_at") or b.get("created_at")
    dt = datetime.fromisoformat(when.replace("Z", "+00:00"))
    excerpt = teaser(b)
    front = [
        "---",
        f"title: {json.dumps(title, ensure_ascii=False)}",
        f"date: {dt.strftime('%Y-%m-%d %H:%M:%S %z')}",
        "categories: [newsletter]",
        "tags: [newsletter]",
        f'kit_id: "{b["id"]}"',
        f"excerpt: {json.dumps(re.sub(chr(92)+'s+', ' ', excerpt)[:160], ensure_ascii=False)}",
    ]
    if b.get("thumbnail_url"):
        front += ["header:", f"  teaser: {json.dumps(b['thumbnail_url'])}"]
    front += ["---", ""]
    body = [
        "{% raw %}", excerpt, "{% endraw %}", "",
        f"[Read the full issue]({b['public_url']}){{: .btn .btn--primary}}", "",
    ]
    name = f"{dt.strftime('%Y-%m-%d')}-{slugify(title, str(b['id']))}.md"
    return name, "\n".join(front + body)


def main():
    key = os.environ.get("KIT_API_KEY")
    if not key:
        sys.exit("KIT_API_KEY is not set. Add it under Settings > Secrets and variables > Actions.")
    POSTS_DIR.mkdir(exist_ok=True)
    seen, created = existing_ids(), 0
    for b in all_broadcasts(key):
        if not b.get("public") or not b.get("public_url") or str(b["id"]) in seen:
            continue
        name, content = build_post(b)
        (POSTS_DIR / name).write_text(content, encoding="utf-8")
        seen.add(str(b["id"]))
        created += 1
        print(f"Created {name}")
    print(f"Done: {created} new post(s).")


if __name__ == "__main__":
    main()
