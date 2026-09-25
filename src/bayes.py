
"""Caatinga.AI — Questão 4.3: Teorema de Bayes."""

import sys

from gerador_pomar import parametros_sensor


MATRICULA_PADRAO = 24114019
MINUTOS_POR_INSPECAO = 12


def valor_preditivo_positivo(prevalencia, sensibilidade, falso_positivo):
    """Calcula P(infestado | sensor positivo)."""

    verdadeiros_positivos = prevalencia * sensibilidade
    falsos_positivos = (1 - prevalencia) * falso_positivo

    return verdadeiros_positivos / (
        verdadeiros_positivos + falsos_positivos
    )


def executar(matricula):
    parametros = parametros_sensor(matricula)

    p = parametros["prevalencia"]
    s = parametros["sensibilidade"]
    f = parametros["taxa_falso_positivo"]
    talhoes_semana = parametros["talhoes_por_semana"]

    print("=== QUESTÃO 4.3 — BAYES ===")
    print("Matrícula-semente:", matricula)
    print("Parâmetros do sensor:", parametros)

    # (a) Probabilidade de infestação dado um alerta positivo.
    verdadeiros_positivos = p * s
    falsos_positivos = (1 - p) * f

    probabilidade_positivo = (
        verdadeiros_positivos + falsos_positivos
    )

    vpp = valor_preditivo_positivo(p, s, f)

    print("\n(a) P(infestado | positivo)")
    print(
        "Fórmula: (sensibilidade × prevalência) / "
        "[(sensibilidade × prevalência) + "
        "(taxa de falsos positivos × (1 - prevalência))]"
    )
    print(
        f"Substituição: ({s} × {p}) / "
        f"[({s} × {p}) + ({f} × (1 - {p}))]"
    )
    print(f"Resultado: {vpp:.6f} = {vpp * 100:.2f}%")

    # (b) Entre os alertas emitidos, quantos são falsos?
    proporcao_alertas_falsos = 1 - vpp

    print("\n(b) Alertas falsos em cada 100 alertas")
    print(
        f"(1 - {vpp:.6f}) × 100 = "
        f"{proporcao_alertas_falsos * 100:.2f}"
    )
    print(
        f"Resposta: cerca de "
        f"{proporcao_alertas_falsos * 100:.0f} "
        "alertas falsos a cada 100 alertas."
    )

    # (c) Falsos alertas entre TODOS os talhões examinados.
    falsos_alertas_semana = (
        talhoes_semana * (1 - p) * f
    )

    horas_desperdicadas = (
        falsos_alertas_semana * MINUTOS_POR_INSPECAO / 60
    )

    print("\n(c) Falsos alertas e horas gastas por semana")
    print(
        f"Alertas falsos: {talhoes_semana} × "
        f"(1 - {p}) × {f}"
    )
    print(
        f"Resultado: {falsos_alertas_semana:.2f} "
        "alertas falsos por semana, em média."
    )
    print(
        f"Horas: {falsos_alertas_semana:.2f} × "
        f"{MINUTOS_POR_INSPECAO} / 60"
    )
    print(
        f"Resultado: {horas_desperdicadas:.2f} "
        "horas por semana, em média."
    )

    # (d) Alteração apenas da sensibilidade para 99,9%.
    nova_sensibilidade = 0.999

    novo_vpp = valor_preditivo_positivo(
        p,
        nova_sensibilidade,
        f,
    )

    print("\n(d) Sensibilidade aumentada para 99,9%")
    print(
        f"Substituição: ({nova_sensibilidade} × {p}) / "
        f"[({nova_sensibilidade} × {p}) + "
        f"({f} × (1 - {p}))]"
    )
    print(f"VPP anterior: {vpp * 100:.2f}%")
    print(f"Novo VPP: {novo_vpp * 100:.2f}%")
    print(
        f"Melhoria: {(novo_vpp - vpp) * 100:.2f} "
        "pontos percentuais."
    )
    print(
        "Os falsos alertas semanais não diminuem, pois "
        "a taxa de falsos positivos permaneceu em 8%."
    )
    print(
        "Para diminuir alertas falsos, é necessário "
        "reduzir a taxa de falsos positivos, por exemplo, "
        "com uma etapa de confirmação validada."
    )


if __name__ == "__main__":
    matricula = (
        int(sys.argv[1])
        if len(sys.argv) > 1
        else MATRICULA_PADRAO
    )

    executar(matricula)
