import os

def generate_markdown_tree(directory, prefix=""):
    """Generates a markdown tree structure of a given directory, excluding __pycache__ folders."""
    result = []
    items = sorted(os.listdir(directory))
    for index, item in enumerate(items):
        path = os.path.join(directory, item)
        
        # Skip __pycache__ folders
        if item == "__pycache__":
            continue

        connector = "├── " if index < len(items) - 1 else "└── "
        result.append(f"{prefix}{connector}{item}")
        if os.path.isdir(path):
            sub_prefix = "│   " if index < len(items) - 1 else "    "
            result.extend(generate_markdown_tree(path, prefix + sub_prefix))
    return result

def save_markdown_tree(directory, output_file="folder_structure.md"):
    """Saves the markdown tree structure to a file with utf-8 encoding, excluding __pycache__ folders."""
    tree = generate_markdown_tree(directory)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(tree))
    print(f"Markdown folder structure saved to {output_file}")

# Replace 'your_directory_path' with the path to your folder
directory_path = './src'
save_markdown_tree(directory_path)