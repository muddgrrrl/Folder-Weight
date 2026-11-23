# Folder Weight

Find the biggest files or folder trees one level below a directory, with a terminal bar chart or JSON output.

```sh
python3 folder_weight.py ~/Downloads --top 12
python3 folder_weight.py . --json
```

Requires Python 3.8+. Totals use apparent file sizes, include hidden files, and count individual paths to hard-linked files. Nested symlinks are skipped. Unreadable paths produce partial results and an exit status of 1. The tool only reads filesystem metadata. [MIT](LICENSE)
