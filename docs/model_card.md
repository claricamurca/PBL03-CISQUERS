# Model card

## Objetivo

Prever risco de baixo desempenho escolar para apoiar gestores publicos na priorizacao de acompanhamento pedagogico.

## Tipo de problema

Classificacao binaria:

- Classe positiva: risco de baixo desempenho (`G3 < 10`).
- Classe negativa: sem risco elevado (`G3 >= 10`).

## Modelo

Rede neural MLP implementada com TensorFlow/Keras:

- Entrada: atributos numericos padronizados e categoricos codificados com one-hot encoding.
- Camadas ocultas: 64, 32 e 16 neuronios.
- Ativacao: ReLU nas camadas ocultas.
- Saida: sigmoid.
- Otimizador: Adam.
- Funcao de perda: binary crossentropy.
- Regularizacao: dropout e early stopping.

## Uso previsto

O sistema deve ser usado como apoio a decisao, nao como decisao automatica final. A saida indica prioridade de acompanhamento, revisao pedagogica e possivel intervencao escolar.

## Limitacoes

- O dataset representa estudantes de duas escolas portuguesas, entao nao deve ser tratado como retrato completo da realidade brasileira.
- Variaveis sociofamiliares podem refletir desigualdades estruturais. O uso deve priorizar apoio e cuidado, nunca punicao.
- O modelo depende de `G1` e `G2`, o que torna a previsao mais adequada durante o ano letivo, antes da nota final.
- A base e pequena para padroes modernos de redes neurais; os resultados devem ser interpretados com cautela.

