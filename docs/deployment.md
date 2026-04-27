# Deployment

## API com Docker

1. Baixe os dados:

```bash
python scripts/download_dataset.py
```

2. Treine o modelo:

```bash
python -m src.training.train_mlp
```

3. Construa a imagem:

```bash
docker build -t student-risk-api .
```

4. Execute:

```bash
docker run -p 8000:8000 student-risk-api
```

## Streamlit

Em outro terminal:

```bash
streamlit run app/streamlit_app.py
```

Por padrao, a interface consulta `http://localhost:8000/predict`.

