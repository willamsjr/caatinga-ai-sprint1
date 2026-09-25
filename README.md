
# Caatinga.AI — Sprint 1

## 1. Identificação

**Disciplina:** Inteligência Artificial — UniRios, 2026.2  
**Professor:** Ronierison Maciel

**Integrantes:**
- Willams Junior — Matrícula: 241.14.025
- Igor Rodrigues — Matrícula: 241.14.019

**Matrícula-semente:** `24114019` (integrante mais velho da dupla).

## 2. Sobre o projeto

O Caatinga.AI simula um agente que percorre um pomar de manga para apoiar a inspeção de pragas. O projeto compara estratégias de busca de rotas (BFS, DFS, UCS e A*), implementa busca local para selecionar talhões de inspeção e utiliza regras e o teorema de Bayes para apoiar decisões sobre alertas do sensor.

## 3. Como executar

**Requisitos:** Python 3 e as dependências listadas em `requirements.txt`.

Na raiz do projeto, execute:

```bash
pip install -r requirements.txt
python src/main.py 24114019
```

O programa deve gerar os arquivos `resultados/resultados.csv`, `resultados/grafico.png` e `resultados/pomar.txt`.

Para testar com outra matrícula, substitua `24114019` no comando.

## 4. Resumo dos resultados

Resultados obtidos com a matrícula-semente `24114019` no pomar 12 × 12:

| Estratégia | Heurística | Custo da rota | Passos | Nós expandidos | Fronteira máxima |
|---|---|---:|---:|---:|---:|
| BFS | — | 52 | 22 | 123 | 12 |
| DFS | — | 109 | 46 | 91 | 44 |
| UCS | — | 37 | 22 | 123 | 18 |
| A* | h1 = 0 | 37 | 22 | 123 | 18 |
| A* | h2 = Manhattan | 37 | 22 | 114 | 24 |
| A* | h3 = 4 × Manhattan | 42 | 24 | 26 | 28 |

## 5. Ordem dos vizinhos e reabertura de estados

**Ordem de expansão dos vizinhos:** Norte, Sul, Oeste e Leste.

Na DFS, os vizinhos são empilhados na ordem inversa para preservar essa ordem de exploração.

A implementação do A* permite reabrir um estado quando encontra um caminho de custo menor.

## 6. Estrutura do repositório

- [`README.md`](README.md): identificação, instruções de execução e resumo dos resultados.
- [`RELATORIO.md`](RELATORIO.md): respostas das partes teóricas e análise dos experimentos.
- [`ANEXO_IA.md`](ANEXO_IA.md): registro do uso de assistentes de IA.
- [`requirements.txt`](requirements.txt): dependências do projeto.
- [`src/gerador_pomar.py`](src/gerador_pomar.py): geração do pomar e dos parâmetros do sensor.
- [`src/buscas.py`](src/buscas.py): BFS, DFS, UCS e A*.
- [`src/busca_local.py`](src/busca_local.py): subida de encosta e têmpera simulada.
- [`src/especialista.py`](src/especialista.py): base de regras e encadeamento para trás.
- [`src/bayes.py`](src/bayes.py): cálculos de probabilidade da Parte 4.3.
- [`src/main.py`](src/main.py): execução principal e geração dos arquivos de resultados.
- [`resultados/resultados.csv`](resultados/resultados.csv): indicadores das estratégias de busca.
- [`resultados/grafico.png`](resultados/grafico.png): gráfico de nós expandidos por estratégia.
- [`resultados/pomar.txt`](resultados/pomar.txt): grade do pomar.

## 7. Limitações conhecidas

- A busca local utiliza prioridades simuladas e uma função de cobertura definida pela dupla. Ela não calcula a rota entre os 15 talhões nem comprova que as inspeções cabem em seis horas de bateria.
- Na questão 2.4, o UCS foi interrompido preventivamente em um pomar 2800 × 2800 após ultrapassar o limite experimental de 1,50 GiB de memória. Não foi observado estouro natural de memória, estouro de pilha ou tempo de execução comprovadamente superior a 60 segundos.
