import pandas as pd

# Join non empty lines
def join_lines(*parts):
    cleaned = [str(p).strip() for p in parts if pd.notna(p) and str(p).strip()]
    return "\n".join(cleaned)