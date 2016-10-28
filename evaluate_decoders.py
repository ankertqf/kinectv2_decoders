import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import sys
import pylab
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import os.path

#
# loads float array images (424x512xtot_ims) from binary file
#
def load_images_bin( filename ):

    infile = open(filename, "r")
    data = np.fromfile(infile, dtype=np.float32)

    tot_ims = len(data)/(512*424)
    depth_images = data.reshape(tot_ims,424, 512).transpose()
    return depth_images, tot_ims

#
# loads float array images (424x510) from binary file
#
def load_gt_bin( filename ):

    infile = open(filename, "r")
    data = np.fromfile(infile, dtype=np.float32)
    depth_images = data.reshape(510, 424).transpose()
    return depth_images
#
# sets image points to inlier or outlier
#
def classify_depth_points(depth_images, ground_truth, inlier_threshold, num_images):

    sh = depth_images[1:511,:,:].shape
    
    mask_inliers = np.zeros(sh,dtype=bool) 
    mask_outliers = np.zeros(sh,dtype=bool) 
    #print("sh = ", sh)
    for i in range(0,num_images):
        
        mask_inliers[:,:,i] = (np.abs(ground_truth.transpose() - depth_images[1:511,:,i]) < inlier_threshold) & (ground_truth.transpose() > 0.0)
        mask_outliers[:,:,i] = (mask_inliers[:,:,i] != True) & (ground_truth.transpose() > 0.0) & (depth_images[1:511,:,i]>0.0)

    return mask_inliers, mask_outliers

#
# calculates inlier/outlier rates
#
def generate_inlier_outlier_rates( max_vals_images, depth, ground_truth, inlier_threshold, num_points, num_images):

    sh = max_vals_images.shape
    max_val_im = max_vals_images[:,:,1]
    sorted_max_vals = np.sort(max_val_im.ravel())
    len_max_val = len(sorted_max_vals)
    max_val_thresh = np.append(np.array(-0.0001), sorted_max_vals[::np.floor(len_max_val/num_points)])
   
    num_thresh = len(max_val_thresh)
    mask_inliers, mask_outliers = classify_depth_points(depth, ground_truth, inlier_threshold, num_images)

    num_pixels = np.count_nonzero(ground_truth)
    num_inliers = np.zeros((num_images,num_thresh))
    num_outliers = np.zeros((num_images,num_thresh))

    for t in range(0,num_thresh):
        for i in range(0,num_images):
            mask = max_vals_images[1:511,:,i] > max_val_thresh[t]
            inliers = mask & mask_inliers[:,:,i]
            num_inliers[i,t] = np.count_nonzero(inliers.ravel())
            outliers = mask & mask_outliers[:,:,i]
            num_outliers[i,t] = np.count_nonzero(outliers.ravel())
            

    inlier_rate = np.mean(num_inliers/num_pixels,axis=0)
    outlier_rate = np.mean(num_outliers/num_pixels,axis=0)
    thresholds = max_val_thresh

    return inlier_rate, outlier_rate, thresholds

def parse_setup_xml(filename, dataset):
    tree=ET.parse(filename)
    root = tree.getroot()

    depth_file_string = []
    conf_file_string = []
    pipeline_names = []
    for pipeline in root.iter('pipeline'):    
        pipeline_name = pipeline.attrib['name']
        
        setup_name = pipeline.attrib['setup_name']

        depth_filename = "dataset/data/"+pipeline_name+"_depth_"+setup_name+"_"+dataset+".bin"
        conf_filename = "dataset/data/"+pipeline_name+"_conf_"+setup_name+"_"+dataset+".bin"
        if os.path.isfile(depth_filename) & os.path.isfile(depth_filename):
            pipeline_names.append(pipeline_name)
            depth_file_string.append(depth_filename)
            conf_file_string.append(conf_filename)

    return depth_file_string, conf_file_string, pipeline_names

def run_test(ground_truth, max_val_file, depth_images_file, inlier_threshold, num_points, fig_num, pipelane_name, marker):
    max_val_images, num_images = load_images_bin( max_val_file )
    depth_images, num_images = load_images_bin( depth_images_file )

    inlier_rate, outlier_rate, thresholds = generate_inlier_outlier_rates(max_val_images, depth_images, ground_truth, inlier_threshold, num_points, num_images)

    plt.figure(fig_num)
    plt.ylabel('inlier rate')
    plt.xlabel('outlier rate')
    line = plt.plot(np.log(outlier_rate),inlier_rate,marker, label=pipelane_name)
    first_legend = plt.legend(loc=4)



def compare_pipelines(xml_filename, dataset):
    gt = load_gt_bin( "data/"+dataset+"_gt.bin" )
    depth_file_string, conf_file_string, pipeline_names = parse_setup_xml(xml_filename, dataset)
    marker = '-'
    i = 0
    while i < len(depth_file_string):
        num_points = 1
        if pipeline_names[i] == 'kde':
            num_points = 20
        elif pipeline_names[i] == 'microsoft':
            marker = 'k*'
        run_test(gt, conf_file_string[i], depth_file_string[i], 300, num_points, 1,pipeline_names[i], marker)
        i += 1
    
    if len(depth_file_string) > 0:
        plt.figure(1)
        plt.title(dataset)
        plt.show()
    else:
        print('no files t be found :(')

def visualize_frame(xml_filename, dataset, frame_num):
    gt = load_gt_bin( "data/"+dataset+"_gt.bin" )
    depth_file_string, conf_file_string, pipeline_names = parse_setup_xml(xml_filename, dataset)
    frame = args[3]

    i = 0
    while i < len(depth_file_string):
        depth_images, num_images = load_images_bin( depth_file_string[i] )
        conf_images, num_images = load_images_bin( conf_file_string[i] )
        depth = depth_images[:,:,int(frame)].transpose()
        conf = conf_images[:,:,int(frame)].transpose()
        plt.figure(i+1)
        plt.subplot(2,2,1)
        plt.imshow(depth,cmap=pylab.gray())
        plt.title('Depth image without outlier rejection, '+pipeline_names[i])
        plt.subplot(2,2,2)
        plt.imshow(conf,cmap=pylab.gray())
        plt.title('Confidence image, '+pipeline_names[i])
        depth_filtered = np.array(depth)
        depth_filtered[np.where(conf < 0.4)] = 0.0
        plt.subplot(2,2,3)
        plt.imshow(depth_filtered,cmap=pylab.gray())
        plt.title('Depth image with outlier rejection, '+pipeline_names[i])
        plt.subplot(2,2,4)
        plt.imshow(gt,cmap=pylab.gray())
        plt.title('Ground truth '+ dataset)
        i=i+1

    plt.show()


# args: ['vis', 'depth_filename', 'conf_filename', frame_num] or ['test', 'xml_file', 'dataset']
if __name__ == "__main__":
    args = sys.argv[1:]

    if args[0] == 'vis':
        if len(args) < 3:
            print('not enough arguments')
            print('len(args) = ', len(args))
            exit()

        visualize_frame(args[1], args[2], args[3])
    elif args[0] == 'test':
        if len(args) < 2:
            print('not enough arguments')
            print('len(args) = ', len(args))
            exit()

        compare_pipelines(args[1], args[2])
    else:
        print('not implemented')
