Goal:
Create a recipe that generates a quarterly business report by analyzing new performance data, comparing it with historical data, and producing a professional document with insights and visualizations.

How:

Input context variables:

- new_data_file: [Required] Path to the CSV file containing the latest quarterly data
- historical_data_file: [Optional] Path to the CSV file containing historical quarterly data
- company_name: [Optional] Name of the company for the report. Defaults to "Our Company"
- quarter: [Optional] Current quarter (e.g., "Q2 2025"). Will attempt to detect from data if not provided.
- output_root: [Optional] Directory to save the output report. Defaults to "output"
- model: [Optional] The model to use. Defaults to "openai/o4-mini"

Steps:

- Read the new quarterly data from the CSV file specified by the new_data_file variable
- Read historical data from the historical_data_file
- Process and analyze the data:
  - Calculate key performance metrics (revenue growth, customer acquisition, etc.)
  - Compare current quarter with historical trends
  - Identify significant patterns and outliers
- Use an LLM to generate insights and recommendations based on the analysis
- Use another LLM to create a comprehensive report that includes:
  - Executive summary
  - Key metrics with Mermaid charts (quarterly trends, product performance)
    - Make sure LLM is aware of the limited available mermaid diagram types:
      - pie
      - timeline
      - mindmap
      - gantt
      - stateDiagram-v2
      - classDiagram
      - sequenceDiagram
      - flowchart
  - Regional performance analysis
  - Strategic recommendations for next quarter
- Write the complete report as markdown to the output directory
