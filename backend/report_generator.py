"""
ReportLab-based PDF Report Generator for LaunchPad AI.
Generates an investor-ready, multi-page PDF due diligence report from database agent outputs.
"""

import io
import json
import html
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total page count and draw
    running header/footer page numbers on all pages except the cover page.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        if self._pageNumber == 1:
            # Skip running headers on cover page
            return

        self.saveState()
        # Top Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))  # Slate 600
        self.drawString(54, 750, "LAUNCHPAD AI — INVESTOR DUE DILIGENCE REPORT")
        self.setFont("Helvetica", 8)
        self.drawRightString(558, 750, "CONFIDENTIAL")

        self.setStrokeColor(colors.HexColor("#CBD5E1"))  # Slate 300
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)

        # Bottom Footer
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Prepared for Investment Committee & Due Diligence Review")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_text)

        self.restoreState()


def clean_text(val, default="") -> str:
    """
    Safely converts any value (list, dict, int, float, str) into a sanitized,
    HTML-safe string for ReportLab Paragraph rendering.
    """
    if val is None:
        return default
    if isinstance(val, list):
        items = [clean_text(item) for item in val if item is not None]
        return "<br/>".join(f"• {item}" for item in items if item)
    if isinstance(val, dict):
        return html.escape(json.dumps(val))

    s = str(val).strip()
    return html.escape(s)


def build_pdf_report(idea_data: dict, agent_outputs_map: dict) -> bytes:
    """
    Builds a professional multi-page PDF document in memory.

    idea_data: dict containing title, description, target_market, region, sector, id, created_at
    agent_outputs_map: dict mapping agent_name -> parsed dict output
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    NAVY = colors.HexColor("#0F172A")
    INDIGO = colors.HexColor("#4338CA")
    SLATE_TEXT = colors.HexColor("#334155")
    SLATE_LIGHT = colors.HexColor("#F8FAFC")
    BORDER_COLOR = colors.HexColor("#E2E8F0")

    # Custom Typography Styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=NAVY,
        spaceAfter=12,
    )

    tagline_style = ParagraphStyle(
        "CoverTagline",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=12,
        leading=16,
        textColor=INDIGO,
        spaceAfter=20,
    )

    meta_style = ParagraphStyle(
        "CoverMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14.5,
        textColor=SLATE_TEXT,
    )

    h1_style = ParagraphStyle(
        "HeaderH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=NAVY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "HeaderH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=INDIGO,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=SLATE_TEXT,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "BulletCustom",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white,
    )

    table_body_style = ParagraphStyle(
        "TableBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=SLATE_TEXT,
    )

    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 30))
    story.append(
        Paragraph(
            "<font size=9 color='#4338CA'><b>LAUNCHPAD AI — STARTUP ACCELERATOR PIPELINE</b></font>",
            body_style,
        )
    )
    story.append(Spacer(1, 10))

    title_text = clean_text(idea_data.get("title", "Untitled Venture Idea"))
    story.append(Paragraph(title_text, title_style))

    # Pull tagline from Business Model value proposition if available
    bm_data = agent_outputs_map.get("business_model", {})
    tagline = ""
    if isinstance(bm_data, dict):
        tagline = bm_data.get("value_proposition", "")
    if not tagline:
        tagline = idea_data.get("description", "")[:140]

    story.append(Paragraph(f"“{clean_text(tagline)}”", tagline_style))
    story.append(HRFlowable(width="100%", thickness=2, color=INDIGO, spaceAfter=20))

    # Metadata Block
    created_dt = datetime.now().strftime("%B %d, %Y")
    idea_id = clean_text(idea_data.get("id", "N/A"))
    target_market = clean_text(idea_data.get("target_market") or "Global Target Market")
    sector = clean_text(idea_data.get("sector") or "Technology & Innovation")

    meta_html = f"""
    <b>Document Type:</b> Investor Due Diligence Report<br/>
    <b>Idea Identifier:</b> {idea_id}<br/>
    <b>Date Generated:</b> {created_dt}<br/>
    <b>Sector Category:</b> {sector}<br/>
    <b>Target Market:</b> {target_market}<br/>
    <b>Pipeline Status:</b> Verified Autonomous Agent Execution
    """
    story.append(Paragraph(meta_html, meta_style))
    story.append(Spacer(1, 30))

    # Executive Summary Card on Cover Page
    desc = clean_text(idea_data.get("description", "No description provided."))
    summary_box_data = [
        [
            Paragraph(
                f"<b>Executive Summary:</b><br/>{desc}",
                body_style,
            )
        ]
    ]
    summary_table = Table(summary_box_data, colWidths=[504])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SLATE_LIGHT),
                ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
                ("PADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story.append(summary_table)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: IDEA VALIDATION & FEASIBILITY (Agent 1)
    # =========================================================================
    story.append(Paragraph("1. Idea Validation & Feasibility Analysis", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10))

    val_data = agent_outputs_map.get("idea_validator", {})
    if isinstance(val_data, dict) and val_data:
        score = clean_text(val_data.get("validation_score", "N/A"))
        rec = clean_text(val_data.get("recommendation", "N/A"))
        notes = clean_text(val_data.get("feasibility_notes", "N/A"))

        score_html = f"<b>Validation Score:</b> <font color='#4338CA' size=11><b>{score}/100</b></font>"
        story.append(Paragraph(score_html, body_style))
        story.append(Paragraph(f"<b>Strategic Recommendation:</b> {rec}", body_style))
        story.append(Paragraph(f"<b>Feasibility Assessment:</b> {notes}", body_style))

        strengths = val_data.get("strengths", [])
        if strengths and isinstance(strengths, list):
            story.append(Paragraph("<b>Key Strengths:</b>", h2_style))
            for s in strengths:
                story.append(Paragraph(f"• {clean_text(s)}", bullet_style))

        weaknesses = val_data.get("weaknesses", [])
        if weaknesses and isinstance(weaknesses, list):
            story.append(Paragraph("<b>Key Risks & Weaknesses:</b>", h2_style))
            for w in weaknesses:
                story.append(Paragraph(f"• {clean_text(w)}", bullet_style))
    else:
        story.append(Paragraph("<i>Analysis pending completion...</i>", body_style))

    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 2: MARKET OPPORTUNITY & TRENDS (Agent 3)
    # =========================================================================
    story.append(Paragraph("2. Market Opportunity & Growth Drivers", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10))

    mkt_data = agent_outputs_map.get("market_research", {})
    if isinstance(mkt_data, dict) and mkt_data:
        tam = clean_text(mkt_data.get("market_size_estimate", "N/A"))
        cagr = clean_text(mkt_data.get("growth_trends", "N/A"))
        demos = clean_text(mkt_data.get("target_demographics", "N/A"))

        story.append(Paragraph(f"<b>Market Size Estimate (TAM/SAM):</b> {tam}", body_style))
        story.append(Paragraph(f"<b>Growth Drivers & Trends:</b> {cagr}", body_style))
        story.append(Paragraph(f"<b>Target Demographics:</b> {demos}", body_style))

        sources = mkt_data.get("sources", [])
        if sources and isinstance(sources, list):
            story.append(Paragraph("<b>Verified Research Sources:</b>", h2_style))
            for src in sources[:4]:
                story.append(Paragraph(f"• {clean_text(src)}", bullet_style))
    else:
        story.append(Paragraph("<i>Analysis pending completion...</i>", body_style))

    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 3: COMPETITIVE LANDSCAPE (Agent 4)
    # =========================================================================
    story.append(Paragraph("3. Competitive Landscape & Differentiation", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10))

    comp_data = agent_outputs_map.get("competitor_analysis", {})
    if isinstance(comp_data, dict) and comp_data:
        diff = clean_text(comp_data.get("differentiation_opportunities", "N/A"))
        story.append(Paragraph(f"<b>Differentiation Moat & White Space:</b> {diff}", body_style))
        story.append(Spacer(1, 4))

        competitors = comp_data.get("competitors", [])
        if competitors and isinstance(competitors, list):
            table_data = [
                [
                    Paragraph("<b>Competitor</b>", table_header_style),
                    Paragraph("<b>Overview & Offerings</b>", table_header_style),
                    Paragraph("<b>Strengths</b>", table_header_style),
                    Paragraph("<b>Weaknesses</b>", table_header_style),
                ]
            ]
            for c in competitors[:5]:
                if isinstance(c, dict):
                    name = clean_text(c.get("name", "N/A"))
                    desc_c = clean_text(c.get("description", "N/A"))
                    str_c = clean_text(c.get("strengths", "N/A"))
                    wk_c = clean_text(c.get("weaknesses", "N/A"))
                else:
                    name = clean_text(c)
                    desc_c = str_c = wk_c = "N/A"

                table_data.append([
                    Paragraph(f"<b>{name}</b>", table_body_style),
                    Paragraph(desc_c, table_body_style),
                    Paragraph(str_c, table_body_style),
                    Paragraph(wk_c, table_body_style),
                ])

            comp_table = Table(table_data, colWidths=[90, 154, 130, 130])
            comp_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    ("PADDING", (0, 0), (-1, -1), 5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SLATE_LIGHT]),
                ])
            )
            story.append(comp_table)
    else:
        story.append(Paragraph("<i>Analysis pending completion...</i>", body_style))

    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 4: STRATEGIC BUSINESS MODEL CANVAS (Agent 5)
    # =========================================================================
    story.append(Paragraph("4. Strategic Business Model Canvas", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10))

    if isinstance(bm_data, dict) and bm_data:
        val_prop = clean_text(bm_data.get("value_proposition", "N/A"))
        story.append(Paragraph(f"<b>Core Value Proposition:</b> {val_prop}", body_style))
        story.append(Spacer(1, 4))

        bm_sections = [
            ("Revenue Streams", bm_data.get("revenue_streams", [])),
            ("Cost Structure", bm_data.get("cost_structure", [])),
            ("Customer Segments", bm_data.get("customer_segments", [])),
            ("Distribution Channels", bm_data.get("channels", [])),
        ]

        for sec_title, items in bm_sections:
            story.append(Paragraph(f"<b>{sec_title}:</b>", h2_style))
            if isinstance(items, list) and items:
                for it in items:
                    story.append(Paragraph(f"• {clean_text(it)}", bullet_style))
            elif items:
                story.append(Paragraph(clean_text(items), body_style))
            else:
                story.append(Paragraph("N/A", body_style))
    else:
        story.append(Paragraph("<i>Analysis pending completion...</i>", body_style))

    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 5: PITCH DECK OUTLINE (Agent 6)
    # =========================================================================
    story.append(Paragraph("5. Investor Pitch Deck Outline", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10))

    pitch_data = agent_outputs_map.get("pitch_deck", {})
    if isinstance(pitch_data, dict) and pitch_data:
        slides = pitch_data.get("slides", [])
        if isinstance(slides, list) and slides:
            for s_idx, slide in enumerate(slides, 1):
                if isinstance(slide, dict):
                    stitle = clean_text(slide.get("title", f"Slide {s_idx}"))
                    scontent = clean_text(slide.get("content", ""))
                else:
                    stitle = f"Slide {s_idx}"
                    scontent = clean_text(slide)

                slide_box_data = [
                    [
                        Paragraph(f"<b>SLIDE {s_idx}: {stitle.upper()}</b>", ParagraphStyle("SHead", parent=table_header_style, textColor=NAVY)),
                    ],
                    [
                        Paragraph(scontent, table_body_style),
                    ]
                ]
                slide_table = Table(slide_box_data, colWidths=[504])
                slide_table.setStyle(
                    TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                        ("BACKGROUND", (0, 1), (-1, 1), colors.white),
                        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                        ("PADDING", (0, 0), (-1, -1), 5),
                    ])
                )
                story.append(KeepTogether([slide_table, Spacer(1, 6)]))
    else:
        story.append(Paragraph("<i>Analysis pending completion...</i>", body_style))

    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 6: INVESTOR MATCHING & SYNDICATES (Agent 7)
    # =========================================================================
    story.append(Paragraph("6. Targeted Investor & VC Syndicate Matches", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10))

    inv_data = agent_outputs_map.get("investor_matching", {})
    if isinstance(inv_data, dict) and inv_data:
        investors = inv_data.get("matched_investors", [])
        if isinstance(investors, list) and investors:
            inv_table_data = [
                [
                    Paragraph("<b>VC Firm / Investor</b>", table_header_style),
                    Paragraph("<b>Focus Area / Stage</b>", table_header_style),
                    Paragraph("<b>Strategic Match Rationale</b>", table_header_style),
                ]
            ]
            for inv in investors[:5]:
                if isinstance(inv, dict):
                    iname = clean_text(inv.get("name", "N/A"))
                    ifocus = clean_text(inv.get("focus_area", "N/A"))
                    ireason = clean_text(inv.get("reason", "N/A"))
                else:
                    iname = clean_text(inv)
                    ifocus = ireason = "N/A"

                inv_table_data.append([
                    Paragraph(f"<b>{iname}</b>", table_body_style),
                    Paragraph(ifocus, table_body_style),
                    Paragraph(ireason, table_body_style),
                ])

            inv_table = Table(inv_table_data, colWidths=[130, 144, 230])
            inv_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    ("PADDING", (0, 0), (-1, -1), 5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SLATE_LIGHT]),
                ])
            )
            story.append(inv_table)
    else:
        story.append(Paragraph("<i>Analysis pending completion...</i>", body_style))

    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 7: IP & PRIOR ART APPENDIX (Agent 2)
    # =========================================================================
    story.append(Paragraph("7. Intellectual Property & Freedom-To-Operate Appendix", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=10))

    pat_data = agent_outputs_map.get("patent_search", {})
    if isinstance(pat_data, dict) and pat_data:
        risk = clean_text(pat_data.get("risk_level", "medium")).upper()
        pnotes = clean_text(pat_data.get("notes", "N/A"))

        risk_color = "#16A34A" if "LOW" in risk else ("#DC2626" if "HIGH" in risk else "#D97706")
        story.append(Paragraph(f"<b>IP Infringement Risk Level:</b> <font color='{risk_color}'><b>{risk}</b></font>", body_style))
        story.append(Paragraph(f"<b>Freedom-To-Operate Assessment:</b> {pnotes}", body_style))
        story.append(Spacer(1, 4))

        patents = pat_data.get("similar_patents", [])
        if isinstance(patents, list) and patents:
            pat_table_data = [
                [
                    Paragraph("<b>Patent / Prior Art Title</b>", table_header_style),
                    Paragraph("<b>Summary & Overlap</b>", table_header_style),
                    Paragraph("<b>Reference Link</b>", table_header_style),
                ]
            ]
            for p in patents[:4]:
                if isinstance(p, dict):
                    ptitle = clean_text(p.get("title", "N/A"))
                    psummary = clean_text(p.get("summary", "N/A"))
                    purl = clean_text(p.get("source_url", "N/A"))
                else:
                    ptitle = clean_text(p)
                    psummary = purl = "N/A"

                pat_table_data.append([
                    Paragraph(f"<b>{ptitle}</b>", table_body_style),
                    Paragraph(psummary, table_body_style),
                    Paragraph(f"<font color='#4338CA'>{purl[:45]}</font>", table_body_style),
                ])

            pat_table = Table(pat_table_data, colWidths=[150, 224, 130])
            pat_table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    ("PADDING", (0, 0), (-1, -1), 5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SLATE_LIGHT]),
                ])
            )
            story.append(pat_table)
    else:
        story.append(Paragraph("<i>Analysis pending completion...</i>", body_style))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
