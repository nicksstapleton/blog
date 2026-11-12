#!/usr/bin/env python3
"""Turn new YouTube videos and Shorts into Jekyll posts.

Runs from the repo root (see .github/workflows/youtube-sync.yml). Uses only the
Python standard library. Safe to re-run: a video that already has a post
(matched by its youtube_id) is skipped.
"""
import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

CHANNEL_ID = "UCiJCQpWk2ajVbap8FoF0STQ"
POSTS_DIR = Path("_posts")

NS = {
    "a": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; blog-youtube-sync)"}


def feed_url(playlist_id=None):
    base = "https://www.youtube.com/feeds/videos.xml"
    if playlist_id:
        return f"{base}?playlist_id={playlist_id}"
    return f"{base}?channel_id={CHANNEL_ID}"


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def parse_feed(xml_bytes):
    root = ET.fromstring(xml_bytes)
    items = []
    for e in root.findall("a:entry", NS):
        desc_el = e.find("media:group/media:description", NS)
        items.append(
            {
                "id": e.find("yt:videoId", NS).text,
                "title": (e.find("a:title", NS).text or "").strip(),
                "published": e.find("a:published", NS).text,
                "description": (desc_el.text or "").strip() if desc_el is not None else "",
            }
        )
    return items


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def is_short(video_id):
    """A Short's /shorts/ URL returns 200; a normal video redirects to /watch."""
    opener = urllib.request.build_opener(_NoRedirect)
    req = urllib.request.Request(
        f"https://www.youtube.com/shorts/{video_id}", headers=HEADERS
    )
    try:
        return opener.open(req, timeout=30).status == 200
    except urllib.error.HTTPError:
        return False


def collect():
    """Return [(item, kind)] where kind is 'videos' or 'shorts'."""
    suffix = CHANNEL_ID[2:]
    try:
        # YouTube's auto-generated playlists: UULF = long-form, UUSH = Shorts.
        long_form = parse_feed(fetch(feed_url("UULF" + suffix)))
        shorts = parse_feed(fetch(feed_url("UUSH" + suffix)))
        return [(i, "videos") for i in long_form] + [(i, "shorts") for i in shorts]
    except Exception as err:  # fall back to the main feed + per-video check
        print(f"Playlist feeds unavailable ({err}); using channel feed instead.")
        items = parse_feed(fetch(feed_url()))
        return [(i, "shorts" if is_short(i["id"]) else "videos") for i in items]


def existing_ids():
    ids = set()
    for p in POSTS_DIR.glob("*.md"):
        m = re.search(r'^youtube_id:\s*"?([\w-]+)"?\s*$', p.read_text(encoding="utf-8"), re.M)
        if m:
            ids.add(m.group(1))
    return ids


def slugify(text, fallback):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60].strip("-")
    return slug or fallback


def format_description(text):
    text = re.sub(r"(https?://[^\s<>]+)", r"<\1>", text)  # autolink URLs
    return text.replace("\r\n", "\n").replace("\n", "  \n")  # keep line breaks


def embed(video_id, kind):
    src = f"https://www.youtube-nocookie.com/embed/{video_id}"
    attrs = (
        'loading="lazy" allowfullscreen '
        'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
        'referrerpolicy="strict-origin-when-cross-origin"'
    )
    if kind == "shorts":
        return (
            '<div style="max-width:360px;margin:0 auto 1.5em;aspect-ratio:9/16;">'
            f'<iframe src="{src}" title="YouTube Short" {attrs} '
            'style="width:100%;height:100%;border:0;"></iframe></div>'
        )
    return (
        '<div class="responsive-video-container">'
        f'<iframe src="{src}" title="YouTube video" {attrs}></iframe></div>'
    )


def build_post(item, kind):
    dt = datetime.fromisoformat(item["published"].replace("Z", "+00:00"))
    first_line = item["description"].split("\n")[0]
    excerpt = re.sub(r"[{}]", "", first_line)[:160]
    front = [
        "---",
        f"title: {json.dumps(item['title'], ensure_ascii=False)}",
        f"date: {dt.strftime('%Y-%m-%d %H:%M:%S %z')}",
        f"categories: [{kind}]",
        "tags: [youtube]",
        f'youtube_id: "{item["id"]}"',
        f"excerpt: {json.dumps(excerpt, ensure_ascii=False)}",
        "header:",
        f'  teaser: "https://i.ytimg.com/vi/{item["id"]}/hqdefault.jpg"',
        "---",
        "",
    ]
    body = [embed(item["id"], kind), ""]
    if item["description"]:
        body += ["{% raw %}", format_description(item["description"]), "{% endraw %}", ""]
    body += [f"[Watch on YouTube](https://www.youtube.com/watch?v={item['id']})", ""]
    filename = f"{dt.strftime('%Y-%m-%d')}-{slugify(item['title'], item['id'])}.md"
    return filename, "\n".join(front + body)


def main():
    POSTS_DIR.mkdir(exist_ok=True)
    seen = existing_ids()
    created = 0
    for item, kind in collect():
        if item["id"] in seen:
            continue
        filename, content = build_post(item, kind)
        (POSTS_DIR / filename).write_text(content, encoding="utf-8")
        seen.add(item["id"])
        created += 1
        print(f"Created {filename} ({kind})")
    print(f"Done: {created} new post(s).")


if __name__ == "__main__":
    main()
