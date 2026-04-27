# Sistema Inteligente de Previsão de Desempenho Escolar

Projeto acadêmico de Inteligência Artificial e Engenharia de Software para apoiar gestores da educação pública na identificação de estudantes com risco de baixo desempenho escolar.

O sistema usa exclusivamente o dataset **Student Performance / Student Alcohol Consumption** da UCI/Kaggle, treina uma rede neural MLP, expõe previsões por API FastAPI e oferece uma interface simples em Streamlit para testes manuais.

## 1. Entendimento do problema

Gestores públicos precisam priorizar ações pedagógicas com recursos limitados. A hipótese deste projeto é que dados históricos escolares, familiares e sociais podem indicar risco de baixo desempenho antes da nota final, permitindo acompanhamento preventivo.

Objetivo da solução:

- analisar e preparar dados históricos de estudantes;
- treinar um modelo de classificação binária;
- prever risco de baixo desempenho acadêmico;
- disponibilizar o resultado em uma API e em uma interface web simples;
- organizar o projeto como uma entrega de equipe técnica real.

## 2. Dataset

Dataset principal e único:

- UCI/Kaggle Student Performance / Student Alcohol Consumption.
- Arquivos usados: `student-mat.csv` e `student-por.csv`.
- A pipeline adiciona a coluna `subject` para diferenciar Matemática e Português.

Para baixar os dados oficiais:

```bash
python scripts/download_dataset.py
```

Os arquivos baixados ficam em `data/raw/`.

## 3. Variável alvo

O problema foi definido como **classificação binária**.

A nota final `G3` varia de 0 a 20. Foi criada a variável:

```text
risk_low_performance = 1 se G3 < 10
risk_low_performance = 0 se G3 >= 10
```

Justificativa: em uma escala de 0 a 20, o valor 10 representa o ponto mínimo usual de aprovação. Portanto, `G3 < 10` indica desempenho final insuficiente e é um limiar claro para uma ação de gestão escolar.

`G3` não é usado como entrada do modelo, pois serve apenas para gerar a classe alvo. As notas `G1` e `G2` permanecem como atributos porque representam desempenho parcial disponível antes da nota final.

## 4. Estrutura do projeto

```text
.
├── analysis/                 # EDA e geração de gráficos
├── api/                      # Backend FastAPI
├── app/                      # Interface Streamlit
├── data/
│   ├── raw/                  # CSVs originais baixados
│   └── processed/            # Dados processados
├── docs/                     # Documentação complementar
├── models/                   # Modelo e preprocessor persistidos
├── outputs/                  # Métricas, histórico e gráficos
├── scripts/                  # Scripts operacionais
└── src/
    ├── inference/            # Predição reutilizável
    ├── preprocessing/        # Carga, limpeza e transformação
    ├── training/             # Treinamento da MLP
    └── utils/
```

Essa separação permite colaboração por uma equipe de 4 pessoas: dados/EDA, modelagem, backend e frontend/documentação.

## 5. Pipeline de dados

Implementado em `src/preprocessing/`:

- leitura dos CSVs da UCI;
- remoção de duplicidades;
- tratamento de strings e valores ausentes;
- criação da variável alvo;
- separação entre variáveis numéricas e categóricas;
- imputação de valores ausentes;
- padronização de numéricos com `StandardScaler`;
- codificação de categóricos com `OneHotEncoder`;
- persistência do preprocessor com `joblib`.

Para gerar EDA:

```bash
python -m analysis.eda
```

Saídas em `outputs/`:

- `eda_summary.json`;
- `final_grade_distribution.png`;
- `risk_by_previous_failures.png`;
- `g2_vs_final_grade.png`.

## 6. Modelo de IA

Modelo escolhido: **MLP (Multilayer Perceptron)** com TensorFlow/Keras.

Arquitetura:

- entrada com atributos transformados;
- camada densa com 64 neurônios e ReLU;
- dropout de 0.25;
- camada densa com 32 neurônios e ReLU;
- dropout de 0.15;
- camada densa com 16 neurônios e ReLU;
- saída sigmoid para probabilidade de risco.

Configuração:

- otimizador: Adam;
- função de perda: binary crossentropy;
- validação estratificada;
- early stopping;
- pesos de classe para lidar com desbalanceamento.

Treinamento:

```bash
python -m src.training.train_mlp
```

Artefatos gerados:

- `models/mlp_student_risk.h5`;
- `models/preprocessor.joblib`;
- `models/feature_schema.json`;
- `outputs/metrics.json`;
- `outputs/training_history.csv`.

## 7. Resultados obtidos

Execução local com 1.044 registros combinando Matemática e Português:

| Métrica | Valor |
|---|---:|
| Accuracy | 0.885 |
| Precision | 0.690 |
| Recall | 0.870 |
| F1-score | 0.769 |

Matriz de confusão no teste:

```text
[[145, 18],
 [  6, 40]]
```

Interpretação:

- O recall da classe de risco ficou alto, o que é adequado para gestão educacional porque reduz o número de estudantes em risco não identificados.
- A precision é menor que o recall, indicando alguns falsos positivos. Em um contexto público, isso é aceitável quando a ação resultante é acompanhamento pedagógico, não punição.
- A análise de treino/validação não indicou sinal forte de overfitting ou underfitting. O modelo usa dropout e early stopping para reduzir esse risco.

## 8. API FastAPI

Rodar localmente:

```bash
uvicorn api.main:app --reload
```

Endpoints:

- `GET /`: status do projeto;
- `GET /health`: health check;
- `GET /features`: schema de atributos;
- `POST /predict`: previsão de risco.

Exemplo de payload:

```json
{
  "school": "GP",
  "sex": "F",
  "age": 16,
  "address": "U",
  "famsize": "GT3",
  "Pstatus": "T",
  "Medu": 3,
  "Fedu": 2,
  "Mjob": "services",
  "Fjob": "other",
  "reason": "course",
  "guardian": "mother",
  "traveltime": 1,
  "studytime": 2,
  "failures": 0,
  "schoolsup": "no",
  "famsup": "yes",
  "paid": "no",
  "activities": "yes",
  "nursery": "yes",
  "higher": "yes",
  "internet": "yes",
  "romantic": "no",
  "famrel": 4,
  "freetime": 3,
  "goout": 3,
  "Dalc": 1,
  "Walc": 2,
  "health": 3,
  "absences": 4,
  "G1": 9,
  "G2": 8,
  "subject": "mathematics"
}
```

## 9. Interface Streamlit

Com a API rodando:

```bash
streamlit run app/streamlit_app.py
```

A interface permite preencher manualmente os dados de um estudante e consultar a API para obter:

- probabilidade de risco;
- classe prevista;
- rótulo operacional para o gestor.

## 10. Deploy

Opção com Docker:

```bash
docker build -t student-risk-api .
docker run -p 8000:8000 student-risk-api
```

Também há um `Procfile` para plataformas compatíveis com processos web.

Observação para Windows: se a instalação do TensorFlow falhar por limite de caminho, habilite Windows Long Path Support ou use Docker/WSL/ambiente virtual em um caminho curto.

## 11. Limitações e uso responsável

- O dataset vem de escolas portuguesas e não representa automaticamente todas as redes públicas brasileiras.
- O sistema deve apoiar decisões humanas, não substituir avaliação pedagógica.
- As variáveis sociofamiliares podem refletir desigualdades estruturais; o uso correto é priorizar apoio, cuidado e acompanhamento.
- A base é pequena para redes neurais profundas, então os resultados devem ser interpretados como evidência acadêmica e protótipo funcional.

## 12. Checklist atendido

- problema e objetivo definidos;
- dataset único escolhido e justificado;
- limpeza, transformação e feature engineering;
- EDA com gráficos;
- classificação binária com MLP;
- treinamento, validação e métricas;
- análise de overfitting/underfitting;
- persistência de modelo e preprocessor;
- API FastAPI;
- frontend Streamlit;
- estrutura modular para equipe;
- documentação e setup de deploy.
