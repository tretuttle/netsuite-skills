#!/usr/bin/env python3
"""Build Oracle NetSuite help indexes from Oracle's live TOC."""

from __future__ import annotations

import argparse
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.request import urlopen

DEFAULT_TOC_URL = "https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/toc.htm"
DEFAULT_BASE_URL = "https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/"


class FlatLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_anchor = False
        self.href: str | None = None
        self.text: list[str] = []
        self.items: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attr_map = dict(attrs)
        href = attr_map.get("href")
        if href and href.endswith(".html"):
            self.in_anchor = True
            self.href = href
            self.text = []

    def handle_data(self, data: str) -> None:
        if self.in_anchor:
            self.text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self.in_anchor:
            return
        title = " ".join("".join(self.text).split())
        href = self.href
        self.in_anchor = False
        self.href = None
        self.text = []
        if title and href and title.lower() != "next":
            self.items.append((title, href))


class TOCTreeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.root: list[dict] = []
        self.list_stack: list[list[dict]] = [self.root]
        self.current_li: dict | None = None
        self.capture_anchor = False
        self.current_href: str | None = None
        self.current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if tag == "ul" and attr_map.get("class") == "contents":
            if self.current_li is not None:
                self.list_stack.append(self.current_li["children"])
            return
        if tag == "li":
            node = {"title": None, "href": None, "children": []}
            self.list_stack[-1].append(node)
            self.current_li = node
            return
        if tag == "a":
            href = attr_map.get("href")
            if href and href.endswith(".html") and self.current_li is not None:
                self.capture_anchor = True
                self.current_href = href
                self.current_text = []

    def handle_data(self, data: str) -> None:
        if self.capture_anchor:
            self.current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.capture_anchor:
            title = " ".join("".join(self.current_text).split())
            if title and self.current_li is not None:
                self.current_li["title"] = title
                self.current_li["href"] = self.current_href
            self.capture_anchor = False
            self.current_href = None
            self.current_text = []
            return
        if tag == "li":
            self.current_li = None
            return
        if tag == "ul" and len(self.list_stack) > 1:
            self.list_stack.pop()


def fetch_html(url: str) -> str:
    with urlopen(url) as response:
        return response.read().decode("utf-8", errors="ignore")


def base_url_from_toc(toc_url: str) -> str:
    return toc_url.rsplit("/", 1)[0] + "/"


def prune_tree(nodes: list[dict]) -> list[dict]:
    pruned: list[dict] = []
    for node in nodes:
        children = prune_tree(node["children"])
        title = node["title"]
        href = node["href"]
        if title and href and title.lower() != "next":
            pruned.append({"title": title, "href": href, "children": children})
        else:
            pruned.extend(children)
    return pruned


def unique_items(items: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    ordered: list[tuple[str, str]] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def build_alphabetical_markdown(items: list[tuple[str, str]], toc_url: str) -> str:
    sections: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for title, url in sorted(items, key=lambda x: (x[0].casefold(), x[1])):
        first = title[0].upper()
        if not first.isalnum():
            first = "#"
        sections[first].append((title, url))

    lines = [
        "# Oracle NetSuite Full Help Index",
        "",
        f"Source: live Oracle NetSuite help TOC at {toc_url}",
        "",
        f"Total links: {len(items)}",
        "",
        "This file is alphabetized for quick search in-editor.",
        "",
    ]
    for section in sorted(sections):
        lines.append(f"## {section}")
        lines.append("")
        for title, url in sections[section]:
            lines.append(f"- [{title}]({url})")
        lines.append("")
    return "\n".join(lines) + "\n"


def emit_tree(nodes: list[dict], base_url: str, depth: int = 0) -> list[str]:
    lines: list[str] = []
    for node in nodes:
        lines.append(f"{'  ' * depth}- [{node['title']}]({base_url}{node['href']})")
        lines.extend(emit_tree(node["children"], base_url, depth + 1))
    return lines


def count_tree(nodes: list[dict]) -> int:
    return sum(1 + count_tree(node["children"]) for node in nodes)


def build_hierarchy_markdown(nodes: list[dict], toc_url: str, base_url: str) -> str:
    lines = [
        "# Oracle NetSuite Full Help TOC (Hierarchical)",
        "",
        f"Source: live Oracle NetSuite help TOC at {toc_url}",
        "",
        f"Total links: {count_tree(nodes)}",
        "",
    ]
    lines.extend(emit_tree(nodes, base_url))
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toc-url", default=DEFAULT_TOC_URL, help="Oracle TOC URL")
    parser.add_argument("--output-dir", default=".", help="Directory for generated files")
    parser.add_argument(
        "--alphabetical-name",
        default="oracle_netsuite_full_toc.md",
        help="Filename for the alphabetical index",
    )
    parser.add_argument(
        "--hierarchy-name",
        default="oracle_netsuite_full_toc_hierarchy.md",
        help="Filename for the hierarchical index",
    )
    parser.add_argument(
        "--query",
        action="append",
        default=[],
        help="Keyword to search for in titles; can be passed multiple times",
    )
    args = parser.parse_args()

    toc_url = args.toc_url
    base_url = base_url_from_toc(toc_url)
    html = fetch_html(toc_url)

    flat_parser = FlatLinkParser()
    flat_parser.feed(html)
    items = unique_items(
        (
            title,
            href if href.startswith("http") else base_url + href,
        )
        for title, href in flat_parser.items
    )

    tree_start = html.find('<ul class="contents">')
    if tree_start == -1:
        raise SystemExit("Could not find root TOC list in Oracle HTML.")
    tree_parser = TOCTreeParser()
    tree_parser.feed(html[tree_start:])
    nodes = prune_tree(tree_parser.root)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    alphabetical_path = output_dir / args.alphabetical_name
    hierarchy_path = output_dir / args.hierarchy_name
    alphabetical_path.write_text(build_alphabetical_markdown(items, toc_url))
    hierarchy_path.write_text(build_hierarchy_markdown(nodes, toc_url, base_url))

    print(f"Wrote {alphabetical_path} ({len(items)} unique links)")
    print(f"Wrote {hierarchy_path} ({count_tree(nodes)} hierarchical entries)")

    for term in args.query:
        needle = term.casefold()
        matches = [(title, url) for title, url in items if needle in title.casefold()]
        print(f"\nQuery: {term} ({len(matches)} matches)")
        for title, url in matches:
            print(f"{title}\t{url}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
