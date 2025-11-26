# django-new ✨

> It is like `django-admin startproject mysite djangotutorial`, but better.

## Features 🚀

- Create new Django projects based on typical use cases, e.g. API, website, worker
- Support "classic" and "minimal" project types
- When creating new apps, automatically add them to `INSTALLED_APPS`
- Create other files that are typically used in a Django project with sensible defaults
    - `.env`
    - `.gitignore`
    - `pyproject.toml`
    - `README.md`

## Goals 🎯

- Strike a balance between `django-admin startproject` / `django-admin startapp` and more full-fledged starter projects.
- Have some opinions about the structure for different use cases, but try not to recommend specific libraries.
- Reduce the confusion between a "project" and "app".
- Be backwards-compatible with existing Django projects.
- Create folders and files automatically with sensible defaults for modern Python workflows that the majority of developers will need.

NOTE: this is a work in progress and is not yet ready for production use. If you are an expert Django developer, you might disagree with at least some of the opinions here. And that's ok. There is a ton of bike shedding around project creation. I am open to different opinions and feedback, but I am also focused on creating a tool that handles the 80/20 use cases for a new Django project and provide some patterns based on my experience in the past.

## Guiding principles 🕯️

- There are three main use cases for Django: website, API, and worker; they serve different use cases, and each has a unique (but defined) file structure.
- The distinction between "project" and "app" is [unnecessarily confusing](#project-vs-app-terminology-confusion).
- Tools can understand when a "project" needs to be created or whether an "app" should be added to an existing project.
- Having both `django-admin` and `manage.py` is confusing for new Django developers.
- `DJANGO_SETTINGS_MODULE` is confusing for new Django developers.
- Having a slightly non-ideal standard that mostly works for a majority of developers is better than no standard at all.

### Hot takes 🔥

- Creating a bare project without an app is almost never useful.
- Project-specific files should be in a "config" directory.
- When creating a new app, it should automatically be added to `INSTALLED_APPS`.
- Tests should be in a root `tests` directory and use `pytest`.
- Settings should be split into multiple files (e.g. `config/settings/base.py`, `config/settings/production.py`, etc.)

## Usage 📖

`django-new` is designed to be used with `uv` or `pipx`, however it can be called from inside a virtual environment, as well.

```bash
uv run django-new [--api] [--web] [--worker] name [folder]
```

`django-new` has _some_ opinions about the folder structure and what files are most useful for certain use cases. For example, `config` is used to store "project-level" files like `settings.py`. The `--api`, `--web`, and `--worker` flags can be used as an additional modifier to create a specific types of applications.

Along with the typical Django files, `django-new` also creates a few typically used files (if they do not already exist) when creating a new project:

- `.env` for environment variables
- `.gitignore`
- `pyproject.toml` for dependency management
- `README.md`

If `pyproject.toml` exists, `django-new` will add `Django` to the project dependencies.

### Create a new API

```bash
uv run django-new --api name [folder]
```

```text
.
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── api
│   ├── migrations
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── .env
├── .gitignore
├── manage.py
├── pyproject.toml
└── README.md
```

### Create a new website

```bash
uv run django-new --web name [folder]
```

```text
.
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── web
│   ├── migrations
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
uv run django-new --worker name [folder]
```

```text
.
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
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
uv run django-new name [folder]
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
├── .env
├── .gitignore
├── manage.py
├── pyproject.toml
└── README.md
```

### Add new apps to an existing project

If a project already exists in the specified folder, `django-new` will add a new app to it. Use the same flags as above to create specific types of applications.

```bash
uv run django-new --api name [folder]
uv run django-new --web name [folder]
uv run django-new --worker name [folder]
uv run django-new name [folder]
```

### Create a minimal project

`django-new` can create a "minimal" project with a single directory, similar to the ideas in [DEP-15](https://github.com/django/deps/blob/main/accepted/0015-extended-startproject.rst).

```bash
uv run django-new --api --minimal name [folder]
uv run django-new --web --minimal name [folder]
uv run django-new --worker --minimal name [folder]
uv run django-new --minimal name [folder]
```

```text
.
├── mysite
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
├── .env
├── .gitignore
├── manage.py
├── pyproject.toml
└── README.md
```

### Create a bare project

When a non-project folder is specified and an app should _not_ be created, use the `--project` flag.

```bash
uv run django-new --project name [folder]
```

```text
.
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .env
├── .gitignore
├── manage.py
├── pyproject.toml
└── README.md
```

### Create a bare app

When a non-project folder is specified and a project should _not_ be created, use the `--app` flag.

```bash
uv run django-new --app name [folder]
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

For a **classic** Django application, "project" refers to the entire deployable, e.g. it's the entire website, and "app" refers to smaller, contained namespaces of functionality. For example, a `wwww.my-cool-django-app.com` blog website might have a `project` named "my_cool_django_app", a "my_cool_django_app" subfolder with settings, and two folders for `apps`: "blog" and "profile".

```text
.
└── my_cool_django_app
    ├── my_cool_django_app
    │   ├── settings.py
    │   └── ...
    ├── blog
    │   ├── apps.py
    │   └── ...
    └── profile
        ├── apps.py
        └── ...
```

```{note}
More details about the distinction between "project" and "app" are in the [Django documentation](https://docs.djangoproject.com/en/stable/ref/applications/).
```

## Inspiration ❤️

Heavily inspired by [DEP-15](https://github.com/django/deps/blob/main/accepted/0015-extended-startproject.rst), although it approaches the same solution from a different angle than https://github.com/knyghty/django-new.

 Instead of new template files, `django-new` calls the existing `startproject` and `startapp` commands and tweaks the output. This prevents `django-new` from having to handle different template files across Django versions.

- https://github.com/django/deps/blob/main/accepted/0015-extended-startproject.rst
- https://github.com/knyghty/django-new
- https://forum.djangoproject.com/t/dep-15-improved-startproject-interface/43384
