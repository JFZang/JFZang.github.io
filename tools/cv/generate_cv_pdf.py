from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

TOOL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TOOL_DIR.parent.parent
SOURCE = PROJECT_ROOT / 'content' / 'cv' / 'CV.md'
OUTPUT = PROJECT_ROOT / 'assets' / 'documents' / 'Jiefu-Zhang-CV.pdf'
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_X = 12 * mm
CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN_X)
DATE_COL_WIDTH = 38 * mm
TITLE_COL_WIDTH = CONTENT_WIDTH - DATE_COL_WIDTH


def inline_html(text: str) -> str:
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    while '**' in text:
        start = text.find('**')
        end = text.find('**', start + 2)
        if end == -1:
            break
        inner = text[start + 2:end]
        text = text[:start] + f'<b>{inner}</b>' + text[end + 2:]
    return text.replace('  ', '<br/>')


def build_styles():
    styles = getSampleStyleSheet()
    return {
        'name': ParagraphStyle(
            'Name', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=17,
            leading=19, alignment=TA_CENTER, textColor=colors.HexColor('#1f2a44'), spaceAfter=3,
        ),
        'contact': ParagraphStyle(
            'Contact', parent=styles['BodyText'], fontName='Helvetica', fontSize=8.8,
            leading=10.5, alignment=TA_CENTER, textColor=colors.HexColor('#4b5563'), spaceAfter=7,
        ),
        'section': ParagraphStyle(
            'Section', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=10.2,
            leading=11.6, alignment=TA_CENTER, textColor=colors.HexColor('#1f2a44'),
            spaceBefore=5, spaceAfter=5,
        ),
        'entry_title': ParagraphStyle(
            'EntryTitle', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=10.1,
            leading=11.6, alignment=TA_LEFT, textColor=colors.black,
        ),
        'entry_date': ParagraphStyle(
            'EntryDate', parent=styles['BodyText'], fontName='Helvetica', fontSize=8.9,
            leading=11.0, alignment=TA_RIGHT, textColor=colors.HexColor('#5b6470'),
        ),
        'role': ParagraphStyle(
            'Role', parent=styles['BodyText'], fontName='Helvetica-Oblique', fontSize=8.9,
            leading=10.6, alignment=TA_LEFT, textColor=colors.HexColor('#2f3742'), spaceAfter=1,
        ),
        'body': ParagraphStyle(
            'Body', parent=styles['BodyText'], fontName='Helvetica', fontSize=8.7,
            leading=10.4, alignment=TA_LEFT, textColor=colors.black, spaceAfter=2,
        ),
        'bullet': ParagraphStyle(
            'Bullet', parent=styles['BodyText'], fontName='Helvetica', fontSize=8.55,
            leading=10.1, alignment=TA_LEFT, textColor=colors.black,
        ),
    }


def parse_markdown(text: str):
    lines = text.replace('\r', '').split('\n')
    blocks = []
    current_paragraph = []
    current_list = []

    def flush_paragraph():
        nonlocal current_paragraph
        if current_paragraph:
            blocks.append(('p', ' '.join(current_paragraph).strip()))
            current_paragraph = []

    def flush_list():
        nonlocal current_list
        if current_list:
            blocks.append(('ul', current_list[:]))
            current_list = []

    for raw in lines:
        line = raw.strip()
        if not line:
            flush_paragraph(); flush_list(); continue
        if line.startswith('# '):
            flush_paragraph(); flush_list(); blocks.append(('h1', line[2:].strip())); continue
        if line.startswith('## '):
            flush_paragraph(); flush_list(); blocks.append(('h2', line[3:].strip())); continue
        if line.startswith('### '):
            flush_paragraph(); flush_list(); blocks.append(('h3', line[4:].strip())); continue
        if line.startswith('- '):
            flush_paragraph(); current_list.append(line[2:].strip()); continue
        flush_list(); current_paragraph.append(line)

    flush_paragraph(); flush_list()
    return blocks


def entry_heading(value, styles):
    parts = [part.strip() for part in value.split('||', 1)]
    if len(parts) == 2:
        title, date = parts
    else:
        title, date = value, ''
    table = Table(
        [[Paragraph(inline_html(title), styles['entry_title']), Paragraph(inline_html(date), styles['entry_date'])]],
        colWidths=[TITLE_COL_WIDTH, DATE_COL_WIDTH],
    )
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return table


def section_heading(value, styles):
    table = Table([[Paragraph(inline_html(value), styles['section'])]], colWidths=[CONTENT_WIDTH])
    table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (0, 0), 1.2, colors.HexColor('#1f2a44')),
        ('TOPPADDING', (0, 0), (0, 0), 0),
        ('BOTTOMPADDING', (0, 0), (0, 0), 1),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
        ('RIGHTPADDING', (0, 0), (0, 0), 0),
    ]))
    return table


def build_story(blocks, styles):
    story = []
    i = 0
    while i < len(blocks):
        kind, value = blocks[i]
        if kind == 'h1':
            story.append(Paragraph(inline_html(value), styles['name']))
        elif kind == 'h2':
            story.append(Spacer(1, 3))
            story.append(section_heading(value, styles))
            story.append(Spacer(1, 2))
        elif kind == 'h3':
            group = [entry_heading(value, styles)]
            if i + 1 < len(blocks) and blocks[i + 1][0] == 'p':
                role_text = blocks[i + 1][1]
                if '@' not in role_text and '| +44' not in role_text:
                    group.append(Paragraph(inline_html(role_text), styles['role']))
                    i += 1
            if i + 1 < len(blocks) and blocks[i + 1][0] == 'ul':
                items = [ListItem(Paragraph(inline_html(item), styles['bullet'])) for item in blocks[i + 1][1]]
                group.append(ListFlowable(items, bulletType='bullet', leftIndent=10, bulletFontSize=7.5))
                i += 1
            story.append(KeepTogether(group))
            story.append(Spacer(1, 2))
        elif kind == 'p':
            style = styles['contact'] if '@' in value or '+44' in value else styles['body']
            story.append(Paragraph(inline_html(value), style))
        elif kind == 'ul':
            items = [ListItem(Paragraph(inline_html(item), styles['bullet'])) for item in value]
            story.append(ListFlowable(items, bulletType='bullet', leftIndent=10, bulletFontSize=7.5))
            story.append(Spacer(1, 2))
        i += 1
    return story


def main():
    text = SOURCE.read_text(encoding='utf-8')
    blocks = parse_markdown(text)
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=9 * mm,
        bottomMargin=9 * mm,
        title='Jeff Zhang CV',
        author='Jeff Zhang',
    )
    doc.build(build_story(blocks, styles))
    print(f'Wrote {OUTPUT}')


if __name__ == '__main__':
    main()
