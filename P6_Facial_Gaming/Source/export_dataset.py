# make sure your dataset from kaggle is in a directory named 'kaggle'.
# expected directory tree:
#├── kaggle
#│   ├── train
#│   |   ├── happy
#│   |   ├── neutral
#│   |   ├── ...
#│   |   └── surprise
#│   └── test
#│   |   ├── happy
#│   |   ├── neutral
#│   |   ├── ...
#│   |   └── surprise

from config import train_directory, test_directory, train_size, categories
import os
import shutil

def copy_dataset(source_directory, target_directory, categories = None, target_size = None):
    if categories is None:
        categories = os.listdir(source_directory)
    
    for category in categories:
        source_category_dir = os.path.join(source_directory, category)
        target_category_dir = os.path.join(target_directory, category)
        
        if not os.path.exists(target_category_dir):
            os.makedirs(target_category_dir)
        
        image_files = os.listdir(source_category_dir)
        if target_size is None:
            count = len(image_files)
        else:
            count = int(target_size/len(categories))
            if category == categories[-1]:
                count += target_size%len(categories)
        
        for image_file in image_files[:count]:
            source_image_path = os.path.join(source_category_dir, image_file)
            target_image_path = os.path.join(target_category_dir, image_file)
            shutil.copy(source_image_path, target_image_path)


if __name__ == "__main__":
    source_directory = 'kaggle'
    train_source_directory = os.path.join(source_directory, 'train')
    test_source_directory = os.path.join(source_directory, 'test')
    train_target_directory = train_directory
    test_target_directory = test_directory

    copy_dataset(train_source_directory, train_target_directory, categories, train_size)
    print('Train dataset have been extracted.')
    
    copy_dataset(test_source_directory, test_target_directory, categories, None)
    print('Test dataset have been extracted.')