# Emoji Dataset

> Emoji artwork for your terminal scripts, notifications, and other little tools. :rocket:

## About

Emoji Dataset collects emoji images by vendor, alongside a JSON index of Unicode
sequences, names, image paths, and data URLs.

The repository currently provides the dataset and a legacy Python generator.
A shortcode-based CLI is planned; it is not available yet.

## Installation

Clone the repository to use the checked-in images and JSON locally:

```sh
git clone https://github.com/AdrieanKhisbe/Emoji-Dataset.git
cd Emoji-Dataset
```

Reading the dataset requires no Python dependencies. You can read
`dataset/dataset.json` with your preferred JSON library.

## Usage

:construction: À être défini.

## Dataset maintenance

[`emoji_dataset.py`](emoji_dataset.py) is the legacy generator. It depends on
Python 3, `requests`, and `beautifulsoup4`, and writes directly to `dataset/`.
Its fixed vendor-column positions no longer match the Unicode chart. Running it
against the current chart can overwrite images with artwork from the wrong source.

The task `poetry run poe regenerate` invokes this generator. Preview the command
without running it with `poetry run poe --dry-run regenerate`.

The replacement workflow will keep Unicode as the index and retrieve vendor
artwork separately. See the [intended change](docs/intended-change.md) for the
planned CLI, installation, skin-tone options, and refresh behavior.

## Contributing

For Python development, use Python 3.11+ and [Poetry 2+](https://python-poetry.org/docs/#installation).
Install the locked dependencies from the repository root:

```sh
poetry install
poetry check --lock
```

Poetry manages dependencies only for now; the project is not yet an installable
CLI package. Commit `poetry.lock` when changing dependencies. The legacy generator
still needs the source update described above before it can safely refresh images.

Bug reports and suggestions belong in
[GitHub Issues](https://github.com/AdrieanKhisbe/Emoji-Dataset/issues).
For an image problem, include the emoji, vendor, and affected path.

The [glossary](CONTEXT.md) defines the project's vocabulary, and
[architecture decisions](docs/adr/) record design trade-offs.
