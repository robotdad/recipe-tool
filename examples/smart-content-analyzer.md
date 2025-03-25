# Smart Content Analyzer

I need a system that can analyze a collection of articles, extract key information, identify trends, and generate a comprehensive report. This tool should help content strategists understand what content is performing well and why.

## Steps to perform:

1. First, read the content configuration from "data/content_config.json" which contains settings for the analysis.

2. Read all article files from the "data/articles" directory. Each article is in a JSON format with fields for title, content, publication_date, author, and performance_metrics (views, shares, comments, and conversion_rate).

3. Process each article to extract:

   - Main topic and subtopics
   - Key entities (people, organizations, products)
   - Sentiment (positive, negative, neutral)
   - Reading complexity (using Flesch-Kincaid or similar)
   - Content structure (introduction, body, conclusion patterns)

4. Analyze the performance metrics to identify:

   - Top-performing articles by each metric
   - Correlations between content characteristics and performance
   - Performance trends over time

5. Generate insights such as:

   - What topics are resonating most with our audience?
   - What content structure leads to better conversion?
   - What reading level correlates with higher engagement?
   - Who are our most effective authors?

6. Create visualizations:

   - Performance by topic
   - Performance by content length
   - Sentiment distribution
   - Reading level vs. engagement
   - Trend lines for key metrics over time

7. Compile everything into a comprehensive report with:

   - Executive summary
   - Key findings
   - Detailed analysis by topic
   - Top-performing content examples
   - Recommendations for future content

8. Save the report as "output/content_analysis_report.md" and any visualizations to the "output/visualizations" directory.

If you come across any unusual patterns in the data, flag them in a separate section of the report.

This analysis should help our content team understand what's working, what's not, and how to optimize our content strategy going forward.
