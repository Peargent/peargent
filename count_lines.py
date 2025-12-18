import os

def count_lines(directory):
    total_lines = 0
    extensions = {'.py', '.ts', '.tsx', '.js', '.css', '.mdx'}
    exclude_dirs = {'node_modules', '.next', '__pycache__', '.git', 'build', 'dist', '.gemini'}
    
    file_counts = {}

    for root, dirs, files in os.walk(directory):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in extensions:
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = sum(1 for _ in f)
                        total_lines += lines
                        file_counts[ext] = file_counts.get(ext, 0) + lines
                except Exception as e:
                    print(f"Error reading {path}: {e}")

    print(f"Total Lines: {total_lines}")
    print("Breakdown by extension:")
    for ext, count in file_counts.items():
        print(f"  {ext}: {count}")

if __name__ == "__main__":
    count_lines(os.getcwd())
