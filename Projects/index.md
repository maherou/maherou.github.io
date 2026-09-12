---
title: Research & Legacy Projects
permalink: /Projects/
subtitle: A body of work in scientific and high-performance computing software, spanning two decades.
---

These projects reflect work founded or led during my time at Sandia National Laboratories and the
US Department of Energy. Several continue as active, community-run efforts; others are complete
and preserved here for reference.

<div class="card-grid" style="margin-top: 1.5em;">
{% comment %}site.projects is already in `order` sequence via collections.projects.sort_by in _config.yml{% endcomment %}
{% for project in site.projects %}
  <a class="card-link" href="{{ project.url | relative_url }}">
    <div class="card">
      {% if project.img %}<img class="card-img" src="{{ project.img | prepend: '/assets/img/' | relative_url }}" alt="{{ project.title }}">{% endif %}
      <h3>{{ project.title }}</h3>
      <p>{{ project.description }}</p>
    </div>
  </a>
{% endfor %}
</div>
