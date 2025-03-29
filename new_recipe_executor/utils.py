import re


def render_template(text: str, context) -> str:
    # A simple implementation that replaces ${key} with the corresponding value from context.extras
    def replacer(match):
        key = match.group(1)
        return str(context.get(key, match.group(0)))
    rendered = re.sub(r'\$\{(\w+)\}', replacer, text)
    return rendered
