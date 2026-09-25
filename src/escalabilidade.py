
"""
Caatinga.AI — Experimento de escalabilidade (questão 2.4).

Executa BFS, DFS e UCS em processos separados.
Registra resultados em resultados/escalabilidade.csv.

Proteções para Windows:
- limite de 60 segundos por execução;
- interrupção se o processo ultrapassar o limite
  preventivo de memória configurado;
- interrupção se a memória física livre ficar baixa.

Uma interrupção preventiva NÃO equivale a MemoryError.
"""

import csv
import ctypes
import multiprocessing as mp
import os
import time

from ctypes import wintypes
from pathlib import Path
from queue import Empty

from gerador_pomar import gerar_pomar
from buscas import bfs, dfs, ucs


MATRICULA = 24114019

# Execute somente este tamanho por enquanto.
TAMANHOS = [2800]

LIMITE_TEMPO_S = 60
LIMITE_PROCESSO_GIB = 1.5
MINIMO_MEMORIA_LIVRE_GIB = 2.0

GIB = 1024 ** 3

ESTRATEGIAS = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
}

RAIZ = Path(__file__).resolve().parents[1]
ARQUIVO_CSV = RAIZ / "resultados" / "escalabilidade.csv"


# --------------------------------------------------
# Consulta de memória no Windows, sem bibliotecas
# externas e sem alterar configurações do sistema.
# --------------------------------------------------

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
psapi = ctypes.WinDLL("psapi", use_last_error=True)

kernel32.GlobalMemoryStatusEx.argtypes = [
    ctypes.POINTER(MEMORYSTATUSEX)
]
kernel32.GlobalMemoryStatusEx.restype = wintypes.BOOL

kernel32.OpenProcess.argtypes = [
    wintypes.DWORD,
    wintypes.BOOL,
    wintypes.DWORD,
]
kernel32.OpenProcess.restype = wintypes.HANDLE

kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL

psapi.GetProcessMemoryInfo.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
    wintypes.DWORD,
]
psapi.GetProcessMemoryInfo.restype = wintypes.BOOL


def memoria_livre_gib():
    """Retorna a memória física disponível no Windows."""

    info = MEMORYSTATUSEX()
    info.dwLength = ctypes.sizeof(info)

    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(info)):
        raise OSError("Não foi possível consultar a memória livre.")

    return info.ullAvailPhys / GIB


def memoria_processo_gib(pid):
    """
    Retorna o conjunto de trabalho do processo em GiB.

    Essa medida não representa toda a memória comprometida
    pelo processo nem inclui necessariamente processos filhos.
    """

    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010

    handle = kernel32.OpenProcess(
        PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
        False,
        pid,
    )

    if not handle:
        return None

    try:
        info = PROCESS_MEMORY_COUNTERS()
        info.cb = ctypes.sizeof(info)

        ok = psapi.GetProcessMemoryInfo(
            handle,
            ctypes.byref(info),
            info.cb,
        )

        if not ok:
            return None

        return info.WorkingSetSize / GIB

    finally:
        kernel32.CloseHandle(handle)


# --------------------------------------------------
# Execução e controle dos algoritmos
# --------------------------------------------------

def executar_busca(nome, pomar, fila):
    """Executa o algoritmo e envia somente os indicadores."""

    try:
        inicio = time.perf_counter()
        resultado = ESTRATEGIAS[nome](pomar)
        tempo = time.perf_counter() - inicio

        fila.put({
            "status": "OK",
            "tempo_s": tempo,
            "custo": resultado["custo"],
            "passos": resultado["passos"],
            "nos_expandidos": resultado["nos_expandidos"],
            "fronteira_max": resultado["fronteira_max"],
        })

    except MemoryError:
        fila.put({
            "status": "MEMORY_ERROR",
            "tempo_s": None,
            "mensagem": "O Python lançou MemoryError.",
        })

    except RecursionError:
        fila.put({
            "status": "RECURSION_ERROR",
            "tempo_s": None,
            "mensagem": "O Python lançou RecursionError.",
        })

    except Exception as erro:
        fila.put({
            "status": "ERRO",
            "tempo_s": None,
            "mensagem": repr(erro),
        })


def encerrar_processo(processo):
    """Encerra o processo filho, se ele ainda estiver ativo."""

    if processo.is_alive():
        processo.terminate()
        processo.join(timeout=3)

    if processo.is_alive():
        processo.kill()
        processo.join()


def medir_estrategia(nome, pomar):
    """Executa uma estratégia e monitora tempo e memória."""

    memoria_antes = memoria_livre_gib()

    if memoria_antes < MINIMO_MEMORIA_LIVRE_GIB:
        return {
            "status": "INTERRUPCAO_PREVENTIVA",
            "tempo_s": None,
            "mensagem": (
                f"Memória livre antes da busca: "
                f"{memoria_antes:.2f} GiB."
            ),
        }

    fila = mp.Queue(maxsize=1)

    processo = mp.Process(
        target=executar_busca,
        args=(nome, pomar, fila),
    )

    inicio_total = time.perf_counter()
    processo.start()

    dados = None
    pico_observado = 0.0

    try:
        while True:
            tempo_total = time.perf_counter() - inicio_total

            # O tempo do monitor inclui inicialização e
            # comunicação; tempo_s do resultado OK mede
            # somente a execução do algoritmo.
            if tempo_total > LIMITE_TEMPO_S:
                dados = {
                    "status": "LIMITE_TEMPO",
                    "tempo_s": tempo_total,
                    "mensagem": (
                        "Limite de 60 s do experimento atingido. "
                        "O tempo inclui inicialização do processo."
                    ),
                }
                break

            try:
                dados = fila.get(timeout=0.2)
                break

            except Empty:
                pass

            if not processo.is_alive():
                dados = {
                    "status": "ERRO_PROCESSO",
                    "tempo_s": tempo_total,
                    "mensagem": (
                        f"Processo terminou sem resultado; "
                        f"código de saída: {processo.exitcode}."
                    ),
                }
                break

            uso = memoria_processo_gib(processo.pid)

            if uso is not None:
                pico_observado = max(pico_observado, uso)

                if uso >= LIMITE_PROCESSO_GIB:
                    dados = {
                        "status": "INTERRUPCAO_PREVENTIVA",
                        "tempo_s": tempo_total,
                        "mensagem": (
                            f"Uso observado do processo: "
                            f"{uso:.2f} GiB; limite preventivo: "
                            f"{LIMITE_PROCESSO_GIB:.2f} GiB."
                        ),
                    }
                    break

            livre = memoria_livre_gib()

            if livre < MINIMO_MEMORIA_LIVRE_GIB:
                dados = {
                    "status": "INTERRUPCAO_PREVENTIVA",
                    "tempo_s": tempo_total,
                    "mensagem": (
                        f"Memória física livre: {livre:.2f} GiB; "
                        f"mínimo preventivo: "
                        f"{MINIMO_MEMORIA_LIVRE_GIB:.2f} GiB."
                    ),
                }
                break

    finally:
        encerrar_processo(processo)
        fila.close()
        fila.join_thread()

    dados["pico_observado_gib"] = round(
        pico_observado, 3
    )

    return dados


def salvar_resultado(n, nome, dados):
    """Acrescenta uma linha ao CSV sem apagar testes anteriores."""

    ARQUIVO_CSV.parent.mkdir(parents=True, exist_ok=True)

    precisa_cabecalho = (
        not ARQUIVO_CSV.exists()
        or ARQUIVO_CSV.stat().st_size == 0
    )

    with ARQUIVO_CSV.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as arquivo:

        escritor = csv.writer(arquivo)

        if precisa_cabecalho:
            escritor.writerow([
                "matricula",
                "n",
                "estrategia",
                "status",
                "tempo_s",
                "custo",
                "passos",
                "nos_expandidos",
                "fronteira_max",
                "pico_observado_gib",
                "mensagem",
            ])

        escritor.writerow([
            MATRICULA,
            n,
            nome,
            dados["status"],
            dados.get("tempo_s"),
            dados.get("custo"),
            dados.get("passos"),
            dados.get("nos_expandidos"),
            dados.get("fronteira_max"),
            dados.get("pico_observado_gib"),
            dados.get("mensagem", ""),
        ])


def main():
    if os.name != "nt":
        raise RuntimeError(
            "Este monitor de memória foi preparado para Windows."
        )

    print("=== EXPERIMENTO DE ESCALABILIDADE ===")
    print("Matrícula:", MATRICULA)
    print("Limite de tempo:", LIMITE_TEMPO_S, "s")
    print(
        "Limite preventivo por processo:",
        LIMITE_PROCESSO_GIB,
        "GiB",
    )
    print(
        "Memória física livre mínima:",
        MINIMO_MEMORIA_LIVRE_GIB,
        "GiB",
    )

    for n in TAMANHOS:
        livre = memoria_livre_gib()

        if livre < MINIMO_MEMORIA_LIVRE_GIB:
            print(
                f"\nTeste não iniciado: apenas "
                f"{livre:.2f} GiB livres."
            )
            return

        print(f"\n=== POMAR {n} x {n} ===", flush=True)

        # A geração do pomar ocorre no processo principal.
        pomar = gerar_pomar(MATRICULA, n=n)

        for nome in ESTRATEGIAS:
            dados = medir_estrategia(nome, pomar)
            salvar_resultado(n, nome, dados)

            print(
                f"{nome}: status={dados['status']}, "
                f"tempo={dados.get('tempo_s')}, "
                f"pico_observado_gib="
                f"{dados.get('pico_observado_gib')}",
                flush=True,
            )

            if dados["status"] == "OK":
                print(
                    f"  custo={dados['custo']}, "
                    f"passos={dados['passos']}, "
                    f"expandidos={dados['nos_expandidos']}, "
                    f"fronteira_max={dados['fronteira_max']}",
                    flush=True,
                )
            else:
                print(
                    "  motivo:",
                    dados.get("mensagem", ""),
                    flush=True,
                )
                return


if __name__ == "__main__":
    mp.freeze_support()
    main()
