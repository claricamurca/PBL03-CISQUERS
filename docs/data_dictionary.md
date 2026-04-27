# Dicionario de dados

O projeto usa exclusivamente o dataset UCI/Kaggle **Student Performance / Student Alcohol Consumption**.

Arquivos esperados em `data/raw/`:

- `student-mat.csv`: desempenho em Matematica.
- `student-por.csv`: desempenho em Portugues.

Os dois arquivos possuem a mesma estrutura. A pipeline adiciona a coluna `subject` para identificar a origem do registro.

## Variavel alvo

`risk_low_performance` e criada a partir de `G3`, a nota final:

- `1`: estudante em risco, quando `G3 < 10`.
- `0`: estudante sem risco elevado, quando `G3 >= 10`.

Essa regra usa o limiar 10 porque as notas do dataset variam de 0 a 20 e 10 representa o ponto minimo usual de aprovacao.

## Principais grupos de variaveis

- Dados escolares: `school`, `subject`, `traveltime`, `studytime`, `failures`, `schoolsup`, `paid`, `activities`, `absences`, `G1`, `G2`.
- Dados familiares: `famsize`, `Pstatus`, `Medu`, `Fedu`, `Mjob`, `Fjob`, `guardian`, `famsup`, `famrel`.
- Dados sociais e pessoais: `sex`, `age`, `address`, `nursery`, `higher`, `internet`, `romantic`, `freetime`, `goout`, `Dalc`, `Walc`, `health`.

`G3` nao entra como atributo de entrada, pois e usado apenas para construir a variavel alvo durante o treinamento.

