from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

from rich.console import Console
from rich.markup import escape
from rich.tree import Tree
from rich.text import Text


def write_friendly_summary(project_name, folder_path):
    """Write a friendly summary of the initial project structure.

    What was created?
    What's the rationale?
    Where can the user learn more?
    """
    # Read base template string.
    path_summary_template = Path(__file__).parent / "friendly_summary.html"
    html_string = path_summary_template.read_text()

    # Build context dictionary.
    context = {
        "project_name": project_name,
        "ts_created": datetime.now(timezone.utc).strftime("%m/%d/%Y %H:%M:%S"),
        "tree_string": _get_tree_string(folder_path),
        "expl_project_structure": _get_expl_project_structure(project_name),
    }

    # Make replacements.
    for key, value in context.items():
        html_string = html_string.replace(f"{{{{{key}}}}}", value)

    # Write customized summary to file.
    dest_path = folder_path / "friendly_summary.html"
    dest_path.write_text(html_string)


# --- Helpers ---

def _get_tree_string(folder_path):
    """Get project directory structure as a string."""
    tree = Tree(
        f":open_file_folder: [link file://{folder_path}]{folder_path}",
        guide_style="",
    )
    walk_directory(folder_path, tree)

    buffer = StringIO()
    file_console = Console(file=buffer, force_terminal=False, color_system=None)
    file_console.print(tree)

    return buffer.getvalue()


# This is copied from cli.py to avoid circular import.
def walk_directory(directory: Path, tree: Tree) -> None:
    """Recursively build a Tree with directory contents."""

    # Sort dirs first then by filename
    paths = sorted(
        directory.iterdir(),
        key=lambda path: (path.is_file(), path.name.lower()),
    )

    for path in paths:
        # Remove hidden files
        if path.name.startswith("."):
            continue

        if path.is_dir():
            style = "dim" if path.name.startswith("__") else ""

            branch = tree.add(
                f":open_file_folder: [link file://{path}]{escape(path.name)}",
                style=style,
                guide_style=style,
            )
            walk_directory(path, branch)
        else:
            text_filename = Text(path.name, "blue")
            text_filename.stylize(f"link file://{path}")

            tree.add(text_filename)

def _get_expl_project_structure(project_name):
    """Get an explanation for the specific project structure that was built."""
    expl = f"This project has three main directories. There's a <code>config/</code> directory, which contains project-level settings, urls, and more. There's a <code>{ project_name }/</code> directory, which is where you'll probably do most of your initial work. There's also a <code>tests/</code> directory, where you can start to write tests. <code>manage.py</code> is in the root directory, along with starting <code>pyproject.toml</code> and <code>README.md</code> files."

    return expl