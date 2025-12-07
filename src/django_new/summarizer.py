from datetime import datetime
from io import StringIO
from pathlib import Path

import typer
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from rich.console import Console
from rich.markdown import Markdown
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree

from django_new.transformer import resolve_transformation


class Summarizer:
    def __init__(self, ctx: typer.Context):
        self.ctx = ctx
        self.project_already_existed = self.ctx.obj["project_already_existed"]
        self.folder_path = self.ctx.obj["folder_path"]

    def write_to_console(self, console: Console):
        if self.project_already_existed:
            console.print(Markdown("# Success! 🚀"))
        else:
            console.print(Markdown("# Your new Django application is ready to go! 🚀"))

        # Generate project structure
        console.print("\nProject Structure\n", style="bold underline")

        tree = get_tree(self.folder_path)
        console.print(tree)
        console.print()

        console.print(
            f"To see more details about what was created and why, go to [cyan][link file://{self.folder_path}/django_new/summary.html]{escape('django_new/summary.html')}[/cyan]."
        )
        console.print()

        # Generate next steps
        next_steps = self.get_next_steps()

        if next_steps:
            console.print("Next Steps", style="bold underline")
            console.print(Markdown(next_steps))

    def get_next_steps(self):
        next_steps = []
        next_steps_md = ""

        if self.project_already_existed:
            next_steps.append(
                "Run the following command to start the development server: `uv run python manage.py runserver`"
            )
        else:
            if str(self.folder_path) != ".":
                next_steps.append(f"Go to your project directory: `cd {self.folder_path}`")

            next_steps.append(
                "Run the following command to start the development server: `uv run python manage.py runserver`"
            )

        if self.ctx.params["install"]:
            for transformation_name in self.ctx.params["install"]:
                transformation_cls = resolve_transformation(transformation_name)
                transformation = transformation_cls(root_path=self.folder_path)

                transformation_next_steps = transformation.get_next_steps()
                next_steps.extend(transformation_next_steps)

        for idx, step in enumerate(next_steps):
            next_steps_md += f"{idx + 1}. {step}\n"

        return next_steps_md

    def write_summary_markdown(self) -> None:
        """Write a file."""

        docs_dir = self.folder_path / "django_new/md/"
        docs_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now().isoformat()
        content = ""

        if self.ctx.params["project"] is True:
            content = f"""# `{self.ctx.obj["project_name"]}` Project

- Path: {self.ctx.obj["folder_path"]}
- Created: {now}
"""
        elif self.ctx.params["app"] is True:
            content = f"""# `{self.ctx.obj["app_name"]}` App

- Path: {self.ctx.obj["folder_path"]}
- Created: {now}
"""
        else:
            content = f"""# `{self.ctx.params["name"]}`

- Path: {self.ctx.obj["folder_path"]}
- Created: {now}
"""

        content += """
## Project Structure

The following files and directories were created:
"""

        tree_markdown = get_tree_markdown(self.folder_path)
        content += f"""
```test
{tree_markdown}
```
"""

        if self.ctx.params["project"] is False and self.ctx.params["app"] is False:
            content += f"""
### Directories

- `config`: Project-level settings, top-level urls, and required files for deploying the application.
- `{self.ctx.obj["app_name"]}`: Where you'll probably do most of your work.
- `tests`: Where any tests you write will go.

### Files in the root directory

- `manage.py`: The way Django runs command-line commands. You can run it with `python manage.py`.
- `README.md`: A README file for the application.
- `pyproject.toml`: Application-level dependencies.
"""

        if self.ctx.params["install"]:
            content += "\n## Installed Packages\n"

            for transformation_name in self.ctx.params["install"]:
                transformation_cls = resolve_transformation(transformation_name)
                transformation = transformation_cls(root_path=self.folder_path)

                summary = transformation.get_summary()
                content += summary

        next_steps = self.get_next_steps()

        if next_steps:
            content += f"""
## Next Steps

{next_steps}
"""

        markdown_file = docs_dir / f"{now}.md"
        markdown_file.write_text(f"""---
date: {now}
---

{content}
""")

    def write_summary_html(self) -> None:
        """Write an HTML file."""

        docs_dir = self.folder_path / "django_new"
        docs_dir.mkdir(parents=True, exist_ok=True)

        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <!-- https://github.com/oxalorg/sakura v1.5.1 -->
    <style>html{font-size:62.5%;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif}body{font-size:1.8rem;line-height:1.618;max-width:38em;margin:auto;color:#4a4a4a;background-color:#f9f9f9;padding:13px}@media (max-width:684px){body{font-size:1.53rem}}@media (max-width:382px){body{font-size:1.35rem}}h1,h2,h3,h4,h5,h6{line-height:1.1;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif;font-weight:700;margin-top:3rem;margin-bottom:1.5rem;overflow-wrap:break-word;word-wrap:break-word;-ms-word-break:break-all;word-break:break-word}h1{font-size:2.35em}h2{font-size:2em}h3{font-size:1.75em}h4{font-size:1.5em}h5{font-size:1.25em}h6{font-size:1em}p{margin-top:0;margin-bottom:2.5rem}small,sub,sup{font-size:75%}hr{border-color:#1d7484}a{text-decoration:none;color:#1d7484}a:visited{color:#144f5a}a:hover{color:#982c61;border-bottom:2px solid #4a4a4a}ul{padding-left:1.4em;margin-top:0;margin-bottom:2.5rem}li{margin-bottom:.4em}blockquote{margin-left:0;margin-right:0;padding-left:1em;padding-top:.8em;padding-bottom:.8em;padding-right:.8em;border-left:5px solid #1d7484;margin-bottom:2.5rem;background-color:#f1f1f1}blockquote p{margin-bottom:0}img,video{height:auto;max-width:100%;margin-top:0;margin-bottom:2.5rem}pre{background-color:#f1f1f1;display:block;padding:1em;overflow-x:auto;margin-top:0;margin-bottom:2.5rem;font-size:.9em}code,kbd,samp{font-size:.9em;padding:0 .5em;background-color:#f1f1f1;white-space:pre-wrap}pre>code{padding:0;background-color:#fff0;white-space:pre;font-size:1em}table{text-align:justify;width:100%;border-collapse:collapse;margin-bottom:2rem}td,th{padding:.5em;border-bottom:1px solid #f1f1f1}input,textarea{border:1px solid #4a4a4a}input:focus,textarea:focus{border:1px solid #1d7484}textarea{width:100%}.button,button,input[type=submit],input[type=reset],input[type=button],input[type=file]::file-selector-button{display:inline-block;padding:5px 10px;text-align:center;text-decoration:none;white-space:nowrap;background-color:#1d7484;color:#f9f9f9;border-radius:1px;border:1px solid #1d7484;cursor:pointer;box-sizing:border-box}.button:hover,button:hover,input[type=submit]:hover,input[type=reset]:hover,input[type=button]:hover,input[type=file]::file-selector-button:hover{background-color:#982c61;color:#f9f9f9;outline:0}.button[disabled],button[disabled],input[type=submit][disabled],input[type=reset][disabled],input[type=button][disabled],input[type=file][disabled]{cursor:default;opacity:.5}.button:focus-visible,button:focus-visible,input[type=submit]:focus-visible,input[type=reset]:focus-visible,input[type=button]:focus-visible,input[type=file]:focus-visible{outline-style:solid;outline-width:2px}textarea,select,input{color:#4a4a4a;padding:6px 10px;margin-bottom:10px;background-color:#f1f1f1;border:1px solid #f1f1f1;border-radius:4px;box-shadow:none;box-sizing:border-box}textarea:focus,select:focus,input:focus{border:1px solid #1d7484;outline:0}input[type=checkbox]:focus{outline:1px dotted #1d7484}label,legend,fieldset{display:block;margin-bottom:.5rem;font-weight:600}</style>
</head>
<body>
<main>
"""

        md = MarkdownIt().use(front_matter_plugin)

        for md_file in (self.folder_path / "django_new/md").glob("*.md"):
            rendered_html = md.render(md_file.read_text())
            html += rendered_html

        html += "</main></body></html>"

        html_file = docs_dir / "summary.html"
        html_file.write_text(html)


def get_tree(directory: Path) -> str:
    """Get the tree markdown."""

    tree = Tree(
        f":open_file_folder: [link file://{directory}]{directory}",
        guide_style="",
    )
    walk_directory(directory, tree)

    return tree


def get_tree_markdown(directory: Path) -> str:
    """Get the tree markdown."""

    tree = get_tree(directory)

    # Capture tree output
    capture_console = Console(file=StringIO(), width=100, force_terminal=False, color_system=None)
    capture_console.print(tree)
    tree_content = capture_console.file.getvalue()

    return tree_content


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
