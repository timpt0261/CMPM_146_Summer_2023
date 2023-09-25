import numpy as np
import pydot
from sklearn.metrics import confusion_matrix
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.utils import plot_model

class Model:
    def __init__(self, input_shape, categories_count):
        self._define_model(input_shape, categories_count)
        self._compile_model()

    def _define_model(self, input_shape, categories_count):
        raise Exception("define_model not implemented yet.")

    def _compile_model(self):
        raise Exception("define_model not implemented yet.")

    def train_model(self, train_dataset, validation_dataset, epochs):
        history = self.model.fit(
            x=train_dataset,
            epochs=epochs,
            verbose="auto",
            validation_data=validation_dataset
        )

        return history

    def save_model(self, filename):
        self.model.save(filename)
    
    def evaluate(self, test_dataset):
        self.model.evaluate(
            x=test_dataset,
            verbose='auto',
        )
    
    def get_confusion_matrix(self, test_dataset):
        prediction = self.model.predict(test_dataset)
        labels = np.concatenate([y for x, y in test_dataset], axis=0)
        y_pred = np.argmax(prediction, axis=-1)
        y = np.argmax(labels, axis=-1)
        return confusion_matrix(y, y_pred)

    def print_summary(self, print_fn=None):
        if print_fn == None:
            self.model.summary()
        else:
            self.model.summary(print_fn=print_fn)
    
    def plot_model_shape(self,file_name=None):
        if file_name == None:
            plot_model(self.model, show_shapes=True, to_file='test.png')
        else:
            plot_model(self.model, show_shapes=True, to_file='{}_plot_shape.png'.format(file_name))
    
    def predict(self, norm):
        predictions = self.model.predict(norm)
        return predictions