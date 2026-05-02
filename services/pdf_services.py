from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


def gerar_pdf_relatorio(insights: dict, caminho_arquivo: str):
    # Cria o documento PDF
    doc = SimpleDocTemplate(caminho_arquivo, pagesize=A4)
    styles = getSampleStyleSheet()

    elementos = []

    # Título principal do relatório
    elementos.append(Paragraph("Relatório Financeiro", styles["Title"]))
    elementos.append(Spacer(1, 12))

    # Informações do score do usuário
    score = insights["score"]
    elementos.append(Paragraph(f"Score: {score['valor']} ({score['nivel']})", styles["Normal"]))

    for motivo in score["motivos"]:
        elementos.append(Paragraph(f"- {motivo}", styles["Normal"]))

    elementos.append(Spacer(1, 12))

    # Comparação com outros usuários da mesma região
    comp = insights["comparativo_regional"]

    elementos.append(Paragraph("Comparativo Regional", styles["Heading2"]))
    elementos.append(Paragraph(f"Média usuário: {comp['media_mensal_usuario']}", styles["Normal"]))
    elementos.append(Paragraph(f"Média regional: {comp['media_mensal_regional']}", styles["Normal"]))
    elementos.append(Paragraph(f"Situação: {comp['situacao']}", styles["Normal"]))
    elementos.append(Paragraph(f"Usuários na região: {comp['total_usuarios_regiao']}", styles["Normal"]))

    elementos.append(Spacer(1, 12))

    # Previsão futura baseada no comportamento atual
    elementos.append(Paragraph("Previsão de gastos", styles["Heading2"]))
    elementos.append(Paragraph(f"Total projetado: {insights['previsao_total']}", styles["Normal"]))

    elementos.append(Spacer(1, 12))

    # Detalhamento dos gastos por categoria
    elementos.append(Paragraph("Detalhamento por categoria", styles["Heading2"]))

    for tipo, dados in insights["categorias"].items():
        elementos.append(Paragraph(f"{tipo.upper()}", styles["Heading3"]))
        elementos.append(Paragraph(f"Último mês: {dados['ultimo_mes']}", styles["Normal"]))
        elementos.append(Paragraph(f"Tendência: {dados['tendencia']}", styles["Normal"]))
        elementos.append(Spacer(1, 8))

    # Gera o arquivo final
    doc.build(elementos)