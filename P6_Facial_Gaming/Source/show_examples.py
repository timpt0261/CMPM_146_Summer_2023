import numpy as np
import seaborn as sns
from keras.utils import load_img
import matplotlib.pyplot as plt
import os

from config import original_image_size, train_directory, categories

def show_examples(count, scale=0.7):
    base_dir = train_directory
    fig = plt.figure(0, figsize=(count*scale,len(categories)*scale))
    cpt = 0

    for category in categories:
        category_dir = os.path.join(base_dir, category)
        for filename in os.listdir(category_dir)[:count]:
            cpt = cpt + 1
            plt.subplot(len(categories),count,cpt)
            img = load_img(os.path.join(category_dir, filename), target_size=original_image_size)
            plt.imshow(img, cmap="gray")
    plt.setp(plt.gcf().get_axes(), xticks=[], yticks=[]);
    plt.subplots_adjust(wspace=0.1, hspace=0.1)
    plt.show()

if __name__ == "__main__":
    show_examples(5)