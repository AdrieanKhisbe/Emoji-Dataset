# Intended change

Status: design ready for final confirmation. Literal-emoji fallback remains tentative. Implementation has not started.

## Settled intent

- Provide an easily installed CLI for terminal power users, including notification-tool integrations.
- Support macOS and Linux, with installation through Python tooling such as uv or pipx.
- Select emojis by GitHub-compatible shortcode, accepting aliases with or without surrounding colons.
- Return a PNG filepath or data URL content.
- Version the images in this repository and include all seven vendors in the initial installation for offline use.
- Refresh existing artwork using the replacement vendor-image acquisition method. This supersedes the initial preservation requirement.
- Keep Unicode as the emoji index. Emojipedia is the preferred replacement image source; alternatives remain open.
- Retain the vendor identifiers apple, emojione, facebook, google, samsung, twitter, and windows.
- Default to Apple, allow configuration of the default vendor, and report missing artwork as an error without automatic vendor substitution.
- Defer fzf selection and image previews.
- Keep existing image paths stable. Simplify JSON and generate data URLs from PNGs on demand if no existing consumer depends on the JSON structure.
- Select the latest available artwork for each vendor at refresh time and record the source and release used. CLI lookups use the packaged images.
- Cover all fully qualified Unicode emoji sequences, including skin tones, gender variants, flags, and joined sequences, even where vendor artwork is unavailable.
- Refresh each vendor atomically: validate downloads before replacing its artwork; retain its previous images if the refresh fails. Successful vendors can update independently.
- Provide `emoji get SHORTCODE`, `--vendor VENDOR`, `--format data-url`, and the shortcut `--data-url`, plus `emoji list`.
- Print an absolute PNG path by default. Keep stdout for requested output, report errors on stderr, and exit nonzero on failure.
- Allow `EMOJI_VENDOR` to override the default vendor.
- Distribute through Git installation with uv/pipx first; use Poetry for contributor dependency management.
- Preserve downloaded PNG dimensions and transparency.
- Select skin tone with an optional per-command flag; persistent skin-tone configuration is deferred.
- Accept `--skin-tone light|medium-light|medium|medium-dark|dark`. Omission selects the unmodified emoji; unsupported combinations return an error. Apply the same tone to everyone in supported multi-person combinations; mixed-tone selection is deferred.
- Preserve an emoji's previous vendor artwork when the newly selected release genuinely lacks it. Per-image provenance must distinguish retained artwork from refreshed artwork.
- Map `emojione` to JoyPixels, `google` to classic flat Noto Color Emoji, `twitter` to Twitter/X artwork, and `windows` to Windows 2D artwork. Select the latest release within each design family; use the latest Apple, Facebook, and Samsung releases for the other identifiers.

## Final confirmation

- Literal-emoji input is tentatively included as an optional fallback for emojis without GitHub aliases. The user expressed reservations; it is not a requirement for ordinary shortcode lookup.
- Confirm the consolidated design before implementation.

## Implementation checks

- Check existing JSON consumers before simplifying its structure; preserve compatibility where needed.
- Validate actual PNG contents before accepting vendor downloads; a filename extension alone is insufficient.
- Retained legacy images with unverified origins must not be attributed to a newly downloaded vendor release.

## Findings relevant to preservation

The current generator assigns vendors by table-column position. Unicode's current chart has Sample and legacy vendor columns in those positions. The working-tree Apple butterfly and cucumber images match the Sample-column images byte for byte, so their directory names do not establish Apple provenance. The existing user changes have been left intact during the interview; refreshing existing artwork is now explicitly in scope for implementation.

GitHub's [gemoji metadata](https://github.com/github/gemoji/blob/master/db/emoji.json) supplies Unicode-to-shortcode aliases, but does not enumerate skin-tone sequences. Complete Unicode coverage therefore requires a lookup policy for sequences without those aliases.

Vendor names alone do not fully select artwork: EmojiOne is now JoyPixels, Google offers classic and 3D designs, Microsoft offers distinct styles, and Twitter/X artwork is distinct from independently maintained Twemoji. The selected mappings are recorded above.
