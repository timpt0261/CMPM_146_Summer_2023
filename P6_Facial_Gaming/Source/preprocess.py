from tensorflow.keras.layers.experimental.preprocessing import Rescaling, RandomFlip, RandomRotation
from tensorflow.keras.utils import image_dataset_from_directory
import tensorflow as tf
from config import train_directory, test_directory, image_size, batch_size, validation_split

AUTOTUNE = tf.data.AUTOTUNE

# Set GPU device to be used (optional, but recommended)
physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

def _split_data(train_directory, test_directory, batch_size, validation_split):
    print('train dataset:')
    train_dataset, validation_dataset = image_dataset_from_directory(
        train_directory,
        label_mode='categorical',
        color_mode='rgb',
        batch_size=batch_size,
        image_size=image_size,
        validation_split=validation_split,
        subset="both",
        seed=47
    )
    print('test dataset:')
    test_dataset = image_dataset_from_directory(
        test_directory,
        label_mode='categorical',
        color_mode='rgb',
        batch_size=batch_size,
        image_size=image_size,
        shuffle=False
    )

    return train_dataset, validation_dataset, test_dataset

def _augment_dataset(dataset):
    data_augmentation = tf.keras.Sequential([
        Rescaling(1./255),  # Rescaling to [0, 1]
        RandomFlip('horizontal'),
        RandomRotation(0.2),
    ])

    augmented_dataset = dataset.map(
        lambda x, y: (data_augmentation(x, training=True), y),
        num_parallel_calls=AUTOTUNE
    )
    return augmented_dataset

def get_datasets():
    train_dataset, validation_dataset, test_dataset = _split_data(
        train_directory, test_directory, batch_size, validation_split)

    train_dataset = _augment_dataset(train_dataset)
    validation_dataset = _augment_dataset(validation_dataset)
    test_dataset = _augment_dataset(test_dataset)

    return train_dataset, validation_dataset, test_dataset
