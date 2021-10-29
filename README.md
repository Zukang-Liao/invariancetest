General guideline to run the code:

### (1). Standard CNN training (train.py)

A series of CNNs on either MNIST or CIFAR or other databases should be trained in advance. We use the code train.py to train many CNNs using the metadata specify in metadata.txt (which will be released later on our website).
    
After the CNNs are trained, we use model id (mid) to record them.


### (2). Model database (model.py)

Our model database consists of 4 different partitions:
- partition (a): mid: 1-100, t1-t50. VGG13bn trained on CIFAR for rotation testing.
- partition (b): mid: 101-200, t101-t150. VGG13bn trained on CIFAR for brightness testing.
- partition (c): mid: 201-300, t201-t250. VGG13bn trained on CIFAR for scaling testing.
- partition (d): mid: 301-400, t301-t350. CNN5 trained on MNIST for rotation testing.
	    
Mid starting with "t" is a hold-out set. 

When using three-fold cross validation, the hold-out set is always treated as one fold.

While the rest 100 "regular" models are randomly split into two folds.

The assessment labels are provided in mlabel.txt. In this work, we focus on invariance quality.

Notes: Model 1 to 15 are trained on CPU, other models are trained on GPU.

Model 101 to 200, t101 to t150: preprocessing -- normalised to [0, 1], Others: [-0.5, 0.5]


### (3). Invariance testing data (save_invariance_results.py)
    For a given CNN, please run:
    ```
    python save_invariance_results.py --mid=mid --aug_type=r
    ```
    where mid is the index of the CNN and aug_type: "r" for "rotation", "s" for "scaling" and "b" for "brightness".
    The script will generate two .npy files, namely test_results1515.npy (CONF) and test_actoverall1515.npy (CONV).
    For partition (d), please specify --dbname=mnist:
    ```
    python save_invariance_results.py --mid=mid --aug_type=r --dbname=mnist
    ```


### (4). Variance matrices (matrices_CONF.py and matrices_CONV.py)
    To generate variance matrices (CONF):
    ```
    python matrices_CONF.py --mid=mid --aug_type=r
    ```
    To generate variance matrices (CONV):
    ```
    python matrices_CONV.py --mid=mid --aug_type=r
    ```


### (5). Measurements (measurements.py)
    To generate a json file consisting of all measurements for the model:
    ```
    python measurements.py --mid=mid --aug_type=r
    ```
    For partition (d), please specify --dbname="mnist":
    ```
    python measurements.py --mid=mid --aug_type=r --dbname="mnist"
    ```
    
    
### (6). ML4ML assessors (ML4MLassessor.py)
    To train an ML4ML assessor with different types of ml algorithms. And test the performance of the assessor on the testing set of the model-database.
    ```
    python ML4MLassessor.py --aug_type=r
    ```
    For partition (d), please specify --dbname=mnist:
    ```
    python ML4MLassessor.py --aug_type=r --dbname=mnist
    ```
