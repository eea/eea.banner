"""Release notes produced by the release-notes agent.

The agent commits MANIFEST.json and RELEASE_NOTES.md into the helm chart; the
chart mounts them (read-only ConfigMap) into the Plone container and points
RELEASE_NOTES_DIR at that folder. This module reads them for the release
banner. It has no Plone dependencies so it can be unit tested on its own.

Only the release version and a short plain-text summary leave this module:
the rest of the manifest (commits, authors, changed files) and the technical
section of the notes are never exposed.
"""

import json
import os
import re

RELEASE_NOTES_DIR_ENV = "RELEASE_NOTES_DIR"
MANIFEST_FILE = "MANIFEST.json"
NOTES_FILE = "RELEASE_NOTES.md"
MANIFEST_SCHEMA_PREFIX = "release-notes-agent/manifest/"

MAX_FILE_BYTES = 512 * 1024
MAX_RELEASE_LENGTH = 64
MAX_SUMMARY_LENGTH = 500

_cache = {"key": None, "value": None}

_HTML_TAG = re.compile(r"<[^>]*>")
_MD_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_MD_CODE = re.compile(r"`([^`]*)`")
_MD_EMPHASIS = re.compile(r"(\*\*|__|\*|_|~~)(.+?)\1")
_WHITESPACE = re.compile(r"\s+")
_SPACE_BEFORE_PUNCTUATION = re.compile(r"\s+([.,;:!?])")


def to_plain_text(markdown):
    """Strip HTML tags and inline markdown, collapse whitespace"""
    text = _HTML_TAG.sub("", markdown or "")
    text = _MD_IMAGE.sub(r"\1", text)
    text = _MD_LINK.sub(r"\1", text)
    text = _MD_CODE.sub(r"\1", text)
    text = _MD_EMPHASIS.sub(r"\2", text)
    text = _WHITESPACE.sub(" ", text).strip()
    return _SPACE_BEFORE_PUNCTUATION.sub(r"\1", text)


def truncate(text, limit=MAX_SUMMARY_LENGTH):
    """Cut text to `limit` characters on a word boundary"""
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return cut + "…"


def extract_summary(notes_md):
    """The plain-language summary right after the title of RELEASE_NOTES.md

    The agent writes "# Release notes - <release>", then a 1-3 sentence
    summary, then "## What's new". Everything after the first heading that
    follows the summary (including "## Technical detail") is ignored.
    """
    lines = []
    for line in (notes_md or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("##"):
            # "## What's new" / "## Technical detail": the summary is over,
            # and nothing below it may leak into the banner.
            break
        if stripped.startswith("#"):
            if lines:
                break
            continue
        if not stripped or stripped.startswith(("-", "*", ">", "|", "```")):
            # Only the prose paragraph is the summary, not lists or code.
            continue
        lines.append(stripped)
    return truncate(to_plain_text(" ".join(lines)))


def _read_small(path):
    """Read a UTF-8 text file, refusing anything over MAX_FILE_BYTES"""
    if os.path.getsize(path) > MAX_FILE_BYTES:
        raise ValueError("%s is larger than %d bytes" % (path, MAX_FILE_BYTES))
    with open(path, encoding="utf-8") as stream:
        return stream.read(MAX_FILE_BYTES + 1)


def _stat_key(folder):
    """Cache key: changes whenever either file is replaced or edited"""
    key = [folder]
    for name in (MANIFEST_FILE, NOTES_FILE):
        try:
            st = os.stat(os.path.join(folder, name))
        except OSError:
            key.append(None)
        else:
            key.append((st.st_mtime_ns, st.st_size, st.st_ino))
    return tuple(key)


def parse_release_notes(folder):
    """Return {"release": ..., "summary": ...} or None when unusable"""
    try:
        manifest = json.loads(_read_small(os.path.join(folder, MANIFEST_FILE)))
    except (OSError, ValueError):
        return None
    if not isinstance(manifest, dict):
        return None
    schema = manifest.get("schema")
    if not isinstance(schema, str) or not schema.startswith(MANIFEST_SCHEMA_PREFIX):
        return None
    release = manifest.get("release")
    if not isinstance(release, str):
        return None
    release = to_plain_text(release)
    if not release or len(release) > MAX_RELEASE_LENGTH:
        return None

    try:
        summary = extract_summary(_read_small(os.path.join(folder, NOTES_FILE)))
    except (OSError, ValueError):
        summary = ""
    return {"release": release, "summary": summary}


def load_release_notes(folder=None):
    """Release notes from RELEASE_NOTES_DIR (or `folder`), cached per file
    version. Returns None when the folder is not configured or the files are
    missing or invalid, so callers can simply hide the banner.
    """
    folder = folder if folder is not None else os.environ.get(RELEASE_NOTES_DIR_ENV)
    if not folder or not os.path.isdir(folder):
        return None
    key = _stat_key(folder)
    if key[1] is None:
        return None
    if _cache["key"] != key:
        _cache["value"] = parse_release_notes(folder)
        _cache["key"] = key
    return _cache["value"]
