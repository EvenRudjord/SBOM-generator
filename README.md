# SBOM Generator - Python Command Line Tool

This is a simple **Software Bill Of Materials (SBOM)** generator written in Python 3.
It scans a directory of source code repositories and outputs a list of dependencies, including their names, versions, types (pip/npm), and paths. The SBOM is saved in both CSV and JSON formats.

---

## Features

* Recursively scans a directory for Python (`requirements.txt`) and JavaScript (`package.json` / `package-lock.json`) repositories.
* Supports indirect dependencies for JavaScript via `package-lock.json`.
* Outputs SBOM in:

  * `sbom.csv` (columns: `name`, `version`, `type`, `path`)
  * `sbom.json` (structured with the same information)
* Cleans version operators (`^`, `~`, `>=`, etc.) to show plain version numbers.
* Provides helpful error messages for missing or invalid directory paths.
* Works with multiple repositories and subdirectories.

---

## Requirements

* Python 3.x
* Only uses Python standard library modules: `os`, `sys`, `json`, `csv`.

---

## Usage

Run the script from the command line, providing the path to the directory containing repositories:

```bash
python3 sbom.py /path/to/code/repos/
```

Example output:

```
Found 10 repositories in '/path/to/code/repos/'
SBOM files saved as sbom.json and sbom.csv in /path/to/code/repos/
```

The generated files (`sbom.csv` and `sbom.json`) will contain all dependencies found in all repositories under the given path.

---

## Known Issues / Bugs

* Malformed or unusual dependency files may produce incorrect results:
  
  * `package.json` or `package-lock.json` missing `dependencies` or `devDependencies` may result in error.

---

## Ideas for Future Features

* Optional deduplication of dependencies across repositories.
* Handle malformed dependency files gracefully and report warnings.
* Include summary statistics: number of unique packages, most common versions, etc.

---
