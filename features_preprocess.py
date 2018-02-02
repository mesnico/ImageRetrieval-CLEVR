import numpy as np
import pickle
import h5py

def load_features(name, filename):
    f = open(filename, 'rb')
    features = pickle.load(f)
    features = [f[1] for f in features]
    features = np.vstack(features)
    print('processed #{} features each of size {}'.format(features.shape[0], features.shape[1]))
    return {name:(features, l2_dist)}

def load_rmac_features(feat_filename, feat_order_filename):
    features = h5py.File(feat_filename, 'r')['/rmac']
    img_names = open(feat_order_filename, 'r').readlines()
    
    assert len(features) == len(img_names)

    #takes only val features
    filtered = [feat for feat, name in zip(features, img_names) if 'val' in name]
    filtered = np.vstack(filtered)
    return {'rmac':(filtered, dot_dist)}            

def process_conv_features(loaded_features):
    global_max = []
    global_avg = []
    flatten = []
    subwindow3 = []
    for f in loaded_features:
        #calculate indexes over the entire image (5x5)
        global_max.append(np.amax(f,axis=(2,3)))
        global_avg.append(np.mean(f,axis=(2,3)))
        flatten.append(np.reshape(f,(f.shape[0],-1)))

        '''#calculate maximum over subwindows of size 3x3
        m = nn.MaxPool2d(3, stride=2)
        i = autograd.Variable(from_numpy(f))
        o = m(i)
        o = o.data.numpy()
        o = np.reshape(o,(o.shape[0],-1))'''
        #compute manually a max pooling with window size=3 and stride=2
        o1 = np.amax(f[:,:,0:3,0:3],axis=(2,3))
        o2 = np.amax(f[:,:,2:5,0:3],axis=(2,3))
        o3 = np.amax(f[:,:,0:3,2:5],axis=(2,3))
        o4 = np.amax(f[:,:,2:5,2:5],axis=(2,3))
        #take also the central subwindow
        o5 = np.amax(f[:,:,1:4,1:4],axis=(2,3))
        subwindow3.append(np.concatenate((o1,o2,o3,o4,o5),axis=1))

    global_max = np.vstack(global_max)
    global_avg = np.vstack(global_avg)
    flatten = np.vstack(flatten)
    subwindow3 = np.vstack(subwindow3)

    return ({'conv_max':(global_max, l2_dist), 
            'conv_avg':(global_avg, l2_dist), 
            'conv_flatten':(flatten, l2_dist), 
            'conv_3x3_max':(subwindow3, l2_dist)})

def dot_dist(a,b):
    a_norm = normalized(a)
    b_norm = normalized(b)
    return 1-np.dot(a_norm, b_norm)
    
def l2_dist(a,b):
    return np.linalg.norm(a-b)

def normalized(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return np.squeeze(a / np.expand_dims(l2, axis))
