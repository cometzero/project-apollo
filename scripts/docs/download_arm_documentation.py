#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "beautifulsoup4>=4.12",
#     "httpx2[http2,brotli,zstd]>=2.5.0",
#     "markdownify>=0.13",
#     "rich>=13.0",
# ]
# ///
#
# How to run:
#   uv run scripts/docs/download_arm_documentation.py \
#     https://developer.arm.com/documentation/107612/0001 \
#     --output-dir doc/mhu-320ae \
#     --title "MHU-320AE Markdown Pages" \
#     --accept-arm-terms
#
# The --accept-arm-terms flag records that you reviewed and accepted the Arm
# terms referenced by the source document before saving a local copy.

from __future__ import annotations

import argparse
import base64
import binascii
from dataclasses import dataclass
import html
import io
import re
import shutil
import socket
import sys
from pathlib import Path
from typing import Final
from urllib.parse import parse_qs, quote, urlencode, urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup, NavigableString, Tag
import httpx2
from markdownify import markdownify as html_to_markdown
from rich.console import Console
from rich.markdown import Markdown


DOC_URL_RE: Final = re.compile(r"^/documentation/(?P<docid>[^/]+)/(?P<version>[^/?#]+)(?P<slug>/[^?#]*)?")
WHITESPACE_RE: Final = re.compile(r"[ \t]+$")
BLANK_LINES_RE: Final = re.compile(r"\n{3,}")
SLUG_RE: Final = re.compile(r"[^A-Za-z0-9._'-]+")
TABLE_MARKER: Final = "ARMDOCXTABLE"


@dataclass(frozen=True, slots=True)
class CliArgs:
    source_url: str
    output_dir: Path
    title: str
    accept_arm_terms: bool
    language: str
    clean: bool
    render_smoke: bool


@dataclass(frozen=True, slots=True)
class DocumentId:
    docid: str
    version: str


@dataclass(frozen=True, slots=True)
class Page:
    index: int
    label: str
    slug: str
    api_url: str
    public_url: str
    filename: str


@dataclass(frozen=True, slots=True)
class Resource:
    href: str
    name: str
    extension: str


@dataclass(frozen=True, slots=True)
class GeneratedPage:
    page: Page
    image_count: int
    table_count: int


def parse_args(argv: list[str]) -> CliArgs:
    parser = argparse.ArgumentParser(
        description="Download an Arm Developer documentation tree as flat Markdown files.",
    )
    parser.add_argument("source_url", help="Arm Developer documentation URL")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write Markdown files")
    parser.add_argument("--title", required=True, help="Title for the generated index.md")
    parser.add_argument(
        "--accept-arm-terms",
        action="store_true",
        help="Confirm that Arm's terms for the source document have been reviewed and accepted.",
    )
    parser.add_argument("--language", default="en", help="Document language code")
    parser.add_argument("--no-clean", dest="clean", action="store_false", help="Do not clean output-dir first")
    parser.add_argument(
        "--no-render-smoke",
        dest="render_smoke",
        action="store_false",
        help="Skip Rich Markdown render smoke validation.",
    )
    parser.set_defaults(clean=True, render_smoke=True)
    ns = parser.parse_args(argv)
    return CliArgs(
        source_url=ns.source_url,
        output_dir=ns.output_dir,
        title=ns.title,
        accept_arm_terms=ns.accept_arm_terms,
        language=ns.language,
        clean=ns.clean,
        render_smoke=ns.render_smoke,
    )


def create_client() -> httpx2.Client:
    limits = httpx2.Limits(max_connections=40, max_keepalive_connections=20, keepalive_expiry=30.0)
    timeout = httpx2.Timeout(connect=5.0, read=30.0, write=10.0, pool=10.0)
    transport = httpx2.HTTPTransport(
        http2=True,
        retries=3,
        limits=limits,
        socket_options=[(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)],
    )
    return httpx2.Client(transport=transport, timeout=timeout, follow_redirects=True)


def parse_document_url(source_url: str) -> DocumentId:
    parts = urlsplit(source_url)
    match = DOC_URL_RE.match(parts.path)
    if match is None:
        raise SystemExit(f"Unsupported Arm documentation URL: {source_url}")
    return DocumentId(docid=match.group("docid"), version=match.group("version"))


def documentation_api_url(doc: DocumentId, language: str) -> str:
    query = urlencode({"lang": language, "baseUrl": "/documentation"})
    return f"https://documentation-service.arm.com/documentation/{doc.docid}/{doc.version}?{query}"


def fetch_json(client: httpx2.Client, url: str) -> dict[str, object]:
    response = client.get(url)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise SystemExit(f"Expected JSON object from {url}")
    return data


def fetch_bytes(client: httpx2.Client, url: str) -> tuple[bytes, str]:
    response = client.get(url)
    response.raise_for_status()
    return response.content, response.headers.get("content-type", "")


def strip_trailing_svg_whitespace(content: bytes) -> bytes:
    text = content.decode("utf-8")
    stripped = "\n".join(line.rstrip(" \t") for line in text.splitlines())
    return f"{stripped}\n".encode("utf-8")


def extract_topic(data: dict[str, object]) -> dict[str, object]:
    topic = data.get("topic", data)
    if not isinstance(topic, dict):
        raise SystemExit("Document topic is missing or malformed")
    return topic


def topic_children(topic: dict[str, object]) -> list[dict[str, object]]:
    children = topic.get("topics", [])
    if not isinstance(children, list):
        return []
    return [child for child in children if isinstance(child, dict)]


def topic_self_url(topic: dict[str, object]) -> str:
    links = topic.get("_links")
    if not isinstance(links, dict):
        raise SystemExit(f"Topic has no links: {topic.get('label')}")
    self_links = links.get("self")
    if not isinstance(self_links, list) or not self_links:
        raise SystemExit(f"Topic has no self link: {topic.get('label')}")
    first = self_links[0]
    if not isinstance(first, dict) or not isinstance(first.get("href"), str):
        raise SystemExit(f"Topic self link is malformed: {topic.get('label')}")
    return first["href"]


def clean_label(raw: str) -> str:
    return " ".join(html.unescape(raw).split())


def slugify_label(label: str) -> str:
    text = clean_label(label).replace("&", "and")
    text = text.replace("<", " ").replace(">", " ")
    slug = SLUG_RE.sub("-", text).strip("-")
    return re.sub(r"-{2,}", "-", slug)[:150].strip("-") or "page"


def public_url_for(doc: DocumentId, slug: str) -> str:
    suffix = f"/{quote(slug, safe='/')}" if slug else ""
    return f"https://developer.arm.com/documentation/{doc.docid}/{doc.version}{suffix}"


def flatten_pages(root: dict[str, object], doc: DocumentId) -> list[Page]:
    pages: list[Page] = []

    def walk(topic: dict[str, object]) -> None:
        label = clean_label(str(topic.get("label", "Untitled")))
        slug = str(topic.get("slug", ""))
        index = len(pages) + 1
        stem = f"{index:04d}-{slugify_label(label)}"
        pages.append(
            Page(
                index=index,
                label=label,
                slug=slug,
                api_url=topic_self_url(topic),
                public_url=public_url_for(doc, slug),
                filename=f"{stem}.md",
            ),
        )
        for child in topic_children(topic):
            walk(child)

    walk(root)
    return pages


def resource_key(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def collect_resources(data: dict[str, object]) -> dict[str, Resource]:
    links = data.get("_links")
    if not isinstance(links, dict):
        return {}
    raw_resources = links.get("resources", [])
    if not isinstance(raw_resources, list):
        return {}
    resources: dict[str, Resource] = {}
    for item in raw_resources:
        if not isinstance(item, dict):
            continue
        href = item.get("href")
        name = item.get("name")
        extension = item.get("extension")
        if isinstance(href, str) and isinstance(name, str) and isinstance(extension, str):
            resources[resource_key(href)] = Resource(href=href, name=name, extension=extension)
    return resources


def decode_content(raw: object) -> str:
    if not isinstance(raw, str) or not raw:
        return ""
    try:
        return base64.b64decode(raw, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return raw


def image_extension(src: str, resource: Resource | None, content_type: str) -> str:
    if resource is not None and resource.extension:
        return resource.extension.lstrip(".")
    suffix = Path(urlsplit(src).path).suffix.lstrip(".")
    if suffix:
        return suffix
    if "svg" in content_type:
        return "svg"
    if "png" in content_type:
        return "png"
    if "jpeg" in content_type or "jpg" in content_type:
        return "jpg"
    return "bin"


def prepare_output(output_dir: Path, clean: bool) -> Path:
    if clean and output_dir.exists():
        for child in output_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)
    return images_dir


def body_soup(decoded_html: str) -> BeautifulSoup:
    soup = BeautifulSoup(decoded_html, "html.parser")
    for tag in soup.find_all(["script", "style", "head"]):
        tag.decompose()
    body = soup.body
    if body is None:
        return soup
    return BeautifulSoup("".join(str(child) for child in body.children), "html.parser")


def localize_images(
    client: httpx2.Client,
    soup: BeautifulSoup,
    page: Page,
    images_dir: Path,
    resources: dict[str, Resource],
) -> int:
    count = 0
    stem = Path(page.filename).stem
    for img in soup.find_all("img"):
        if not isinstance(img, Tag):
            continue
        src_value = img.get("src")
        if not isinstance(src_value, str) or not src_value:
            continue
        count += 1
        absolute_src = urljoin(page.public_url, src_value)
        resource = resources.get(resource_key(absolute_src))
        content, content_type = fetch_bytes(client, absolute_src)
        extension = image_extension(absolute_src, resource, content_type)
        if extension == "svg":
            content = strip_trailing_svg_whitespace(content)
        image_name = f"{stem}-img{count:02d}.{extension}"
        image_path = images_dir / image_name
        image_path.write_bytes(content)
        img["src"] = f"images/{image_name}"
        img.attrs.pop("document-resource-id", None)
    return count


def protect_tables(soup: BeautifulSoup) -> tuple[str, int]:
    tables: list[str] = []
    for table in soup.find_all("table"):
        if not isinstance(table, Tag):
            continue
        marker = f"{TABLE_MARKER}{len(tables):04d}"
        tables.append(table.prettify(formatter="html"))
        table.replace_with(NavigableString(marker))
    converted = html_to_markdown(str(soup), heading_style="ATX", bullets="-")
    for index, table_html in enumerate(tables):
        converted = converted.replace(f"{TABLE_MARKER}{index:04d}", f"\n\n{table_html}\n\n")
    return converted, len(tables)


def normalize_markdown(text: str) -> str:
    lines = [WHITESPACE_RE.sub("", line) for line in text.splitlines()]
    normalized = "\n".join(lines).strip()
    normalized = BLANK_LINES_RE.sub("\n\n", normalized)
    return f"{normalized}\n"


def write_page_markdown(
    client: httpx2.Client,
    page: Page,
    output_dir: Path,
    images_dir: Path,
    resources: dict[str, Resource],
) -> GeneratedPage:
    data = fetch_json(client, page.api_url)
    topic = extract_topic(data)
    decoded = decode_content(topic.get("content", ""))
    soup = body_soup(decoded)
    image_count = localize_images(client, soup, page, images_dir, resources)
    body_markdown, table_count = protect_tables(soup)
    markdown = normalize_markdown(f"# {page.label}\n\nSource: <{page.public_url}>\n\n{body_markdown}")
    (output_dir / page.filename).write_text(markdown, encoding="utf-8")
    return GeneratedPage(page=page, image_count=image_count, table_count=table_count)


def write_index(output_dir: Path, title: str, generated: list[GeneratedPage]) -> None:
    lines = [f"# {title}", ""]
    for item in generated:
        page = item.page
        lines.append(f"- [{page.index:04d} {page.label}]({page.filename})")
    output_dir.joinpath("index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_output(output_dir: Path, render_smoke: bool) -> dict[str, int]:
    markdown_files = sorted(output_dir.glob("*.md"))
    image_files = sorted(output_dir.joinpath("images").glob("*"))
    missing_images: list[str] = []
    table_starts = 0
    table_ends = 0
    image_refs = 0
    console = Console(file=io.StringIO(), width=120, force_terminal=False, color_system=None)

    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        table_starts += text.count("<table")
        table_ends += text.count("</table>")
        refs = re.findall(r"!\[[^\]]*]\((images/[^)]+)\)", text)
        refs.extend(re.findall(r'<img[^>]+src="(images/[^"]+)"', text))
        image_refs += len(refs)
        for ref in refs:
            if not output_dir.joinpath(ref).exists():
                missing_images.append(f"{path.name}: {ref}")
        if render_smoke:
            console.print(Markdown(text[:200_000]))

    invalid_children = [
        child.name
        for child in output_dir.iterdir()
        if child.name != "images" and not (child.is_file() and child.suffix == ".md")
    ]
    if invalid_children:
        raise SystemExit(f"Unexpected files in {output_dir}: {', '.join(sorted(invalid_children))}")
    if missing_images:
        raise SystemExit("Missing local image references:\n" + "\n".join(missing_images[:20]))
    if table_starts != table_ends:
        raise SystemExit(f"Unbalanced table tags: <table={table_starts}, </table={table_ends}")

    return {
        "markdown_files": len(markdown_files),
        "image_files": len(image_files),
        "image_refs": image_refs,
        "tables": table_starts,
    }


def run(args: CliArgs) -> int:
    if not args.accept_arm_terms:
        raise SystemExit("--accept-arm-terms is required for local Arm documentation export")

    doc = parse_document_url(args.source_url)
    images_dir = prepare_output(args.output_dir, args.clean)
    with create_client() as client:
        root_data = fetch_json(client, documentation_api_url(doc, args.language))
        root_topic = extract_topic(root_data)
        resources = collect_resources(root_data)
        pages = flatten_pages(root_topic, doc)
        generated: list[GeneratedPage] = []
        for page in pages:
            generated.append(write_page_markdown(client, page, args.output_dir, images_dir, resources))
        write_index(args.output_dir, args.title, generated)

    stats = validate_output(args.output_dir, args.render_smoke)
    print(
        "Generated "
        f"{stats['markdown_files']} Markdown files, "
        f"{stats['image_files']} images, "
        f"{stats['tables']} tables, "
        f"{stats['image_refs']} image references in {args.output_dir}",
    )
    return 0


def main() -> int:
    return run(parse_args(sys.argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
