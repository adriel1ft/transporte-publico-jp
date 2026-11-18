# Transporte público em João Pessoa — análise de dados

Site-report sobre a frota, as linhas e a tarifa dos ônibus de João Pessoa, com a série histórica da passagem, o peso dela no salário mínimo, ônibus por habitante e a comparação com as capitais e com o Brasil.

## Estrutura

```
data/                       dados brutos (CSV, com a fonte em cada linha)
  tarifas_jp.csv            tarifa por ano, 2013–2026
  salario_minimo.csv        salário mínimo nacional, 2013–2026
  linhas_jp.csv             número de linhas, 2016–2025
  populacao_jp.csv          população (IBGE)
  frota.csv                 frota de JP e do Brasil, população do Brasil
  tarifas_capitais_2026.csv tarifa das 27 capitais (jan/2026)
analysis/
  build.py                  calcula os indicadores e gera o site
  template.html             layout do site (os dados são inseridos no build)
docs/index.html             relatório gerado (arquivo único, abre direto no navegador)
```

## Como atualizar

1. Edite os CSVs em `data/`.
2. Rode:

```bash
python3 analysis/build.py
```

3. Abra `docs/index.html`.

## Pendências de dados

- **Série da frota:** não encontrei uma série anual aberta. Para obtê-la, faça um pedido pela LAI à Semob-JP.
- **População de 2016 a 2021:** confira as estimativas no SIDRA/IBGE (tabela 6579).
- **Tarifas das capitais:** os valores vêm de levantamentos de imprensa de jan/2026.
