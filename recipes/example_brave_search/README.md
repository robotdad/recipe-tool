# Brave Search Recipe

This recipe demonstrates use of the Brave Search API to perform a search and retrieve results.

It allows for passing of the BRAVE_API_KEY as either a context variable or an environment variable.

## Run the Recipe

### Use env var for API key

```bash
export BRAVE_API_KEY=your_api_key

# From the repo root, run the recipe with the test project
recipe-tool --execute recipes/example_brave_search/search.json \
   query="Tell me about model context protocol." \
   model=openai/o4-mini
```

### Use context variable for API key

```bash
# From the repo root, run the recipe with the test project
recipe-tool --execute recipes/example_brave_search/search.json \
   query="Tell me about model context protocol." \
   model=openai/o4-mini \
   brave_api_key=your_api_key
```
