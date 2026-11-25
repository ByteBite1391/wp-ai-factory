# WP AI Factory — Technical Documentation & User Guide

**Documentation version:** 1.0  
**Documentation basis:** Inspection of the supplied `wp-ai-factory.zip` source archive  
**Language:** English  
**Status:** Documents the code currently present. Planned features that are not implemented are explicitly identified.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Implemented Features](#2-implemented-features)
3. [Application Architecture](#3-application-architecture)
4. [Prerequisites and Installation](#4-prerequisites-and-installation)
5. [Running the Application](#5-running-the-application)
6. [User Guide](#6-user-guide)
7. [DeepSeek Workflow](#7-deepseek-workflow)
8. [JSON Import Contract](#8-json-import-contract)
9. [WordPress Project Workspace](#9-wordpress-project-workspace)
10. [File Management and Versions](#10-file-management-and-versions)
11. [Exporting Projects](#11-exporting-projects)
12. [Database Models](#12-database-models)
13. [Application Routes](#13-application-routes)
14. [Source Directory Structure](#14-source-directory-structure)
15. [Security and Limitations](#15-security-and-limitations)
16. [Troubleshooting](#16-troubleshooting)
17. [Tests](#17-tests)
18. [Future Development](#18-future-development)

---

## 1. Overview

WP AI Factory is a local web application for managing WordPress file-generation projects through a manual DeepSeek workflow. A user records a customer's website requirements, generates a prompt for a project stage, submits that prompt to DeepSeek, and imports the structured response. The application writes permitted files into the project's workspace and provides file management and ZIP export features.

### AI integration model

- The current application does not connect to the DeepSeek API.
- Users do not sign in to a DeepSeek account inside WP AI Factory.
- The user copies a generated prompt into DeepSeek.
- The user copies the JSON response back into the application's Import page.
- There is no automatic DeepSeek authentication, scraping, or response retrieval.

### Output goal

The primary output is a `wp-content` directory containing themes and plugins returned by DeepSeek. WordPress Core is not included.

---

## 2. Implemented Features

| Feature | Status in supplied source |
|---|---|
| Dashboard and project statistics | Implemented |
| Create, edit, delete, and duplicate projects | Implemented |
| Store requirements, pages, and design preferences | Implemented |
| Store and approve a project architecture | Implemented |
| Stage-based prompt generation | Implemented |
| Prompt history | Implemented |
| Import response and extract JSON | Implemented |
| Validate file paths | Implemented |
| Write files to a project workspace | Implemented |
| Browse, edit, and delete files | Implemented |
| Store previous file contents when overwriting | Implemented |
| Project-folder backup and restore | Implemented |
| ZIP export for wp-content, themes, and plugins | Implemented |
| HTML project file report | Implemented |
| Built-in help center with seeded articles | Implemented |
| Docker-based live WordPress preview | Not found in the supplied source |
| Direct DeepSeek/API integration | Intentionally absent |
| Automatic execution of imported PHP or other code | Not present |
| User authentication and multi-user support | Not found in the supplied source |
| Complete security audit of generated PHP | Not fully implemented |
| Dedicated UI for browsing/restoring every file version | Not found in the current UI |

---

## 3. Application Architecture

The application uses Flask and separates HTTP routes, services, database models, prompts, templates, and static assets.

### Layers

- **Routes:** Handle HTTP requests and render pages.
- **Services:** Implement project, prompt, parsing, file, backup, validation, and export logic.
- **Models:** SQLAlchemy models backed by SQLite.
- **Prompts:** Define the stages and instructions sent to DeepSeek.
- **Templates:** Jinja-based HTML pages.
- **Static:** CSS and JavaScript assets.
- **Core:** Shared helpers, path security, and initial help content.

### Data flow

```text
Browser
  |
  v
Flask Routes
  |
  +--> Project / Prompt / Import / File / Export Services
  |                      |
  |                      v
  |                 SQLAlchemy
  |                      |
  |                      v
  |                   SQLite
  |
  +--> Workspace Files
  |
  v
Jinja Templates + Static Assets
```

### Dependencies declared in requirements.txt

- Flask 3.0.3
- Flask-SQLAlchemy 3.1.1
- Werkzeug 3.0.3
- pytest 8.2.2

Python must be installed. The repository does not pin an exact Python version.

---

## 4. Prerequisites and Installation

### Prerequisites

- Windows 10/11 or another operating system with Python
- Python available through the `python` command
- Write permission in the application directory
- A modern browser
- Internet access is needed to use the DeepSeek website; the local application itself does not require internet access.

### Windows installation

1. Extract the project ZIP.
2. Open the project root directory—the directory containing `app.py` and `requirements.txt`.
3. Run `start.bat`.

The supplied `start.bat` creates a `venv` directory if missing, activates it, installs requirements, and runs `python app.py`.

### Manual installation

Run these commands in the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If PowerShell blocks script activation, use Command Prompt:

```bat
venv\Scripts\activate
```

### Data directories

At startup, the application creates these directories beside the source:

- `instance/` — SQLite database
- `workspace/` — generated WordPress project files
- `exports/` — downloadable exports
- `backups/` — project backups

The default database file is `instance/wpai.db`.

---

## 5. Running the Application

Running `app.py` starts Flask at:

```text
http://127.0.0.1:5000
```

The current source binds to `127.0.0.1`, port `5000`, with `debug=False`.

Press `Ctrl+C` in the terminal to stop the application.

**Important:** This configuration is intended for local use. Do not expose the application to the public internet without implementing and reviewing authentication, security controls, and production configuration.

---

## 6. User Guide

### 6.1 Dashboard

The `/` page displays project statistics, including total projects, active projects, completed projects, recent projects, and recent activity.

The dashboard counts `requirements`, `architecture`, and `generating` as active statuses. `completed` is the completed status.

### 6.2 Create a project

Open Projects and choose Create Project. The form accepts:

- Project name (required)
- Project type
- Customer requirements
- Website language
- Design preferences
- Target WordPress version
- Features
- Required pages

Predefined project types include e-commerce, company, personal, news, education, blog, services, portfolio, and custom.

The project service may add default features and pages when lists are empty. Review the form carefully to ensure the saved requirements match the customer's request.

### 6.3 Edit, duplicate, and delete

The project list supports searching by project name and filtering by status. Project routes also support editing, duplication, and deletion.

Deleting a project also deletes that project's workspace directory. Export or back up important files before deleting a project.

### 6.4 Website architecture

The architecture page lets the user submit page and feature lists. The submitted data is stored as JSON in SQLite, marked as approved, and changes the project status to `architecture`.

Example:

```json
{
  "website": ["Homepage", "About", "Contact"],
  "features": ["Blog", "Contact Form"]
}
```

Architecture approval is required before prompts for the code-generation stages can be generated.

### 6.5 Generate a prompt

Choose one of the available stages:

1. Requirements analysis (`requirements_analysis`)
2. Architecture design (`architecture_design`)
3. UI/UX design (`ui_ux_design`)
4. Theme generation (`theme_generation`)
5. Plugin generation (`plugin_generation`)
6. Feature implementation (`feature_implementation`)
7. Code review (`code_review`)
8. Final packaging (`final_packaging`)

The generated prompt includes project details, pages, features, design preferences, target WordPress version, and the stored architecture. Prompt history is saved in SQLite.

In the current implementation, `theme_generation`, `plugin_generation`, and `feature_implementation` require approved architecture.

### 6.6 Import a DeepSeek response

Open the project's Import page, paste the DeepSeek response, and submit it.

The parser attempts to extract JSON either directly or from a Markdown code block such as ` ```json `. If the JSON and file paths pass validation, the files are written to the project workspace.

An import can be successful, partial, or contain errors. Import history is stored in the database.

### 6.7 File manager

The Files page displays a directory tree for the project. Text files can be viewed, edited, and deleted.

When an existing file is saved, its previous content is stored in the file-version table. This per-file versioning is separate from a full project-folder backup.

### 6.8 Built-in help center

The `/help` section contains categories for Quick Start, DeepSeek, Project Management, WordPress, Troubleshooting, and FAQ. Initial articles are seeded on first database initialization.

The current help search filters article titles; it does not perform full-text search across article bodies.

---

## 7. DeepSeek Workflow

1. Create a project.
2. Enter customer requirements and requested pages.
3. Review and approve the architecture.
4. Select a stage on the Prompt page.
5. Copy the generated prompt.
6. Submit it in the DeepSeek chat website.
7. Ask DeepSeek to return the result using the exact JSON contract.
8. Copy the response.
9. Paste it into the project's Import page.
10. Review the import result.
11. If the response is partial, request the next batch and import it separately.
12. Review generated files in the File Manager.
13. Export the required package.

### Long responses

Prefer a unique `batch_id` for each response batch. Each batch should be a standalone valid JSON object containing only the files for that batch. Import each batch separately.

---

## 8. JSON Import Contract

The current prompt contract expects:

```json
{
  "project_id": "project-slug",
  "batch_id": "batch-001",
  "files": [
    {
      "path": "wp-content/themes/custom-theme/style.css",
      "content": "/* CSS content */"
    }
  ],
  "completed": false,
  "message": "More files will follow."
}
```

### Fields

| Field | Type | Description |
|---|---|---|
| `project_id` | string | Project slug; if supplied, it must match the current project |
| `batch_id` | string | Identifier for this response batch |
| `files` | array | List of generated files |
| `files[].path` | string | Relative file path |
| `files[].content` | string | Complete file content |
| `completed` | boolean | Indicates whether DeepSeek considers the generation complete |
| `message` | string | Optional note |

### Path rules

- Paths must be relative.
- Absolute paths are rejected.
- A `..` path segment is rejected.
- Only paths beginning with `wp-content/` or `docs/` are accepted.
- Duplicate paths in one response cause a validation error.
- File content is expected to be a string.

### Meaning of completed

The Import route updates project status based on the `completed` flag. This flag does not verify that every file required for a working website exists. Actual completion must be confirmed by reviewing and testing the generated WordPress project.

---

## 9. WordPress Project Workspace

Generated files are stored under:

```text
workspace/<project-slug>/
```

Example layout:

```text
workspace/
└── my-site/
    ├── wp-content/
    │   ├── themes/
    │   │   └── custom-theme/
    │   │       ├── style.css
    │   │       ├── functions.php
    │   │       ├── index.php
    │   │       └── ...
    │   └── plugins/
    │       └── custom-plugin/
    │           └── ...
    └── docs/
        └── ...
```

This is an example only. The actual structure depends on the files returned by DeepSeek.

**WP AI Factory does not download or install WordPress Core.** The current source also does not automatically install generated themes or plugins into a running WordPress site.

---

## 10. File Management and Versions

### File versioning

When an existing file is overwritten through Import or manual save, its previous content is stored in `project_versions`. Version numbers are incremented per file path.

### Full project backup

The Backup operation copies the project workspace to:

```text
backups/<project-slug>/<timestamp>/
```

Restore copies the backup files into the current workspace using `copytree(..., dirs_exist_ok=True)`. Existing files are overwritten, but files created after the backup are not necessarily deleted. Therefore, the current Restore operation is not an exact clean snapshot rollback.

---

## 11. Exporting Projects

The project export page provides four export types:

| Type | Output | Contents |
|---|---|---|
| `wp-content` | `<slug>-wp-content.zip` | wp-content folder, stored under a `wp-content` root inside the ZIP |
| `theme` | `<slug>-theme.zip` | Contents of the themes directory |
| `plugins` | `<slug>-plugins.zip` | Contents of the plugins directory |
| `report` | `<slug>-report.html` | HTML report listing project files and their sizes |

Generated exports are stored in `exports/`.

### Installing a wp-content export

1. Back up the destination WordPress site first.
2. Extract the ZIP.
3. Locate the `wp-content` directory in the export.
4. Transfer its contents to the destination WordPress `wp-content` directory using a safe deployment process, preferably in staging first.
5. Install and activate required third-party dependencies separately.
6. Activate the theme from the WordPress dashboard.
7. Review pages, menus, permalinks, and plugin settings.

The ZIP is not a complete WordPress installation. It does not automatically create database settings, real site content, media assets, or customer secrets.

---

## 12. Database Models

SQLite is managed through Flask-SQLAlchemy. Main models:

| Model | Purpose |
|---|---|
| `Project` | Project details and status |
| `ProjectRequirement` | Requested features and pages |
| `ProjectArchitecture` | JSON architecture and approval state |
| `ProjectFile` | File metadata, size, and checksum |
| `ProjectVersion` | Previous file contents |
| `PromptHistory` | Generated prompts |
| `ImportHistory` | Imported responses and results |
| `ProjectActivity` | Project activity events |
| `HelpCategory` | Help categories |
| `HelpArticle` | Help articles |

### Relationships

- A project has many requirements.
- A project has at most one architecture record.
- A project can have many files, versions, prompts, imports, and activities.
- A help category has many articles.

The application calls `db.create_all()` during startup. This creates missing tables but is not a replacement for a database migration system when schema changes become more complex.

---

## 13. Application Routes

The following routes are derived from the Blueprints registered in `app.py` and the route definitions in the source.

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Dashboard |
| GET | `/projects/` | Project list |
| GET, POST | `/projects/create` | Create project |
| GET | `/projects/<id>` | Project details |
| GET, POST | `/projects/<id>/edit` | Edit project |
| POST | `/projects/<id>/delete` | Delete project |
| POST | `/projects/<id>/duplicate` | Duplicate project |
| GET, POST | `/projects/<id>/architecture` | View and approve architecture |
| GET, POST | `/projects/<id>/prompts/` | Generate prompts |
| GET, POST | `/projects/<id>/imports/` | Import a response |
| GET | `/projects/<id>/files/` | Browse project files |
| POST | `/projects/<id>/files/save` | Save a file |
| POST | `/projects/<id>/files/delete` | Delete a file |
| POST | `/projects/<id>/files/backup` | Create a backup |
| POST | `/projects/<id>/files/restore` | Restore a backup |
| GET | `/projects/<id>/exports/` | Export page |
| GET | `/projects/<id>/exports/<kind>` | Download an export |
| GET | `/help/` | Help index |
| GET | `/help/<slug>` | Help article |

---

## 14. Source Directory Structure

```text
wp-ai-factory/
├── app.py
├── config.py
├── database.py
├── requirements.txt
├── start.bat
├── run_tests.bat
├── conftest.py
├── pytest.ini
├── core/
│   ├── helpers.py
│   ├── security.py
│   └── seed.py
├── models/
│   └── models.py
├── prompts/
│   └── stages.py
├── routes/
│   ├── dashboard.py
│   ├── projects.py
│   ├── prompts.py
│   ├── imports.py
│   ├── files.py
│   ├── exports.py
│   └── help.py
├── services/
│   ├── project_service.py
│   ├── prompt_service.py
│   ├── parser_service.py
│   ├── file_service.py
│   ├── validation_service.py
│   ├── backup_service.py
│   └── export_service.py
├── templates/
├── static/
├── tests/
├── workspace/
├── exports/
├── backups/
└── instance/
```

### Key files

- `app.py`: Creates the Flask app, registers Blueprints, creates tables, and seeds help content.
- `config.py`: Configures paths, database, session secret, and request-size limit.
- `database.py`: SQLAlchemy instance.
- `prompts/stages.py`: Prompt stages and base instructions.
- `services/parser_service.py`: JSON extraction and validation.
- `services/file_service.py`: File read/write operations.
- `core/security.py`: File path validation.
- `services/export_service.py`: ZIP and HTML report generation.

---

## 15. Security and Limitations

### Path validation

`safe_join` rejects absolute paths and `..` segments and ensures the resolved path remains inside the workspace. The parser additionally accepts only paths beginning with `wp-content/` or `docs/`.

### Current security limitations

- The supplied source does not implement user accounts or authentication.
- `config.py` contains a fixed default Flask secret. Set a strong, private `SECRET_KEY` for each environment.
- CSRF protection was not found in the reviewed source.
- PHP/JS content is not safe merely because it is inside valid JSON.
- PHP syntax checking exists in `validation_service.py`, but the Import route does not automatically invoke it.
- If PHP CLI is unavailable, the fallback only checks basic brace balance; it does not prove PHP validity.
- A complete security audit, sandboxed execution, malware scanning, and WordPress runtime testing are not confirmed in this version.
- The HTML report inserts the project name and paths into HTML; untrusted values should be escaped appropriately.

### Operational recommendation

Review generated code and test the project in a separate staging WordPress installation before deploying it to a customer's website. Do not trust AI-generated code without review. Back up both files and the database before production deployment.

---

## 16. Troubleshooting

### The application does not start

- Confirm Python is installed.
- Run `start.bat` from the project root.
- Review dependency installation errors.
- If necessary, follow the manual installation commands in Section 4.

### The browser cannot open the application

- Confirm the terminal process is still running.
- Open `http://127.0.0.1:5000`.
- Check whether another process is using port 5000.

### Invalid JSON

- Ask DeepSeek to return the response inside a ` ```json ` code block.
- Make sure the JSON is complete and does not contain malformed extra text.
- Check quotes and commas.
- If the response is split into batches, each batch must be a standalone valid JSON object.

### A file path is rejected

- The path must begin with `wp-content/` or `docs/`.
- Absolute paths and `..` are not allowed.
- Use allowed ASCII letters, digits, hyphens, underscores, periods, and slashes.

### A file is missing from the ZIP

- Confirm the file exists in File Manager.
- The wp-content export requires `workspace/<slug>/wp-content`.
- Theme and plugin exports require their corresponding directories.

### Restore does not exactly return to the previous project state

The current Restore implementation copies snapshot files over the current workspace and does not necessarily remove files that were added later. Back up the current workspace before restoring and manually clean the directory if an exact rollback is required.

---

## 17. Tests

The `tests/` directory contains tests for:

- Backup Service
- Export Service
- File Service
- Helpers
- Models
- Parser
- Project Service
- Prompt Service
- Routes
- Security
- Validation Service

Run tests with:

```powershell
pip install -r requirements.txt
python -m pytest -q
```

The supplied `run_tests.bat` references `requirements-dev.txt`, but that file was not present in the archive listing. Running the batch file as-is may therefore fail. The command above is the recommended alternative using the supplied `requirements.txt`.

**Archive inspection test result:** Test collection in the inspection environment stopped because `Flask-SQLAlchemy` was not installed. Therefore, this inspection cannot claim that the test suite passes or fails. Install dependencies and run the tests to obtain a valid result.

---

## 18. Future Development

The following items were discussed as goals, but cannot be confirmed as complete features in the supplied source:

1. Live WordPress preview and Docker orchestration.
2. Automated PHP and WordPress tests inside a sandbox.
3. Graphical file-version comparison and full version rollback UI.
4. User authentication and multi-user support.
5. Database migrations using Alembic/Flask-Migrate.
6. Full-text search across help articles.
7. Comprehensive security and quality analysis of generated code.
8. Automatic WordPress and dependency plugin installation.
9. Browser-based theme compatibility and performance reports.

This section separates the actual current implementation from the future roadmap.
