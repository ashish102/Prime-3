"""
TensorFlow-based neural network for prime classification.

This module trains a small feed-forward neural network to predict whether a
number is prime. It uses the numbers 1-1000 for training and 1001-2000 for
testing, extracting bit-level and modular arithmetic features to help the
model learn patterns that distinguish prime numbers from composites.

The script can be executed directly:

    python -m prime.prime_nn

It will output training metrics, evaluation results on the held-out test set,
and a few example predictions.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterable, Tuple

import numpy as np
import tensorflow as tf

from prime.nt import is_prime_64


# Seed everything for reproducibility
def _set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def _binary_features(numbers: np.ndarray, width: int) -> np.ndarray:
    """Return binary representation features for each number."""
    # Shape: (n_samples, width)
    return ((numbers[:, None] >> np.arange(width)) & 1).astype(np.float32)


def _modular_features(numbers: np.ndarray, moduli: Iterable[int]) -> np.ndarray:
    """Return normalized remainders for each modulus in `moduli`."""
    features = []
    for modulus in moduli:
        remainder = (numbers % modulus) / float(modulus)
        features.append(remainder.astype(np.float32))
    return np.stack(features, axis=1)


def _build_feature_matrix(numbers: np.ndarray) -> np.ndarray:
    """
    Build feature matrix using binary digits, normalized magnitude, square root,
    and modular remainders.
    """
    numbers = numbers.astype(np.int32)
    max_number = float(numbers.max())

    # 11 bits cover numbers up to 2047
    binary = _binary_features(numbers, width=11)

    normalized = (numbers / max_number).astype(np.float32)[:, None]
    sqrt_normalized = (np.sqrt(numbers) / math.sqrt(max_number)).astype(np.float32)[:, None]

    modular = _modular_features(numbers, moduli=(2, 3, 5, 7, 11, 13))

    return np.concatenate([binary, normalized, sqrt_normalized, modular], axis=1)


def _build_labels(numbers: Iterable[int]) -> np.ndarray:
    """Compute primality labels for the provided numbers."""
    labels = [1 if is_prime_64(int(n)) else 0 for n in numbers]
    return np.array(labels, dtype=np.float32)


def _train_test_split(
    train_range: Tuple[int, int] = (1, 1000),
    test_range: Tuple[int, int] = (1001, 2000),
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate training and testing datasets."""
    train_numbers = np.arange(train_range[0], train_range[1] + 1, dtype=np.int32)
    test_numbers = np.arange(test_range[0], test_range[1] + 1, dtype=np.int32)

    x_train = _build_feature_matrix(train_numbers)
    y_train = _build_labels(train_numbers)

    x_test = _build_feature_matrix(test_numbers)
    y_test = _build_labels(test_numbers)

    return x_train, y_train, x_test, y_test, train_numbers, test_numbers


def _build_model(input_dim: int) -> tf.keras.Model:
    """Construct the neural network architecture."""
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(input_dim,)),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="accuracy"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
        ],
    )
    return model


@dataclass
class EvaluationResult:
    accuracy: float
    precision: float
    recall: float
    specificity: float
    f1_score: float


def _evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> EvaluationResult:
    """Compute common classification metrics."""
    y_hat = (y_pred >= 0.5).astype(np.float32)

    tp = float(np.sum((y_true == 1) & (y_hat == 1)))
    tn = float(np.sum((y_true == 0) & (y_hat == 0)))
    fp = float(np.sum((y_true == 0) & (y_hat == 1)))
    fn = float(np.sum((y_true == 1) & (y_hat == 0)))

    accuracy = (tp + tn) / max(len(y_true), 1)
    precision = tp / (tp + fp) if tp + fp > 0 else 0.0
    recall = tp / (tp + fn) if tp + fn > 0 else 0.0
    specificity = tn / (tn + fp) if tn + fp > 0 else 0.0
    if precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0.0

    return EvaluationResult(
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        specificity=specificity,
        f1_score=f1,
    )


def train_and_evaluate(
    epochs: int = 200,
    batch_size: int = 32,
    patience: int = 20,
) -> Tuple[tf.keras.Model, EvaluationResult]:
    """Train the neural network and evaluate it on the held-out test set."""
    _set_seed()

    x_train, y_train, x_test, y_test, train_numbers, test_numbers = _train_test_split()
    model = _build_model(input_dim=x_train.shape[1])

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=patience,
            restore_best_weights=True,
            verbose=1,
        )
    ]

    history = model.fit(
        x_train,
        y_train,
        validation_split=0.1,
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=0,
    )

    _, acc, prec, rec = model.evaluate(x_test, y_test, verbose=0)
    y_pred = model.predict(x_test, verbose=0).flatten()
    summary = _evaluate_predictions(y_test, y_pred)

    print("Training complete.")
    print(f"Best validation accuracy: {max(history.history['val_accuracy']):.4f}")
    print(f"Test accuracy: {acc:.4f}")
    print(f"Test precision: {prec:.4f}")
    print(f"Test recall: {rec:.4f}")
    print(f"Test specificity: {summary.specificity:.4f}")
    print(f"Test F1 score: {summary.f1_score:.4f}")

    # Show a few example predictions
    sample_indices = np.linspace(0, len(test_numbers) - 1, num=10, dtype=int)
    print("\nSample predictions (number -> predicted probability, label):")
    for idx in sample_indices:
        number = int(test_numbers[idx])
        probability = y_pred[idx]
        label = "prime" if probability >= 0.5 else "composite"
        actual = "prime" if y_test[idx] == 1 else "composite"
        print(f"{number:4d} -> {probability:0.4f} ({label}, actual: {actual})")

    return model, summary


if __name__ == "__main__":
    train_and_evaluate()
