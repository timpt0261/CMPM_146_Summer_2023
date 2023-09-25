from models.model import Model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.optimizers import RMSprop, SGD, Adam, Nadam


class BasicModel(Model):
    def _define_model(self, input_shape, categories_count):
        print(f"input_shape: {input_shape}")
        self.model = Sequential([
            # Convolutional layer 1
            Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
            MaxPooling2D((2, 2)),
            
            # Convolutional layer 2
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            
            # Convolutional layer 3
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            
            # Flatten layer
            Flatten(),
            
            # Fully connected layer 1
            Dense(128, activation='relu'),
            
            # Fully connected layer 2
            Dense(64, activation='relu'),
            
            # Output layer
            Dense(3, activation='softmax')
        ])
        
        
    def _compile_model(self):
        opt = Adam(learning_rate = 0.002)
        self.model.compile(
            optimizer=opt,
            loss='categorical_crossentropy',
            metrics=['accuracy'])