# Pre-commits

This repository contains a set of custom pre-commit hooks for the Centre for Population Genomics.

## Usage

Add these into your `.pre-commit-config.yaml` file to use them!

### cpg-id-checker

Automatically checks for CPG IDs in your repository. You can extend this check by adding `--extra-pattern 'REGEX'` into the `args:`, see the example below:

```yaml
- repo: https://github.com/populationgenomics/pre-commits
rev: "v0.1.3"
hooks:
    - id: cpg-id-checker
    args: ["--extra-pattern", 'ABC\d+']
```

Note that this will only check some string based files, and will skip a file if it's detected to be a binary file.

Arguments:

- `--extra-pattern <value>`: A python flavoured regex to match lines for, any matches will cause the pre-commit to return exitcode = 1.
- `--ignore-filename-format <value>`: A python flavoured regex to ignore filenames that match this format. Consider using the pre-commit `exclude`.

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
