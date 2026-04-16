from huggingface_hub import HfApi
import sys
import os

token = "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"
api = HfApi(token=token)

try:
    user_info = api.whoami()
    username = user_info['name']
    repo_id = f"{username}/Simulador-Odorata"
    
    print(f"Authenticated as {username}")
    print(f"Creating repo {repo_id} as a Docker Space...")
    api.create_repo(repo_id=repo_id, repo_type="space", space_sdk="docker", exist_ok=True)
    
    print("Uploading project files to Hugging Face...")
    api.upload_folder(
        folder_path=r"c:\JGA\JGA\estudos_ufg",
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=["*.sqlite3", "__pycache__/*", ".venv/*", "deploy_hf.py"]
    )
    print(f"\nSuccessfully deployed!")
    print(f"App URL: https://huggingface.co/spaces/{repo_id}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
