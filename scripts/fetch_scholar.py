#!/usr/bin/env python3
# fetch_scholar.py
# Fetch Google Scholar highlights for Michael Heroux and write
# scholar_highlights.json with:
#   highly_cited: every paper with >= 500 citations (most cited first)
#   recent: the 5 newest papers with >= 20 citations (newest first)
#
# Google Scholar has no official API. This uses the 'scholarly' library,
# which reads the public profile page. If Scholar blocks the request, the
# script exits without touching the existing JSON file.
#
# The profile list does not include author names, and Scholar blocks scripts
# that open individual paper pages. So author names come from OpenAlex
# (https://openalex.org), a free scholarly database with an official API,
# matched on exact title. A paper with no exact match is listed without
# authors.
#
# Copyright (c) 2026 Michael A. Heroux. Code under the MIT License.

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from scholarly import scholarly

SCHOLAR_ID = '3o3TleEAAAAJ'
PROFILE_URL = f'https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en'
OUTPUT_FILE = 'scholar_highlights.json'

HIGH_CITATION_MIN = 500
RECENT_CITATION_MIN = 20
RECENT_COUNT = 5
OPENALEX_URL = 'https://api.openalex.org/works'
OPENALEX_DELAY_SECONDS = 0.2   # pause between lookups, to be polite


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


def normalize_title(title):
    # Lowercase, drop punctuation and extra spaces, for exact-title matching.
    return ' '.join(re.sub(r'[^\w\s]', ' ', title.lower()).split())


def openalex_authors(title):
    # Return the author list for an exact title match on OpenAlex, or ''.
    query = urllib.parse.urlencode({'search': title, 'per-page': 5})
    request = urllib.request.Request(
        f'{OPENALEX_URL}?{query}',
        headers={'User-Agent': 'fetch_scholar.py'})
    with urllib.request.urlopen(request, timeout=30) as response:
        results = json.load(response).get('results', [])
    wanted = normalize_title(title)
    for work in results:
        if normalize_title(work.get('title') or '') == wanted:
            names = [a.get('author', {}).get('display_name', '')
                     for a in work.get('authorships', [])]
            return ', '.join(n for n in names if n)
    return ''


def add_authors(selected):
    # A paper that appears in both lists is looked up only once.
    todo = list({id(p): p for p in selected}.values())
    print(f'Looking up authors on OpenAlex for {len(todo)} papers...')
    for i, p in enumerate(todo, 1):
        if i > 1:
            time.sleep(OPENALEX_DELAY_SECONDS)
        try:
            authors = openalex_authors(p['title'])
        except Exception as e:
            print(f'  {i}/{len(todo)}  lookup failed ({e}); '
                  f'listing without authors: {p["title"][:50]}')
            continue
        if authors:
            p['authors'] = authors
            print(f'  {i}/{len(todo)}  found   {p["title"][:60]}')
        else:
            print(f'  {i}/{len(todo)}  no match, listing without authors: '
                  f'{p["title"][:50]}')


def main():
    print('Looking up the Scholar profile...')
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=['publications'])

    papers = [simplify(p) for p in author.get('publications', [])]
    papers = [p for p in papers if p['title']]
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
