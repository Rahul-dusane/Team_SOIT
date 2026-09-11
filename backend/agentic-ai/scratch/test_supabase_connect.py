import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

regions = ["ap-south-1", "us-east-1", "us-west-1", "eu-central-1", "sa-east-1", "eu-west-1", "ap-southeast-1"]
password = "Msc@14056$$"
project_ref = "grcihwgasjgofsrlhdox"
db_user = f"postgres.{project_ref}"

print(f"Testing Supabase connection with project reference '{project_ref}'...")

# First test direct connection
try:
    print("\n[1] Testing direct connection URI...")
    direct_url = f"postgresql://postgres:Msc%4014056%24%24@db.{project_ref}.supabase.co:5432/postgres"
    conn = psycopg.connect(direct_url, connect_timeout=5)
    print("SUCCESS! Direct connection works.")
    conn.close()
except Exception as e:
    print(f"Direct connection failed: {e}")

# Next test poolers
for region in regions:
    for port in [5432, 6543]:
        pooler_host = f"aws-0-{region}.pooler.supabase.com"
        print(f"\n[2] Testing Pooler {pooler_host}:{port} with user '{db_user}'...")
        try:
            conn = psycopg.connect(
                host=pooler_host,
                port=port,
                dbname="postgres",
                user=db_user,
                password=password,
                connect_timeout=5
            )
            print(f"\n>>> SUCCESS! Connected to Supabase via Pooler {pooler_host}:{port} <<<")
            
            # Print connection pooler URI
            pooler_url = f"postgresql://postgres.{project_ref}:Msc%4014056%24%24@{pooler_host}:{port}/postgres"
            print(f"Working DATABASE_URL: {pooler_url}\n")
            conn.close()
            break
        except Exception as e:
            print(f"Failed ({pooler_host}:{port}): {e}")
