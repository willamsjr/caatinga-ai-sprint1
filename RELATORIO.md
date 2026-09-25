### 2.4 — Experimento de escalabilidade

Aumentamos a dimensão do pomar utilizando a matrícula-semente `24114019` e executamos BFS, DFS e UCS. Cada estratégia foi executada em um processo separado, com limite de 60 segundos. Para proteger o computador, também configuramos a interrupção preventiva caso a memória observada do processo atingisse 1,50 GiB ou a memória física livre do sistema ficasse abaixo de 2,00 GiB.

| Dimensão | BFS (s) | DFS (s) | UCS (s) |
|---|---:|---:|---:|
| 12 × 12 | 0,00033 | 0,00032 | 0,00051 |
| 40 × 40 | 0,00298 | 0,00225 | 0,00521 |
| 100 × 100 | 0,02141 | 0,01564 | 0,03380 |
| 200 × 200 | 0,06923 | 0,06117 | 0,14159 |
| 400 × 400 | 0,29984 | 0,25801 | 0,60216 |
| 800 × 800 | 1,60835 | 1,15924 | 2,66053 |
| 1.000 × 1.000 | 2,57779 | 1,78484 | 4,46130 |
| 1.200 × 1.200 | 3,71859 | 2,64123 | 6,48840 |
| 1.600 × 1.600 | 6,70881 | 4,56667 | 11,97992 |
| 2.000 × 2.000 | 9,83735 | 7,15459 | 20,35290 |
| 2.800 × 2.800 | 20,92496 | 14,18857 | Interrompido* |

*Em `n = 2800`, o UCS foi interrompido preventivamente após 37,72 segundos de monitoramento. Esse valor não representa seu tempo de conclusão.*

**Limite experimental encontrado:** em `n = 2800`, a BFS e a DFS concluíram normalmente. O UCS foi interrompido pelo monitor porque seu processo atingiu 1,76 GiB de memória observada, ultrapassando o limite preventivo configurado de 1,50 GiB. O programa registrou `INTERRUPCAO_PREVENTIVA`, e não `MemoryError`. Portanto, identificamos um limite de recursos **do ambiente experimental configurado**, mas não comprovamos que o UCS esgotou a memória física do computador.

**Relação com a complexidade:** um pomar `n × n` possui até `n²` posições distintas. Com `n = 2800`, são `7.840.000` posições possíveis. A BFS expandiu `6.259.861` nós nessa grade; em `n = 2000`, havia expandido `3.194.540`. Esse crescimento acompanha o aumento do espaço de estados e das estruturas necessárias para registrar posições descobertas e predecessores.

A fórmula de complexidade da busca em árvore estudada na Aula 03 utiliza o fator de ramificação `b` e a profundidade da solução `d`. Neste projeto, porém, implementamos busca em grafo: os algoritmos registram estados já descobertos e evitam expandir indefinidamente as mesmas posições. Como cada posição da grade tem no máximo quatro vizinhos, o espaço contém até `n²` estados distintos, embora filas de prioridade e outras estruturas possam armazenar entradas adicionais. Para o UCS, a manutenção de custos acumulados, predecessores e entradas na fila de prioridade contribui para o consumo de recursos observado.

**Limitação:** a interrupção em `n = 2800` foi causada pelo limite preventivo de memória estabelecido para proteger o computador. Nenhuma estratégia apresentou estouro natural de memória, estouro de pilha ou tempo de execução comprovadamente superior a 60 segundos nos testes realizados.

### 3.4 — Busca local: escolha de 15 talhões para inspeção

**Estado:** conjunto de 15 talhões livres e distintos do pomar.

**Vizinhança:** retirar um talhão da seleção e substituí-lo por outro talhão livre ainda não selecionado.

**Função objetivo:** maximizar a soma das prioridades simuladas dos talhões selecionados e a cobertura de inspeção. Cada talhão recebe uma prioridade simulada de 1 a 100, gerada de forma reproduzível a partir da matrícula-semente `24114019`. Cada talhão selecionado cobre sua própria posição e os talhões livres imediatamente ao norte, sul, oeste e leste. Uma posição coberta por mais de um talhão selecionado é contabilizada apenas uma vez.

A pontuação da seleção é:

`pontuação = soma das prioridades + 12 × quantidade de posições livres cobertas`

As prioridades, a área de cobertura e o peso 12 são hipóteses de modelagem adotadas pela dupla, e não medições reais de infestação. A seleção de 15 talhões representa a quantidade escolhida para inspeção, mas o modelo não calcula a rota entre eles nem comprova que todas as visitas cabem nas seis horas de bateria, pois o enunciado não fornece tempos de deslocamento e inspeção.

**Algoritmos:** a subida de encosta examina todas as trocas possíveis e escolhe a que proporciona a maior melhoria, encerrando quando nenhuma troca individual melhora a pontuação. A têmpera simulada sorteia trocas e pode aceitar uma piora com probabilidade `exp(Δ/temperatura)`, em que `Δ` é a diferença entre a pontuação da solução candidata e a atual. A temperatura diminui ao longo das iterações. Os algoritmos partiram da mesma seleção inicial em cada uma das 30 execuções comparadas.

**Resultados experimentais:**

| Algoritmo | Execuções | Média (pontos) | Desvio-padrão amostral (pontos) | Melhor valor (pontos) |
|---|---:|---:|---:|---:|
| Subida de encosta | 30 | 2.104,83 | 2,95 | 2.107 |
| Têmpera simulada | 30 | 2.100,13 | 6,05 | 2.107 |

A têmpera simulada aceitou **2.227 movimentos de piora** nas 30 execuções. Em todas elas, o programa registrou pelo menos uma ocasião em que, após aceitar uma piora, a busca alcançou um valor superior ao seu recorde anterior.

Na execução 08, por exemplo, a têmpera encontrou 2.107 pontos, enquanto a subida de encosta, partindo da mesma seleção inicial, terminou com 2.105 pontos. A têmpera também superou a subida de encosta nas execuções 24, 25 e 28.

**Interpretação:** aceitar temporariamente uma piora permite que a têmpera simulada continue explorando soluções em vez de encerrar a busca assim que deixa de encontrar uma melhoria imediata. Esse mecanismo pode ajudar a escapar de ótimos locais. No experimento, a têmpera superou a subida de encosta em 4 das 30 execuções, mas apresentou média menor e maior dispersão. A sequência “piora aceita → novo recorde” demonstra o comportamento da busca; isoladamente, não prova que a piora tenha sido indispensável para atingir aquele recorde.

### 4.2 — Caso que quebra a base de regras e sua correção

**Caso de falha:** um talhão apresenta `sensor_positivo`, `umidade_alta` e `sem_inspecao_recente`, com `agronomo_disponivel`. Entretanto, foi identificada uma falha de calibração no sensor (`sensor_com_falha`). A base original não verifica se a leitura do sensor foi validada antes de utilizá-la para recomendar uma inspeção de prioridade alta.

**Antes da correção:** ao consultar o objetivo `agendar_inspecao`, o sistema comprovou a conclusão pela cadeia R7 → R3 → R1, utilizando o alerta positivo e a umidade alta para inferir `suspeita_alta`. Assim, recomendou o agendamento com base em uma leitura cuja confiabilidade estava comprometida.

```text
=== 4.2 — ANTES DA CORREÇÃO ===
Objetivo: agendar_inspecao
Conclusão comprovada!
Cadeia de justificativa:
- R7: tentar concluir agendar_inspecao
- R3: tentar concluir inspecionar_prioridade_alta
- R1: tentar concluir suspeita_alta
- FATO: sensor_positivo
- FATO: umidade_alta
- R1: conclusão suspeita_alta
- FATO: sem_inspecao_recente
- R3: conclusão inspecionar_prioridade_alta
- FATO: agronomo_disponivel
- R7: conclusão agendar_inspecao
```

**Correção:** acrescentamos a condição `sensor_validado` às regras R1 e R2, que inferem `suspeita_alta` a partir de uma leitura positiva. Também incluímos a regra R8:

**R8: SE `sensor_com_falha`, ENTÃO `verificar_sensor`.**

A condição `sensor_validado` só deve ser registrada após a validação efetiva do equipamento. Dessa forma, uma leitura positiva de um sensor com falha não basta para sustentar a conclusão de suspeita alta. A correção preserva as demais regras e mantém o agendamento para o caso normal, no qual a leitura foi validada.

**Depois da correção:** utilizando os mesmos fatos do caso de falha, o sistema deixou de comprovar o agendamento e passou a justificar a verificação do sensor.

```text
=== 4.2 — DEPOIS DA CORREÇÃO ===
Objetivo: agendar_inspecao
Conclusão NÃO comprovada.

=== 4.2 — CONDUTA APÓS A CORREÇÃO ===
Objetivo: verificar_sensor
Conclusão comprovada!
Cadeia de justificativa:
- R8: tentar concluir verificar_sensor
- FATO: sensor_com_falha
- R8: conclusão verificar_sensor
```

**Resultado:** o experimento demonstrou uma classificação inadequada da base original e a correção de sua justificativa. No caso normal, com `sensor_validado`, o sistema continuou comprovando `agendar_inspecao` pela cadeia R7 → R3 → R1.

### 4.3 — Teorema de Bayes com os parâmetros da dupla

A função `parametros_sensor(24114019)` retornou:

| Parâmetro | Valor |
|---|---:|
| Prevalência de infestação | 0,0211 (2,11%) |
| Sensibilidade | 0,95 (95%) |
| Taxa de falsos positivos | 0,08 (8%) |
| Talhões examinados por semana | 2.000 |

**(a) Probabilidade de um talhão estar infestado dado um alerta positivo**

Pelo teorema de Bayes:

\[
P(\text{infestado}\mid\text{positivo}) =
\frac{P(\text{positivo}\mid\text{infestado})P(\text{infestado})}
{P(\text{positivo}\mid\text{infestado})P(\text{infestado})+
P(\text{positivo}\mid\text{não infestado})P(\text{não infestado})}
\]

Substituindo os parâmetros da dupla:

\[
P(\text{infestado}\mid\text{positivo}) =
\frac{0{,}95\times0{,}0211}
{(0{,}95\times0{,}0211)+(0{,}08\times0{,}9789)}
\approx 0{,}203798
\]

**Resultado: 20,38%.** Entre os alertas positivos, a probabilidade de infestação é de aproximadamente 20,38%, considerando os parâmetros informados.

**(b) Quantos alertas serão falsos a cada 100 alertas?**

\[
P(\text{não infestado}\mid\text{positivo})
=1-0{,}203798
=0{,}796202
\]

**Resposta:** a cada 100 alertas do sistema, cerca de **80 serão falsos**.

**(c) Quantos alertas falsos e quantas horas de inspeção por semana?**

A quantidade esperada de alertas falsos considera todos os 2.000 talhões examinados na semana:

\[
2.000\times(1-0{,}0211)\times0{,}08
=156{,}624
\]

**Resultado:** aproximadamente **156,62 alertas falsos por semana**, em média.

Considerando 12 minutos de inspeção em campo para cada alerta falso:

\[
\frac{156{,}624\times12}{60}
=31{,}3248\text{ horas}
\]

**Resultado:** aproximadamente **31,32 horas por semana** são gastas investigando alertas falsos.

**(d) Efeito de aumentar a sensibilidade para 99,9%**

Mantendo a prevalência em 2,11% e a taxa de falsos positivos em 8%:

\[
P(\text{infestado}\mid\text{positivo}) =
\frac{0{,}999\times0{,}0211}
{(0{,}999\times0{,}0211)+(0{,}08\times0{,}9789)}
\approx 0{,}2121
\]

O valor preditivo positivo aumenta de **20,38% para 21,21%**, uma melhora de aproximadamente **0,83 ponto percentual**. Entretanto, a quantidade esperada de alertas falsos por semana não diminui, pois a taxa de falsos positivos permanece em 8%.

Para reduzir os alertas falsos encaminhados ao agrônomo, a cooperativa deveria **priorizar a redução da taxa de falsos positivos**, por exemplo, avaliando uma etapa de confirmação cuja eficácia tenha sido validada. Aumentar apenas a sensibilidade permite identificar mais talhões realmente infestados, mas não resolve o problema de tantos alertas positivos serem falsos.

### 4.4 — Uma decisão que deve permanecer em regra explícita

**Decisão:** o Caatinga.AI não pode autorizar automaticamente a aplicação de defensivos agrícolas. Mesmo que o sensor indique suspeita de infestação ou que um modelo atribua alta prioridade ao talhão, a pulverização só poderá ser autorizada após avaliação e aprovação de um profissional responsável.

**Regra explícita:**

**SE** houver recomendação de pulverização **E** não houver aprovação registrada do profissional responsável, **ENTÃO** bloquear a autorização de pulverização e encaminhar o caso para avaliação humana.

**Justificativa:** essa decisão deve permanecer em uma regra explícita porque é necessário identificar quem autorizou a intervenção e verificar se a aprovação ocorreu antes da execução. A regra permite auditar a decisão por meio dos registros de recomendação, avaliação e autorização. Um modelo aprendido pode auxiliar na identificação de talhões suspeitos, mas não deve substituir a responsabilidade humana pela autorização de uma intervenção com possíveis consequências para a plantação, os trabalhadores e o ambiente.