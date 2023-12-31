import numpy as np
import os
import glob
from sklearn.cluster import KMeans

def build_vocabulary(image_paths, vocab_size):
    """ Sample SIFT descriptors, cluster them using k-means, and return the fitted k-means model.
    NOTE: We don't necessarily need to use the entire training dataset. You can use the function
    sample_images() to sample a subset of images, and pass them into this function.

    Parameters
    ----------
    image_paths: an (n_image, 1) array of image paths.
    vocab_size: the number of clusters desired.
    
    Returns
    -------
    kmeans: the fitted k-means clustering model.
    """
    n_image = len(image_paths)

    # Since want to sample tens of thousands of SIFT descriptors from different images, we
    # calculate the number of SIFT descriptors we need to sample from each image.
    n_each = int(np.ceil(10000 / n_image))

    # Initialize an array of features, which will store the sampled descriptors
    # keypoints = np.zeros((n_image * n_each, 2))
    descriptors = np.zeros((n_image * n_each, 128))
    
    n_descriptors_found = 0
    for i, path in enumerate(image_paths):
        # Load features from each image
        features = np.loadtxt(path, delimiter=',',dtype=float)
        sift_keypoints = features[:, :2]
        sift_descriptors = features[:, 2:]

        # TODO: Randomly sample n_each descriptors from sift_descriptor and store them into descriptors
        n_descriptors = sift_descriptors.shape[0]  
        n_samples = min(n_each, n_descriptors)              
        # Select n_each random indices
        idx_samples = np.random.choice(n_descriptors, size=n_samples, replace=False)
        # Slice out random slected descriptors and store them into descriptors
        descriptors[n_descriptors_found:n_descriptors_found+n_samples, :] = sift_descriptors[idx_samples, :]
        n_descriptors_found += n_samples
        
    # Resize the descriptors array to remove uninitialized rows
    descriptors = descriptors[:n_descriptors_found, :]
        
    print("Clustering", descriptors.shape[0], "features")    
    kmeans = KMeans(n_clusters=vocab_size).fit(descriptors)
    
    return kmeans
    
def get_bags_of_sifts(image_paths, kmeans):
    """ Represent each image as bags of SIFT features histogram.

    Parameters
    ----------
    image_paths: an (n_image, 1) array of image paths.
    kmeans: k-means clustering model with vocab_size centroids.

    Returns
    -------
    image_feats: an (n_image, vocab_size) matrix, where each row is a histogram.
    """
    n_image = len(image_paths)
    vocab_size = kmeans.cluster_centers_.shape[0]

    image_feats = np.zeros((n_image, vocab_size))

    for i, path in enumerate(image_paths):
        # Load features from each image
        features = np.loadtxt(path, delimiter=',',dtype=float)

        # TODO: Assign each feature to the closest cluster center
        # Again, each feature consists of the (x, y) location and the 128-dimensional sift descriptor
        # You can access the sift descriptors part by features[:, 2:]
        
        # We use the prdict method of the kmeans model to assign each feature to the closest cluster center
        cluster_labels = kmeans.predict(features[:, 2:])
        
        # TODO: Build a histogram normalized by the number of descriptors      
        hist, bin_edges = np.histogram(cluster_labels, bins=vocab_size, range=(0, vocab_size), density=True)
        image_feats[i, :] = hist
        
    print(f'Image features shape: {image_feats.shape}')    

    return image_feats

def load(ds_path):
    """ Load from the training/testing dataset.

    Parameters
    ----------
    ds_path: path to the training/testing dataset.
             e.g., sift/train or sift/test 
    
    Returns
    -------
    image_paths: a (n_sample, 1) array that contains the paths to the descriptors. 
    labels: class labels corresponding to each image
    """
    # Grab a list of paths that matches the pathname
    files = glob.glob(os.path.join(ds_path, "*", "*.txt"))
    n_files = len(files)
    image_paths = np.asarray(files)
 
    # Get class labels
    classes = glob.glob(os.path.join(ds_path, "*"))
    labels = np.zeros(n_files)

    for i, path in enumerate(image_paths):
        folder, fn = os.path.split(path)
        labels[i] = np.argwhere(np.core.defchararray.equal(classes, folder))[0,0]

    # Randomize the order
    idx = np.random.choice(n_files, size=n_files, replace=False)
    image_paths = image_paths[idx]
    labels = labels[idx]

    return image_paths, labels


if __name__ == "__main__":
    paths, labels = load("sift/train")
    #build_vocabulary(paths, 10)
