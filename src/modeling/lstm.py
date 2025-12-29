import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class LstmModel:
    def __init__(self, input_shape):
        """
        input_shape: (TimeSteps, Features)
        """
        self.input_shape = input_shape
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        # Layer 1: LSTM with return sequences
        model.add(LSTM(64, return_sequences=True, input_shape=self.input_shape))
        model.add(Dropout(0.2))
        
        # Layer 2: LSTM without return sequences
        model.add(LSTM(32, return_sequences=False))
        model.add(Dropout(0.2))
        
        # Output Layer
        model.add(Dense(1)) # Predict PM2.5
        
        model.compile(optimizer='adam', loss='mse')
        return model

    def train(self, X_train, y_train, validation_data=None):
        print("Training LSTM Model (Advanced)...")
        
        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
            tf.keras.callbacks.ModelCheckpoint(
                filepath=os.path.join(Config.MODEL_DIR, "lstm_best.keras"),
                monitor='val_loss',
                save_best_only=True
            )
        ]
        
        history = self.model.fit(
            X_train, y_train,
            epochs=Config.LSTM_EPOCHS,
            batch_size=Config.LSTM_BATCH_SIZE,
            validation_data=validation_data,
            callbacks=callbacks,
            verbose=1
        )
        # self.model.save(os.path.join(Config.MODEL_DIR, "lstm_model.h5")) # Legacy
        self.model.save(os.path.join(Config.MODEL_DIR, "lstm_model.keras"))
        print("LSTM model saved.")
        return history

    def predict(self, X):
        return self.model.predict(X)
