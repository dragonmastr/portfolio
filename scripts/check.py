#!/usr/bin/env python3
"""Pre-deploy sanity checks. Fails the build rather than shipping a broken page."""

import re
import sys
from html.parser import HTMLParser

VOID = {"br", "img", "meta", "link", "input", "hr", "source", "col",
        "line", "rect", "path", "circle", "text", "use", "polygon", "ellipse"}


class Balance(HTMLParser):
	def __init__(self):
		super().__init__()
		self.stack = []
		self.errors = []

	def handle_starttag(self, tag, attrs):
		if tag not in VOID:
			self.stack.append((tag, self.getpos()))

	def handle_endtag(self, tag):
		if tag in VOID:
			return
		if not self.stack:
			self.errors.append(f"stray </{tag}> at {self.getpos()}")
			return
		open_tag, pos = self.stack.pop()
		if open_tag != tag:
			self.errors.append(f"expected </{open_tag}> (opened {pos}), got </{tag}> at {self.getpos()}")


def main():
	failures = []
	html = open("index.html", encoding="utf-8").read()

	parser = Balance()
	parser.feed(html)
	failures += parser.errors
	failures += [f"unclosed <{t}> opened at {p}" for t, p in parser.stack]

	css = html[html.index("<style>"):html.index("</style>")]
	if css.count("{") != css.count("}"):
		failures.append(f"unbalanced CSS braces: {css.count('{')} open, {css.count('}')} close")

	body = html[html.index("</style>"):]
	used = {c for group in re.findall(r'class="([^"]+)"', body) for c in group.split()}
	defined = set(re.findall(r"\.([a-zA-Z][\w-]*)", css))
	for missing in sorted(used - defined):
		failures.append(f"class '{missing}' used in markup but has no CSS rule")

	panels = set(re.findall(r'id="(panel-[\w-]+)"', body))
	for target in sorted(set(re.findall(r'aria-controls="([\w-]+)"', body))):
		if target not in panels:
			failures.append(f"tab points at missing panel '{target}'")

	for anchor in sorted(set(re.findall(r'href="#([\w-]+)"', body))):
		if f'id="{anchor}"' not in body:
			failures.append(f"in-page link #{anchor} has no target")

	if failures:
		print("FAILED")
		for f in failures:
			print("  -", f)
		return 1

	print(f"ok - {len(used)} classes, {len(panels)} panels, {len(html) // 1024} KB")
	return 0


if __name__ == "__main__":
	sys.exit(main())
