from collections import defaultdict
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.usuario import Usuario
from models.consumo import Consumo


TIPOS_VALIDOS = {
    "transporte",
    "alimentacao",
    "agua",
    "energia",
    "produtos",
    "outros"
}


def normalizar_tipo(tipo: str) -> str:
    if not tipo:
        return "outros"

    tipo = str(tipo).strip().lower()

    if tipo in TIPOS_VALIDOS:
        return tipo

    return "outros"


def buscar_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return usuario


def _data_limite(janela_meses: int):
    hoje = datetime.now()
    ano = hoje.year - (janela_meses // 12)
    mes = hoje.month - (janela_meses % 12)
    if mes <= 0:
        mes += 12
        ano -= 1
    return datetime(ano, mes, 1)


def buscar_consumos_usuario(db: Session, usuario_id: int, janela_meses: int):
    data_limite = _data_limite(janela_meses)
    consumos = (
        db.query(Consumo)
        .filter(Consumo.usuario_id == usuario_id, Consumo.data >= data_limite)
        .all()
    )

    if not consumos:
        raise HTTPException(
            status_code=404,
            detail="Nenhum consumo encontrado na janela selecionada para este usuário"
        )

    return consumos


def filtrar_ultimos_meses(consumos, quantidade_meses: int):
    meses_disponiveis = sorted(
        {consumo.data.strftime("%Y-%m") for consumo in consumos}
    )

    meses_selecionados = set(meses_disponiveis[-quantidade_meses:])

    consumos_filtrados = [
        consumo for consumo in consumos
        if consumo.data.strftime("%Y-%m") in meses_selecionados
    ]

    return consumos_filtrados, sorted(meses_selecionados)


def agrupar_consumos_por_tipo_e_mes(consumos):
    dados = defaultdict(lambda: defaultdict(float))

    for consumo in consumos:
        mes = consumo.data.strftime("%Y-%m")
        tipo = normalizar_tipo(consumo.tipo)
        dados[tipo][mes] += float(consumo.gasto)

    return dados


def calcular_tendencia(crescimento: float):
    if crescimento > 0.05:
        return "alta"
    elif crescimento < -0.05:
        return "queda"
    return "estavel"


def gerar_projecao_por_tipo(dados_usuario, meses_projetados: int):
    categorias = {}
    total_previsao = 0.0
    houve_tendencia_alta = False
    houve_tendencia_queda = False

    for tipo, meses_dict in dados_usuario.items():
        meses_ordenados = sorted(meses_dict.items(), key=lambda item: item[0])
        valores = [valor for _, valor in meses_ordenados]

        if len(valores) == 1:
            primeiro = valores[0]
            ultimo = valores[0]
            crescimento = 0
        else:
            primeiro = valores[0]
            ultimo = valores[-1]
            crescimento = 0 if primeiro == 0 else (ultimo - primeiro) / primeiro

        tendencia = calcular_tendencia(crescimento)
        crescimento_percentual = round(crescimento * 100, 2)

        if tendencia == "alta":
            houve_tendencia_alta = True
        elif tendencia == "queda":
            houve_tendencia_queda = True

        previsoes = []
        valor_atual = ultimo

        for _ in range(meses_projetados):
            valor_atual = valor_atual * (1 + crescimento)
            previsoes.append(round(valor_atual, 2))

        total_tipo = round(sum(previsoes), 2)
        total_previsao += total_tipo

        categorias[tipo] = {
            "ultimo_mes": round(ultimo, 2),
            "crescimento_percentual": crescimento_percentual,
            "tendencia": tendencia,
            "previsao": previsoes,
            "total_projetado": total_tipo
        }

    return {
        "categorias": categorias,
        "previsao_total": round(total_previsao, 2),
        "houve_tendencia_alta": houve_tendencia_alta,
        "houve_tendencia_queda": houve_tendencia_queda
    }


def calcular_media_mensal_geral(consumos):
    gastos_por_mes = defaultdict(float)

    for consumo in consumos:
        mes = consumo.data.strftime("%Y-%m")
        gastos_por_mes[mes] += float(consumo.gasto)

    valores = list(gastos_por_mes.values())

    if not valores:
        return 0.0

    return sum(valores) / len(valores)


def buscar_consumos_mesma_regiao(db: Session, regiao: str, janela_meses: int):
    data_limite = _data_limite(janela_meses)

    ids_regiao = [
        row[0]
        for row in db.query(Usuario.id).filter(Usuario.regiao == regiao).all()
    ]

    if not ids_regiao:
        return [], 0

    consumos_regiao = (
        db.query(Consumo)
        .filter(Consumo.usuario_id.in_(ids_regiao), Consumo.data >= data_limite)
        .all()
    )

    return consumos_regiao, len(ids_regiao)


def calcular_media_regional(consumos_regiao):
    gastos_por_usuario_mes = defaultdict(lambda: defaultdict(float))

    for consumo in consumos_regiao:
        mes = consumo.data.strftime("%Y-%m")
        gastos_por_usuario_mes[consumo.usuario_id][mes] += float(consumo.gasto)

    medias = []

    for _, meses_dict in gastos_por_usuario_mes.items():
        valores = list(meses_dict.values())
        if valores:
            medias.append(sum(valores) / len(valores))

    if not medias:
        return 0.0

    return sum(medias) / len(medias)


def calcular_media_mensal_por_tipo(consumos):
    gastos_por_tipo_mes = defaultdict(lambda: defaultdict(float))

    for consumo in consumos:
        mes = consumo.data.strftime("%Y-%m")
        tipo = normalizar_tipo(consumo.tipo)
        gastos_por_tipo_mes[tipo][mes] += float(consumo.gasto)

    medias_por_tipo = {}

    for tipo, meses_dict in gastos_por_tipo_mes.items():
        valores = list(meses_dict.values())
        medias_por_tipo[tipo] = sum(valores) / len(valores) if valores else 0.0

    return medias_por_tipo


def calcular_media_regional_por_tipo(consumos_regiao):
    gastos_tipo_usuario_mes = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    for consumo in consumos_regiao:
        mes = consumo.data.strftime("%Y-%m")
        tipo = normalizar_tipo(consumo.tipo)
        gastos_tipo_usuario_mes[tipo][consumo.usuario_id][mes] += float(consumo.gasto)

    medias_regionais_por_tipo = {}

    for tipo, usuarios_dict in gastos_tipo_usuario_mes.items():
        medias_usuarios = []

        for _, meses_dict in usuarios_dict.items():
            valores = list(meses_dict.values())
            if valores:
                medias_usuarios.append(sum(valores) / len(valores))

        medias_regionais_por_tipo[tipo] = (
            sum(medias_usuarios) / len(medias_usuarios)
            if medias_usuarios else 0.0
        )

    return medias_regionais_por_tipo


def montar_comparativo_por_tipo_mensal(consumos_usuario, consumos_regiao):
    media_usuario_por_tipo = calcular_media_mensal_por_tipo(consumos_usuario)
    media_regional_por_tipo = calcular_media_regional_por_tipo(consumos_regiao)

    todos_os_tipos = sorted(TIPOS_VALIDOS | set(media_usuario_por_tipo.keys()) | set(media_regional_por_tipo.keys()))
    comparativo = {}

    for tipo in todos_os_tipos:
        media_usuario = media_usuario_por_tipo.get(tipo, 0.0)
        media_regional = media_regional_por_tipo.get(tipo, 0.0)

        if media_regional == 0:
            situacao = "sem dados suficientes"
        elif media_usuario > media_regional:
            situacao = "acima da média"
        elif media_usuario < media_regional:
            situacao = "abaixo da média"
        else:
            situacao = "igual à média"

        comparativo[tipo] = {
            "media_mensal_usuario": round(media_usuario, 2),
            "media_mensal_regional": round(media_regional, 2),
            "diferenca": round(media_usuario - media_regional, 2),
            "situacao": situacao
        }

    return comparativo


def calcular_situacao_regional(media_usuario: float, media_regional: float):
    if media_regional == 0:
        return "sem dados suficientes na região"
    elif media_usuario > media_regional:
        return "acima da média regional"
    elif media_usuario < media_regional:
        return "abaixo da média regional"
    return "igual à média regional"


def calcular_indice_concentracao(categorias):
    totais = [dados["ultimo_mes"] for dados in categorias.values()]

    if not totais:
        return 0.0

    total = sum(totais)
    if total == 0:
        return 0.0

    return max(totais) / total


def classificar_confianca_amostra(total_usuarios_regiao: int):
    if total_usuarios_regiao <= 2:
        return {
            "nivel": "muito_baixa",
            "mensagem": "A comparação regional foi feita com poucos usuários. Use essa média apenas como referência inicial."
        }
    elif total_usuarios_regiao <= 5:
        return {
            "nivel": "baixa",
            "mensagem": "A comparação regional ainda tem uma base pequena de usuários."
        }
    elif total_usuarios_regiao <= 15:
        return {
            "nivel": "media",
            "mensagem": "A comparação regional já tem uma base razoável."
        }
    return {
        "nivel": "alta",
        "mensagem": "A comparação regional foi feita com uma base mais consistente de usuários."
    }


def calcular_score_justo(
    media_usuario,
    media_regional,
    houve_tendencia_alta,
    houve_tendencia_queda,
    categorias,
    total_usuarios_regiao
):
    score = 50
    motivos = []

    if houve_tendencia_alta:
        score -= 10
        motivos.append("Foi detectada tendência de aumento em pelo menos uma categoria")

    if houve_tendencia_queda:
        score += 5
        motivos.append("Houve queda de gastos em pelo menos uma categoria")

    if media_regional > 0 and total_usuarios_regiao >= 5:
        diferenca_percentual = (media_usuario - media_regional) / media_regional

        if diferenca_percentual > 0.20:
            score -= 15
            motivos.append("Seu gasto médio está muito acima da média da sua região")
        elif diferenca_percentual > 0.05:
            score -= 8
            motivos.append("Seu gasto médio está um pouco acima da média da sua região")
        elif diferenca_percentual < -0.15:
            score += 12
            motivos.append("Seu gasto médio está bem abaixo da média da sua região")
        elif diferenca_percentual < -0.05:
            score += 6
            motivos.append("Seu gasto médio está abaixo da média da sua região")
    elif total_usuarios_regiao > 0:
        motivos.append("A comparação regional foi feita com uma amostra pequena, então teve peso reduzido no score")

    crescimentos_altos = 0
    crescimentos_moderados = 0

    for _, dados_tipo in categorias.items():
        crescimento = dados_tipo["crescimento_percentual"]

        if crescimento > 25:
            crescimentos_altos += 1
        elif crescimento > 10:
            crescimentos_moderados += 1

    if crescimentos_altos > 0:
        score -= 12
        motivos.append("Uma ou mais categorias tiveram crescimento muito alto")
    elif crescimentos_moderados > 0:
        score -= 6
        motivos.append("Algumas categorias apresentaram crescimento moderado")

    indice_concentracao = calcular_indice_concentracao(categorias)

    if indice_concentracao > 0.65:
        score -= 8
        motivos.append("Seus gastos estão muito concentrados em uma única categoria")
    elif indice_concentracao < 0.40 and len(categorias) > 1:
        score += 4
        motivos.append("Seus gastos estão relativamente equilibrados entre as categorias")

    score = max(0, min(score, 100))

    if score >= 85:
        nivel = "Excelente"
    elif score >= 70:
        nivel = "Bom"
    elif score >= 50:
        nivel = "Regular"
    else:
        nivel = "Crítico"

    if not motivos:
        motivos.append("Seu comportamento financeiro está estável dentro da janela analisada")

    return {
        "valor": score,
        "nivel": nivel,
        "motivos": motivos
    }


def gerar_insights_completos(
    db: Session,
    usuario_id: int,
    meses_projetados: int = 3,
    janela_meses: int = 3
):
    usuario = buscar_usuario(db, usuario_id)

    consumos_usuario_filtrados = buscar_consumos_usuario(db, usuario_id, janela_meses)

    consumos_usuario_filtrados, meses_analisados = filtrar_ultimos_meses(
        consumos_usuario_filtrados,
        janela_meses
    )

    if not consumos_usuario_filtrados:
        raise HTTPException(
            status_code=404,
            detail="Não há consumos suficientes na janela analisada"
        )

    dados_usuario = agrupar_consumos_por_tipo_e_mes(consumos_usuario_filtrados)
    resultado_projecao = gerar_projecao_por_tipo(dados_usuario, meses_projetados)

    consumos_regiao, total_usuarios_regiao = buscar_consumos_mesma_regiao(
        db, usuario.regiao, janela_meses
    )

    if consumos_regiao:
        consumos_regiao_filtrados, _ = filtrar_ultimos_meses(consumos_regiao, janela_meses)
    else:
        consumos_regiao_filtrados = []

    media_usuario = calcular_media_mensal_geral(consumos_usuario_filtrados)
    media_regional = calcular_media_regional(consumos_regiao_filtrados)

    comparativo_por_tipo = montar_comparativo_por_tipo_mensal(
        consumos_usuario_filtrados,
        consumos_regiao_filtrados
    )

    situacao_regional = calcular_situacao_regional(media_usuario, media_regional)
    confianca_amostra = classificar_confianca_amostra(total_usuarios_regiao)

    score = calcular_score_justo(
        media_usuario=media_usuario,
        media_regional=media_regional,
        houve_tendencia_alta=resultado_projecao["houve_tendencia_alta"],
        houve_tendencia_queda=resultado_projecao["houve_tendencia_queda"],
        categorias=resultado_projecao["categorias"],
        total_usuarios_regiao=total_usuarios_regiao
    )

    return {
        "usuario_id": usuario_id,
        "regiao": usuario.regiao,
        "janela_meses_analisada": janela_meses,
        "meses_considerados": meses_analisados,
        "meses_projetados": meses_projetados,
        "previsao_total": round(resultado_projecao["previsao_total"], 2),
        "categorias": resultado_projecao["categorias"],
        "comparativo_regional": {
            "media_mensal_usuario": round(media_usuario, 2),
            "media_mensal_regional": round(media_regional, 2),
            "diferenca": round(media_usuario - media_regional, 2),
            "situacao": situacao_regional,
            "total_usuarios_regiao": total_usuarios_regiao,
            "confianca_amostra": confianca_amostra,
            "por_tipo": comparativo_por_tipo
        },
        "score": score
    }