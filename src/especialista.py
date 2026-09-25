
"""Caatinga.AI — Questões 4.1 e 4.2: sistema especialista."""

REGRAS_ORIGINAIS = [
    {
        "nome": "R1",
        "condicoes": ["sensor_positivo", "umidade_alta"],
        "conclusao": "suspeita_alta",
    },
    {
        "nome": "R2",
        "condicoes": ["sensor_positivo", "historico_pragas"],
        "conclusao": "suspeita_alta",
    },
    {
        "nome": "R3",
        "condicoes": ["suspeita_alta", "sem_inspecao_recente"],
        "conclusao": "inspecionar_prioridade_alta",
    },
    {
        "nome": "R4",
        "condicoes": ["sensor_positivo", "inspecao_recente"],
        "conclusao": "acompanhar_talhao",
    },
    {
        "nome": "R5",
        "condicoes": ["sensor_negativo", "historico_pragas"],
        "conclusao": "acompanhar_talhao",
    },
    {
        "nome": "R6",
        "condicoes": ["sensor_negativo", "sem_historico_pragas"],
        "conclusao": "manter_rotina",
    },
    {
        "nome": "R7",
        "condicoes": [
            "inspecionar_prioridade_alta",
            "agronomo_disponivel",
        ],
        "conclusao": "agendar_inspecao",
    },
]

# Copiamos as regras originais para preservar a comparação.
REGRAS_CORRIGIDAS = [
    {
        "nome": regra["nome"],
        "condicoes": regra["condicoes"].copy(),
        "conclusao": regra["conclusao"],
    }
    for regra in REGRAS_ORIGINAIS
]

# A suspeita alta depende de uma leitura validada.
for regra in REGRAS_CORRIGIDAS:
    if regra["nome"] in ("R1", "R2"):
        regra["condicoes"].append("sensor_validado")

# Nova regra para tratar uma falha identificada no sensor.
REGRAS_CORRIGIDAS.append(
    {
        "nome": "R8",
        "condicoes": ["sensor_com_falha"],
        "conclusao": "verificar_sensor",
    }
)


def provar(objetivo, fatos, regras, trilha=None):
    """Encadeamento para trás com registro da justificativa."""

    if trilha is None:
        trilha = set()

    if objetivo in fatos:
        return [f"FATO: {objetivo}"]

    if objetivo in trilha:
        return None

    nova_trilha = trilha | {objetivo}

    for regra in regras:
        if regra["conclusao"] != objetivo:
            continue

        explicacao = [
            f"{regra['nome']}: tentar concluir {objetivo}"
        ]

        for condicao in regra["condicoes"]:
            prova = provar(
                condicao,
                fatos,
                regras,
                nova_trilha,
            )

            if prova is None:
                break

            explicacao.extend(prova)
        else:
            explicacao.append(
                f"{regra['nome']}: conclusão {objetivo}"
            )
            return explicacao

    return None


def consultar(titulo, objetivo, fatos, regras):
    print(f"\n=== {titulo} ===")
    print("Fatos:", ", ".join(sorted(fatos)))
    print("Objetivo:", objetivo)

    explicacao = provar(objetivo, fatos, regras)

    if explicacao is None:
        print("Conclusão NÃO comprovada.")
    else:
        print("Conclusão comprovada!")
        print("Cadeia de justificativa:")

        for passo in explicacao:
            print("-", passo)


def main():
    # Questão 4.1: o sensor está validado.
    fatos_normais = {
        "sensor_positivo",
        "sensor_validado",
        "umidade_alta",
        "sem_inspecao_recente",
        "agronomo_disponivel",
    }

    consultar(
        "4.1 — CASO NORMAL",
        "agendar_inspecao",
        fatos_normais,
        REGRAS_CORRIGIDAS,
    )

    # Questão 4.2: há alerta positivo, mas o sensor
    # apresenta falha de calibração identificada.
    fatos_falha = {
        "sensor_positivo",
        "sensor_com_falha",
        "umidade_alta",
        "sem_inspecao_recente",
        "agronomo_disponivel",
    }

    consultar(
        "4.2 — ANTES DA CORREÇÃO",
        "agendar_inspecao",
        fatos_falha,
        REGRAS_ORIGINAIS,
    )

    consultar(
        "4.2 — DEPOIS DA CORREÇÃO",
        "agendar_inspecao",
        fatos_falha,
        REGRAS_CORRIGIDAS,
    )

    consultar(
        "4.2 — CONDUTA APÓS A CORREÇÃO",
        "verificar_sensor",
        fatos_falha,
        REGRAS_CORRIGIDAS,
    )


if __name__ == "__main__":
    main()
