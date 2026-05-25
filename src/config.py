# src/config.py

BENNER_COLUMNS = {
    "process_number": "Numerodistribuicao",
    "case_id": "Handle",
    "valor_ajuizado": "Valorajuizado",
    "estimativa_perda": "Estimativa_De_Perda",
    "passivel_acordo": "Passiveldeacordo",
    "processo_relevante": "Processorelevante",
    "carteira": "Carteira",
    "produto": "Nm_Produto",
    "fase": "Fasedoprocesso",
    "escritorio": "Escritorio",
    "advogado": "Advogado",
}

DEEPLEGAL_PROCESSOS_COLUMNS = {
    "process_number": "numero_processo",
    "status": "status_texto",
    "fase_processual": "fase_processual_texto",
    "resultado_final": "resultado_final_processo_text",
    "sentenca_tipo": "sentenca_tipo",
    "condenacao_valor": "condenacao_valor",
    "valor_acordo": "valor_do_acordo_valor",
    "orgao_julgador": "orgao_julgador",
    "vara": "vara",
    "cidade": "cidade",
    "uf": "uf",
    "comarca": "comarca",
}

DEEPLEGAL_EVENTOS_COLUMNS = {
    "process_number": "numero_processo",
    "event_type": "tipo_evento",
    "event_text": "texto_evento",
    "event_date": "data_evento",
}

GRAPH_FEATURES = [
    "produto",
    "carteira",
    "fase",
    "estimativa_perda",
    "passivel_acordo",
    "processo_relevante",
    "escritorio",
    "advogado",
    "status",
    "fase_processual",
    "orgao_julgador",
    "vara",
    "cidade",
    "uf",
    "comarca",
]

SIMILARITY_FEATURES = [
    "produto",
    "carteira",
    "fase",
    "estimativa_perda",
    "escritorio",
    "status",
    "fase_processual",
    "vara",
    "cidade",
    "uf",
    "comarca",
]