from gerador_pomar import CUSTO, BLOQUEADO, gerar_pomar
from collections import deque


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