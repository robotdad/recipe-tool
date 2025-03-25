Develop a workflow that generates a comprehensive customer support knowledge base from existing data:

1. Import customer support tickets from our database (SQL query in 'support_data.sql').
2. Import product documentation from markdown files in the 'docs/' directory.
3. Analyze customer tickets to identify:
   - Most common customer issues (frequency and severity)
   - Language patterns customers use to describe problems
   - Average resolution time per issue type
4. For each of the top 20 issue types:
   - Generate a detailed FAQ entry with clear problem description
   - Write step-by-step resolution instructions with screenshots
   - Create troubleshooting decision trees
   - Add preventive advice to avoid the issue
5. Organize all entries into a logical hierarchy with categories and subcategories.
6. Generate metadata tags for each entry to improve searchability.
7. Create an introduction and general guide for using the knowledge base.
8. Generate multiple versions optimized for different platforms:
   - Internal support team reference (detailed technical version)
   - Customer-facing web articles (simplified language)
   - Chatbot training data (Q&A format)
9. Include version tracking and last-updated timestamps.
10. If any product documentation is outdated (older than 6 months), flag it for review.

The knowledge base should prioritize clarity and practical solutions over technical jargon.
