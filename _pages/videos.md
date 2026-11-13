---
title: "Videos"
permalink: /videos/
layout: archive
author_profile: true
---

Everything from my [YouTube channel](https://youtube.com/nickstapleton), updated automatically.

{% assign all_videos = site.posts | where_exp: "p", "p.categories contains 'videos' or p.categories contains 'shorts'" %}
{% for post in all_videos %}
  {% include archive-single.html %}
{% endfor %}
