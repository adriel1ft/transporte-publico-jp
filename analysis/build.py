"""Lê os CSVs em data/, calcula os indicadores e gera docs/index.html (autocontido).

Uso:  python3 analysis/build.py   (a partir da raiz do projeto)
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TEMPLATE = ROOT / "analysis" / "template.html"
OUT = ROOT / "docs" / "index.html"

# Hipótese de uso: 2 viagens por dia útil, 22 dias úteis por mês
VIAGENS_MES = 44


def ler(nome):
    with open(DATA / nome, encoding="utf-8") as f:
        return list(csv.DictReader(f))


tarifas = ler("tarifas_jp.csv")
salario = {int(r["ano"]): float(r["salario_minimo"]) for r in ler("salario_minimo.csv")}
linhas = ler("linhas_jp.csv")
pop = {int(r["ano"]): int(r["populacao"]) for r in ler("populacao_jp.csv")}
frota = {r["indicador"]: float(r["valor"]) for r in ler("frota.csv")}
capitais = ler("tarifas_capitais_2026.csv")

# --- Série de tarifa x salário mínimo --------------------------------------
serie_tarifa = []
base = float(tarifas[0]["tarifa"])
base_sm = salario[int(tarifas[0]["ano"])]
for r in tarifas:
    ano, t = int(r["ano"]), float(r["tarifa"])
    sm = salario[ano]
    serie_tarifa.append({
        "ano": ano,
        "tarifa": t,
        "salario_minimo": sm,
        "pct_sm_passagem": round(100 * t / sm, 3),
        "custo_mensal": round(t * VIAGENS_MES, 2),
        "pct_sm_mensal": round(100 * t * VIAGENS_MES / sm, 2),
        "indice_tarifa": round(100 * t / base, 1),
        "indice_sm": round(100 * sm / base_sm, 1),
        "nota": r["mudancas_no_ano"],
        "confianca": r["confianca"],
        "fonte": r["fonte"],
    })

# --- Linhas e linhas por 100 mil habitantes --------------------------------
serie_linhas = []
for r in linhas:
    ano, n = int(r["ano"]), int(r["linhas"])
    p = pop.get(ano)
    serie_linhas.append({
        "ano": ano,
        "linhas": n,
        "populacao": p,
        "linhas_100k": round(n / p * 1e5, 2) if p else None,
    })

# --- Capitais 2026 ----------------------------------------------------------
sm26 = salario[2026]
caps = sorted(
    ({"capital": c["capital"], "uf": c["uf"], "regiao": c["regiao"],
      "tarifa": float(c["tarifa"]), "nota": c["nota"]} for c in capitais),
    key=lambda c: -c["tarifa"],
)
for i, c in enumerate(caps, 1):
    c["rank"] = i
media_cap = sum(c["tarifa"] for c in caps) / len(caps)
ne = [c["tarifa"] for c in caps if c["regiao"] == "Nordeste"]
media_ne = sum(ne) / len(ne)
jp_cap = next(c for c in caps if c["uf"] == "PB")
rank_ne = sorted(ne, reverse=True).index(jp_cap["tarifa"]) + 1

# --- Frota / habitante ------------------------------------------------------
pop_jp = pop[2026]
onibus_mil_jp_cad = frota["frota_cadastrada_jp"] / pop_jp * 1000
onibus_mil_jp_op = frota["frota_operacional_jp"] / pop_jp * 1000
onibus_mil_br = frota["frota_onibus_urbanos_brasil"] / frota["populacao_brasil"] * 1000

atual = serie_tarifa[-1]
resumo = {
    "tarifa_atual": atual["tarifa"],
    "ano_atual": atual["ano"],
    "linhas_atual": serie_linhas[-1]["linhas"],
    "frota_cadastrada": int(frota["frota_cadastrada_jp"]),
    "frota_operacional": int(frota["frota_operacional_jp"]),
    "idade_media_frota": frota["idade_media_frota_jp_anos"],
    "passageiros_mes": int(frota["passageiros_mes_jp"]),
    "onibus_novos_2025": int(frota["onibus_novos_2025_jp"]),
    "populacao_jp": pop_jp,
    "viagens_mes": VIAGENS_MES,
    "pct_sm_mensal": atual["pct_sm_mensal"],
    "custo_mensal": atual["custo_mensal"],
    "media_capitais": round(media_cap, 2),
    "media_nordeste": round(media_ne, 2),
    "pct_sm_mensal_media_capitais": round(100 * media_cap * VIAGENS_MES / sm26, 2),
    "rank_jp_capitais": jp_cap["rank"],
    "rank_jp_nordeste": rank_ne,
    "n_capitais": len(caps),
    "onibus_mil_jp_cadastrada": round(onibus_mil_jp_cad, 3),
    "onibus_mil_jp_operacional": round(onibus_mil_jp_op, 3),
    "onibus_mil_brasil": round(onibus_mil_br, 3),
    "hab_por_onibus_jp": round(pop_jp / frota["frota_cadastrada_jp"]),
    "hab_por_onibus_brasil": round(frota["populacao_brasil"] / frota["frota_onibus_urbanos_brasil"]),
    "var_tarifa_pct": round(100 * (atual["tarifa"] / base - 1), 1),
    "var_sm_pct": round(100 * (atual["salario_minimo"] / base_sm - 1), 1),
    "ano_base": serie_tarifa[0]["ano"],
    "var_linhas_pct": round(100 * (serie_linhas[-1]["linhas"] / serie_linhas[0]["linhas"] - 1), 1),
}

payload = {"resumo": resumo, "tarifas": serie_tarifa, "linhas": serie_linhas, "capitais": caps}
dados_js = "window.DADOS = " + json.dumps(payload, ensure_ascii=False) + ";"
OUT.write_text(TEMPLATE.read_text(encoding="utf-8").replace("/*__DADOS__*/", dados_js), encoding="utf-8")
print(json.dumps(resumo, ensure_ascii=False, indent=1))
