import csv
from pathlib import Path

rows = [
    ["Mudança de entrada", "delta_entrada_abs", "entrada_atual - entrada_anterior", "Mede quanto o cliente mudou a entrada em relação à simulação anterior", "Alta"],
    ["Mudança de entrada", "delta_entrada_pct", "(entrada_atual - entrada_anterior) / entrada_anterior", "Mede a intensidade relativa da mudança de entrada", "Alta"],
    ["Mudança de entrada", "flag_aumentou_entrada", "1 se entrada_atual > entrada_anterior", "Cliente aumentou capital próprio na operação", "Alta"],
    ["Mudança de entrada", "flag_reduziu_entrada", "1 se entrada_atual < entrada_anterior", "Cliente reduziu desembolso inicial", "Alta"],
    ["Mudança de entrada", "flag_mudou_entrada", "1 se entrada_atual != entrada_anterior", "Houve ajuste real na condição", "Alta"],
    ["Tendência de entrada", "slope_entrada_ultimas_5", "Inclinação da regressão linear da entrada nas últimas 5 simulações", "Entrada está subindo, caindo ou estável", "Alta"],
    ["Tendência de entrada", "qtd_aumentos_entrada_7d", "Soma de flag_aumentou_entrada nos últimos 7 dias", "Frequência de movimentos para maior entrada", "Alta"],
    ["Tendência de entrada", "qtd_reducoes_entrada_7d", "Soma de flag_reduziu_entrada nos últimos 7 dias", "Frequência de movimentos para menor entrada", "Alta"],
    ["Tendência de entrada", "ratio_aumentos_entrada_7d", "qtd_aumentos_entrada_7d / qtd_simulacoes_7d", "Proporção da jornada em que cliente aumenta entrada", "Alta"],
    ["Tendência de entrada", "ratio_reducoes_entrada_7d", "qtd_reducoes_entrada_7d / qtd_simulacoes_7d", "Proporção da jornada em que cliente reduz entrada", "Alta"],
    ["Exploração de entrada", "qtd_valores_distintos_entrada_7d", "nunique(entrada) nos últimos 7 dias", "Mede se cliente testou entradas diferentes", "Alta"],
    ["Exploração de entrada", "amplitude_entrada_7d", "max(entrada) - min(entrada) nos últimos 7 dias", "Mede distância máxima percorrida na entrada", "Alta"],
    ["Exploração de entrada", "std_entrada_7d", "Desvio padrão da entrada nos últimos 7 dias", "Mede volatilidade da entrada", "Média"],
    ["Exploração de entrada", "coef_var_entrada_7d", "std_entrada_7d / media_entrada_7d", "Volatilidade relativa da entrada", "Média"],
    ["Convergência", "flag_convergencia_entrada_ultimas_6", "1 se os deltas recentes estão diminuindo", "Cliente está refinando a proposta e convergindo para uma condição", "Alta"],
    ["Convergência", "delta_abs_medio_entrada_primeira_metade", "Média dos deltas absolutos na primeira metade da janela", "Usado para comparar com a fase recente", "Média"],
    ["Convergência", "delta_abs_medio_entrada_segunda_metade", "Média dos deltas absolutos na segunda metade da janela", "Se menor que a primeira metade, indica convergência", "Média"],
    ["Oscilação", "qtd_inversoes_tendencia_entrada_ultimas_5", "Conta mudanças de direção: sobe -> cai -> sobe", "Cliente está indeciso ou testando cenários muito diferentes", "Alta"],
    ["Distância desde início", "delta_entrada_desde_inicio_jornada", "entrada_atual - entrada_primeira_simulacao", "Quanto o cliente cedeu desde o começo da jornada", "Alta"],
    ["Distância desde início", "delta_pct_entrada_desde_inicio_jornada", "delta_entrada_desde_inicio / entrada_primeira", "Intensidade relativa da mudança desde o início", "Alta"],
    ["Distância desde início", "flag_entrada_maior_que_inicio", "1 se entrada_atual > entrada_primeira", "Cliente aumentou capital próprio ao longo da jornada", "Alta"],
    ["Distância desde início", "flag_entrada_menor_que_inicio", "1 se entrada_atual < entrada_primeira", "Cliente reduziu capital próprio ao longo da jornada", "Média"],
    ["LTV", "delta_ltv_abs", "ltv_atual - ltv_anterior", "Mede se a operação ficou mais ou menos alavancada", "Alta"],
    ["LTV", "delta_ltv_desde_inicio", "ltv_atual - ltv_primeira_simulacao", "Mede trajetória de alavancagem desde o início", "Alta"],
    ["LTV", "flag_ltv_reduziu", "1 se ltv_atual < ltv_anterior", "Cliente migrou para operação mais financiável", "Alta"],
    ["LTV", "flag_ltv_aumentou", "1 se ltv_atual > ltv_anterior", "Cliente aumentou alavancagem da operação", "Média"],
    ["LTV", "slope_ltv_ultimas_5", "Inclinação do LTV nas últimas 5 simulações", "Tendência de melhora ou piora da estrutura da operação", "Alta"],
    ["Valor financiado", "delta_valor_financiado_abs", "valor_financiado_atual - valor_financiado_anterior", "Mede mudança no volume financiado", "Alta"],
    ["Valor financiado", "delta_valor_financiado_pct", "delta_valor_financiado / valor_financiado_anterior", "Mede intensidade relativa da mudança", "Média"],
    ["Valor financiado", "flag_valor_financiado_reduziu", "1 se valor financiado caiu", "Cliente reduziu exposição financiada", "Alta"],
    ["Valor financiado", "slope_valor_financiado_ultimas_5", "Inclinação do valor financiado nas últimas simulações", "Direção da exposição financiada", "Média"],
    ["Parcela", "delta_parcela_abs", "parcela_atual - parcela_anterior", "Mede se o cliente está buscando reduzir ou aceitar parcela maior", "Alta"],
    ["Parcela", "delta_parcela_pct", "delta_parcela / parcela_anterior", "Intensidade relativa da mudança de parcela", "Alta"],
    ["Parcela", "flag_parcela_reduziu", "1 se parcela_atual < parcela_anterior", "Cliente buscou condição mensal mais leve", "Alta"],
    ["Parcela", "flag_parcela_aumentou", "1 se parcela_atual > parcela_anterior", "Cliente tolerou parcela maior", "Alta"],
    ["Parcela", "slope_parcela_ultimas_5", "Inclinação da parcela nas últimas simulações", "Tendência de aceitação ou restrição mensal", "Alta"],
    ["Taxa", "delta_taxa_abs", "taxa_atual - taxa_anterior", "Mede mudança da taxa observada", "Alta"],
    ["Taxa", "flag_taxa_aumentou", "1 se taxa_atual > taxa_anterior", "Cliente foi exposto a taxa maior", "Alta"],
    ["Taxa", "flag_taxa_reduziu", "1 se taxa_atual < taxa_anterior", "Cliente recebeu condição melhor", "Média"],
    ["Taxa", "flag_continuou_apos_aumento_taxa", "1 se houve simulação posterior após aumento da taxa", "Sinal de baixa elasticidade / maior disposição", "Muito alta"],
    ["Taxa", "maior_taxa_observada_na_jornada", "max(taxa) até a simulação atual", "Maior taxa que o cliente continuou considerando", "Alta"],
    ["Taxa", "delta_taxa_desde_inicio", "taxa_atual - taxa_primeira", "Quanto a taxa mudou desde o início", "Média"],
    ["Elasticidade proxy", "qtd_avancos_com_taxa_maior", "Conta vezes em que taxa subiu e cliente continuou simulando/avançando", "Proxy de tolerância a preço", "Muito alta"],
    ["Elasticidade proxy", "ratio_avancos_com_taxa_maior", "qtd_avancos_com_taxa_maior / qtd_mudancas_taxa", "Proporção de movimentos aceitos com taxa maior", "Alta"],
    ["Elasticidade proxy", "taxa_maxima_com_avanco", "Maior taxa após a qual cliente continuou a jornada", "Sinal de disposição máxima observada", "Muito alta"],
    ["Prazo", "delta_prazo_abs", "prazo_atual - prazo_anterior", "Cliente alongou ou encurtou financiamento", "Média"],
    ["Prazo", "flag_prazo_aumentou", "1 se prazo aumentou", "Cliente buscou reduzir parcela via prazo", "Média"],
    ["Prazo", "flag_prazo_reduziu", "1 se prazo reduziu", "Cliente aceitou prazo menor", "Média"],
    ["Prazo", "slope_prazo_ultimas_5", "Inclinação do prazo nas últimas simulações", "Tendência de alongamento ou encurtamento", "Média"],
    ["Veículo", "delta_idade_veiculo", "idade_veiculo_atual - idade_veiculo_anterior", "Cliente migrou para veículo mais novo ou velho", "Alta"],
    ["Veículo", "flag_veiculo_mais_novo", "1 se idade_veiculo_atual < idade_anterior", "Cliente migrou para operação mais financiável", "Alta"],
    ["Veículo", "flag_veiculo_mais_velho", "1 se idade_veiculo_atual > idade_anterior", "Cliente migrou para operação potencialmente mais arriscada", "Média"],
    ["Veículo", "qtd_mudancas_veiculo_7d", "Conta mudanças de veículo nos últimos 7 dias", "Cliente está explorando alternativas de ativo", "Média"],
    ["Retorno lojista", "delta_retorno_lojista", "retorno_atual - retorno_anterior", "Mudança na economia do parceiro/lojista", "Alta"],
    ["Retorno lojista", "slope_retorno_lojista_ultimas_5", "Inclinação do retorno nas últimas simulações", "Tendência de alteração na margem/repasse", "Média"],
    ["Retorno lojista", "flag_retorno_lojista_aumentou", "1 se retorno aumentou", "Operação pode ter ficado mais cara/econômica para a financeira", "Média"],
    ["Jornada geral", "distancia_total_percorrida_jornada", "Soma normalizada dos deltas de entrada, LTV, valor financiado, prazo, taxa etc.", "Mede quanto o cliente se moveu no espaço de condições", "Muito alta"],
    ["Jornada geral", "distancia_media_por_simulacao", "distancia_total / qtd_simulacoes", "Mede intensidade média de ajuste por simulação", "Alta"],
    ["Jornada geral", "qtd_variaveis_alteradas_ultima_simulacao", "Conta quantas condições mudaram vs. simulação anterior", "Mede se a mudança foi pontual ou ampla", "Alta"],
    ["Jornada geral", "qtd_variaveis_alteradas_7d", "Soma de variáveis alteradas nos últimos 7 dias", "Mede exploração econômica recente", "Alta"],
    ["Jornada geral", "flag_operacao_mais_financiavel", "1 se entrada ↑, LTV ↓, valor financiado ↓ ou veículo mais novo", "Cliente migrou para uma proposta mais aprovável/viável", "Muito alta"],
    ["Jornada geral", "score_direcao_financiabilidade", "Score combinando entrada ↑, LTV ↓, veículo mais novo, valor financiado ↓", "Resume direção econômica da jornada", "Muito alta"],
    ["Jornada geral", "flag_jornada_sem_mudanca_economica", "1 se várias simulações sem mudar entrada/LTV/valor/prazo/taxa", "Muitas simulações sem mudança real; pode indicar fricção", "Alta"],
    ["Jornada geral", "ratio_simulacoes_com_mudanca_economica", "qtd_simulacoes_com_alguma_mudanca / qtd_simulacoes", "Qualidade econômica da exploração", "Muito alta"],
]

headers = ["familia", "feature", "como_calcular", "interpretacao_negocio", "prioridade"]

out_path = Path("/mnt/data/features_tendencia_jornada_pricing.csv")

with out_path.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(headers)
    writer.writerows(rows)

print(f"CSV criado em: {out_path}")
print(f"Linhas exportadas: {len(rows)}")
