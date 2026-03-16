# Word Document Export Demo

This example demonstrates how to generate Word documents with dynamic tables from pandas DataFrames using **docxtpl**.

## How It Works

1. **Template**: A Word document (`pto_template.docx`) contains Jinja2 placeholders
2. **Data**: A pandas DataFrame with species occurrence data
3. **Render**: docxtpl fills the template and clones table rows as needed

## Quick Start

```bash
cd examples/word_export

# Install dependencies
pip install python-docx docxtpl pandas

# Create the template (normally you'd design this in Word)
python create_template.py

# Run the demo
python demo_pto_export.py

# Open the generated file
open output_pto_report.docx
```

## The Magic: Dynamic Table Rows

In a normal Word table, you specify exact row counts. With docxtpl, you create a **2-row table**:

| Row | Purpose |
|-----|---------|
| Row 1 | Header (static) |
| Row 2 | Template row with Jinja2 tags (gets cloned N times) |

### Template Row Syntax

In your Word template, the data row contains:

```
{%tr for species in species_data %}{{ species.scientific_name }} | {{ species.common_name }} | ... {%tr endfor %}
```

- `{%tr for ... %}` — Start loop, operates on the table row (`<w:tr>` in XML)
- `{{ species.field }}` — Variable substitution
- `{%tr endfor %}` — End loop

docxtpl finds the `<w:tr>` element, clones it for each item, and renders variables.

## Files

| File | Purpose |
|------|---------|
| `create_template.py` | Programmatically creates the Word template (bootstrap helper) |
| `demo_pto_export.py` | Main demo script — shows DataFrame → Word |
| `pto_template.docx` | The Word template (generated or hand-crafted) |
| `output_pto_report.docx` | Generated output (created by demo) |

## Adapting for Bio Weavers

1. **Get Rincon's template**: Ask for their actual PTO table Word format
2. **Add placeholders**: Insert `{{ variable }}` and `{%tr for ... %}` tags
3. **Map DataFrame columns**: Ensure your species DataFrame has matching column names
4. **Render**: Use `generate_pto_document()` as a starting point

## Key Benefits

- **Template is a real Word doc** — non-programmers can edit formatting
- **Preserves styles** — fonts, colors, borders, company branding
- **Pure Python** — no external binaries like pandoc
- **Lightweight** — just 2 packages (python-docx + docxtpl)

## References

- [docxtpl documentation](https://docxtpl.readthedocs.io/)
- [python-docx documentation](https://python-docx.readthedocs.io/)
