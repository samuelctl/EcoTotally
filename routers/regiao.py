import requests 
import unicodedata
from urllib.parse import quote

def remover_acentos(texto): # remove os acentos dos estados para nao ter erro no get da api do ibge, onde salva os estados sem acento
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto)#aqui ele percorre a palavra toda(texto)(unicodedata separa o caracter da acentuação, ex:á -> a,´) e o join junta a palavra toda denovo
                    if unicodedata.category(c) != "Mn")#aqui acontece a remoção dos acentos

def get_regiao_por_cidade(cidade):
    busca_limpa = quote(remover_acentos(cidade))# quote tranforam o input em formato de url Sao paulo -> Sao%20Paulo, Urls nao podem ter espacos 
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/municipios?nome={busca_limpa}"

    try:
        response = requests.get(url,timeout=10)# timeout siginifica que se o request demorar mais de 10s ele cancela 
        municipios = response.json()# converte para json
        if not municipios: return None

        selecionado = None
        for m in municipios: # podemos encontrar varias cidades com nomes parecidos, aqui percorre todas
            if remover_acentos(m['nome']).lower() == remover_acentos(cidade).lower(): #padronizando para nao ter erro, SAO PAULO,Sao Paulo = sao paulo
                selecionado = m # se achar, aqui para o loop de procurar 
                break
        if not selecionado:selecionado = municipios[0] #senao encontrar, pega a primeira da api, index[0]
        
        return {
            "cidade" : selecionado.get('nome'),
            "regiao":selecionado['microrregiao']['mesorregiao']['UF']['regiao']['nome']
        }
    except requests.RequestException:
        return None