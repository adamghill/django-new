# django-new ✨

> Create new Django applications with sensible defaults and modern patterns. 🚀

## Features 🚀

- Create new Django applications based on typical use cases, e.g. API, website, worker.
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
- The distinction between "project" and "app" is [unnecessarily confusing](#project-vs-app-terminology-confusion).
- Creating a "project" or "app" without the other doesn't happen that often, so it should be treated as an outlier, not the normal case.
- Knowing when to use either `django-admin` or `manage.py` is a common source of confusion.
- The `DJANGO_SETTINGS_MODULE` environment variable is too flexible and there should be simpler patterns for managing different environments.
- Having a slightly non-ideal standard that mostly works for a majority of developers is better than no standard at all because it reduces cognitive load.

### Hot takes 🔥

- Project-specific files, e.g. `settings.py`, should be in a `config` directory.
- When creating a new app, it should automatically be added to `INSTALLED_APPS`.
- Tests should be written with `pytest` and should be located in a `tests` directory under the root.
- Settings should be split into multiple files per environment (e.g. `config/settings/base.py`, `config/settings/production.py`, etc.)

## Usage 📖

`django-new` is designed to be used with `uvx` or `pipx`.

```bash
uvx django-new [--api] [--web] [--worker] name [folder]
```

`django-new` has _some_ opinions about the folder structure and what files are most useful for certain use cases. For example, `config` is used to store "project-level" files like `settings.py`. The `--api`, `--web`, and `--worker` flags can be used as an additional modifier to create a specific type of application.

Along with the typical Django files, `django-new` also creates a few typically used files (if they do not already exist) when creating a new project:

- `.env` - Environment variables
- `.gitignore` - `git` ignore patterns
- `pyproject.toml` - Python project configuration (PEP 621 compliant)
- `README.md` - Project documentation

### Create a new API

```bash
uvx django-new --api name [folder]
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
uvx django-new --web name [folder]
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
uvx django-new --worker name [folder]
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

### Create a new generic app

```bash
uvx django-new name [folder]
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

### Add new app to an existing Django project

If a project already exists in the specified folder, `django-new` will add a new app to it. Use the same flags as above to create a specific type of app.

```bash
uvx django-new --api name [folder]
uvx django-new --web name [folder]
uvx django-new --worker name [folder]
uvx django-new name [folder]
```

### Create a minimal project

`django-new` can create a "minimal" project with a single directory, similar to the ideas in [DEP-15](https://github.com/django/deps/blob/main/accepted/0015-extended-startproject.rst).

```bash
uvx django-new --api --minimal name [folder]
uvx django-new --web --minimal name [folder]
uvx django-new --worker --minimal name [folder]
uvx django-new --minimal name [folder]
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

### Create a bare project

When a non-project folder is specified and an app should _not_ be created, use the `--project` flag.

```bash
uvx django-new --project name [folder]
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
uvx django-new --app name [folder]
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

## Project vs app terminology confusion

Django's use of "project" and "app" can sometimes cause confusion.

More details about the distinction between "project" and "app" are in the [Django documentation](https://docs.djangoproject.com/en/stable/ref/applications/).

## Inspiration ❤️

Heavily inspired by [DEP-15](https://github.com/django/deps/blob/main/accepted/0015-extended-startproject.rst), although it approaches the solution from a different angle.

- [DEP-15](https://github.com/django/deps/blob/main/accepted/0015-extended-startproject.rst)
- [knyghty's django-new](https://github.com/knyghty/django-new)
- [DEP-15 discussion](https://forum.djangoproject.com/t/dep-15-improved-startproject-interface/43384)
- [startapp template discussion](https://forum.djangoproject.com/t/updating-the-default-startapp-template/24193)
- https://epicserve.com/django/2024/10/24/improving-the-new-django-developer-experience.html
- https://www.mostlypython.com/django-from-first-principles/

## Tests

`just test`