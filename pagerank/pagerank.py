import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Initialize probability distribution
    probability_distribution = {}
    N = len(corpus)
    
    # Get the links from the current page
    links = corpus[page]
    
    # If page has no outgoing links, treat it as having links to all pages
    if not links:
        links = set(corpus.keys())
    
    # Calculate probabilities for each page
    for p in corpus:
        # Base probability from random choice (1-d)/N
        probability_distribution[p] = (1 - damping_factor) / N
        
        # Add probability from following links if page is linked to
        if p in links:
            probability_distribution[p] += damping_factor / len(links)
    
    return probability_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize page counts
    page_counts = {page: 0 for page in corpus}
    
    # Choose first page randomly
    current_page = random.choice(list(corpus.keys()))
    page_counts[current_page] += 1
    
    # Generate n-1 more samples
    for _ in range(n - 1):
        # Get probability distribution for next page
        probabilities = transition_model(corpus, current_page, damping_factor)
        
        # Choose next page based on probability distribution
        pages = list(probabilities.keys())
        weights = list(probabilities.values())
        current_page = random.choices(pages, weights=weights, k=1)[0]
        
        # Increment count for chosen page
        page_counts[current_page] += 1
    
    # Convert counts to probabilities
    return {page: count/n for page, count in page_counts.items()}


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    # Initialize all pages with equal probability
    pagerank = {page: 1/N for page in corpus}
    
    while True:
        new_pagerank = {}
        # Calculate new PageRank for each page
        for page in corpus:
            # Start with the random choice component
            new_pagerank[page] = (1 - damping_factor) / N
            
            # Add contributions from pages linking to this page
            for linking_page in corpus:
                # If linking page has no links, treat it as linking to all pages
                links = corpus[linking_page] if corpus[linking_page] else set(corpus.keys())
                if page in links:
                    new_pagerank[page] += damping_factor * pagerank[linking_page] / len(links)
        
        # Check for convergence
        converged = True
        for page in corpus:
            if abs(new_pagerank[page] - pagerank[page]) > 0.001:
                converged = False
                break
        
        # Update PageRank values
        pagerank = new_pagerank
        
        if converged:
            break
    
    return pagerank


if __name__ == "__main__":
    main()
