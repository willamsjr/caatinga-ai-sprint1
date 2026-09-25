
"""
Testes automatizados do projeto Caatinga.AI.

Execute na raiz do projeto:

python -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path


# Permite importar os arquivos da pasta src.
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))


from gerador_pomar import gerar_pomar

from buscas import (
    estado_inicial,
    estado_objetivo,
    estado_valido,
    obter_vizinhos,
    custo_entrada,
    custo_caminho,
    reconstruir_rota,
    distancia_manhattan,
    calcular_heuristica,
    bfs,
    dfs,
    ucs,
    a_estrela,
)


class TestesCaatingaAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Gera o pomar da dupla uma unica vez
        para reutilizacao nos testes.
        """

        cls.matricula = 24114019

        cls.pomar = gerar_pomar(cls.matricula)

        cls.inicio = estado_inicial()

        cls.objetivo = estado_objetivo(cls.pomar)

    def validar_resultado(self, resultado):
        """
        Verifica propriedades gerais de uma busca.
        """

        rota = resultado["rota"]

        # O caminho precisa existir.
        self.assertTrue(rota)

        # Verifica inicio e destino.
        self.assertEqual(
            rota[0],
            self.inicio
        )

        self.assertEqual(
            rota[-1],
            self.objetivo
        )

        # Todas as posicoes devem ser validas.
        for estado in rota:

            self.assertTrue(
                estado_valido(self.pomar, estado)
            )

        # Cada movimento deve respeitar a vizinhanca.
        for atual, proximo in zip(rota, rota[1:]):

            self.assertIn(
                proximo,
                obter_vizinhos(self.pomar, atual)
            )

        # Recalcula o custo independentemente
        # do valor retornado pelo algoritmo.
        self.assertEqual(
            resultado["custo"],
            custo_caminho(self.pomar, rota)
        )

        # Confere o numero de movimentos.
        self.assertEqual(
            resultado["passos"],
            len(rota) - 1
        )

        # Verifica propriedades basicas dos contadores.
        self.assertGreaterEqual(
            resultado["nos_expandidos"],
            0
        )

        self.assertGreaterEqual(
            resultado["fronteira_max"],
            1
        )

    def test_01_estrutura_do_pomar(self):

        self.assertEqual(len(self.pomar), 12)

        for linha in self.pomar:

            self.assertEqual(len(linha), 12)

        self.assertEqual(
            self.pomar[0][0],
            "."
        )

        self.assertEqual(
            self.pomar[11][11],
            "."
        )

    def test_02_vizinhos_e_custos(self):

        self.assertEqual(
            obter_vizinhos(self.pomar, (0, 0)),
            [(1, 0), (0, 1)]
        )

        self.assertEqual(
            custo_entrada(self.pomar, (0, 1)),
            1
        )

        self.assertEqual(
            custo_entrada(self.pomar, (1, 0)),
            4
        )

        self.assertFalse(
            estado_valido(self.pomar, (0, 7))
        )

        self.assertFalse(
            estado_valido(self.pomar, (-1, 0))
        )

    def test_03_reconstrucao_e_custo(self):

        pais = {
            (0, 0): None,
            (0, 1): (0, 0),
            (0, 2): (0, 1),
            (0, 3): (0, 2)
        }

        rota = reconstruir_rota(
            pais,
            (0, 3)
        )

        self.assertEqual(
            rota,
            [
                (0, 0),
                (0, 1),
                (0, 2),
                (0, 3)
            ]
        )

        self.assertEqual(
            custo_caminho(self.pomar, rota),
            3
        )

        # A funcao deve rejeitar saltos invalidos.
        with self.assertRaises(ValueError):

            custo_caminho(
                self.pomar,
                [(0, 0), (0, 2)]
            )

    def test_04_bfs(self):

        resultado = bfs(self.pomar)

        self.validar_resultado(resultado)

        self.assertEqual(resultado["custo"], 52)

        self.assertEqual(resultado["passos"], 22)

        self.assertEqual(
            resultado["nos_expandidos"],
            123
        )

        self.assertEqual(
            resultado["fronteira_max"],
            12
        )

    def test_05_dfs(self):

        resultado = dfs(self.pomar)

        self.validar_resultado(resultado)

        self.assertEqual(resultado["custo"], 109)

        self.assertEqual(resultado["passos"], 46)

        self.assertEqual(
            resultado["nos_expandidos"],
            91
        )

        self.assertEqual(
            resultado["fronteira_max"],
            44
        )

    def test_06_ucs(self):

        resultado = ucs(self.pomar)

        self.validar_resultado(resultado)

        self.assertEqual(resultado["custo"], 37)

        self.assertEqual(resultado["passos"], 22)

        self.assertEqual(
            resultado["nos_expandidos"],
            123
        )

        self.assertEqual(
            resultado["fronteira_max"],
            18
        )

    def test_07_a_estrela(self):

        custo_ucs = ucs(self.pomar)["custo"]

        resultados_esperados = {
            "h1": (37, 123, 18),
            "h2": (37, 114, 24),
            "h3": (42, 26, 28),
        }

        for heuristica, esperado in resultados_esperados.items():

            with self.subTest(heuristica=heuristica):

                resultado = a_estrela(
                    self.pomar,
                    heuristica
                )

                self.validar_resultado(resultado)

                custo, expandidos, fronteira = esperado

                self.assertEqual(
                    resultado["custo"],
                    custo
                )

                self.assertEqual(
                    resultado["nos_expandidos"],
                    expandidos
                )

                self.assertEqual(
                    resultado["fronteira_max"],
                    fronteira
                )

                if heuristica in ("h1", "h2"):

                    self.assertEqual(
                        resultado["custo"],
                        custo_ucs
                    )

        # Contraexemplo concreto da heuristica h3.
        estado = (11, 10)

        self.assertEqual(
            distancia_manhattan(
                estado,
                self.objetivo
            ),
            1
        )

        self.assertEqual(
            calcular_heuristica(
                estado,
                self.objetivo,
                "h3"
            ),
            4
        )

        self.assertEqual(
            custo_entrada(
                self.pomar,
                self.objetivo
            ),
            1
        )


if __name__ == "__main__":
    unittest.main()
