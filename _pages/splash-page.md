---
title: "Splash Page"
layout: splash
permalink: /splash-page/
date: 2020-04-08
header:
  overlay_color: "#000"
  overlay_filter: "0.5"
  overlay_image: /assets/images/logosheader.png

  actions:
    - label: "Download"
      url: "https://github.com/mmistakes/minimal-mistakes/"
excerpt: "Bacon ipsum dolor sit amet salami ham hock ham, hamburger corned beef short ribs kielbasa biltong t-bone drumstick tri-tip tail sirloin pork chop."
intro: 
  - excerpt: 'Nullam suscipit et nam, tellus velit pellentesque at malesuada, enim eaque. Quis nulla, netus tempor in diam gravida tincidunt, *proin faucibus* voluptate felis id sollicitudin. Centered with `type="center"`'
feature_row:
  - image_path: /assets/images/logosheader.png
    title: "Why You Should Buy Logos 9"
    excerpt: "Sample text 1 with **markdown** formatting."
    url: "https://www.nickstapleton.me/Why-You-Should-Buy-Logos-9/"
    btn_label: "Read More"
    btn_class: "btn--primary"
  - image_path: /assets/images/base-packages-header2.png
    title: "Why You Should Buy Logos 9"
    excerpt: "This is some sample content that goes here with **Markdown** formatting."
    url: "https://www.nickstapleton.me/Why-You-Should-Buy-Logos-9/"
    btn_label: "Read More"
    btn_class: "btn--secondary"
  - image_path: /assets/images/logosheader.png
    title: "Placeholder 3"
    excerpt: "This is some sample content that goes here with **Markdown** formatting."
    url: "#test-link"
    btn_label: "Read More"
    btn_class: "btn--success"
feature_row_left:
  - image_path: /assets/splash/feat1-1.jpg
    title: "Left aligned placeholder 1"
    excerpt: "Left-aligned image centered with"
    url: "#test-link"
    btn_label: "Read More"
    btn_class: "btn--primary"
feature_row_right:
  - image_path: /assets/splash/feat1-2.jpg
    title: "Placeholder 1"
    excerpt: "Right-aligned image with ``"
    url: "#test-link"
    btn_label: "Read More"
    btn_class: "btn--primary"
feature_row_center:
  - image_path: /assets/splash/feat1-3.jpg
    title: "Placeholder 1"
    excerpt: "Center aligned image"
    url: "#test-link"
    btn_label: "Read More"
    btn_class: "btn--primary"
---

{% include feature_row id="intro" type="center" %}

{% include feature_row %}

{% include feature_row id="feature_row_left" type="left" %}

{% include feature_row id="feature_row_center" type="right" %}

{% include feature_row id="feature_row_center" type="center" %}
