from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT


def create_pto_template(output_path="app/utils/pto_template.docx"):
    doc = Document()

    doc.add_heading("PTO Assessment Report", level=1)
    doc.add_heading("Potential to Occur Determinations", level=2)

    # Build table with enough rows for:
    # header, CNPS header, loop start, data row, loop end,
    # CNDDB header, loop start, data row, loop end
    table = doc.add_table(rows=9, cols=7)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = [
        "Scientific Name",
        "Common Name",
        "Life Form",
        "Quads",
        "Habitat",
        "Potential to Occur",
        "Suitability/Observations",
    ]

    # ---------------------------------------------------------
    # HEADER ROW
    # ---------------------------------------------------------
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        run = hdr[i].paragraphs[0].add_run(h)
        run.bold = True

    # ---------------------------------------------------------
    # CNPS MERGED HEADER ROW (real merged row)
    # ---------------------------------------------------------
    cnps_header = table.rows[1].cells
    cnps_header[0].merge(cnps_header[-1])
    cnps_header[0].text = "{% if loop.first %}CNPS Species{% endif %}"

    # ---------------------------------------------------------
    # LOOP START FOR CNPS + CNDDB
    # ---------------------------------------------------------
    table.rows[2].cells[0].text = "{%tr for row in rows %}"

    # ---------------------------------------------------------
    # DATA ROW
    # ---------------------------------------------------------
    data_row = table.rows[3].cells
    data_row[0].text = "{{ row.ScientificName }}"
    data_row[1].text = "{{ row.CommonName }}"
    data_row[2].text = "{{ row.Lifeform }}"
    data_row[3].text = "{{ row.Quads }}"
    data_row[4].text = "{{ row.Habitat }}"
    data_row[5].text = "{{ row.PotentialtoOccur }}"
    data_row[6].text = "{{ row.HabitatSuitabilityObservations }}"

    # ---------------------------------------------------------
    # LOOP END
    # ---------------------------------------------------------
    table.rows[4].cells[0].text = "{%tr endfor %}"

    # ---------------------------------------------------------
    # CNDDB MERGED HEADER ROW (real merged row)
    # ---------------------------------------------------------
    cnddb_header = table.rows[5].cells
    cnddb_header[0].merge(cnddb_header[-1])
    cnddb_header[0].text = "{% if row.Category == 'CNDDB' and loop.previtem.Category != 'CNDDB' %}CNDDB Species{% endif %}"

    # ---------------------------------------------------------
    # SECOND LOOP START (same rows list)
    # ---------------------------------------------------------
    table.rows[6].cells[0].text = "{%tr for row in rows %}"

    # ---------------------------------------------------------
    # SECOND DATA ROW
    # ---------------------------------------------------------
    data_row2 = table.rows[7].cells
    data_row2[0].text = "{{ row.ScientificName }}"
    data_row2[1].text = "{{ row.CommonName }}"
    data_row2[2].text = "{{ row.Lifeform }}"
    data_row2[3].text = "{{ row.Quads }}"
    data_row2[4].text = "{{ row.Habitat }}"
    data_row2[5].text = "{{ row.PotentialtoOccur }}"
    data_row2[6].text = "{{ row.HabitatSuitabilityObservations }}"

    # ---------------------------------------------------------
    # SECOND LOOP END
    # ---------------------------------------------------------
    table.rows[8].cells[0].text = "{%tr endfor %}"

    doc.save(output_path)
