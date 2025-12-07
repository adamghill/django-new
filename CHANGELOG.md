# Changelog

## 0.6.0

- Lots of UI tweaks to the CLI.
- Add `--data` application type.
- Generate markdown files for each action that `django-new` performs.
- Generate `summary.html` for a user-friendly summary of all actions.
- BETA: Added `--install` flag to install packages (only `whitenoise` is supported currently).

## 0.5.0

- Fix checking for running under `uvx`.
- Add `--verbose` flag to show more output.
- Add `--python` flag to specify Python version.
- Add `--django` flag to specify Django version.
- Create folder under `tests` when adding a new app.

## 0.4.0

- Interactive mode for name and folder.
- Show tree structure after application creation.
- Cleaned up prompts and output formatting.

## 0.3.0

- Add `--starter` flag to use custom project templates.
- Improved handling of existing folders by prompting the user.
- Add `--version`.

## 0.2.0

- Initial release with basic project and app generation capabilities.
- Support for creating APIs, websites, and workers.
- Support creating minimal applications similar to DEP-15.

## 0.1.0

- Initial release to start a discussion around figuring out the goals and requirements.
