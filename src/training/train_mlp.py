from __future__ import annotations

import json
import random

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from tensorflow import keras
from tensorflow.keras import layers

from src.config import (
    METRICS_FILE,
    MODEL_FILE,
    RANDOM_STATE,
    TARGET_COLUMN,
    TEST_SIZE,
    TRAINING_HISTORY_FILE,
    VALIDATION_SIZE,
    ensure_project_dirs,
)
from src.preprocessing.data_loader import load_student_performance_data
from src.preprocessing.preprocess import (
    build_preprocessor,
    prepare_features,
    save_preprocessing_artifacts,
    save_processed_dataset,
)


def set_reproducibility(seed: int = RANDOM_STATE) -> None:
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def build_mlp(input_dim: int) -> keras.Model:
    model = keras.Sequential(
        [
            layers.Input(shape=(input_dim,)),
            layers.Dense(64, activation="relu"),
            layers.Dropout(0.25),
            layers.Dense(32, activation="relu"),
            layers.Dropout(0.15),
            layers.Dense(16, activation="relu"),
            layers.Dense(1, activation="sigmoid"),
        ]
    )

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="binary_crossentropy",
        metrics=[
            keras.metrics.BinaryAccuracy(name="accuracy"),
            keras.metrics.Precision(name="precision"),
            keras.metrics.Recall(name="recall"),
        ],
    )
    return model


def _class_weights(y_train: pd.Series) -> dict[int, float]:
    classes = np.unique(y_train)
    weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=y_train.to_numpy(),
    )
    return {int(class_label): float(weight) for class_label, weight in zip(classes, weights)}


def _overfitting_analysis(history: pd.DataFrame) -> str:
    final_train_loss = float(history["loss"].iloc[-1])
    final_val_loss = float(history["val_loss"].iloc[-1])
    final_train_acc = float(history["accuracy"].iloc[-1])
    final_val_acc = float(history["val_accuracy"].iloc[-1])

    loss_gap = final_val_loss - final_train_loss
    acc_gap = final_train_acc - final_val_acc

    if loss_gap > 0.20 and acc_gap > 0.08:
        return (
            "Possible mild overfitting: validation loss is noticeably higher than "
            "training loss. Dropout and early stopping are used to reduce this risk."
        )

    if final_train_acc < 0.70 and final_val_acc < 0.70:
        return (
            "Possible underfitting: both training and validation accuracy are low. "
            "More features, tuning, or a longer training schedule may help."
        )

    return (
        "No strong overfitting or underfitting signal: training and validation curves "
        "remain reasonably close at the end of training."
    )


def train() -> dict:
    ensure_project_dirs()
    set_reproducibility()

    raw_data = load_student_performance_data()
    save_processed_dataset(raw_data)
    prepared = prepare_features(raw_data)

    x_train_full, x_test, y_train_full, y_test = train_test_split(
        prepared.x,
        prepared.y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=prepared.y,
    )
    x_train, x_val, y_train, y_val = train_test_split(
        x_train_full,
        y_train_full,
        test_size=VALIDATION_SIZE,
        random_state=RANDOM_STATE,
        stratify=y_train_full,
    )

    preprocessor = build_preprocessor(
        prepared.numeric_features,
        prepared.categorical_features,
    )
    x_train_transformed = preprocessor.fit_transform(x_train)
    x_val_transformed = preprocessor.transform(x_val)
    x_test_transformed = preprocessor.transform(x_test)

    model = build_mlp(input_dim=x_train_transformed.shape[1])
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=20,
            restore_best_weights=True,
        )
    ]

    history = model.fit(
        x_train_transformed,
        y_train,
        validation_data=(x_val_transformed, y_val),
        epochs=200,
        batch_size=32,
        callbacks=callbacks,
        class_weight=_class_weights(y_train),
        verbose=1,
    )

    probabilities = model.predict(x_test_transformed).reshape(-1)
    predictions = (probabilities >= 0.5).astype(int)

    history_frame = pd.DataFrame(history.history)
    history_frame.to_csv(TRAINING_HISTORY_FILE, index=False)

    metrics = {
        "dataset_rows": int(len(prepared.x)),
        "positive_class": f"{TARGET_COLUMN}=1",
        "test_size": float(TEST_SIZE),
        "decision_threshold": 0.5,
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1_score": float(f1_score(y_test, predictions, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        "classification_report": classification_report(
            y_test,
            predictions,
            target_names=["not_low_performance", "low_performance_risk"],
            zero_division=0,
            output_dict=True,
        ),
        "overfitting_underfitting_analysis": _overfitting_analysis(history_frame),
        "model_architecture": {
            "type": "MLP",
            "hidden_layers": [64, 32, 16],
            "activation": "relu",
            "output_activation": "sigmoid",
            "optimizer": "Adam",
            "loss": "binary_crossentropy",
            "regularization": "Dropout and EarlyStopping",
        },
    }

    model.save(MODEL_FILE)
    save_preprocessing_artifacts(
        preprocessor,
        prepared,
        extra_schema={"transformed_feature_count": int(x_train_transformed.shape[1])},
    )
    METRICS_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    training_metrics = train()
    print(json.dumps(training_metrics, indent=2))

