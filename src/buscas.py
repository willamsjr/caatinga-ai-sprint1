from gerador_pomar import CUSTO, BLOQUEADO, gerar_pomar
from collections import deque

import heapq
from itertools import count

# Um estado representa a posicao (linha, coluna) do agente.
Estado = tuple[int, int]


# Ordem de expansao adotada em todas as estrategias:
# Norte, Sul, Oeste, Leste.
DIRECOES = (
    (-1, 0),  # Norte
    (1, 0),   # Sul
    (0, -1),  # Oeste
    (0, 1),   # Leste
)

def estado_inicial() -> Estado:
    """Retorna a posicao inicial do agente."""
    return (0, 0)

def estado_objetivo(pomar: list[list[str]]) -> Estado:
    """Retorna a posicao do ponto de coleta."""
    return (len(pomar) - 1, len(pomar[0]) - 1)

def dentro_dos_limites(
    pomar: list[list[str]],
    estado: Estado
) -> bool:
    """Verifica se o estado esta dentro da grade."""

    linha, coluna = estado

    if not pomar or not pomar[0]:
        return False

    return (
        0 <= linha < len(pomar)
        and 0 <= coluna < len(pomar[linha])
    )

def estado_valido(
    pomar: list[list[str]],
    estado: Estado
) -> bool:
    """Verifica se o agente pode ocupar o estado."""

    if not dentro_dos_limites(pomar, estado):
        return False

    linha, coluna = estado

    return pomar[linha][coluna] != BLOQUEADO

def obter_vizinhos(
    pomar: list[list[str]],
    estado: Estado
) -> list[Estado]:
    """
    Retorna os vizinhos validos na ordem:
    Norte, Sul, Oeste, Leste.
    """

    if not estado_valido(pomar, estado):
        return []

    linha, coluna = estado

    vizinhos = []

    for deslocamento_linha, deslocamento_coluna in DIRECOES:

        proximo_estado = (
            linha + deslocamento_linha,
            coluna + deslocamento_coluna
        )

        if estado_valido(pomar, proximo_estado):
            vizinhos.append(proximo_estado)

    return vizinhos

def custo_entrada(
    pomar: list[list[str]],
    estado: Estado
) -> int:
    """Retorna o custo para entrar em um talhao valido."""

    if not estado_valido(pomar, estado):
        raise ValueError(
            f"Nao e possivel entrar no talhao {estado}."
        )

    linha, coluna = estado

    terreno = pomar[linha][coluna]

    return CUSTO[terreno]

def custo_caminho(
    pomar: list[list[str]],
    rota: list[Estado]
) -> int:
    """
    Calcula o custo total de uma rota valida.

    O estado inicial da rota nao e contabilizado.
    """

    if not rota:
        return 0

    for estado in rota:
        if not estado_valido(pomar, estado):
            raise ValueError(
                f"A rota contem um estado invalido: {estado}."
            )

    custo_total = 0

    for atual, proximo in zip(rota, rota[1:]):

        if proximo not in obter_vizinhos(pomar, atual):
            raise ValueError(
                f"Movimento invalido: {atual} -> {proximo}."
            )

        custo_total += custo_entrada(pomar, proximo)

    return custo_total

def reconstruir_rota(
    pais: dict[Estado, Estado | None],
    objetivo: Estado
) -> list[Estado]:
    """
    Reconstrói a rota do estado inicial ate o objetivo
    utilizando o dicionario de predecessores.
    """

    if objetivo not in pais:
        return []

    rota = []

    estado_atual = objetivo

    while estado_atual is not None:

        rota.append(estado_atual)

        estado_atual = pais[estado_atual]

    rota.reverse()

    return rota


def bfs(pomar: list[list[str]]) -> dict:
    """
    Executa a busca em largura (BFS).

    Retorna:
        rota: caminho encontrado.
        custo: custo total da rota.
        passos: quantidade de movimentos.
        nos_expandidos: estados cujos vizinhos foram examinados.
        fronteira_max: maior tamanho atingido pela fila.
    """

    inicio = estado_inicial()
    objetivo = estado_objetivo(pomar)

    # Fila FIFO: primeiro a entrar, primeiro a sair.
    fronteira = deque([inicio])

    # Evita inserir o mesmo estado mais de uma vez.
    descobertos = {inicio}

    # Registra de onde cada estado foi alcançado.
    pais = {inicio: None}

    # Contadores da busca.
    nos_expandidos = 0
    fronteira_max = 1

    while fronteira:

        # Remove o estado mais antigo da fila.
        atual = fronteira.popleft()

        # Teste de objetivo antes de expandir os vizinhos.
        if atual == objetivo:

            rota = reconstruir_rota(pais, objetivo)

            return {
                "rota": rota,
                "custo": custo_caminho(pomar, rota),
                "passos": len(rota) - 1,
                "nos_expandidos": nos_expandidos,
                "fronteira_max": fronteira_max,
            }

        # O estado será expandido agora.
        nos_expandidos += 1

        # Examina os vizinhos na ordem:
        # Norte, Sul, Oeste, Leste.
        for vizinho in obter_vizinhos(pomar, atual):

            if vizinho not in descobertos:

                # Marca na descoberta, evitando duplicatas.
                descobertos.add(vizinho)

                # Registra o predecessor.
                pais[vizinho] = atual

                # Insere o vizinho no final da fila.
                fronteira.append(vizinho)

                # Atualiza o maior tamanho da fronteira.
                fronteira_max = max(
                    fronteira_max,
                    len(fronteira)
                )

    # Caso nenhum caminho até o objetivo seja encontrado.
    return {
        "rota": [],
        "custo": None,
        "passos": None,
        "nos_expandidos": nos_expandidos,
        "fronteira_max": fronteira_max,
    }


def dfs(pomar: list[list[str]]) -> dict:
    """
    Executa a busca em profundidade (DFS).

    Ordem de prioridade dos vizinhos:
    Norte, Sul, Oeste, Leste.

    Retorna:
        rota: caminho encontrado.
        custo: custo total da rota.
        passos: quantidade de movimentos.
        nos_expandidos: estados cujos vizinhos foram examinados.
        fronteira_max: maior tamanho atingido pela pilha.
    """

    inicio = estado_inicial()
    objetivo = estado_objetivo(pomar)

    # Pilha LIFO: ultimo a entrar, primeiro a sair.
    fronteira = [inicio]

    # Evita inserir um estado mais de uma vez.
    descobertos = {inicio}

    # Armazena o predecessor de cada estado.
    pais = {inicio: None}

    # Contadores da busca.
    nos_expandidos = 0
    fronteira_max = 1

    while fronteira:

        # Remove o ultimo estado inserido na pilha.
        atual = fronteira.pop()

        # Verifica se o objetivo foi alcançado.
        if atual == objetivo:

            rota = reconstruir_rota(pais, objetivo)

            return {
                "rota": rota,
                "custo": custo_caminho(pomar, rota),
                "passos": len(rota) - 1,
                "nos_expandidos": nos_expandidos,
                "fronteira_max": fronteira_max,
            }

        # O estado sera expandido agora.
        nos_expandidos += 1

        # A ordem de insercao e invertida para que
        # a pilha priorize Norte, Sul, Oeste e Leste.
        vizinhos = obter_vizinhos(pomar, atual)

        for vizinho in reversed(vizinhos):

            if vizinho not in descobertos:

                # Marca o estado no momento da descoberta.
                descobertos.add(vizinho)

                # Registra de onde o estado foi alcançado.
                pais[vizinho] = atual

                # Adiciona o estado ao topo da pilha.
                fronteira.append(vizinho)

                # Atualiza o maior tamanho da fronteira.
                fronteira_max = max(
                    fronteira_max,
                    len(fronteira)
                )

    # Caso nao exista caminho ate o objetivo.
    return {
        "rota": [],
        "custo": None,
        "passos": None,
        "nos_expandidos": nos_expandidos,
        "fronteira_max": fronteira_max,
    }


def ucs(pomar: list[list[str]]) -> dict:
    """
    Executa a Busca de Custo Uniforme (UCS).

    Ordem dos vizinhos:
    Norte, Sul, Oeste, Leste.

    O algoritmo prioriza o menor custo acumulado.

    Retorna:
        rota: caminho encontrado.
        custo: custo total da rota.
        passos: quantidade de movimentos.
        nos_expandidos: estados cujos vizinhos foram examinados.
        fronteira_max: maior tamanho atingido pela fila.
    """

    inicio = estado_inicial()
    objetivo = estado_objetivo(pomar)

    # Contador para desempatar estados de mesmo custo.
    desempate = count()

    # Cada entrada da fila possui:
    # (custo_acumulado, ordem_de_insercao, estado)
    fronteira = []

    heapq.heappush(
        fronteira,
        (0, next(desempate), inicio)
    )

    # Menor custo conhecido para chegar a cada estado.
    melhor_custo = {inicio: 0}

    # Registra o predecessor de cada estado.
    pais = {inicio: None}

    # Estados ja expandidos definitivamente.
    expandidos = set()

    # Contadores da busca.
    nos_expandidos = 0
    fronteira_max = 1

    while fronteira:

        # Retira o estado com menor custo acumulado.
        custo_atual, _, atual = heapq.heappop(
            fronteira
        )

        # Ignora entradas antigas que foram substituidas
        # por caminhos de menor custo.
        if custo_atual != melhor_custo[atual]:
            continue

        # Evita expandir novamente um estado ja finalizado.
        if atual in expandidos:
            continue

        # Testa o objetivo quando ele sai da fila.
        if atual == objetivo:

            rota = reconstruir_rota(pais, objetivo)

            return {
                "rota": rota,
                "custo": custo_atual,
                "passos": len(rota) - 1,
                "nos_expandidos": nos_expandidos,
                "fronteira_max": fronteira_max,
            }

        # Registra que o estado sera expandido.
        expandidos.add(atual)

        nos_expandidos += 1

        # Examina Norte, Sul, Oeste e Leste.
        for vizinho in obter_vizinhos(pomar, atual):

            # O custo de uma nova rota considera
            # o custo para entrar no talhao vizinho.
            novo_custo = (
                custo_atual
                + custo_entrada(pomar, vizinho)
            )

            # Recupera o melhor custo anterior.
            custo_anterior = melhor_custo.get(
                vizinho,
                float("inf")
            )

            # Atualiza apenas quando encontra
            # um caminho estritamente mais barato.
            if novo_custo < custo_anterior:

                melhor_custo[vizinho] = novo_custo

                # Atualiza o predecessor.
                pais[vizinho] = atual

                # Insere a nova alternativa na fila.
                heapq.heappush(
                    fronteira,
                    (
                        novo_custo,
                        next(desempate),
                        vizinho
                    )
                )

                # Registra o maior tamanho da fila.
                fronteira_max = max(
                    fronteira_max,
                    len(fronteira)
                )

    # Caso nenhum caminho ate o objetivo seja encontrado.
    return {
        "rota": [],
        "custo": None,
        "passos": None,
        "nos_expandidos": nos_expandidos,
        "fronteira_max": fronteira_max,
    }


def distancia_manhattan(
    atual: Estado,
    objetivo: Estado
) -> int:
    """
    Calcula a distancia de Manhattan entre dois estados.
    """

    linha_atual, coluna_atual = atual
    linha_objetivo, coluna_objetivo = objetivo

    return (
        abs(linha_atual - linha_objetivo)
        + abs(coluna_atual - coluna_objetivo)
    )


def calcular_heuristica(
    atual: Estado,
    objetivo: Estado,
    tipo: str
) -> int:
    """
    Calcula uma das tres heuristicas do A*.

    h1: heuristica nula.
    h2: distancia de Manhattan.
    h3: quatro vezes a distancia de Manhattan.
    """

    if tipo == "h1":
        return 0

    distancia = distancia_manhattan(
        atual,
        objetivo
    )

    if tipo == "h2":
        return distancia

    if tipo == "h3":
        return 4 * distancia

    raise ValueError(
        f"Heuristica desconhecida: {tipo}"
    )


def a_estrela(
    pomar: list[list[str]],
    heuristica: str = "h2"
) -> dict:
    """
    Executa o algoritmo A*.

    Heuristicas disponiveis:
        h1: zero.
        h2: distancia de Manhattan.
        h3: quatro vezes a distancia de Manhattan.

    Ordem dos vizinhos:
        Norte, Sul, Oeste, Leste.

    Permite reabrir estados quando encontra
    um caminho de menor custo.

    Contadores:
        nos_expandidos: numero de expansoes efetivas.
        fronteira_max: maior tamanho fisico da fila.
    """

    inicio = estado_inicial()
    objetivo = estado_objetivo(pomar)

    # Valida a heuristica antes de iniciar a busca.
    h_inicial = calcular_heuristica(
        inicio,
        objetivo,
        heuristica
    )

    desempate = count()

    # Cada entrada da fila possui:
    # (f, ordem_de_insercao, g, estado)
    fronteira = []

    heapq.heappush(
        fronteira,
        (
            h_inicial,
            next(desempate),
            0,
            inicio
        )
    )

    # Menor custo conhecido ate cada estado.
    melhor_custo = {inicio: 0}

    # Predecessores utilizados para reconstruir a rota.
    pais = {inicio: None}

    # Menor custo com que cada estado foi expandido.
    custo_expandido = {}

    nos_expandidos = 0
    fronteira_max = 1

    while fronteira:

        # Retira a entrada com menor f = g + h.
        f_atual, _, g_atual, atual = heapq.heappop(
            fronteira
        )

        # Ignora entradas antigas da fila.
        if g_atual != melhor_custo[atual]:
            continue

        # Impede expansoes repetidas com o mesmo custo
        # ou com um custo maior que o ja expandido.
        if (
            atual in custo_expandido
            and g_atual >= custo_expandido[atual]
        ):
            continue

        # Testa o objetivo quando sai da fila.
        if atual == objetivo:

            rota = reconstruir_rota(
                pais,
                objetivo
            )

            return {
                "rota": rota,
                "custo": g_atual,
                "passos": len(rota) - 1,
                "nos_expandidos": nos_expandidos,
                "fronteira_max": fronteira_max,
            }

        # Registra a expansao efetiva do estado.
        custo_expandido[atual] = g_atual

        nos_expandidos += 1

        # Examina Norte, Sul, Oeste e Leste.
        for vizinho in obter_vizinhos(pomar, atual):

            # Custo real para chegar ao vizinho.
            novo_g = (
                g_atual
                + custo_entrada(pomar, vizinho)
            )

            custo_anterior = melhor_custo.get(
                vizinho,
                float("inf")
            )

            # Atualiza apenas caminhos mais baratos.
            if novo_g < custo_anterior:

                melhor_custo[vizinho] = novo_g

                pais[vizinho] = atual

                # Estima o custo restante.
                h_vizinho = calcular_heuristica(
                    vizinho,
                    objetivo,
                    heuristica
                )

                # Prioridade do A*.
                novo_f = novo_g + h_vizinho

                heapq.heappush(
                    fronteira,
                    (
                        novo_f,
                        next(desempate),
                        novo_g,
                        vizinho
                    )
                )

                fronteira_max = max(
                    fronteira_max,
                    len(fronteira)
                )

    # Caso nao exista caminho ate o objetivo.
    return {
        "rota": [],
        "custo": None,
        "passos": None,
        "nos_expandidos": nos_expandidos,
        "fronteira_max": fronteira_max,
    }

if __name__ == "__main__":

    MATRICULA = 24114019

    pomar = gerar_pomar(MATRICULA)

    inicio = estado_inicial()
    objetivo = estado_objetivo(pomar)

    print("=== TESTE DAS FUNCOES AUXILIARES ===")

    print("Estado inicial:", inicio)
    print("Estado objetivo:", objetivo)

    print("Vizinhos do inicio:", obter_vizinhos(pomar, inicio))

    print("Custo de entrada em (0, 1):",
          custo_entrada(pomar, (0, 1)))

    print("Custo de entrada em (1, 0):",
          custo_entrada(pomar, (1, 0)))

    rota_teste = [
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3)
    ]

    print("Rota de teste:", rota_teste)

    print("Custo da rota de teste:",
          custo_caminho(pomar, rota_teste))

    pais_teste = {
        (0, 0): None,
        (0, 1): (0, 0),
        (0, 2): (0, 1),
        (0, 3): (0, 2)
    }

    rota_reconstruida = reconstruir_rota(
        pais_teste,
        (0, 3)
    )

    print("Rota reconstruida:", rota_reconstruida)



    # -----------------------------------------------
    # TESTE DO ALGORITMO BFS
    # -----------------------------------------------

    print("\n=== TESTE DO ALGORITMO BFS ===")

    resultado_bfs = bfs(pomar)

    print("Rota encontrada:")
    print(resultado_bfs["rota"])

    print("Custo da rota:",
          resultado_bfs["custo"])

    print("Numero de passos:",
          resultado_bfs["passos"])

    print("Nos expandidos:",
          resultado_bfs["nos_expandidos"])

    print("Fronteira maxima:",
          resultado_bfs["fronteira_max"])


# -----------------------------------------------
    # TESTE DO ALGORITMO DFS
    # -----------------------------------------------

    print("\n=== TESTE DO ALGORITMO DFS ===")

    resultado_dfs = dfs(pomar)

    print("Rota encontrada:")
    print(resultado_dfs["rota"])

    print("Custo da rota:",
          resultado_dfs["custo"])

    print("Numero de passos:",
          resultado_dfs["passos"])

    print("Nos expandidos:",
          resultado_dfs["nos_expandidos"])

    print("Fronteira maxima:",
          resultado_dfs["fronteira_max"])


    # -----------------------------------------------
    # TESTE DO ALGORITMO UCS
    # -----------------------------------------------

    print("\n=== TESTE DO ALGORITMO UCS ===")

    resultado_ucs = ucs(pomar)

    print("Rota encontrada:")
    print(resultado_ucs["rota"])

    print("Custo da rota:",
          resultado_ucs["custo"])

    print("Numero de passos:",
          resultado_ucs["passos"])

    print("Nos expandidos:",
          resultado_ucs["nos_expandidos"])

    print("Fronteira maxima:",
          resultado_ucs["fronteira_max"])

    # Confere se o custo registrado pelo UCS
    # corresponde ao custo real da rota.
    if resultado_ucs["rota"]:

        custo_verificado = custo_caminho(
            pomar,
            resultado_ucs["rota"]
        )

        print(
            "Custo recalculado:",
            custo_verificado
        )

        assert (
            custo_verificado == resultado_ucs["custo"]
        ), "O custo registrado pelo UCS esta incorreto."

        print("Validacao do custo: OK")


    # -----------------------------------------------
    # TESTE DO ALGORITMO A*
    # -----------------------------------------------

    print("\n=== TESTE DO ALGORITMO A* ===")

    for tipo_heuristica in ("h1", "h2", "h3"):

        print(
            f"\n--- Heuristica {tipo_heuristica} ---"
        )

        resultado = a_estrela(
            pomar,
            tipo_heuristica
        )

        print("Rota encontrada:")
        print(resultado["rota"])

        print("Custo da rota:",
              resultado["custo"])

        print("Numero de passos:",
              resultado["passos"])

        print("Nos expandidos:",
              resultado["nos_expandidos"])

        print("Fronteira maxima:",
              resultado["fronteira_max"])

        # Validacao independente do custo da rota.
        if resultado["rota"]:

            custo_verificado = custo_caminho(
                pomar,
                resultado["rota"]
            )

            assert (
                custo_verificado == resultado["custo"]
            ), "Custo da rota inconsistente."

            print("Validacao do custo: OK")

        # A* com h1 deve reproduzir o custo do UCS.
        if tipo_heuristica == "h1":

            assert (
                resultado["custo"]
                == resultado_ucs["custo"]
            ), "A* com h1 divergiu do UCS."

            print("Comparacao com UCS: OK")

        # A* com Manhattan deve encontrar o custo otimo.
        if tipo_heuristica == "h2":

            assert (
                resultado["custo"]
                == resultado_ucs["custo"]
            ), "A* com Manhattan divergiu do UCS."

            print("Otimalidade com Manhattan: OK")