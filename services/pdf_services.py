from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ──────────────────────────────────────────────
# Paleta EcoTotally
# ──────────────────────────────────────────────
ECO_DARK     = colors.HexColor('#060e0b')
ECO_GREEN    = colors.HexColor('#2ef8a0')
ECO_GREEN_2  = colors.HexColor('#19c97d')
ECO_SURFACE  = colors.HexColor('#0a1d18')
ECO_CARD     = colors.HexColor('#0c3c2e')
ECO_TEXT     = colors.HexColor('#e0f5ea')
ECO_MUTED    = colors.HexColor('#96dcb9')
ECO_BORDER   = colors.HexColor('#1a5c44')
ECO_WARNING  = colors.HexColor('#ffd66e')
ECO_ERROR    = colors.HexColor('#ff8b8b')

W, H = A4
MARGIN = 18 * mm


def _styles():
    base = getSampleStyleSheet()

    title = ParagraphStyle(
        'EcoTitle',
        parent=base['Normal'],
        fontSize=26, leading=32,
        textColor=ECO_GREEN,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT, spaceAfter=4,
    )
    subtitle = ParagraphStyle(
        'EcoSubtitle',
        parent=base['Normal'],
        fontSize=10, leading=14,
        textColor=ECO_MUTED,
        fontName='Helvetica', spaceAfter=6,
    )
    section = ParagraphStyle(
        'EcoSection',
        parent=base['Normal'],
        fontSize=13, leading=16,
        textColor=ECO_GREEN,
        fontName='Helvetica-Bold',
        spaceBefore=16, spaceAfter=8,
    )
    body = ParagraphStyle(
        'EcoBody',
        parent=base['Normal'],
        fontSize=10, leading=15,
        textColor=ECO_TEXT,
        fontName='Helvetica',
    )
    muted = ParagraphStyle(
        'EcoMuted',
        parent=base['Normal'],
        fontSize=9, leading=13,
        textColor=ECO_MUTED,
        fontName='Helvetica',
    )
    score_big = ParagraphStyle(
        'EcoScoreBig',
        parent=base['Normal'],
        fontSize=36, leading=40,
        textColor=ECO_GREEN,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
    )
    label_right = ParagraphStyle(
        'EcoLabelRight',
        parent=base['Normal'],
        fontSize=9, leading=13,
        textColor=ECO_MUTED,
        fontName='Helvetica',
        alignment=TA_RIGHT,
    )
    return title, subtitle, section, body, muted, score_big, label_right


def _header_table(nome_usuario: str, regiao: str, styles):
    title, subtitle, *_ = styles
    data_str = datetime.now().strftime('%d/%m/%Y às %H:%M')
    left = [
        Paragraph('🌱 EcoTotally', title),
        Paragraph('Relatório de Consumo Energético', subtitle),
        Paragraph(f'Gerado em {data_str}', subtitle),
    ]
    right = [
        Paragraph(f'<b>Usuário</b><br/>{nome_usuario}', subtitle),
        Paragraph(f'<b>Região</b><br/>{regiao}', subtitle),
    ]
    tbl = Table([[left, right]], colWidths=[W - 2 * MARGIN - 50 * mm, 50 * mm])
    tbl.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('ALIGN',         (1, 0), (1, 0),   'RIGHT'),
        ('BACKGROUND',    (0, 0), (-1, -1), ECO_SURFACE),
        ('TOPPADDING',    (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('LEFTPADDING',   (0, 0), (0, 0),   16),
        ('RIGHTPADDING',  (1, 0), (1, 0),   16),
    ]))
    return tbl


def _score_card(score: dict, styles):
    title, subtitle, section, body, muted, score_big, *_ = styles

    nivel = score.get('nivel', '—')
    valor = score.get('valor', 0)
    motivos = score.get('motivos', [])

    cor = ECO_GREEN if valor >= 80 else (ECO_WARNING if valor >= 50 else ECO_ERROR)

    score_style = ParagraphStyle('ScoreBig2', parent=score_big, textColor=cor)
    nivel_style = ParagraphStyle(
        'NivelStyle', parent=body, fontSize=12,
        textColor=cor, fontName='Helvetica-Bold', alignment=TA_CENTER,
    )

    left_content = [
        Paragraph(str(valor), score_style),
        Paragraph(nivel, nivel_style),
        Paragraph('/100', muted),
    ]
    motivos_txt = '<br/>'.join(f'• {m}' for m in motivos) if motivos else '—'
    right_content = [
        Paragraph('<b>Pontos de atenção</b>', section),
        Paragraph(motivos_txt, body),
    ]

    tbl = Table(
        [[left_content, right_content]],
        colWidths=[40 * mm, W - 2 * MARGIN - 40 * mm]
    )
    tbl.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN',         (0, 0), (0, 0),   'CENTER'),
        ('BACKGROUND',    (0, 0), (-1, -1), ECO_CARD),
        ('TOPPADDING',    (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('LEFTPADDING',   (0, 0), (0, 0),   14),
        ('LEFTPADDING',   (1, 0), (1, 0),   14),
        ('RIGHTPADDING',  (1, 0), (1, 0),   14),
        ('LINEAFTER',     (0, 0), (0, 0),    1, ECO_BORDER),
    ]))
    return tbl


def _regional_table(comp: dict, styles):
    *_, section, body, muted, __, label_right = styles

    media_u = comp.get('media_mensal_usuario', 0)
    media_r = comp.get('media_mensal_regional', 0)
    dif     = comp.get('diferenca', 0)
    situacao = comp.get('situacao', '—')
    total_u = comp.get('total_usuarios_regiao', 0)

    dif_txt = f'+R$ {dif:.2f}' if dif >= 0 else f'-R$ {abs(dif):.2f}'
    dif_cor = ECO_ERROR if dif > 0 else ECO_GREEN

    header = ['', 'Valor mensal (R$)', 'Diferença']
    rows = [
        ['Você',           f'R$ {media_u:.2f}', '—'],
        ['Média da região', f'R$ {media_r:.2f}', dif_txt],
    ]

    tbl = Table([header] + rows, colWidths=[55 * mm, 55 * mm, 55 * mm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  ECO_SURFACE),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  ECO_GREEN),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0),  9),
        ('ALIGN',         (0, 0), (-1, 0),  'CENTER'),
        ('BACKGROUND',    (0, 1), (-1, -1), ECO_CARD),
        ('TEXTCOLOR',     (0, 1), (-1, -1), ECO_TEXT),
        ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 1), (-1, -1), 10),
        ('ALIGN',         (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR',     (2, 2), (2, 2),   dif_cor),
        ('FONTNAME',      (2, 2), (2, 2),   'Helvetica-Bold'),
        ('LINEBELOW',     (0, 0), (-1, -1), 0.5, ECO_BORDER),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING',   (0, 0), (0, -1),  12),
    ]))

    return [
        tbl,
        Spacer(1, 8),
        Paragraph(
            f'Situação: <b>{situacao}</b>  ·  Total de usuários na região: <b>{total_u}</b>',
            muted
        ),
    ]


def _categorias_table(categorias: dict, styles):
    *_, section, body, muted, __, ___ = styles

    header = ['Categoria', 'Último mês (R$)', 'Tendência', 'Projetado (R$)']
    rows = []

    for tipo, dados in categorias.items():
        tend = dados.get('tendencia', '—')
        tend_emoji = {
            'alta':   '📈 alta',
            'queda':  '📉 queda',
            'estavel':'➡️ estável'
        }.get(tend, tend)
        rows.append([
            tipo.title(),
            f"R$ {dados.get('ultimo_mes', 0):.2f}",
            tend_emoji,
            f"R$ {dados.get('total_projetado', 0):.2f}",
        ])

    if not rows:
        return [Paragraph('Sem dados de categorias.', muted)]

    col_w = [(W - 2 * MARGIN) / 4] * 4
    tbl = Table([header] + rows, colWidths=col_w)
    tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  ECO_SURFACE),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  ECO_GREEN),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0),  9),
        ('ALIGN',         (0, 0), (-1, 0),  'CENTER'),
        ('BACKGROUND',    (0, 1), (-1, -1), ECO_CARD),
        ('TEXTCOLOR',     (0, 1), (-1, -1), ECO_TEXT),
        ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 1), (-1, -1), 10),
        ('ALIGN',         (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW',     (0, 0), (-1, -1), 0.5, ECO_BORDER),
        ('TOPPADDING',    (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('LEFTPADDING',   (0, 0), (0, -1),  12),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [ECO_CARD, ECO_SURFACE]),
    ]))
    return [tbl]


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(ECO_MUTED)
    canvas.setFont('Helvetica', 8)
    page_num = canvas.getPageNumber()
    text = f'EcoTotally  ·  Relatório gerado em {datetime.now().strftime("%d/%m/%Y")}  ·  Página {page_num}'
    canvas.drawCentredString(W / 2, 12 * mm, text)
    canvas.setStrokeColor(ECO_BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 16 * mm, W - MARGIN, 16 * mm)
    canvas.restoreState()


def gerar_pdf_relatorio(insights: dict, caminho_arquivo: str):
    doc = SimpleDocTemplate(
        caminho_arquivo,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN,  bottomMargin=25 * mm,
    )

    styles = _styles()
    _, subtitle, section, body, muted, *_ = styles
    elementos = []

    # ── Cabeçalho ─────────────────────────────────────────────
    nome   = insights.get('nome_usuario', 'Usuário')
    regiao = insights.get('regiao', '—')
    elementos.append(_header_table(nome, regiao, styles))
    elementos.append(Spacer(1, 16))

    # ── Score ─────────────────────────────────────────────────
    elementos.append(Paragraph('🏅 Score de Sustentabilidade', section))
    elementos.append(_score_card(insights.get('score', {}), styles))
    elementos.append(Spacer(1, 16))

    # ── Previsão ──────────────────────────────────────────────
    prev   = insights.get('previsao_total', 0)
    meses_p = insights.get('meses_projetados', 3)
    elementos.append(HRFlowable(width='100%', thickness=0.5, color=ECO_BORDER, spaceAfter=8))
    elementos.append(Paragraph('📊 Previsão de Gastos', section))

    prev_data = [
        ['Horizonte', 'Total projetado (R$)'],
        [f'Próximos {meses_p} meses', f'R$ {prev:.2f}'],
    ]
    prev_tbl = Table(prev_data, colWidths=[80 * mm, 80 * mm])
    prev_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  ECO_SURFACE),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  ECO_GREEN),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0),  9),
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND',    (0, 1), (-1, -1), ECO_CARD),
        ('TEXTCOLOR',     (0, 1), (-1, -1), ECO_TEXT),
        ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 1), (-1, -1), 14),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW',     (0, 0), (-1, -1), 0.5, ECO_BORDER),
    ]))
    elementos.append(prev_tbl)
    elementos.append(Spacer(1, 16))

    # ── Comparativo Regional ──────────────────────────────────
    elementos.append(HRFlowable(width='100%', thickness=0.5, color=ECO_BORDER, spaceAfter=8))
    elementos.append(Paragraph('🗺️ Comparativo Regional', section))
    for el in _regional_table(insights.get('comparativo_regional', {}), styles):
        elementos.append(el)
    elementos.append(Spacer(1, 16))

    # ── Categorias ────────────────────────────────────────────
    elementos.append(HRFlowable(width='100%', thickness=0.5, color=ECO_BORDER, spaceAfter=8))
    elementos.append(Paragraph('⚡ Detalhamento por Categoria', section))
    for el in _categorias_table(insights.get('categorias', {}), styles):
        elementos.append(el)
    elementos.append(Spacer(1, 16))

    # ── Nota final ────────────────────────────────────────────
    elementos.append(HRFlowable(width='100%', thickness=0.5, color=ECO_BORDER, spaceAfter=6))
    elementos.append(Paragraph(
        'Este relatório foi gerado automaticamente pelo EcoTotally com base nos seus registros de consumo. '
        'Para dúvidas ou suporte, entre em contato: <b>ectotally@gmail.com</b>',
        muted
    ))

    doc.build(elementos, onFirstPage=_footer, onLaterPages=_footer)
