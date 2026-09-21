# Repo Doctor 🩺

A tiny, zero-dependency Python CLI that gives a quick health check for a code repository.

It checks common GitHub repository basics, counts source-code lines by language, finds `TODO` / `FIXME` markers, and warns about large files.

## Why?

Before publishing a project to GitHub, it is easy to forget small but important things such as a `LICENSE`, tests, CI, or a `.gitignore`. Repo Doctor gives you a 10-second sanity check.

## Features

- Repository health score
- Checks for README, LICENSE, `.gitignore`, tests, CI and package config
- Approximate lines of code by language
- Counts `TODO` and `FIXME` markers
- Detects files larger than 5 MB
- Zero runtime dependencies
- Works with Python 3.9+

## Installation

Clone and install locally:

```bash
git clone <your-repository-url>
cd repo-doctor
python -m pip install .
```

Or simply run the single file:

```bash
python repo_doctor.py /path/to/project
```

## Usage

```bash
repo-doctor .
```

Example output:

```text
Repo Doctor
===========
Path: /home/user/project
Health score: 83/100
Files scanned: 42

Repository essentials:
  [OK] README
  [OK] LICENSE
  [OK] .gitignore
  [OK] tests
  [OK] CI
  [!!] package config

Languages by lines:
  Python          628
  Shell            41

TODO/FIXME markers: 3
Large files: none >= 5 MB

Suggestions: add package config.
```

## Development

```bash
python -m pip install pytest .
pytest -q
```

## Project structure

```text
repo-doctor/
├── repo_doctor.py
├── tests/
│   └── test_repo_doctor.py
├── .github/
│   └── workflows/
│       └── test.yml
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## Ideas for future versions

- JSON output for CI pipelines
- Custom scoring rules
- Git commit statistics
- GitHub Actions recommendations
- Duplicate-file detection

## License

MIT
