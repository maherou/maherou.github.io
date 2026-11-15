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
# Copyright, 2026, Michael A. Heroux. Code under the MIT License.

import json
import sys
from datetime import datetime, timezone

from scholarly import scholarly

SCHOLAR_ID = '3o3TleEAAAAJ'
PROFILE_URL = f'https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en'
OUTPUT_FILE = 'scholar_highlights.json'

HIGH_CITATION_MIN = 500
RECENT_CITATION_MIN = 20
RECENT_COUNT = 5


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


def simplify(pub):
    bib = pub.get('bib', {})
    return {
        'title': bib.get('title', ''),
        'authors': bib.get('author', ''),
        'venue': bib.get('citation', ''),
        'year': to_int(bib.get('pub_year')),
        'citations': to_int(pub.get('num_citations')),
        'url': paper_url(pub),
    }


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
