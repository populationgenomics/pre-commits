# Pre-commits

This repository contains

## Usage

Add these into your `.pre-commit-config.yaml` file to use them!

### cpg-id-checker

Automatically checks for CPG IDs in your repository. You can extend this check by adding `--extra-pattern 'REGEX'` into the `args:`, see the example below:

```yaml
- repo: https://github.com/populationgenomics/pre-commits
rev: "v0.1.2"
hooks:
    - id: cpg-id-checker
    args: ["--extra-pattern", 'ABC\d+']
```

## How a hook is set up

Each pre-commit hook is:

- a file inside the `pre_commit_hooks` folder,
- then installed as an entrypoint in the `setup.py`, eg:

    ```python
    setup(
        # ...
        entry_points={
            "console_scripts": [
                "cpg-id-checker = pre_commit_hooks.cpg_id_checker:main"
            ],
        },
    )
    ```

- Added as an available option (based on the console-script name) in the `.pre-commit-hooks.yaml`.
