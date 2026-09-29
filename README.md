# Emoji Dataset

> Emoji artwork for your terminal scripts, notifications, and other little tools. :rocket:

## About

Emoji Dataset collects emoji images by vendor, alongside a JSON index of Unicode
sequences, names, image paths, and data URLs.

The repository currently provides the dataset and a Python generator.
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

[`emoji_dataset.py`](emoji_dataset.py) reads Unicode's fully qualified emoji index
and downloads the latest released vendor artwork from Emojipedia. Each PNG is
validated before publication; its source, release, and checksum are recorded in
`dataset.json`. `unicode-source.json` records the Unicode index version and source.

```sh
poetry run poe regenerate
poetry run poe regenerate --vendor apple
# Small refresh in a separate directory:
poetry run poe regenerate --output /tmp/emoji-sample --vendor apple --emoji U+1F600
poetry run poe test
```

The local identifiers remain `apple`, `emojione` (JoyPixels), `facebook`,
`google` (classic Noto Color Emoji), `samsung`, `twitter` (Twitter/X), and
`windows` (Microsoft Windows 2D). Repeat `--vendor` or `--emoji` to select several;
`--emoji` limits artwork downloads while retaining the complete Unicode index.

A failed download leaves that vendor unchanged; other vendors can still update.
Artwork missing from a new release is retained with its earlier provenance.
Legacy images without verified origins are marked as such. Existing indexed
image paths remain stable except for legacy collisions: when two emojis share a
path, the second receives a Unicode suffix and a copy of the retained image.

Validated downloads are cached in `.cache/emoji-dataset/` for later retries.
Requests are spaced by `--request-delay` seconds (default: 0.25). HTTP 429 stops
requests to that host for the run and reports `Retry-After`; wait that long before
retrying. The public website endpoint currently requires no authentication.
It is not a stable public API; source-format changes cause the refresh to fail.

Publication uses a staged directory and rollback, with a lock against concurrent
generators. If interrupted during publication, a sibling `.dataset-previous`
recovery copy may remain (named after `--output`). Inspect and restore or move it
before retrying. Keep `--output` dedicated to the dataset and the cache outside it.

See the [intended change](docs/intended-change.md) for the planned CLI,
installation, and skin-tone options.

## Contributing

For Python development, use Python 3.11+ and [Poetry 2+](https://python-poetry.org/docs/#installation).
Install the locked dependencies from the repository root:

```sh
poetry install
poetry check --lock
```

Poetry manages dependencies only for now; the project is not yet an installable
CLI package. Commit `poetry.lock` when changing dependencies.

Bug reports and suggestions belong in
[GitHub Issues](https://github.com/AdrieanKhisbe/Emoji-Dataset/issues).
For an image problem, include the emoji, vendor, and affected path.

The [glossary](CONTEXT.md) defines the project's vocabulary, and
[architecture decisions](docs/adr/) record design trade-offs.
