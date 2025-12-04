# django-new ✨

> Create new Django applications with pizazz. 🚀

## Features 🚀

- Interactive mode for creating new applications.
- Predefined structure for typical use cases:
    - API
    - website
    - worker
- Create new Django applications based on a `starter` template.
- Create "minimal" projects (aka [DEP-15](https://github.com/django/deps/blob/main/accepted/0015-extended-startproject.rst)) for a streamlined codebase.
- When creating new apps, automatically add them to `INSTALLED_APPS`.
- Create other files that are typically used in a Django project with sensible defaults:
    - `.env` - Environment variables
    - `.gitignore` - `git` ignore patterns
    - `pyproject.toml` - Python project configuration (PEP 621 compliant)
    - `README.md` - Project documentation

## Goals 🎯

- Strike a balance between `django-admin startproject` / `django-admin startapp` and more full-fledged starter projects.
- Have some opinions about the structure for different use cases, but try to avoid prescribing specific libraries.
- Reduce the confusion between a "project" and "app".
- Be backwards-compatible with existing Django projects.
- Create folders and files automatically with sensible defaults for modern Python workflows that the majority of developers will need.

> NOTE: this is a work in progress and is not yet ready for production use. If you are an expert Django developer, you might disagree with at least some of the opinions here. That's ok. There is a ton (too much?) of bike shedding around project creation. I am open to different opinions and feedback, but I am also focused on handling the 80/20 for new Django projects and provide some patterns based on my personal experience.

## Guiding principles 🕯️

- There are three main use cases for Django: website, API, and worker; they serve different use cases, and each has a unique (but defined) file structure.
- The distinction between ["project" and "app"](https://docs.djangoproject.com/en/stable/ref/applications/) can be confusing for new developers, and creating a "project" without an "app" is an outlier.
- Knowing when to use either `django-admin` or `manage.py` is a common source of confusion.
- The `DJANGO_SETTINGS_MODULE` environment variable is flexible, but annoying to deal with; there should be simpler patterns for managing different environments.
- Having a slightly non-ideal standard that mostly works for a majority of developers is better than no standard at all.

### Hot takes 🔥

- Project-specific files, e.g. `settings.py`, should be in a `config` directory.
- When creating a new app in a project, it should automatically be added to `INSTALLED_APPS`.
- Tests should be written with `pytest` and should be located in a `tests` directory under the project root.
- Settings should be split into multiple files per environment (e.g. `config/settings/base.py`, `config/settings/production.py`, etc.)

## Usage 📖

`django-new` is designed to be used with `uvx` or `pipx`.

```bash
uvx django-new [--api | --web | --worker] [name] [folder]
```

`django-new` creates a standard folder structure for different use cases (based on the --api, --web, or --worker flag) along with a `config` folder to store "project-level" files like `settings.py`. `django-new` also creates a few typically used files (if they do not already exist) when creating a new application:

- `.env` - Local Environment variables
- `.gitignore` - `git` configuration
- `pyproject.toml` - Configuration and dependencies
- `README.md` - Documentation

### Interactive mode

When no arguments are provided, `django-new` will prompt you for the application name and folder location.

```bash
uvx django-new
```

### Create a new API

```bash
uvx django-new --api [name] [folder]
```

```text
.
├── api
│   ├── migrations
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tests
│   └── __init__.py
├── .env
├── .gitignore
├── manage.py
├── pyproject.toml
└── README.md
```

### Create a new website

```bash
uvx django-new --web [name] [folder]
```

```text
.
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static
│   ├── css
│   ├── img
│   └── js
├── tests
│   └── __init__.py
├── web
│   ├── migrations
│   │   └── __init__.py
│   ├── templates
│   ├── templatetags
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── .env
├── .gitignore
├── manage.py
├── pyproject.toml
└── README.md
```

### Create a new worker

```bash
uvx django-new --worker [name] [folder]
```

```text
.
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tests
│   └── __init__.py
├── worker
│   ├── migrations
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   └── tasks.py
├── .env
├── .gitignore
├── manage.py
├── pyproject.toml
└── README.md
```

### Create a new default application

```bash
uvx django-new [name] [folder]
```

```text
.
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── {name}
│   ├── migrations
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── tests
│   └── __init__.py
├── .env
├── .gitignore
├── manage.py
├── pyproject.toml
└── README.md
```

### Create a new "minimal" application

Based on the minimal project in [DEP-15](https://github.com/django/deps/blob/main/accepted/0015-extended-startproject.rst), this will create a new Django project and app within a single directory.

```bash
uvx django-new --api --minimal [name] [folder]
uvx django-new --web --minimal [name] [folder]
uvx django-new --worker --minimal [name] [folder]
uvx django-new --minimal [name] [folder]
```

```text
.
├── {name}
│   ├── migrations
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── asgi.py
│   ├── models.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── tests
│   └── __init__.py
├── .env
├── .gitignore
├── manage.py
├── pyproject.toml
└── README.md
```

### Create a new application based on a starter

Use the provided path to create a custom application.

```bash
uvx django-new --starter={path} [name] [folder]
```

>Starters use the built-in Django `startproject --template` functionality under the hood.

The path passed into the `starter` option can be a directory, local archive file, or a remote URL. Remote URLs must point to an archive file using a `http`, `https`, or `ftp` protocol.

>Supported archive file extensions: `.zip`, `.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz`, `.tar.lzma`, `.tgz`, `.tbz2`, `.txz`, `.tlz`

```bash
uvx django-new --starter=https://github.com/githubuser/django-app-template/archive/main.zip new_project
```

>Starters from untrusted sources should be carefully inspected before use to prevent potential security issues.

#### Variable replacement

Starters can use variables that will be replaced in the included `.py` files using Django template syntax, like `{{ project_name }}`.

The context used for variable replacement:

```python
{
    "project_name": "the project name provided to django-new, e.g. 'myproject'",
    "project_directory": "/full/path/to/the/myproject",
    "secret_key": "a randomly generated secret key",
    "docs_version": "version of the documentation",
    "django_version": "version of Django"
}
```

### Add new app to an existing Django project

If a project already exists in the specified folder, `django-new` will add a new app to it. Use the same flags as above to create a specific type of app.

```bash
uvx django-new --api [name] [folder]
uvx django-new --web [name] [folder]
uvx django-new --worker [name] [folder]
uvx django-new [name] [folder]
```

### Create a bare project

When a non-project folder is specified and an app should _not_ be created, use the `--project` flag.

```bash
uvx django-new --project [name] [folder]
```

```text
.
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tests
│   └── __init__.py
├── .env
├── .gitignore
├── manage.py
├── pyproject.toml
└── README.md
```

### Create a bare app

When a non-project folder is specified and a project should _not_ be created, use the `--app` flag.

```bash
uvx django-new --app [name] [folder]
```

```text
.
└── {name}
    ├── migrations
    │   └── __init__.py
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── urls.py
    └── views.py
```

## Inspiration ❤️

Heavily inspired by [DEP-15](https://github.com/django/deps/blob/main/accepted/0015-extended-startproject.rst), although it approaches the solution from a different angle.

- [DEP-15](https://github.com/django/deps/blob/main/accepted/0015-extended-startproject.rst)
- [knyghty's django-new](https://github.com/knyghty/django-new)
- [DEP-15 discussion](https://forum.djangoproject.com/t/dep-15-improved-startproject-interface/43384)
- [startapp template discussion](https://forum.djangoproject.com/t/updating-the-default-startapp-template/24193)
- https://epicserve.com/django/2024/10/24/improving-the-new-django-developer-experience.html
- https://www.mostlypython.com/django-from-first-principles/
- [djinit](https://github.com/S4NKALP/djinit)
- [`typer`](https://typer.tiangolo.com)
- [`rich`](https://rich.readthedocs.io)

## Tests

`just test`