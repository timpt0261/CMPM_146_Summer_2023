from models.model import Model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.optimizers import RMSprop

class VGGModel(Model):
    def _define_model(self, input_shape, categories_count):
        # Your code goes here

        # self.model = <model definition>
        pass

    def _compile_model(self):
        # Your code goes here


        self.model.compile(optimizer=RMSprop(learning_rate=0.001),
        loss = 'categorical_crossentropy',
        metrics= ['accuracy'])
