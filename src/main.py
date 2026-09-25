
"""Execução principal do Caatinga.AI."""

import csv
import sys
import time
from pathlib import Path

from gerador_pomar import gerar_pomar
from buscas import bfs, dfs, ucs, a_estrela


RAIZ = Path(__file__).resolve().parents[1]
PASTA_RESULTADOS = RAIZ / "resultados"


def salvar_pomar(matricula, pomar):
    caminho = PASTA_RESULTADOS / "pomar.txt"

    with caminho.open("w", encoding="utf-8") as arquivo:
        arquivo.write(f"Matricula-semente: {matricula}\n")

        for linha in pomar:
            arquivo.write(" ".join(linha) + "\n")


def salvar_resultados(resultados):
    caminho = PASTA_RESULTADOS / "resultados.csv"

    campos = [
        "estrategia",
        "heuristica",
        "custo",
        "passos",
        "nos_expandidos",
        "fronteira_max",
        "tempo_ms",
    ]

    with caminho.open(
        "w", newline="", encoding="utf-8"
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=campos
        )

        escritor.writeheader()
        escritor.writerows(resultados)


def gerar_grafico(resultados):
    import matplotlib.pyplot as plt

    nomes = [
        linha["estrategia"]
        + (
            f" ({linha['heuristica']})"
            if linha["heuristica"]
            else ""
        )
        for linha in resultados
    ]

    expandidos = [
        linha["nos_expandidos"]
        for linha in resultados
    ]

    plt.figure(figsize=(10, 5))
    plt.bar(nomes, expandidos)
    plt.xlabel("Estratégia de busca")
    plt.ylabel("Nós expandidos")
    plt.title("Caatinga.AI — Nós expandidos por estratégia")
    plt.xticks(rotation=20)
    plt.tight_layout()

    plt.savefig(PASTA_RESULTADOS / "grafico.png")
    plt.close()


def executar_busca(nome, heuristica, funcao):
    inicio = time.perf_counter()
    resultado = funcao()
    tempo_ms = (time.perf_counter() - inicio) * 1000

    linha = {
        "estrategia": nome,
        "heuristica": heuristica,
        "custo": resultado["custo"],
        "passos": resultado["passos"],
        "nos_expandidos": resultado["nos_expandidos"],
        "fronteira_max": resultado["fronteira_max"],
        "tempo_ms": round(tempo_ms, 4),
    }

    return linha


def main():
    if len(sys.argv) != 2:
        print("Uso: python src/main.py <matricula>")
        sys.exit(1)

    try:
        matricula = int(sys.argv[1])
    except ValueError:
        print("ERRO: informe uma matrícula numérica.")
        sys.exit(1)

    pomar = gerar_pomar(matricula)
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    resultados = [
        executar_busca("BFS", "", lambda: bfs(pomar)),
        executar_busca("DFS", "", lambda: dfs(pomar)),
        executar_busca("UCS", "", lambda: ucs(pomar)),
        executar_busca(
            "A*", "h1", lambda: a_estrela(pomar, "h1")
        ),
        executar_busca(
            "A*", "h2", lambda: a_estrela(pomar, "h2")
        ),
        executar_busca(
            "A*", "h3", lambda: a_estrela(pomar, "h3")
        ),
    ]

    salvar_pomar(matricula, pomar)
    salvar_resultados(resultados)
    gerar_grafico(resultados)

    print(f"Matricula-semente: {matricula}")
    print("\n=== RESULTADOS ===")

    for linha in resultados:
        nome = linha["estrategia"]
        if linha["heuristica"]:
            nome += f" {linha['heuristica']}"

        print(
            f"{nome}: custo={linha['custo']}, "
            f"passos={linha['passos']}, "
            f"expandidos={linha['nos_expandidos']}, "
            f"fronteira={linha['fronteira_max']}, "
            f"tempo={linha['tempo_ms']:.4f} ms"
        )

    print("\nArquivos gerados em resultados/:")
    print("resultados.csv")
    print("grafico.png")
    print("pomar.txt")


if __name__ == "__main__":
    main()
