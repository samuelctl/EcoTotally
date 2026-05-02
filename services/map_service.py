import requests
from fastapi import HTTPException

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter"
]

def buscar_pontos(lat: float, lon: float):

    query = f"""
    [out:json][timeout:25];
    node["amenity"="recycling"](around:5000,{lat},{lon});
    out body;
    """

    headers = {
        "Content-Type": "text/plain"
    }

    response = None

    # 🔥 tenta vários servidores até um funcionar
    for url in OVERPASS_URLS:
        try:
            response = requests.post(
                url,
                data=query.strip(),
                headers=headers,
                timeout=30,
            )

            if response.status_code == 200:
                break  # funcionou, sai do loop

        except requests.RequestException:
            continue

    # se nenhum servidor funcionou
    if not response or response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Falha ao consultar Overpass (todos os servidores estão indisponíveis)"
        )

    try:
        data = response.json()
    except Exception:
        raise HTTPException(
            status_code=502,
            detail=f"Resposta inválida do Overpass: {response.text[:200]}"
        )

    pontos_formatados = []

    for item in data.get("elements", []):
        tags = item.get("tags", {})

        tipos = []

        if tags.get("recycling:glass") == "yes":
            tipos.append("vidro")
        if tags.get("recycling:paper") == "yes":
            tipos.append("papel")
        if tags.get("recycling:plastic") == "yes":
            tipos.append("plástico")
        if tags.get("recycling:electronics") == "yes":
            tipos.append("eletrônicos")

        pontos_formatados.append({
            "nome": tags.get("name", "Ponto de Reciclagem"),
            "latitude": item.get("lat"),
            "longitude": item.get("lon"),
            "tipos": tipos or ["reciclagem geral"]
        })

    return pontos_formatados