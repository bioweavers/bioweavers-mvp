# Templating & Jinja2: A Quick Introduction

This tutorial covers the fundamentals of templating and Jinja2 syntax — everything you need to understand how the Word document generation works.

---

## What is Templating?

**Templating** is a way to separate *structure* from *data*.

Instead of writing code that manually builds a document piece by piece:

```python
# ❌ The hard way: building output manually
output = "Project: " + project_name + "\n"
output += "Date: " + date + "\n"
output += "Species found:\n"
for species in species_list:
    output += "- " + species['name'] + " (" + species['status'] + ")\n"
```

You create a **template** with placeholders, then fill in the data:

```
# ✅ The template way
Project: {{ project_name }}
Date: {{ date }}
Species found:
{% for species in species_list %}
- {{ species.name }} ({{ species.status }})
{% endfor %}
```

The template engine (Jinja2) combines the template + data to produce output.

---

## Why Use Templates?

| Without Templates | With Templates |
|-------------------|----------------|
| Format mixed with logic | Format and logic separated |
| Hard to modify layout | Easy to change layout |
| Programmers control everything | Non-programmers can edit templates |
| Changes require code changes | Changes often just need template edits |

For Bio Weavers: Rincon can design/adjust the Word document format without touching Python code.

---

## Jinja2 Basics

Jinja2 is a popular Python templating engine. It uses special syntax to mark where data should go.

### 1. Variables: `{{ }}`

Double curly braces output a value:

```jinja2
Hello, {{ name }}!
The project is located in {{ location }}.
```

With data `{'name': 'Kelly', 'location': 'Santa Barbara'}`:

```
Hello, Kelly!
The project is located in Santa Barbara.
```

#### Accessing Object Properties

```jinja2
{{ species.scientific_name }}    {# Access attribute #}
{{ species['common_name'] }}     {# Also works #}
{{ species.status | upper }}     {# Filter: converts to uppercase #}
```

### 2. Control Flow: `{% %}`

Curly-brace-percent for logic (loops, conditionals):

#### For Loops

```jinja2
{% for item in items %}
  - {{ item }}
{% endfor %}
```

With data `{'items': ['apple', 'banana', 'cherry']}`:

```
  - apple
  - banana
  - cherry
```

#### Looping Over Dictionaries

```jinja2
{% for species in species_list %}
  {{ species.name }}: {{ species.status }}
{% endfor %}
```

With data:
```python
{'species_list': [
    {'name': 'Red-legged frog', 'status': 'FT'},
    {'name': 'Gnatcatcher', 'status': 'FT'},
]}
```

Output:
```
  Red-legged frog: FT
  Gnatcatcher: FT
```

#### Conditionals

```jinja2
{% if species.status == 'FT' %}
  ⚠️ Federally Threatened
{% elif species.status == 'FE' %}
  🚨 Federally Endangered
{% else %}
  State/Other status
{% endif %}
```

### 3. Comments: `{# #}`

```jinja2
{# This is a comment - won't appear in output #}
{{ name }}  {# inline comment #}
```

---

## Putting It Together: A Complete Example

### Template (`report.txt`)

```jinja2
PTO Assessment Report
=====================
Project: {{ project_name }}
Location: {{ project_location }}
Date: {{ assessment_date }}

Species Assessed: {{ species_list | length }}

{% for species in species_list %}
{{ loop.index }}. {{ species.common_name }} ({{ species.scientific_name }})
   Status: {{ species.status }}
   PTO: {{ species.pto }}
   {% if species.pto != 'Not Expected' %}
   ⚠️ Surveys may be required
   {% endif %}

{% endfor %}
--- End of Report ---
```

### Python Code

```python
from jinja2 import Template

template_text = open('report.txt').read()
template = Template(template_text)

data = {
    'project_name': 'Coastal Development',
    'project_location': 'Goleta, CA',
    'assessment_date': 'March 10, 2026',
    'species_list': [
        {
            'common_name': 'California red-legged frog',
            'scientific_name': 'Rana draytonii',
            'status': 'FT',
            'pto': 'High'
        },
        {
            'common_name': 'Burrowing owl',
            'scientific_name': 'Athene cunicularia',
            'status': 'SSC',
            'pto': 'Not Expected'
        },
    ]
}

output = template.render(data)
print(output)
```

### Output

```
PTO Assessment Report
=====================
Project: Coastal Development
Location: Goleta, CA
Date: March 10, 2026

Species Assessed: 2

1. California red-legged frog (Rana draytonii)
   Status: FT
   PTO: High
   ⚠️ Surveys may be required

2. Burrowing owl (Athene cunicularia)
   Status: SSC
   PTO: Not Expected

--- End of Report ---
```

---

## Jinja2 in Word Documents (docxtpl)

When using **docxtpl** for Word documents, the same Jinja2 syntax works, with one extension for tables:

### Regular Jinja2 (works in Word)

```
Project: {{ project_name }}
Date: {{ assessment_date }}
```

### Table Row Loops (docxtpl extension)

In Word tables, use `{%tr %}` instead of `{% %}` to repeat *table rows*:

```
| Species | Status | PTO |
|---------|--------|-----|
{%tr for s in species_list %}
| {{ s.name }} | {{ s.status }} | {{ s.pto }} |
{%tr endfor %}
```

The `tr` tells docxtpl: "operate on the table row (`<w:tr>`) level in the Word XML."

### Why the Special Syntax?

Word documents are XML internally. A table row is a `<w:tr>` element. docxtpl needs to know you want to clone the entire row, not just the text inside a cell.

```
{%tr for ... %}   →  Clone this <w:tr> element
{% for ... %}     →  Just repeat text (doesn't work for rows)
```

---

## Quick Reference

| Syntax | Purpose | Example |
|--------|---------|---------|
| `{{ var }}` | Output variable | `{{ species.name }}` |
| `{{ var \| filter }}` | Apply filter | `{{ name \| upper }}` |
| `{% for %}...{% endfor %}` | Loop | `{% for s in list %}...{% endfor %}` |
| `{% if %}...{% endif %}` | Conditional | `{% if x > 0 %}...{% endif %}` |
| `{# comment #}` | Comment | `{# TODO: fix this #}` |
| `{%tr for %}` | Table row loop (docxtpl) | `{%tr for s in list %}` |

### Useful Filters

| Filter | Purpose | Example |
|--------|---------|---------|
| `upper` | Uppercase | `{{ name \| upper }}` → `KELLY` |
| `lower` | Lowercase | `{{ name \| lower }}` → `kelly` |
| `title` | Title Case | `{{ name \| title }}` → `Kelly` |
| `length` | Count items | `{{ list \| length }}` → `5` |
| `default` | Fallback value | `{{ x \| default('N/A') }}` |
| `join` | Join list | `{{ items \| join(', ') }}` |

### Loop Variables

Inside a `{% for %}` loop, you have access to:

| Variable | Purpose |
|----------|---------|
| `loop.index` | Current iteration (1-indexed) |
| `loop.index0` | Current iteration (0-indexed) |
| `loop.first` | True if first iteration |
| `loop.last` | True if last iteration |
| `loop.length` | Total number of items |

```jinja2
{% for species in species_list %}
{{ loop.index }} of {{ loop.length }}: {{ species.name }}
{% endfor %}
```

---

## Try It Yourself

Create a file `practice.py`:

```python
from jinja2 import Template

# Simple template
template = Template("""
Shopping List for {{ store }}:
{% for item in items %}
  {{ loop.index }}. {{ item.name }} - ${{ item.price }}
{% endfor %}
Total items: {{ items | length }}
""")

# Data
data = {
    'store': 'Whole Foods',
    'items': [
        {'name': 'Avocados', 'price': 5.99},
        {'name': 'Oat Milk', 'price': 4.49},
        {'name': 'Quinoa', 'price': 7.99},
    ]
}

# Render
print(template.render(data))
```

Run it:
```bash
pip install jinja2
python practice.py
```

---

## Summary

1. **Templates** separate structure from data
2. **Jinja2** uses `{{ }}` for variables and `{% %}` for logic
3. **Loops** repeat content for each item in a list
4. **Conditionals** show/hide content based on conditions
5. **docxtpl** extends Jinja2 for Word docs with `{%tr %}` for table rows

The key insight: **your DataFrame becomes the data, the Word doc becomes the template, and Jinja2 connects them.**

---

## Resources

- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Jinja2 Template Designer Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/)
- [docxtpl Documentation](https://docxtpl.readthedocs.io/)
