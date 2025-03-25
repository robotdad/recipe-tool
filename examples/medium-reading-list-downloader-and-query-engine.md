# Medium Reading List Downloader and Query Engine

Create a system that logs into Medium.com, saves articles from my reading list to local markdown files, and provides an LLM-powered query interface:

1. Log into Medium.com using selenium with my credentials stored in `.env` file (MEDIUM_USERNAME and MEDIUM_PASSWORD).

2. Navigate to my reading list page and extract URLs for all saved articles.

3. Check the local directory `./medium_articles/` for existing downloads by comparing article titles and URLs in a tracking file `article_index.json`.

4. For each new article not already downloaded:

   - Download the article content
   - Clean the HTML to extract just the article text, title, author, and publication date
   - Convert to markdown format with appropriate headings and formatting
   - Save to `./medium_articles/{slugified_title}.md`
   - Update the tracking file with metadata (title, URL, download date, author)

5. When a query is provided via command line:

   - Generate embeddings for the query using sentence-transformers
   - Compare against pre-computed embeddings for all downloaded articles
   - Identify the top 3 most relevant articles
   - Use the LLM to synthesize an answer based on the content of those articles
   - Return a JSON response containing:
     - The LLM-generated answer
     - References to the source articles
     - The full markdown content of the most relevant article

6. Implement a caching system to avoid re-computing embeddings for unchanged articles.

7. Provide appropriate error handling for network issues, authentication failures, or article parsing problems.

8. Run this recipe weekly to keep the local article database updated.
