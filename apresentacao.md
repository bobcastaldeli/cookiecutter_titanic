Roteiro geral da apresentação
Slide 1 — Capa

Legal Intelligence — Early Stage Legal Risk

Objetivo do slide
Abrir a apresentação posicionando o tema como uma solução de priorização jurídica e financeira.

Fala sugerida

“Pessoal, hoje eu vou apresentar a primeira versão do projeto de Legal Intelligence, com foco em early stage legal risk.

A ideia principal é usar dados históricos dos processos para apoiar a priorização da carteira jurídica. O objetivo não é substituir a análise jurídica, mas ajudar o time a decidir melhor onde concentrar esforço primeiro, principalmente quando temos muitos processos, equipe limitada e valores relevantes em jogo.”

Transição

“Antes de entrar no modelo, vou começar explicando qual problema de negócio estamos tentando resolver.”

Slide 2 — Modelo — Early Stage Risk Legal

Objetivo do slide
Reforçar que a apresentação trata de um modelo aplicado ao início da jornada do processo, antes do desfecho final.

Fala sugerida

“Esse modelo foi pensado para atuar em um momento inicial do processo, antes de termos o desfecho final. Por isso usamos o termo early stage.

A proposta é olhar para informações disponíveis no começo ou durante a vida do processo e gerar dois tipos de priorização: uma priorização por risco de perda e uma priorização financeira, combinando probabilidade de perda com valor envolvido.

Com isso, conseguimos transformar uma carteira grande em uma fila mais inteligente para operação, gestão e diretoria.”

Transição

“Agora vou contextualizar o tamanho do problema e por que isso é relevante para o negócio.”

Slide 3 — Early Stage Risk Legal: visão executiva

Objetivo do slide
Explicar em uma página o que é, por que é problema real e o valor financeiro envolvido.

Fala sugerida

“Este slide resume o racional do projeto.

O que estamos fazendo é uma priorização de processos jurídicos usando duas dimensões: a probabilidade de perda e o valor em jogo.

Isso é um problema real porque a carteira é grande, a equipe tem capacidade limitada e as perdas não estão distribuídas de forma uniforme. Em geral, poucos casos concentram parte relevante da exposição e do impacto financeiro.

Na base analisada, temos aproximadamente R$ 2 bilhões em valor total ajuizado, considerando cerca de 79 mil processos massificados passivos. Quando olhamos apenas os processos em curso, ainda temos cerca de R$ 579 milhões em valor ajuizado, distribuídos em pouco mais de 16 mil processos.

Então, a pergunta de negócio é: com esse volume e esse valor em jogo, quais processos devem receber atenção primeiro?”

Transição

“Essa pergunta nos leva diretamente ao problema operacional que o jurídico enfrenta no dia a dia.”

Slide 4 — Problema de negócio

Objetivo do slide
Mostrar que a priorização é necessária por limitação de capacidade e risco de casos relevantes se perderem na massa.

Fala sugerida

“O problema aqui não é apenas ter muitos processos. O problema é ter muitos processos, valores relevantes e capacidade limitada de análise.

Quando não existe uma fila inteligente, a atuação tende a ser mais reativa. O time pode acabar priorizando por ordem de chegada, urgência operacional ou percepção pontual, e com isso casos de alto valor podem ficar perdidos no meio da carteira.

Outro ponto importante é que o valor ajuizado em curso vem crescendo de forma relevante nos últimos anos. Então, quanto maior a carteira, mais difícil fica fazer gestão apenas por análise manual ou regras simples.

A ideia do modelo é justamente ajudar a transformar essa massa de processos em uma fila priorizada, onde o time consegue enxergar primeiro os casos com maior risco e maior impacto.”

Transição

“Para tangibilizar isso, os próximos slides mostram a evolução do valor ajuizado em curso.”

Slide 5 — Valor ajuizado total por ano de início

Objetivo do slide
Mostrar que o volume financeiro dos processos em curso cresceu de forma relevante, especialmente nos anos recentes.

Fala sugerida

“Este gráfico mostra o valor ajuizado dos processos em curso por ano de início.

O que chama atenção é a aceleração nos anos recentes. Em 2023 já temos cerca de R$ 76 milhões, em 2024 cerca de R$ 118 milhões e em 2025 chegamos a aproximadamente R$ 209 milhões.

Isso mostra que a exposição financeira da carteira em curso não é pequena e está bastante concentrada nos anos mais recentes. Portanto, se o time precisa priorizar, faz sentido usar dados para identificar onde está o maior risco e onde está o maior valor.”

Transição

“Se olharmos isso de forma acumulada, a dimensão do problema fica ainda mais clara.”

Slide 6 — Valor ajuizado acumulado por ano de início

Objetivo do slide
Mostrar a exposição acumulada da carteira em curso, chegando a R$ 579 milhões.

Fala sugerida

“Quando acumulamos esse valor ao longo dos anos, chegamos a aproximadamente R$ 579 milhões em valor ajuizado nos processos em curso.

Esse número é importante porque representa a exposição atual da carteira analisada. Não significa que tudo isso será perda, mas mostra o tamanho da mesa onde estamos jogando.

Por isso, o modelo não deve ser visto apenas como uma ferramenta estatística. Ele é uma ferramenta de gestão de carteira. A pergunta que ele ajuda a responder é: dentro desses R$ 579 milhões, quais processos merecem prioridade na análise jurídica e financeira?”

Transição

“Com essa motivação de negócio, agora entro no que o modelo efetivamente faz.”

Slide 7 — O que o modelo faz

Objetivo do slide
Explicar o target, o recorte early-stage e as entregas do modelo sem jargão excessivo.

Fala sugerida

“O modelo foi construído a partir do histórico de processos encerrados, usando o motivo de encerramento para separar os casos em que o banco ganhou dos casos em que o banco perdeu, incluindo situações de condenação ou acordo.

Também fizemos um cuidado importante: o foco foi early-stage. Ou seja, usamos processos passivos massificados, encerrados e com desfecho conhecido, mas evitando informações que só existiriam depois do resultado final. Isso reduz o risco de leakage, ou seja, de o modelo aprender informações que não estariam disponíveis no momento real da decisão.

A entrega principal do modelo é dupla.

Primeiro, um score de risco, que representa a probabilidade de perda do processo.

Segundo, uma prioridade financeira, que combina a probabilidade de perda com o valor ajuizado. Essa segunda visão é importante porque nem todo processo com maior chance de perda é o processo com maior impacto financeiro.”

Transição

“Antes de falar de performance, vale mostrar como a própria base histórica se comporta ao longo do tempo.”

Slide 8 — Volume de processos por ano e desfecho

Objetivo do slide
Mostrar que a taxa de perda varia no tempo e que existe mudança de regime.

Fala sugerida

“Este gráfico mostra o volume de processos por ano e o desfecho: banco ganhou ou banco perdeu.

Além do volume, a linha mostra a taxa de perda. O ponto importante aqui é que a taxa de perda não é estável ao longo do tempo. Ela muda por ano, por contexto, por safra de processos e possivelmente por mudanças operacionais ou jurídicas.

Isso é muito importante para modelagem. Se a gente validasse o modelo de forma aleatória, misturando passado e futuro, poderíamos ter uma visão otimista demais. Por isso, a validação precisa respeitar o tempo.”

Transição

“E é exatamente isso que mostramos no próximo slide: como validamos o modelo.”

Slide 9 — Como validamos

Objetivo do slide
Passar confiança metodológica sem aprofundar demais em técnica.

Fala sugerida

“Para validar o modelo, usamos uma abordagem temporal.

Primeiro, fizemos validação walk-forward, que simula o modelo sendo treinado no passado e testado em períodos futuros. Isso é importante porque se aproxima mais do uso real.

Segundo, separamos um holdout recente, que nunca foi usado para escolher o modelo. Esse holdout funciona como um teste final, mais honesto, para avaliar se o modelo generaliza para um período mais próximo do cenário atual.

Também fizemos calibração usando Venn-Abers, para alinhar melhor a probabilidade prevista com a frequência real observada.

E, por fim, avaliamos o modelo por métricas de priorização, como precision no top 5%, top 10% e top 20%. Para o negócio, isso é mais útil do que olhar apenas AUC, porque o que interessa é saber se os processos no topo da fila realmente concentram perdas.”

Transição

“Visualmente, a lógica da validação temporal é essa aqui.”

Slide 10 — Walk-forward / validação temporal

Objetivo do slide
Explicar a validação temporal de forma visual e intuitiva.

Fala sugerida

“Este desenho ilustra a ideia da validação temporal.

Em cada rodada, treinamos o modelo com um período histórico e testamos em um período posterior. Depois avançamos no tempo e repetimos o processo.

Isso evita uma armadilha comum: treinar e testar o modelo com dados misturados no tempo. Em problemas jurídicos, isso é especialmente importante, porque o comportamento dos processos, os tipos de ação, as decisões e até a estratégia jurídica podem mudar ao longo dos anos.

Então, essa validação nos ajuda a responder: se eu tivesse usado o modelo naquele momento, ele teria ajudado a priorizar melhor os processos futuros?”

Transição

“Com a validação definida, agora podemos olhar para a performance do modelo.”

Slide 11 — Precision-Recall no holdout

Objetivo do slide
Mostrar que o modelo performa acima da taxa base e consegue priorizar melhor que acaso.

Fala sugerida

“Este gráfico é uma curva precision-recall no holdout.

A linha pontilhada representa a taxa base de perda no período de validação, cerca de 40,7%. Isso significa que, se eu escolhesse processos de forma aleatória, em média 4 em cada 10 seriam perdas.

A curva azul mostra o desempenho do modelo. O ponto principal é que, no começo da curva, onde estão os processos com maior score, a precisão fica muito acima da taxa base. Ou seja, o modelo consegue concentrar no topo da fila uma proporção muito maior de processos que de fato viraram perda.

Em termos de negócio: o modelo não é perfeito, mas ele é claramente melhor do que escolher processos ao acaso.”

Transição

“Além de ranquear bem, precisamos garantir que a probabilidade gerada pelo modelo seja interpretável. É aqui que entra a calibração.”

Slide 12 — Calibração

Objetivo do slide
Explicar que a probabilidade do modelo foi ajustada para ficar mais próxima da frequência real.

Fala sugerida

“Este gráfico mostra a calibração do modelo.

A linha pontilhada representa o cenário ideal: se o modelo prevê 70% de risco, esperamos que aproximadamente 70% dos casos daquele grupo virem perda na prática.

A calibração serve para aproximar a probabilidade prevista da taxa observada. Isso é importante porque, para gestão, não basta o modelo ordenar bem os casos. A probabilidade também precisa fazer sentido para ser usada em discussões de risco, priorização e governança.

A versão calibrada, em vermelho, fica mais alinhada à linha ideal em vários pontos. Isso nos dá mais segurança para usar a probabilidade como insumo de decisão, principalmente quando combinamos risco com valor financeiro.”

Transição

“Agora vou traduzir essas métricas em linguagem de negócio, antes de mostrar os resultados principais.”

Slide 13 — Resultado financeiro principal: métricas explicadas

Objetivo do slide
Preparar a audiência para entender precision, recall, lift, share de valor e prioridade financeira.

Fala sugerida

“Antes de olhar os números finais, vale traduzir as principais métricas.

Precision no top k significa: entre os processos que o modelo colocou no topo da fila, quantos de fato foram perda.

Recall no top k significa: de todas as perdas que existiam na carteira, quantas apareceram dentro daquele recorte priorizado.

Lift mostra quantas vezes a fila do modelo é melhor do que escolher ao acaso. Se o lift é duas vezes, significa que a fila é duas vezes mais concentrada em perdas do que uma seleção aleatória.

Share de valor de perdas mostra o percentual do dinheiro das perdas históricas que está coberto pelo top k financeiro.

E a prioridade financeira é uma segunda fila: em vez de ordenar só pela probabilidade de perda, ela ordena por probabilidade de perda vezes valor ajuizado. Ou seja, foca em reais, não apenas em quantidade de processos.”

Transição

“Com essa tradução, agora podemos ir para o principal resultado do modelo.”

Slide 14 — Resultado financeiro principal: acerto na fila

Objetivo do slide
Mostrar que o modelo consegue identificar processos que realmente viram perda no topo da fila.

Fala sugerida

“Este é um dos principais slides da apresentação.

No holdout, a taxa média de perda era de aproximadamente 40,7%. Ou seja, se escolhêssemos processos ao acaso, esperaríamos acertar cerca de 4 em cada 10.

Quando usamos o modelo e olhamos apenas o top 5%, temos 627 processos priorizados. Dentro desse grupo, o acerto é de 80,1%. Em linguagem simples: de cada 10 processos que o modelo coloca como mais críticos, cerca de 8 realmente terminaram como perda.

No top 10%, com 1.254 processos, o acerto continua alto, em 75%. No top 20%, com 2.507 processos, ainda temos 70,1% de acerto.

Então, a mensagem aqui é: o modelo consegue criar uma fila de risco muito melhor do que a escolha aleatória. Ele praticamente dobra a capacidade de encontrar perdas no topo da fila.”

Transição

“Mas para o negócio, além de saber quais processos têm maior chance de perda, precisamos entender onde está o maior impacto financeiro em reais.”

Slide 15 — Impacto financeiro em reais

Objetivo do slide
Mostrar quanto valor financeiro é concentrado pela priorização do modelo.

Fala sugerida

“Agora traduzimos a priorização para reais.

No top 5%, estamos falando de 627 processos, que concentram aproximadamente R$ 87 milhões em valor de causa. Dentro desse grupo, cerca de R$ 39 milhões estão associados a perdas históricas capturadas, o que representa aproximadamente 32% do valor total das perdas em reais no holdout.

Quando ampliamos para o top 10%, chegamos a R$ 118 milhões em valor de causa e R$ 54 milhões em perdas capturadas, cerca de 44% das perdas em reais.

E no top 20%, que representa 2.507 processos, temos aproximadamente R$ 162 milhões em valor de causa e R$ 76 milhões em perdas capturadas. Isso equivale a cerca de 62% de todo o valor perdido no período avaliado.

Então, a principal mensagem é: com uma fração da carteira, conseguimos concentrar uma parte muito relevante do dinheiro das perdas. O modelo ajuda a direcionar esforço para onde o impacto financeiro é maior.”

Transição

“Depois de mostrar o resultado, a próxima pergunta natural é: como isso vira operação dentro do Benner e da rotina do jurídico?”

Slide 16 — Como usar em conjunto com o Benner

Objetivo do slide
Transformar o modelo em rotina operacional com papéis claros.

Fala sugerida

“Aqui está a proposta de uso prático em três níveis.

No primeiro nível, temos a fila diária. Essa fila seria usada por analistas e escritórios, priorizando o top 5% ou top 10% de risco e financeiro. A ideia é orientar a primeira ação: quais processos olhar primeiro, quais precisam de atenção mais rápida, quais devem ter SLA diferenciado.

No segundo nível, temos a gestão semanal. A coordenação pode acompanhar um painel com aging, falsos positivos, temas recorrentes, evolução das filas e capacidade de tratamento.

No terceiro nível, temos a diretoria e a governança. Aqui o foco é acompanhar KPIs, captura em reais, capacidade versus top k, exposição por carteira, produto, tema ou escritório.

Ou seja, o modelo não deve ficar apenas como uma planilha ou score isolado. Ele precisa virar uma fila operacional e um painel de gestão.”

Transição

“Para isso funcionar com segurança, precisamos também tratar riscos, governança e evolução contínua do modelo.”

Slide 17 — Riscos e governança (+ active learning)

Objetivo do slide
Mostrar maturidade: o modelo apoia, não decide; precisa de monitoramento, recalibração e aprendizado contínuo.

Fala sugerida

“Este slide é importante para deixar claro o papel do modelo.

O modelo apoia a decisão, mas não decide sozinho. A decisão continua sendo jurídica e de negócio.

Também existe risco de drift temporal. Já vimos que a taxa de perda muda entre períodos. Por exemplo, no desenvolvimento a taxa era diferente da taxa observada no holdout. Isso significa que o modelo precisa ser monitorado e recalibrado ao longo do tempo.

Uma oportunidade importante é usar active learning. Casos em que o modelo tem alta incerteza, por exemplo scores próximos de 0,5 ou intervalos de calibração muito largos, podem ser revisados pelo jurídico e depois usados para melhorar o modelo.

A recomendação é ter recalibração trimestral e uma lógica de champion-challenger. Ou seja, mantemos um modelo campeão em produção, mas testamos novas versões em paralelo antes de substituir.”

Transição

“Com esse cuidado de governança, os próximos passos ficam mais claros.”

Slide 18 — Próximos passos

Objetivo do slide
Fechar com plano de ação concreto e alinhamento com negócio.

Fala sugerida

“Para fechar, os próximos passos estão em cinco frentes.

Primeiro, integrar Benner e DeepLegal para rodar a inferência batch e gerar a fila priorizada na base ativa.

Segundo, incorporar novos dados, principalmente petições e dados internos adicionais. Isso pode melhorar bastante a capacidade do modelo, porque hoje estamos trabalhando principalmente com dados estruturados.

Terceiro, definir como servir o resultado. A pergunta prática é: a fila deve aparecer dentro do Benner, em um painel, em uma exportação recorrente ou em algum fluxo combinado?

Quarto, evoluir para modelos futuros. Além da probabilidade de perda, podemos estimar valor esperado por causa, duração do processo e similaridade textual entre petições.

E quinto, propor um piloto. Minha sugestão é começar com um top 1.000 processos e fazer um workshop jurídico para validar a qualidade da fila, entender falsos positivos, capturar feedback dos especialistas e transformar isso em melhoria do modelo.

A mensagem final é: já temos evidência de que o modelo prioriza melhor que o acaso e concentra valor financeiro relevante. Agora o próximo passo é transformar essa evidência em operação assistida, com governança e validação do jurídico.”

Fechamento geral da apresentação

Você pode encerrar assim:

“Em resumo, o projeto mostra três coisas.

Primeiro, existe uma exposição relevante: a carteira em curso tem cerca de R$ 579 milhões em valor ajuizado.

Segundo, o modelo consegue priorizar melhor do que uma escolha aleatória. No top 5%, cerca de 8 em cada 10 processos priorizados terminariam como perda.

Terceiro, quando usamos a priorização financeira, conseguimos concentrar uma parte importante do valor das perdas. No top 20%, capturamos cerca de 62% do valor histórico das perdas em reais.

Então, o valor do modelo está em ajudar o jurídico e a gestão a sair de uma carteira ampla para uma carteira priorizada por risco e impacto financeiro. Ele não substitui a análise jurídica, mas melhora a fila de trabalho, apoia governança e ajuda a direcionar capacidade para os casos de maior relevância.”

Versão curta, caso você precise apresentar em menos tempo

“Este projeto nasce de um problema simples: temos muitos processos, uma exposição financeira relevante e capacidade limitada para analisar tudo com a mesma profundidade.

A carteira em curso tem cerca de 16 mil processos e aproximadamente R$ 579 milhões em valor ajuizado. Então, a pergunta de negócio é: quais processos devem ser priorizados primeiro?

O modelo responde isso de duas formas. A primeira é a fila de risco, que ordena os processos pela probabilidade de perda. A segunda é a fila financeira, que combina probabilidade de perda com valor ajuizado.

Na validação recente, o modelo mostrou que consegue priorizar melhor do que o acaso. No top 5%, cerca de 8 em cada 10 processos priorizados pelo modelo realmente terminaram como perda, contra uma taxa média da carteira de aproximadamente 4 em cada 10.

Quando traduzimos isso para reais, o resultado também é relevante. No top 20% financeiro, o modelo concentra cerca de R$ 162 milhões em valor de causa e captura aproximadamente R$ 76 milhões em perdas históricas, equivalentes a 62% do valor total das perdas em reais.

A proposta agora é transformar isso em operação: gerar uma fila priorizada no Benner ou em painel, validar com o jurídico em um piloto com os top 1.000 processos, capturar feedback e evoluir o modelo com novos dados, como petições e informações internas.

A mensagem final é: o modelo não decide pelo jurídico, mas ajuda a colocar a energia do time nos processos certos, mais cedo, com foco em risco e impacto financeiro.”