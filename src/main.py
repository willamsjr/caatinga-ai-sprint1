import csv
import sys
from pathlib import Path

from gerador_pomar import gerar_pomar
from buscas import bfs, dfs, ucs, a_estrela


def salvar_pomar(pomar, caminho):
    with open(caminho, "w", encoding="utf-8") as arquivo:
        for linha in pomar:
            arquivo.write(" ".join(linha) + "\n")


def salvar_resultados(resultados, caminho):
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        campos = [
            "estrategia",
            "custo",
            "passos",
            "nos_expandidos",
            "fronteira_max",
        ]

        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()

        for estrategia, resultado in resultados.items():
            escritor.writerow({
                "estrategia": estrategia,
                "custo": resultado["custo"],
                "passos": resultado["passos"],
                "nos_expandidos": resultado["nos_expandidos"],
                "fronteira_max": resultado["fronteira_max"],
            })


def gerar_grafico(resultados, caminho):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print(
            "ERRO: matplotlib nao esta instalado. "
            "Execute: pip install matplotlib"
        )
        sys.exit(1)

    estrategias = list(resultados.keys())
    expandidos = [
        resultados[nome]["nos_expandidos"]
        for nome in estrategias
    ]

    plt.figure(figsize=(8, 5))
    plt.bar(estrategias, expandidos)
    plt.xlabel("Estrategia")
    plt.ylabel("Nos expandidos")
    plt.title("Comparacao de nos expandidos")
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()


def main():
    if len(sys.argv) != 2:
        print("Uso: python src/main.py <matricula>")
        sys.exit(1)

    try:
        matricula = int(sys.argv[1])
    except ValueError:
        print("ERRO: a matricula deve conter apenas numeros.")
        sys.exit(1)

    print(f"Matricula: {matricula}")
    print("Gerando pomar...")

    pomar = gerar_pomar(matricula)

    print("Executando buscas...")

    resultados = {
        "BFS": bfs(pomar),
        "DFS": dfs(pomar),
        "UCS": ucs(pomar),
        "A*_h1": a_estrela(pomar, "h1"),
        "A*_h2": a_estrela(pomar, "h2"),
        "A*_h3": a_estrela(pomar, "h3"),
    }

    pasta_resultados = Path("resultados")
    pasta_resultados.mkdir(exist_ok=True)

    salvar_pomar(
        pomar,
        pasta_resultados / "pomar.txt"
    )

    salvar_resultados(
        resultados,
        pasta_resultados / "resultados.csv"
    )

    gerar_grafico(
        resultados,
        pasta_resultados / "grafico.png"
    )

    print()
    print("=== RESULTADOS ===")

    for estrategia, resultado in resultados.items():
        print(
            f"{estrategia}: "
            f"custo={resultado['custo']}, "
            f"passos={resultado['passos']}, "
            f"expandidos={resultado['nos_expandidos']}, "
            f"fronteira={resultado['fronteira_max']}"
        )

    print()
    print("Arquivos gerados:")
    print("resultados/resultados.csv")
    print("resultados/grafico.png")
    print("resultados/pomar.txt")


if __name__ == "__main__":
    main()