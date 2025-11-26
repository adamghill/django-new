# django-new ✨

> It is like `django-admin startproject mysite djangotutorial`, but better.

## Features 🚀

- Create a new Django project
- Support "classic" and "minimal" project types
- Add a new app to an existing project (and automatically add it to `INSTALLED_APPS`)
- Create other files that are typically used in a Django project (e.g. `pyproject.toml`, `.env`, `.gitignore`, `README.md`)

## Goals 🎯

- Strike a balance between `django-admin startproject` and other more full-fledged starter projects: have some opinions about the structure for different use cases, but try not to recommend specific libraries.
- Reduce the confusion between a "project" and "app".
- Be "backwards-compatible" with existing Django projects.
- Create folders and files automatically with sensible defaults for modern Python workflows that the majority of developers will need.

Note: this is a work in progress, and is not yet ready for production use. There is a massive amount of bike shedding around project creation and no one will agree completely with each other. I am open to different opinions and feedback, but no promises.

## Guiding principles 🕯️

- the distinction between "project" and "app" is unnecessarily confusing; tools can understand when a "project" needs to be created or whether an "app" should be added to an existing project
- having both `django-admin` and `manage.py` is confusing
- there are three types of projects: site, api, worker, they all serve different use cases, and each has a unique (but defined) file structure
- project structure is a prime bike shedding topic, but having a standard that mostly works for a majority of developers is better than no standard at all

### Hot takes 🔥

- creating a bare project without an app is almost never useful
- project configuration should be in a "config" directory
- when creating a new app, the tool should automatically add it to `INSTALLED_APPS`
- tests should be in a root `tests` directory and written with `pytest`
- settings should be split into multiple files (e.g. `config/settings/base.py`, `config/settings/production.py`, etc.)

## Usage

`django-new` is designed to be used with `uv`, but can also be used with `pipx` or other package managers.

```

## Project vs app terminology

Django's use of "project" and "app" can sometimes cause confusion.

For a **classic** Django application, "project" refers to the entire deployable, e.g. it's the entire website, and "app" refers to smaller, contained namespaces of functionality. For example, a `wwww.my-cool-django-app.com` blog website might have a "project" named "my_cool_django_app", a "config" folder with settings, and two "apps": `blog` and `users`.

```text
.
└── my_cool_django_app
    ├── config
    │   ├── ...
    │   └── settings.py
    ├── blog
    │   ├── ...
    │   └── apps.py
    └── users
        ├── ...
        └── apps.py
```

For a **minimal** Django application, the "app" is in the same folder as the configuration.

```text
.
└── my_cool_django_app
    ├── ...
    ├── settings.py
    └── apps.py
```

```{note}
More details about the distinction between "project" and "app" are in the [Django documentation](https://docs.djangoproject.com/en/stable/ref/applications/).
```

## Inspiration ❤️

`django-new` was inspired by [DEP-15](https://github.com/django/deps/blob/main/accepted/0015-extended-startproject.rst), although it approaches the same solution from a different angle -- it calls the existing `startproject` and `startapp` commands and tweaks the output. Since this is an external tool, this prevents having to keep template files up to date when new Django versions are released. Another approach would be to use the `app_template` and `project_template` folders in [django/conf](https://github.com/django/django/tree/main/django/conf) module.

- https://github.com/django/deps/blob/main/accepted/0015-extended-startproject.rst
- https://github.com/knyghty/django-new
- https://forum.djangoproject.com/t/dep-15-improved-startproject-interface/43384
