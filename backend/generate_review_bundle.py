import os
import zipfile
from pathlib import Path

def create_bundle():
    # Define root of the workspace
    workspace_root = Path(__file__).resolve().parent.parent
    output_zip = workspace_root / "code-review-bundle.zip"
    
    print(f"Generating bundle at: {output_zip}")
    
    # Extensions and dirs to include
    include_extensions = {".py", ".ts", ".tsx", ".css", ".md", ".json", ".html", ".js"}
    exclude_dirs = {
        "node_modules", 
        "__pycache__", 
        ".git", 
        ".vscode", 
        "dist", 
        "build", 
        "coverage", 
        ".pytest_cache",
        "venv",
        ".devcontainer",
        "raw_landing_zone", # Data folder exclusion - usually large
        "catalogs_brand",   # Data folder exclusion
    }

    # Specific large data files to exclude even if extension matches
    exclude_files = {
        "package-lock.json",
        "pnpm-lock.yaml", 
        "code-review-bundle.zip"
    }

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(workspace_root):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check exclusion list
                if file in exclude_files:
                    continue
                
                # Check extension
                if file_path.suffix not in include_extensions and file != "Dockerfile":
                    continue
                    
                # Calculate relative path for zip structure
                arcname = file_path.relative_to(workspace_root)
                
                # Further filtering based on path components (e.g. inside public/data)
                if "public/data" in str(arcname):
                    # We might want to exclude large generated data files
                     if file_path.suffix == ".json" and file != "index.json":
                         # fast check if file is too big?
                         if file_path.stat().st_size > 1024 * 1024:
                             print(f"Skipping large data file: {arcname}")
                             continue

                print(f"Adding: {arcname}")
                zipf.write(file_path, arcname)

    print("Bundle creation complete.")

if __name__ == "__main__":
    create_bundle()
