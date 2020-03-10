"""
Credit: https://github.com/rohanbaisantry/image-clustering

Modified by Roman Sorin <roman@romansorin.com> [https://github.com/romansorin] for use in 2019-2020 research study
"""

import os
import random
import shutil
import sys

import cv2
import keras
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from main import file_safe_timestamp
import datetime
from config.app import CLUSTER_DATA_PATH, CLUSTER_OUTPUT_PATH, STORAGE_LOGS_PATH


class Clustering:
    def __init__(self, folder_path="data", n_clusters=10, max_examples=None, use_imagenets=False, use_pca=False):
        filename = f"clustering_{file_safe_timestamp()}.log"
        self.file = open(f"{STORAGE_LOGS_PATH}/{filename}", "x")
        self.file.write(str(datetime.datetime.now()) + "\n\n")
        self.file.write("\n\n \t\t START\n\n")
        paths = os.listdir(folder_path)

        self.max_examples = len(paths) if max_examples is None else len(paths) if max_examples > len(
            paths) else max_examples

        self.n_clusters = n_clusters
        self.folder_path = folder_path
        random.shuffle(paths)
        self.image_paths = paths[:self.max_examples]
        self.use_imagenets = use_imagenets
        self.use_pca = use_pca
        del paths

        try:
            shutil.rmtree(CLUSTER_OUTPUT_PATH)
        except FileExistsError:
            pass

        print("\n output folders created.")
        self.file.write("\n output folders created.")
        os.makedirs(CLUSTER_OUTPUT_PATH)

        for i in range(self.n_clusters):
            os.makedirs(f"{CLUSTER_OUTPUT_PATH}/cluster{str(i)}")

        print("\n Object of class \"Clustering\" has been initialized.")
        self.file.write("\n Object of class \"Clustering\" has been initialized.")

    def load_images(self):
        self.images = []

        for image in self.image_paths:
            if image.endswith('.png'):
                self.images.append(cv2.cvtColor(cv2.resize(cv2.imread(
                    f"{self.folder_path}/{image}"), (224, 224)), cv2.COLOR_BGR2RGB))

        self.images = np.float32(self.images).reshape(len(self.images), -1)
        self.images /= 255

        print(
            f"\n {str(self.max_examples)} images from the {self.folder_path} folder have been loaded in a random order.")
        self.file.write(
            f"\n {str(self.max_examples)} images from the {self.folder_path} folder have been loaded in a random order.")

    def get_new_imagevectors(self):
        if not self.use_imagenets:
            self.images_new = self.images
        else:
            if use_imagenets.lower() == "vgg16":
                model = keras.applications.vgg16.VGG16(
                    include_top=False, weights="imagenet", input_shape=(224, 224, 3))
            elif use_imagenets.lower() == "vgg19":
                model = keras.applications.vgg19.VGG19(
                    include_top=False, weights="imagenet", input_shape=(224, 224, 3))
            elif use_imagenets.lower() == "resnet50":
                model = keras.applications.resnet50.ResNet50(
                    include_top=False, weights="imagenet", input_shape=(224, 224, 3))
            elif use_imagenets.lower() == "xception":
                model = keras.applications.xception.Xception(
                    include_top=False, weights='imagenet', input_shape=(224, 224, 3))
            elif use_imagenets.lower() == "inceptionv3":
                keras.applications.inception_v3.InceptionV3(
                    include_top=False, weights='imagenet', input_shape=(224, 224, 3))
            elif use_imagenets.lower() == "inceptionresnetv2":
                model = keras.applications.inception_resnet_v2.InceptionResNetV2(
                    include_top=False, weights='imagenet', input_shape=(224, 224, 3))
            elif use_imagenets.lower() == "densenet":
                model = keras.applications.densenet.DenseNet201(
                    include_top=False, weights='imagenet', input_shape=(224, 224, 3))
            elif use_imagenets.lower() == "mobilenetv2":
                model = keras.applications.mobilenetv2.MobileNetV2(input_shape=(
                    224, 224, 3), alpha=1.0, depth_multiplier=1, include_top=False, weights='imagenet', pooling=None)
            else:
                print(
                    "\n\n Please use one of the following keras applications only [ \"vgg16\", \"vgg19\", "
                    "\"resnet50\", \"xception\", \"inceptionv3\", \"inceptionresnetv2\", \"densenet\", "
                    "\"mobilenetv2\" ] or False")
                self.file.write(
                    "\n\n Please use one of the following keras applications only [ \"vgg16\", \"vgg19\", "
                    "\"resnet50\", \"xception\", \"inceptionv3\", \"inceptionresnetv2\", \"densenet\", "
                    "\"mobilenetv2\" ] or False")
                self.file.close()
                sys.exit()

            pred = model.predict(self.images)
            images_temp = pred.reshape(self.images.shape[0], -1)
            if not self.use_pca:
                self.images_new = images_temp
            else:
                model2 = PCA(n_components=None, random_state=728)
                model2.fit(images_temp)
                self.images_new = model2

    def clustering(self):
        model = KMeans(n_clusters=self.n_clusters, n_jobs=-1, random_state=728)
        model.fit(self.images_new)
        predictions = model.predict(self.images_new)
        for i in range(self.max_examples):
            shutil.copy2(f"{self.folder_path}/{self.image_paths[i]}",
                         f"{CLUSTER_OUTPUT_PATH}/cluster{str(predictions[i])}")
        print(
            f"\n Clustering complete! \n\n Clusters and the respective images are stored in the \"{CLUSTER_OUTPUT_PATH}\" folder.")
        self.file.write(
            f"\n Clustering complete! \n\n Clusters and the respective images are stored in the \"{CLUSTER_OUTPUT_PATH}\" folder.")
        self.file.write("\n\n\t\t END\n\n")
        self.file.close()


if __name__ == "__main__":
    print("\n\n \t\t START\n\n")

    number_of_clusters = 4
    data_path = CLUSTER_DATA_PATH
    max_examples = None
    use_imagenets = False

    if not use_imagenets:
        use_pca = False
    else:
        use_pca = False

    kmeans = Clustering(data_path, number_of_clusters,
                      max_examples, use_imagenets, use_pca)
    kmeans.load_images()
    kmeans.get_new_imagevectors()
    kmeans.clustering()

    print("\n\n\t\t END\n\n")
