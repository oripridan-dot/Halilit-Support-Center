import os

# Priority files to include in the review bundle
FILES_TO_INCLUDE = [
    "README.md",
    "HANDOFF_v7.5.md",
    "backend/conductor_main.py",
    "backend/server.py",
    "backend/unified_data_service_v76.py",
    "backend/unified_agent_orchestrator_v76.py",
    "backend/unified_quality_gates_v76.py",
    "backend/unified_learning_system_v76.py",
    "backend/ingestion/orchestrator.py",
    "backend/ingestion/visual_validator.py",
    "backend/ingestion/data_models.py",
    "backend/ingestion/taxonomy_manager.py",
    "frontend/src/lib/imageResolver.ts",
    "frontend/src/App.tsx",
    "frontend/src/components/views/SpectrumModule.tsx",
    "frontend/src/components/views/GalaxyDashboard.tsx",
    "frontend/src/components/views/ProductPage.tsx",
]

OUTPUT_FILE = "GEMINI_REVIEW_BUNDLE.md"

def generate_tree(startpath):
    tree_str = "## Project Structure\n\n```text\n"
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        if ".git" in root or "node_modules" in root or "__pycache__" in root or "public/data" in root:
            continue
        tree_str += '{}{}/\n'.format(indent, os.path.basename(root))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f.endswith(".json"): continue # Skip json data files
            tree_str += '{}{}\n'.format(subindent, f)
    tree_str += "```\n\n"
    return tree_str

def create_bundle():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        outfile.write("# Halilit Support Center - Code Review Bundle (v7.6)\n\n")
        outfile.write("Generated for Gemini 3 Pro Code Review.\n\n")
        
        # 1. Add File Tree (Simplified)
        # outfile.write(generate_tree(".")) # Can be too large, let's skip strict tree and just list included files
        outfile.write("## Included Files\n\n")
        for f in FILES_TO_INCLUDE:
            outfile.write(f"- {f}\n")
        outfile.write("\n")

        # 2. Add File Contents
        for filepath in FILES_TO_INCLUDE:
            if os.path.exists(filepath):
                outfile.write(f"## File: {filepath}\n\n")
                ext = filepath.split('.')[-1]
                lang = "python" if ext == "py" else "typescript" if ext in ["ts", "tsx"] else "markdown"
                
                outfile.write(f"```{lang}\n")
                try:
                    with open(filepath, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Error reading file: {e}")
                outfile.write("\n```\n\n")
            else:
                outfile.write(f"## File: {filepath} (NOT FOUND)\n\n")

    print(f"Bundle created at {OUTPUT_FILE}")

if __name__ == "__main__":
    create_bundle()
