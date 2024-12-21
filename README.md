# md-ref-checker

A powerful tool for checking references in Markdown files, especially designed for Obsidian-style wiki links.

## Features

- Check markdown references:
  - Document references `[[filename]]` or `[[filename|display text]]`
  - Image references `![[image_filename]]`
  - Web image references `![alt text](https://image_url)`
  - Check unidirectional links: A references B, but B doesn't reference A
  - Generate reference statistics

- File organization checks:
  - Support for pinyin index + Chinese name in root directory
  - Direct Chinese names for subdirectories and files
  - Images stored in the `assets/` folder

- Image specification checks:
  - Detect unreferenced image files
  - Support common image formats: PNG, JPG, etc.
  - Check image reference integrity

## Installation

```bash
pip install md-ref-checker
```

## Usage

Basic usage:

```bash
md-ref-checker --dir /path/to/markdown/files
```

Options:

- `--dir`: Directory path to check (default: current directory)
- `-v, --verbosity`: Output verbosity (0-2)
  - 0: Show only invalid references and unused images
  - 1: Show invalid references, unused images, and unidirectional links
  - 2: Show all reference statistics
- `--no-color`: Disable colored output
- `--ignore`: Add file patterns to ignore (can be used multiple times)

Example:

```bash
md-ref-checker --dir ./docs -v 2 --ignore "*.tmp" --ignore "drafts/*"
```

## Features

- Support for relative and absolute paths
- Ignore references in code blocks
- Ignore references in inline code
- Correctly handle task lists and other Markdown syntax
- Support for `.gitignore` and custom ignore rules
- Detailed error location reporting (line number, column)

## Development

To set up the development environment:

```bash
git clone https://github.com/yourusername/md-ref-checker.git
cd md-ref-checker
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 