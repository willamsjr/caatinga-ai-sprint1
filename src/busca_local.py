
"""Caatinga.AI — Parte 3.4: busca local para escolher 15 talhões."""

import math
import random
import statistics

from gerador_pomar import BLOQUEADO, gerar_pomar


MATRICULA = 24114019
K = 15
EXECUCOES = 30

# Hipóteses de modelagem, não dados medidos no pomar:
PESO_PRIORIDADE = 1
PESO_COBERTURA = 12

# Parâmetros experimentais da têmpera simulada:
TEMPERATURA_INICIAL = 35.0
RESFRIAMENTO = 0.997
ITERACOES_TEMPERA = 2500


def preparar_problema(pomar, matricula):
    """Cria os talhões candidatos, prioridades e áreas cobertas."""

    livres = [
        (i, j)
        for i, linha in enumerate(pomar)
        for j, terreno in enumerate(linha)
        if terreno != BLOQUEADO
    ]

    if len(livres) < K:
        raise ValueError("O pomar possui menos de 15 talhões livres.")

    rng = random.Random(matricula + 12345)

    # Prioridades SIMULADAS de 1 a 100.
    prioridades = {
        talhao: rng.randint(1, 100)
        for talhao in livres
    }

    # Um talhão selecionado cobre sua própria posição e
    # talhões livres imediatamente ao norte, sul, oeste e leste.
    conjunto_livres = set(livres)
    cobertura = {}

    for i, j in livres:
        area = {
            (i, j),
            (i - 1, j),
            (i + 1, j),
            (i, j - 1),
            (i, j + 1),
        }

        cobertura[(i, j)] = area & conjunto_livres

    return livres, prioridades, cobertura


def avaliar(estado, prioridades, cobertura):
    """
    Maximiza prioridade + cobertura sem contar a mesma
    área duas vezes.

    A pontuação depende da COMBINAÇÃO dos 15 talhões.
    """

    prioridade_total = sum(
        prioridades[talhao]
        for talhao in estado
    )

    area_coberta = set()

    for talhao in estado:
        area_coberta.update(cobertura[talhao])

    return (
        PESO_PRIORIDADE * prioridade_total
        + PESO_COBERTURA * len(area_coberta)
    )


def criar_estado_inicial(livres, rng):
    """Seleciona exatamente 15 talhões livres e distintos."""

    return frozenset(rng.sample(livres, K))


def trocar_talhao(estado, retirar, adicionar):
    """Produz um vizinho substituindo um talhão por outro."""

    return frozenset(
        (estado - {retirar}) | {adicionar}
    )


def subida_de_encosta(
    livres,
    prioridades,
    cobertura,
    estado_inicial,
):
    """Examina todas as trocas e escolhe a melhor melhoria."""

    atual = estado_inicial
    valor_atual = avaliar(atual, prioridades, cobertura)

    while True:
        melhor_estado = None
        melhor_valor = valor_atual

        fora = [
            talhao
            for talhao in livres
            if talhao not in atual
        ]

        for retirar in sorted(atual):
            for adicionar in fora:
                vizinho = trocar_talhao(
                    atual,
                    retirar,
                    adicionar,
                )

                valor = avaliar(
                    vizinho,
                    prioridades,
                    cobertura,
                )

                if valor > melhor_valor:
                    melhor_estado = vizinho
                    melhor_valor = valor

        # Parada em um ótimo local para esta vizinhança:
        # nenhuma troca individual melhora o valor.
        if melhor_estado is None:
            return {
                "estado": atual,
                "valor": valor_atual,
            }

        atual = melhor_estado
        valor_atual = melhor_valor


def tempera_simulada(
    livres,
    prioridades,
    cobertura,
    estado_inicial,
    rng,
):
    """Aceita melhorias e, às vezes, aceita pioras."""

    atual = estado_inicial
    valor_atual = avaliar(atual, prioridades, cobertura)

    melhor_estado = atual
    melhor_valor = valor_atual

    temperatura = TEMPERATURA_INICIAL
    pioras_aceitas = 0

    # Registra uma sequência observável:
    # aceitou piora e posteriormente superou o melhor
    # valor que havia encontrado antes dessa piora.
    piora_desde_recorde = False
    exemplo_superacao = None

    for iteracao in range(1, ITERACOES_TEMPERA + 1):
        retirar = rng.choice(tuple(sorted(atual)))

        fora = [
            talhao
            for talhao in livres
            if talhao not in atual
        ]

        adicionar = rng.choice(fora)

        vizinho = trocar_talhao(
            atual,
            retirar,
            adicionar,
        )

        valor_vizinho = avaliar(
            vizinho,
            prioridades,
            cobertura,
        )

        diferenca = valor_vizinho - valor_atual

        aceitar = (
            diferenca >= 0
            or rng.random() < math.exp(
                diferenca / temperatura
            )
        )

        if aceitar:
            if diferenca < 0:
                pioras_aceitas += 1
                piora_desde_recorde = True

            atual = vizinho
            valor_atual = valor_vizinho

            if valor_atual > melhor_valor:
                valor_anterior = melhor_valor

                melhor_estado = atual
                melhor_valor = valor_atual

                if (
                    piora_desde_recorde
                    and exemplo_superacao is None
                ):
                    exemplo_superacao = {
                        "iteracao": iteracao,
                        "melhor_anterior": valor_anterior,
                        "novo_melhor": melhor_valor,
                    }

                piora_desde_recorde = False

        temperatura *= RESFRIAMENTO

    return {
        "estado": melhor_estado,
        "valor": melhor_valor,
        "pioras_aceitas": pioras_aceitas,
        "exemplo_superacao": exemplo_superacao,
    }


def executar_experimentos(pomar, matricula):
    livres, prioridades, cobertura = preparar_problema(
        pomar,
        matricula,
    )

    resultados_encosta = []
    resultados_tempera = []

    print("=== BUSCA LOCAL — K = 15 ===")
    print("Matrícula-semente:", matricula)
    print("Talhões livres:", len(livres))
    print("Execuções por algoritmo:", EXECUCOES)
    print(
        "Objetivo: prioridade simulada + "
        "cobertura de talhões livres."
    )

    # Os dois algoritmos recebem o MESMO estado inicial
    # em cada execução, tornando a comparação mais clara.
    for numero in range(1, EXECUCOES + 1):
        rng_inicial = random.Random(
            matricula + 100_000 + numero
        )

        rng_tempera = random.Random(
            matricula + 200_000 + numero
        )

        inicial = criar_estado_inicial(
            livres,
            rng_inicial,
        )

        encosta = subida_de_encosta(
            livres,
            prioridades,
            cobertura,
            inicial,
        )

        tempera = tempera_simulada(
            livres,
            prioridades,
            cobertura,
            inicial,
            rng_tempera,
        )

        resultados_encosta.append(encosta)
        resultados_tempera.append(tempera)

        print(
            f"Execução {numero:02d}: "
            f"encosta={encosta['valor']}, "
            f"têmpera={tempera['valor']}, "
            f"pioras_aceitas={tempera['pioras_aceitas']}"
        )

        exemplo = tempera["exemplo_superacao"]

        if exemplo is not None:
            print(
                "  Após aceitar piora, a têmpera "
                f"superou seu recorde anterior: "
                f"{exemplo['melhor_anterior']} -> "
                f"{exemplo['novo_melhor']} "
                f"(iteração {exemplo['iteracao']})."
            )

    for nome, resultados in (
        ("Subida de encosta", resultados_encosta),
        ("Têmpera simulada", resultados_tempera),
    ):
        valores = [
            resultado["valor"]
            for resultado in resultados
        ]

        print(f"\n=== RESUMO: {nome} ===")
        print(f"Média: {statistics.mean(valores):.2f}")
        print(
            "Desvio-padrão amostral: "
            f"{statistics.stdev(valores):.2f}"
        )
        print(f"Melhor valor: {max(valores)}")

    total_pioras = sum(
        resultado["pioras_aceitas"]
        for resultado in resultados_tempera
    )

    superacoes = sum(
        resultado["exemplo_superacao"] is not None
        for resultado in resultados_tempera
    )

    tempera_superou_encosta = sum(
        t["valor"] > e["valor"]
        for e, t in zip(
            resultados_encosta,
            resultados_tempera,
        )
    )

    print("\n=== COMPARAÇÃO FINAL ===")
    print("Pioras aceitas pela têmpera:", total_pioras)
    print(
        "Execuções com recorde superado após piora:",
        superacoes,
    )
    print(
        "Execuções em que a têmpera superou "
        "a subida de encosta:",
        tempera_superou_encosta,
    )


if __name__ == "__main__":
    pomar = gerar_pomar(MATRICULA)
    executar_experimentos(pomar, MATRICULA)
