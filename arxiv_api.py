import urllib.request
import feedparser

# Base API query URL and search parameters
base_url = 'http://export.arxiv.org/api/query?'

search_query = 'all:llm'  # search for "llm" in all fields
start = 0                 # retreive the first 5 results
max_results = 1
query = f'search_query={search_query}&start={start}&max_results={max_results}'

url = base_url + query

data = urllib.request.urlopen(base_url+query).read()
feed = feedparser.parse(data)

# print out feed information
print(f"Feed title: {feed.feed.get('title', 'N/A')}")
print(f"Feed last updated: {feed.feed.get('updated', 'N/A')}")

# print opensearch metadata
print(f"Total results for this query: {feed.feed.get('opensearch_totalresults', 'N/A')}")
print(f"Items per page: {feed.feed.get('opensearch_itemsperpage', 'N/A')}")
print(f"Start index: {feed.feed.get('opensearch_startindex', 'N/A')}\n")

# Run through each entry, and print out information
for entry in feed.entries:
    print('=' * 80)
    print("e-print metadata")
    print(f"arXiv ID: {entry.id.split('/abs/')[-1]}")
    print(f"Published: {entry.published}")
    print(f"Title: {entry.title.strip()}\n")

    # Authors
    if entry.authors:
        print(f"Authors: {', '.join(author.name for author in entry.authors)}")

    affiliation = getattr(entry, 'arxiv_affiliation', None)
    if affiliation:
        print(f"Affiliation: {affiliation}")

    # Links
    for link in entry.links:
        if getattr(link, 'title', '') == 'pdf':
            print(f"PDF link: {link.href}")

    # Journal reference and comments
    journal_ref = getattr(entry, 'arxiv_journal_ref', 'No journal ref found')
    comment = getattr(entry, 'arxiv_comment', 'No comment found')
    print(f"Journal reference: {journal_ref}")
    print(f"Comments: {comment}")

    # Categories
    if hasattr(entry, 'tags'):
        primary_cat = entry.tags[0]['term']
        all_categories = [t['term'] for t in entry.tags]
        print(f"Primary category: {primary_cat}")
        print(f"All categories: {', '.join(all_categories)}")

    # Abstract
    print("\nAbstract:")
    print(entry.summary.strip())
    print('=' * 80 + '\n')


# Feed title: ArXiv Query: search_query=all:llm&amp;id_list=&amp;start=0&amp;max_results=1
# Feed last updated: 2025-10-11T00:00:00-04:00
# Total results for this query: 46108
# Items per page: 1
# Start index: 0

# ================================================================================
# e-print metadata
# arXiv ID: 2412.18022v1
# Published: 2024-12-23T22:34:40Z
# Title: Trustworthy and Efficient LLMs Meet Databases

# Authors: Kyoungmin Kim, Anastasia Ailamaki
# PDF link: http://arxiv.org/pdf/2412.18022v1
# Journal reference: No journal ref found
# Comments: No comment found
# Primary category: cs.DB
# All categories: cs.DB, cs.AI

# Abstract:
# In the rapidly evolving AI era with large language models (LLMs) at the core,
# making LLMs more trustworthy and efficient, especially in output generation
# (inference), has gained significant attention. This is to reduce plausible but
# faulty LLM outputs (a.k.a hallucinations) and meet the highly increased
# inference demands. This tutorial explores such efforts and makes them
# transparent to the database community. Understanding these efforts is essential
# in harnessing LLMs in database tasks and adapting database techniques to LLMs.
# Furthermore, we delve into the synergy between LLMs and databases, highlighting
# new opportunities and challenges in their intersection. This tutorial aims to
# share with database researchers and practitioners essential concepts and
# strategies around LLMs, reduce the unfamiliarity of LLMs, and inspire joining
# in the intersection between LLMs and databases.
# ================================================================================
