from models.model import Model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout 
from tensorflow.keras.optimizers import RMSprop, SGD, Adam, Nadam

class DropoutModel(Model):
    def _define_model(self, input_shape, categories_count):
        # Your code goes here

        self.model = Sequential()
        # Block 1
        self.model.add(Conv2D(16, (3, 3), activation='relu',
                       kernel_initializer='he_uniform', padding='same', input_shape=input_shape))
        self.model.add(MaxPooling2D((2, 2)))
        self.model.add(Dropout(0.2))
        
        # Block 2
        self.model.add(Conv2D(32, (3, 3), activation='relu',
                       kernel_initializer='he_uniform', padding='same'))
        self.model.add(MaxPooling2D((2, 2)))
        self.model.add(Dropout(0.2))

        # Block 3
        self.model.add(Conv2D(64, (3, 3), activation='relu',
                       kernel_initializer='he_uniform', padding='same'))
        self.model.add(MaxPooling2D((2, 2)))
        self.model.add(Dropout(0.2))

        # Flatten layer
        self.model.add(Flatten())

        # Fully connected layers
        self.model.add(Dense(128, activation='relu'))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dropout(0.5))

        # Softmax activation for classification
        self.model.add(Dense(categories_count, activation='softmax'))

    def _compile_model(self):
        # Your code goes here
        self.model.compile(
            optimizer="RMSprop",
            loss='categorical_crossentropy',
            metrics=['accuracy'])
