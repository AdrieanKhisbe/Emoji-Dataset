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

Reading the dataset requires no Python dependencies. The JSON examples below use
`jq`; you can also read `dataset/dataset.json` with your preferred JSON library.

## Usage

Run these examples from the repository root.

### Get an image path

For example, use the Apple rocket image in a tool that accepts a local image:

```sh
printf '%s\n' "$PWD/dataset/images/apple/rocket.png"
```

To look up a repository-relative path by its dataset name:

```sh
jq -er --arg name 'rocket' \
  '.[] | select(.name == $name) | .apple_emoji.image_path // empty' \
  dataset/dataset.json
```

Names such as `rocket` and `grinning face` are dataset names, not shortcodes.
Quote paths when passing them to another command: many filenames contain spaces.

### Get a data URL

```sh
jq -er --arg name 'rocket' \
  '.[] | select(.name == $name) | .apple_emoji.data_uri // empty' \
  dataset/dataset.json
```

This prints the stored data URL, suitable for consumers that accept inline images.

### Choose a vendor

The image directories use these identifiers:

`apple`, `emojione`, `facebook`, `google`, `samsung`, `twitter`, `windows`.

In the JSON, vendor records are named `<vendor>_emoji`, such as `apple_emoji`.
Each contains `image_path` and `data_uri`. An emoji record also has a `name`, a
`unicode` array of code points, and an `index` from the source chart. The chart
index is not a stable emoji identifier; use the Unicode sequence for identity.

Coverage varies by vendor, and a file on disk may have no corresponding vendor
record in the JSON. The existing collection also contains incorrectly labelled
vendor images and non-PNG data stored with `.png` filenames. Check the actual
image format and artwork before relying on a particular asset.

## Dataset maintenance

[`emoji_dataset.py`](emoji_dataset.py) is the legacy generator. It depends on
Python 3, `requests`, and `beautifulsoup4`, and writes directly to `dataset/`.
Its fixed vendor-column positions no longer match the Unicode chart. Running it
against the current chart can overwrite images with artwork from the wrong source.

The replacement workflow will keep Unicode as the index and retrieve vendor
artwork separately. See the [intended change](docs/intended-change.md) for the
planned CLI, installation, skin-tone options, and refresh behavior.

## Contributing

Bug reports and suggestions belong in
[GitHub Issues](https://github.com/AdrieanKhisbe/Emoji-Dataset/issues).
For an image problem, include the emoji, vendor, and affected path.

The [glossary](CONTEXT.md) defines the project's vocabulary, and
[architecture decisions](docs/adr/) record design trade-offs.
