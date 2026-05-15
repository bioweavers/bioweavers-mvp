from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT


def create_pto_template(output_path="src/pto_template.docx"):
    doc = Document()

    doc.add_heading("PTO Assessment Report", level=1)
    doc.add_heading("Potential to Occur Determinations", level=2)

    table = doc.add_table(rows=5, cols=5)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = [
        "Scientific Name\nCommon Name",
        "Status",
        "Habitat Requirements",
        "Potential to Occur",
        "Habitat Suitability/\nObservations",
    ]

    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h

    # Taxon group loop start
    table.rows[1].cells[0].text = "{%tr for group in taxon_groups %}"

    # Taxon group header row
    group_header = table.rows[2].cells
    group_header[0].merge(group_header[-1])
    group_header[0].text = "{{ group.TaxonGroup }}"

    # Species row loop start
    table.rows[3].cells[0].text = "{%tr for row in group.rows %}"

    # Species data row
    data = table.rows[4].cells
    data[0].text = "{{ row.SpeciesDisplay }}"
    data[1].text = "{{ row.StatusDisplay }}"
    data[2].text = "{{ row.HabitatRequirements }}"
    data[3].text = "{{ row.PotentialtoOccur }}"
    data[4].text = "{{ row.HabitatSuitabilityObservations }}"

    # You need two extra rows for the loop endings
    row_end = table.add_row().cells
    row_end[0].text = "{%tr endfor %}"

    group_end = table.add_row().cells
    group_end[0].text = "{%tr endfor %}"

    doc.save(output_path)


if __name__ == "__main__":
<<<<<<< HEAD
    create_pto_template()
=======
    create_pto_template()
>>>>>>> 4803462ce6584d69bdc8082f99271a653c11f38b
