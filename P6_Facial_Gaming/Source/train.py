from preprocess import get_datasets
from models.basic_model import BasicModel
from models.dropout_model import DropoutModel
from models.vgg_model import VGGModel
from models.merged_model import MergedModel
from config import image_size, categories
import matplotlib.pyplot as plt
import time
import os


input_shape = (image_size[0], image_size[1], 3)
categories_count = 3

models = {
    'basic_model': BasicModel,
    'drop_out_model': DropoutModel,
    #'vgg_model': VGGModel,
    #'merged_model': MergedModel,
}

def plot_history(history):
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs = range(1, len(acc) + 1)

    plt.figure(figsize = (24, 6))
    plt.subplot(1,2,1)
    plt.plot(epochs, acc, 'b', label = 'Training Accuracy')
    plt.plot(epochs, val_acc, 'r', label = 'Validation Accuracy')
    plt.grid(True)
    plt.legend()
    plt.xlabel('Epoch')

    plt.subplot(1,2,2)
    plt.plot(epochs, loss, 'b', label = 'Training Loss')
    plt.plot(epochs, val_loss, 'r', label = 'Validation Loss')
    plt.grid(True)
    plt.legend()
    plt.xlabel('Epoch')
    plt.show()

if __name__ == "__main__":
    epochs = 60
    print('* Data preprocessing')
    train_dataset, validation_dataset, test_dataset = get_datasets()
    for name, model_class in models.items():
        print('* Training {} for {} epochs'.format(name, epochs))
        model = model_class(input_shape, categories_count)
        history = model.train_model(train_dataset, validation_dataset, epochs)
        
    
        summary_filename = '{}_summary.txt'.format(name)
        with open(summary_filename, 'w') as f:
            if name == 'basic_model':
                f.write("Initial Network:\n")
            elif name == 'drop_out_model':
                f.write("With Dropout:\n")
            model.print_summary(print_fn=lambda x: f.write(x + '\n'))

        print('* Evaluating {}'.format(name))
        model.evaluate(test_dataset)
        print('* Confusion Matrix for {}'.format(name))
        print(model.get_confusion_matrix(test_dataset))
        filename = '{}_{}_epochs_timestamp_{}.keras'.format(name, epochs, int(time.time()))
        model.save_model(filename)
        print('* Model saved as {}'.format(filename))
        plot_history(history)
        model.plot_model_shape(name)