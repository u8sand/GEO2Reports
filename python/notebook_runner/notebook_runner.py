import papermill as pm
import nbformat
from nbconvert import HTMLExporter
from minio import Minio
from urllib.parse import urlparse
from tempfile import TemporaryDirectory
import os
import shutil
import psycopg2 
import dotenv
import json
import io
from datetime import date 

dotenv.load_dotenv()

def run_notebook(gse_id, tmpdir):
    root_dir = os.path.realpath(os.path.join(os.getcwd(), '..')) #check on this. still a bit uneasy.
    print(root_dir)
    print(f"temp directory created at: {tmpdir}")
    input_path = os.path.join(root_dir, "notebooks", "report_template.ipynb") #where template notebook is located
    temp_input_path = os.path.join(tmpdir, "report_template.ipynb") 
    shutil.copyfile(input_path, temp_input_path) #copy it into the temp directory
    temp_output_path = os.path.join(tmpdir, f"{gse_id}.ipynb")
    output_html = os.path.join(tmpdir, f"{gse_id}.html")

    pm.execute_notebook(
        input_path=temp_input_path,
        output_path=temp_output_path,
        parameters={
            "gse": gse_id,
            "working_dir": tmpdir
        },
    )
    print(f"Notebook executed and saved at {temp_output_path}")

    #save to html
    with open(temp_output_path, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    html_exporter = HTMLExporter() #optional: template
    html_exporter.exclude_input = True
    html_exporter.exclude_output_prompt = True
    html_exporter.exclude_input_prompt = True
    html_data, _ = html_exporter.from_notebook_node(nb)
    
    with open(output_html, 'w') as f:
        f.write(html_data)

    print(f"HTML generated and saved at {output_html}")
    #os.remove(temp_input_path) #remove to avoid it being uploaded to S3

def update_postgres(tmpdir, conn, cur):
    json_path = os.path.join(tmpdir, "metadata.json")
    with open(json_path, 'r') as f:
        metadata = json.load(f)
    
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    print(cur.fetchall()) #print the table names for debugging.

    columns = metadata.keys()
    values = [metadata[col] for col in columns]

    query = f"""
        INSERT INTO reports ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
        ON CONFLICT (id) DO UPDATE SET
        {', '.join([f"{col}=EXCLUDED.{col}" for col in columns if col != 'id'])}
    """

    cur.execute(query, values)
    conn.commit()
    print("successfully committed")

def update_s3(gse_id, tmpdir, s3, bucket):
    
    for root, _, files in os.walk(tmpdir):
        for filename in files:
            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, tmpdir).replace("\\", "/")
            object_key = f"{gse_id}/{relative_path}"

            s3.fput_object(bucket, object_key, local_path)
    
    print(f"✅ Uploaded GSE {gse_id} contents to MinIO bucket '{bucket}'")

        

def process_gse(gse_id, conn, cur, s3, bucket):
    cur.execute("SELECT 1 FROM reports WHERE id = %s LIMIT 1;", (gse_id,))
    exists = cur.fetchone() is not None
    if exists:
        print(f"GSE {gse_id} already exists in Postgres. Skipping processing.")
        return
    
    with TemporaryDirectory() as tmpdir:
        print(f"started processing for {gse_id} in temp directory {tmpdir}")
        try:
            run_notebook(gse_id, tmpdir)
            update_s3(gse_id, tmpdir, s3, bucket)
            update_postgres(tmpdir, conn, cur)
            print("processing successful!")
        except Exception as e:
            print(f"Error processing {gse_id}: {e}")
            raise #get rid of in production so it doesnt interrupt execution