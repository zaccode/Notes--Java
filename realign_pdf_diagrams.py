from __future__ import annotations

import io
import os
from dataclasses import dataclass

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas


ROOT_DIR = r"D:\Notes"
OUTPUT_DIR = os.path.join(ROOT_DIR, "Aligned Notes")
PDF_EXT = ".pdf"

BLOCK_CHARS = {"■", "□"}
ARROW_MAP = str.maketrans(
    {
        "▲": "^",
        "▼": "v",
        "◀": "<",
        "▶": ">",
        "→": "->",
        "←": "<-",
        "↑": "^",
        "↓": "v",
        "\x7f": "-",
    }
)

@dataclass
class RenderLine:
    text: str
    is_diagram: bool
    is_blank: bool


def is_pdf(filename: str) -> bool:
    return filename.lower().endswith(PDF_EXT)


def normalize_text(text: str) -> str:
    return text.translate(ARROW_MAP)


def diagram_score(text: str) -> int:
    score = sum(text.count(ch) for ch in BLOCK_CHARS)
    score += 8 * text.count("Diagram:")
    score += 8 * text.count("Graph:")
    score += 6 * text.count("Tree:")
    score += 4 * text.count("-->")
    score += 4 * text.count("->")
    return score


def is_diagram_page(text: str) -> bool:
    if not text:
        return False
    if diagram_score(text) >= 8:
        return True
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("Graph:", "Tree:", "Diagram:", "Flow:")):
            return True
        if sum(ch in BLOCK_CHARS for ch in stripped) >= 6:
            return True
        if ("-->" in stripped or "->" in stripped) and "  " in line:
            return True
    return False


def is_diagram_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(("Graph:", "Tree:", "Diagram:", "Flow:")):
        return True
    if any(ch in stripped for ch in BLOCK_CHARS):
        return True
    if "-->" in stripped or "<--" in stripped or "->" in stripped or "<-" in stripped:
        return True
    if line.startswith("   ") and any(ch in stripped for ch in "|-_+"):
        return True
    return False


def wrap_line(text: str, font_name: str, font_size: float, max_width: float) -> list[str]:
    if not text:
        return [""]

    words = text.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = word
        else:
            token = word
            while token:
                piece = token
                while piece and pdfmetrics.stringWidth(piece, font_name, font_size) > max_width:
                    piece = piece[:-1]
                if not piece:
                    piece = token[0]
                lines.append(piece)
                token = token[len(piece) :]
            current = ""
    if current:
        lines.append(current)
    return lines or [""]


def is_block_char(ch: str) -> bool:
    return ch in BLOCK_CHARS


def convert_block_grid(lines: list[str]) -> list[str]:
    if not lines:
        return lines

    width = max(len(line) for line in lines)
    grid = [list(line.ljust(width)) for line in lines]
    out = [row[:] for row in grid]
    height = len(grid)

    def filled(r: int, c: int) -> bool:
        return 0 <= r < height and 0 <= c < width and is_block_char(grid[r][c])

    for r in range(height):
        for c in range(width):
            if not is_block_char(grid[r][c]):
                continue
            neighbors = set()
            if filled(r - 1, c):
                neighbors.add("up")
            if filled(r + 1, c):
                neighbors.add("down")
            if filled(r, c - 1):
                neighbors.add("left")
            if filled(r, c + 1):
                neighbors.add("right")

            horizontal = "left" in neighbors or "right" in neighbors
            vertical = "up" in neighbors or "down" in neighbors

            if horizontal and vertical:
                out[r][c] = "+"
            elif horizontal:
                out[r][c] = "+" if len(neighbors) == 1 else "-"
            elif vertical:
                out[r][c] = "|"
            else:
                out[r][c] = "+"

    return ["".join(row).rstrip() for row in out]


def normalize_diagram_lines(lines: list[str]) -> list[str]:
    cleaned = [normalize_text(line.rstrip()) for line in lines]
    cleaned = convert_block_grid(cleaned)
    result: list[str] = []
    for line in cleaned:
        collapsed = line.replace("`", "'")
        result.append(collapsed.rstrip())
    return result


def build_render_lines(text: str, body_font_size: float) -> list[RenderLine]:
    render_lines: list[RenderLine] = []
    max_width = 595.27 - (54 * 2)
    raw_lines = normalize_text(text).splitlines()
    i = 0

    while i < len(raw_lines):
        normalized = raw_lines[i].replace("\t", "    ").rstrip()
        if not normalized.strip():
            render_lines.append(RenderLine("", False, True))
            i += 1
            continue

        if is_diagram_line(normalized):
            block: list[str] = []
            while i < len(raw_lines):
                current = raw_lines[i].replace("\t", "    ").rstrip()
                if current.strip() and is_diagram_line(current):
                    block.append(current)
                    i += 1
                    continue
                break
            for line in normalize_diagram_lines(block):
                render_lines.append(RenderLine(line, True, not line.strip()))
            continue

        for wrapped in wrap_line(normalized, "Helvetica", body_font_size, max_width):
            render_lines.append(RenderLine(wrapped, False, False))
        i += 1

    return render_lines


def page_fits(page_width: float, page_height: float, lines: list[RenderLine], body_font_size: float) -> bool:
    top_margin = 54
    bottom_margin = 42
    body_leading = body_font_size + 3
    diagram_leading = body_font_size + 4
    needed = 0.0
    for line in lines:
        if line.is_blank:
            needed += body_font_size * 0.8
        elif line.is_diagram:
            needed += diagram_leading
        else:
            needed += body_leading
    return needed <= (page_height - top_margin - bottom_margin)


def replacement_page(page_width: float, page_height: float, text: str) -> bytes:
    body_font_size = 11.0
    while body_font_size >= 7.0:
        lines = build_render_lines(text, body_font_size)
        if page_fits(page_width, page_height, lines, body_font_size):
            break
        body_font_size -= 0.5

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    pdf.setTitle("Aligned diagram page")

    left_margin = 54
    right_margin = 54
    top_margin = 54
    bottom_margin = 42
    usable_width = page_width - left_margin - right_margin

    body_font = "Helvetica"
    diagram_font = "Courier"
    body_leading = body_font_size + 3
    diagram_font_size = max(7.0, body_font_size - 1)
    diagram_leading = diagram_font_size + 4

    y = page_height - top_margin
    lines = build_render_lines(text, body_font_size)

    for line in lines:
        if line.is_blank:
            y -= body_font_size * 0.8
            continue

        if line.is_diagram:
            font_size = diagram_font_size
            text_width = pdfmetrics.stringWidth(line.text, diagram_font, font_size)
            while text_width > usable_width and font_size > 6.0:
                font_size -= 0.5
                text_width = pdfmetrics.stringWidth(line.text, diagram_font, font_size)
            x = max(left_margin, (page_width - text_width) / 2)
            pdf.setFont(diagram_font, font_size)
            pdf.setFillColor(black)
            pdf.drawString(x, y, line.text)
            y -= max(diagram_leading, font_size + 3)
            continue

        pdf.setFont(body_font, body_font_size)
        pdf.setFillColor(black)
        pdf.drawString(left_margin, y, line.text)
        y -= body_leading

        if y < bottom_margin:
            break

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def process_pdf(input_path: str, output_path: str) -> tuple[int, int]:
    reader = PdfReader(input_path)
    writer = PdfWriter()
    replaced = 0

    for page in reader.pages:
        text = page.extract_text() or ""
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        if is_diagram_page(text):
            page_pdf = replacement_page(width, height, text)
            replacement_reader = PdfReader(io.BytesIO(page_pdf))
            writer.add_page(replacement_reader.pages[0])
            replaced += 1
        else:
            writer.add_page(page)

    if reader.metadata:
        writer.add_metadata(
            {
                key: str(value)
                for key, value in reader.metadata.items()
                if isinstance(key, str) and value is not None
            }
        )

    with open(output_path, "wb") as handle:
        writer.write(handle)

    return len(reader.pages), replaced


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results: list[tuple[str, int, int]] = []
    for filename in sorted(os.listdir(ROOT_DIR)):
        if not is_pdf(filename):
            continue
        input_path = os.path.join(ROOT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        total_pages, replaced_pages = process_pdf(input_path, output_path)
        results.append((filename, total_pages, replaced_pages))

    for filename, total_pages, replaced_pages in results:
        print(f"{filename}: {replaced_pages} aligned page(s) out of {total_pages}")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
