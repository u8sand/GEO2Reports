import papermill as pm
from pathlib import Path
import argparse
import nbformat
from nbconvert import HTMLExporter

project_root = Path(__file__).resolve().parents[2]  
output_dir = project_root / "public"
output_dir.mkdir(parents=True, exist_ok=True)

def run_notebook(gse_id):
    input_nb = project_root/"python"/"notebooks"/"report_template.ipynb"
    output_nb = output_dir/f"{gse_id}"/f"{gse_id}.ipynb"
    output_html = output_dir/f"{gse_id}"/f"{gse_id}.html"

    output_nb.parent.mkdir(parents=True, exist_ok=True)

    print(f"Running notebook for {gse_id}...")

    pm.execute_notebook(
        input_path=input_nb,
        output_path=output_nb,
        parameters={
            "gse": gse_id,
            "project_root": str(project_root)
        },
    )

    print(f"Notebook executed and saved at {output_nb}")

    with open(output_nb, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    html_exporter = HTMLExporter()
    html_exporter.exclude_input = True
    html_exporter.exclude_output_prompt = True
    html_exporter.exclude_input_prompt = True
    html_data, _ = html_exporter.from_notebook_node(nb)
    
    with open(output_html, 'w') as f:
        f.write(html_data)

    print(f"HTML generated and saved at {output_html}")

#allow it to be ran from the command line

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run analysis notebook for a given GEO study.")
    parser.add_argument("gse_id", help="GSE ID to run the notebook for (e.g., GSE12345)")
    args = parser.parse_args()

    run_notebook(args.gse_id)