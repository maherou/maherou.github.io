#!/usr/bin/env python3
# fetch_scholar.py
# Fetch Google Scholar highlights for Michael Heroux and write
# scholar_highlights.json with:
#   highly_cited: every paper with >= 500 citations (most cited first)
#   recent: the 5 newest papers with >= 20 citations (newest first)
#
# Google Scholar has no official API. This uses the 'scholarly' library,
# which reads the public profile page. The profile list does not include
# author names, so the script then opens each selected paper's Scholar page
# (about a dozen requests, a few seconds apart) to get its authors.
# If Scholar blocks any request, the script exits without touching the
# existing JSON file.
#
# Copyright (c) 2026 Michael A. Heroux. Code under the MIT License.

import json
import sys
import time
from datetime import datetime, timezone

from scholarly import scholarly

SCHOLAR_ID = '3o3TleEAAAAJ'
PROFILE_URL = f'https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en'
OUTPUT_FILE = 'scholar_highlights.json'

HIGH_CITATION_MIN = 500
RECENT_CITATION_MIN = 20
RECENT_COUNT = 5
DETAIL_DELAY_SECONDS = 3   # pause between per-paper lookups, to be polite


def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def paper_url(pub):
    # Prefer the publisher URL when present; otherwise link to the
    # paper's page on the Scholar profile.
    url = pub.get('pub_url')
    if url:
        return url
    pub_id = pub.get('author_pub_id')
    if pub_id:
        return ('https://scholar.google.com/citations?view_op=view_citation'
                f'&hl=en&user={SCHOLAR_ID}&citation_for_view={pub_id}')
    return PROFILE_URL


def format_authors(value):
    # Scholar gives 'First Author and Second Author and ...'.
    if isinstance(value, list):
        names = value
    else:
        names = str(value or '').split(' and ')
    return ', '.join(n.strip() for n in names if n.strip())


def simplify(pub):
    bib = pub.get('bib', {})
    return {
        'title': bib.get('title', ''),
        'authors': format_authors(bib.get('author', '')),
        'venue': bib.get('citation', ''),
        'year': to_int(bib.get('pub_year')),
        'citations': to_int(pub.get('num_citations')),
        'url': paper_url(pub),
    }


def add_authors(selected):
    # Open each selected paper's Scholar page to get its author list (and its
    # publisher link, when the profile list did not have one). A paper that
    # appears in both lists is looked up only once.
    todo = list({id(p): p for p in selected}.values())
    print(f'Looking up authors for {len(todo)} papers...')
    for i, p in enumerate(todo, 1):
        if i > 1:
            time.sleep(DETAIL_DELAY_SECONDS)
        try:
            filled = scholarly.fill(p['_raw'])
        except Exception as e:
            print(f'Scholar blocked or failed on paper {i} of {len(todo)} '
                  f'("{p["title"]}"): {e}')
            print('Not overwriting the existing file. Try again later.')
            sys.exit(1)
        authors = format_authors(filled.get('bib', {}).get('author', ''))
        if authors:
            p['authors'] = authors
        p['url'] = paper_url(filled)
        print(f'  {i}/{len(todo)}  {p["title"][:60]}')


def main():
    print('Looking up the Scholar profile...')
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=['publications'])

    papers = []
    for raw in author.get('publications', []):
        p = simplify(raw)
        if p['title']:
            p['_raw'] = raw   # kept so we can look up authors later
            papers.append(p)
    print(f'Found {len(papers)} publications.')

    if not papers:
        print('No publications returned. Scholar may be blocking us. '
              'Not overwriting the existing file.')
        sys.exit(1)

    highly_cited = sorted(
        (p for p in papers if p['citations'] >= HIGH_CITATION_MIN),
        key=lambda p: p['citations'],
        reverse=True,
    )

    recent = sorted(
        (p for p in papers
         if p['citations'] >= RECENT_CITATION_MIN and p['year'] > 0),
        key=lambda p: (p['year'], p['citations']),
        reverse=True,
    )[:RECENT_COUNT]

    add_authors(highly_cited + recent)

    for p in highly_cited + recent:
        p.pop('_raw', None)

    output = {
        'profile_url': PROFILE_URL,
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'criteria': {
            'highly_cited_min_citations': HIGH_CITATION_MIN,
            'recent_min_citations': RECENT_CITATION_MIN,
            'recent_count': RECENT_COUNT,
        },
        'highly_cited': highly_cited,
        'recent': recent,
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f'Wrote {OUTPUT_FILE}: {len(highly_cited)} highly cited, '
          f'{len(recent)} recent.')


if __name__ == '__main__':
    main()
