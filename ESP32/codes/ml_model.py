import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, precision_score, recall_score, mean_squared_error, ConfusionMatrixDisplay
import keras_tuner as kt
import matplotlib.pyplot as plt
from scipy.ndimage import rotate, shift, gaussian_filter

# Load dataset
def load_data(dataset_dir):
    X, y = [], []

    for file in os.listdir(dataset_dir):
        if file.endswith('.npy'):
            path = os.path.join(dataset_dir, file)
            frame = np.load(path)
            label = int(file.split('_')[3])
            X.append(frame)
            y.append(label)

    X = np.array(X)
    y = np.array(y)
    print(f"Loaded dataset: {X.shape}, labels: {y.shape}")
    return X, y

# Data augmentation
def augment_data(X, y):
    X_aug, y_aug = [], []

    for img, label in zip(X, y):
        X_aug.append(img)
        y_aug.append(label)

        for angle in [90, 180, 270]:
            X_aug.append(rotate(img, angle, reshape=False))
            y_aug.append(label)

        X_aug.append(np.fliplr(img))
        y_aug.append(label)

        X_aug.append(shift(img, (1,1), mode='nearest'))
        y_aug.append(label)

        X_aug.append(img + np.random.normal(0, 0.1, img.shape))
        y_aug.append(label)

        X_aug.append(gaussian_filter(img, sigma=0.5))
        y_aug.append(label)

    return np.array(X_aug, dtype=np.float32), np.array(y_aug, dtype=np.int32)

# Model builder
def model_builder(hp):
    model = models.Sequential([
        layers.Input(shape=(24,32,1)),
        layers.Conv2D(hp.Int('filters1',16,64,16), 3, activation='relu'),
        layers.MaxPooling2D(2),
        layers.Conv2D(hp.Int('filters2',32,128,32), 3, activation='relu'),
        layers.MaxPooling2D(2),
        layers.Flatten(),
        layers.Dense(hp.Int('dense_units',32,128,32), activation='relu'),
        layers.Dropout(hp.Float('dropout',0.2,0.5,0.1)),
        layers.Dense(len(np.unique(y)), activation='softmax')
    ])

    optimizer_choice = hp.Choice('optimizer',['adam','rmsprop','sgd'])
    lr = hp.Float('lr',1e-5,1e-2,sampling='log')

    if optimizer_choice == 'adam':
        optimizer = optimizers.Adam(lr)
    elif optimizer_choice == 'rmsprop':
        optimizer = optimizers.RMSprop(lr)
    else:
        optimizer = optimizers.SGD(lr, momentum=0.9)

    model.compile(
        optimizer=optimizer,
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

# Plotting function enhanced with RMSE, Precision, Recall, Confusion Matrix
def plot_results(history, model, X_test, y_test):
    y_pred = np.argmax(model.predict(X_test), axis=1)

    # Accuracy and Loss plots
    fig, axs = plt.subplots(1, 2, figsize=(12,4))
    axs[0].plot(history.history['accuracy'], label='Train Accuracy')
    axs[0].plot(history.history['val_accuracy'], label='Val Accuracy')
    axs[0].set_title('Accuracy')
    axs[0].legend()

    axs[1].plot(history.history['loss'], label='Train Loss')
    axs[1].plot(history.history['val_loss'], label='Val Loss')
    axs[1].set_title('Loss')
    axs[1].legend()
    plt.tight_layout()
    plt.show()

    # RMSE Plot
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    plt.figure(figsize=(5,4))
    plt.bar(['RMSE'], [rmse], color='skyblue')
    plt.title(f'Root Mean Squared Error (RMSE): {rmse:.4f}')
    plt.ylabel('RMSE')
    plt.show()

    # Precision and Recall
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)

    plt.figure(figsize=(5,4))
    plt.bar(['Precision', 'Recall'], [precision, recall], color=['lightgreen','orange'])
    plt.title('Precision and Recall')
    plt.ylim([0,1])
    plt.ylabel('Score')
    plt.show()

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(cm, display_labels=np.unique(y_test))
    fig, ax = plt.subplots(figsize=(6,6))
    disp.plot(ax=ax, cmap='Blues')
    plt.title('Confusion Matrix')
    plt.show()

if __name__ == "__main__":
    DATASET_DIR = "./dataset"

    X, y = load_data(DATASET_DIR)
    X, y = augment_data(X, y)

    X = X[..., np.newaxis] / np.max(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    tuner = kt.RandomSearch(
        model_builder,
        objective='val_accuracy',
        max_trials=20,
        executions_per_trial=2,
        directory='keras_tuner_dir',
        project_name='thermal_cnn_tuning_v2'
    )

    tuner.search(
        X_train, y_train,
        epochs=50,
        validation_split=0.2,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        ]
    )

    best_hp = tuner.get_best_hyperparameters()[0]
    print(f"\nBest Hyperparameters:\n"
          f"Conv Filters 1: {best_hp.get('filters1')}\n"
          f"Conv Filters 2: {best_hp.get('filters2')}\n"
          f"Dense Units: {best_hp.get('dense_units')}\n"
          f"Dropout Rate: {best_hp.get('dropout')}\n"
          f"Optimizer: {best_hp.get('optimizer')}\n"
          f"Learning Rate: {best_hp.get('lr'):.5f}")

    best_model = tuner.hypermodel.build(best_hp)
    history = best_model.fit(
        X_train, y_train,
        epochs=50,
        validation_data=(X_test, y_test),
        callbacks=[
            tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        ]
    )

    # Evaluate and plot results
    plot_results(history, best_model, X_test, y_test)

    # Final evaluation
    test_loss, test_acc = best_model.evaluate(X_test, y_test, verbose=2)
    print(f"\nFinal Test accuracy: {test_acc:.4f}")

    # Save the final model
    model_name = "DATH-V0.02.keras"
    best_model.save(model_name)
    print(f"Model saved as '{model_name}'")
