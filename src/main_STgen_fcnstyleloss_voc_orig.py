
import tensorflow as tf
from model_STgen_fcnstyleloss_voc_orig import STnet
import os
#from cityscapes_dataset import CityscapesDataset
#from gta_dataset import GTADataset
from gta_dataset_voc import GTADataset_VOC
from glob import glob
import pdb

flags = tf.app.flags
flags.DEFINE_integer('jobs', 4, 'limits cpus/threads generated by TF')
flags.DEFINE_integer('num_epochs', 2, 'Number of epochs')
flags.DEFINE_integer('batch_size', 1, 'Number of images used for each iteration')
flags.DEFINE_integer('height', 512, 'Image height during training')
flags.DEFINE_integer('width', 1024, 'Image width during training')
#flags.DEFINE_float('learning_rate', 2e-5, 'Learning rate for the Adam optimizer')
flags.DEFINE_float('learning_rate', 2e-6, 'Learning rate for the Adam optimizer')
flags.DEFINE_float('tau', float('inf'), 'Time constant for learning rate decay (in steps)')
flags.DEFINE_string('data_cache_dir', '../data', 'Where to store cached info about dataset (e.g mean image)')
flags.DEFINE_string('checkpoint_dir', '../out/checkpoints', 'Where to store the checkpoints')
flags.DEFINE_string('checkpoint_number', None, 'Specific checkpoint to load, e.g 1000')
flags.DEFINE_string('result_dir', '../out/results', 'Where to store the results')
flags.DEFINE_string('log_dir', '../out/logs', 'Where to store the logs')
flags.DEFINE_string('data_slug_real', 'cityscapes-segmentation', 'slug of first dataset')
flags.DEFINE_string('data_slug_synth', '', 'slug of second dataset')
flags.DEFINE_string('data_dir_real', '/mnt/ngv/datasets/cityscapes-segmentation', 'Path to the training set which contains `gtFine` and `leftImg8bit`')
flags.DEFINE_string('data_dir_synth', '', 'Path to additional dataset')
flags.DEFINE_string('input_fname_pattern_real', '*.jpg', 'file extenstion of real dataset')
flags.DEFINE_string('input_fname_pattern_synth', '*.jpg', 'file extenstion of synthetic dataset')
flags.DEFINE_integer('num_images_real', 1000000, 'Number of images to be used in `data_dir_real` for training')
flags.DEFINE_integer('num_images_synth', 1000000, 'Number of images to be used in `data_dir_synth` for training')
flags.DEFINE_string('phase', 'train', 'Should be `train` or `augment`')
flags.DEFINE_bool('eval_mean', False, 'whether to use the mean image of the evaluation set during evalutation')
flags.DEFINE_bool('load_weights_flag', False, 'whether to use the trained sensor transfer network weights')
flags.DEFINE_string('name', '', 'Name for this run')
flags.DEFINE_string('gpu', '0', 'GPU to be used')
flags.DEFINE_bool('log_weights', False, 'To log weights in TensorBoard or not (during training)')

config = flags.FLAGS

os.environ['CUDA_VISIBLE_DEVICES'] = config.gpu


def main(_):
    #with tf.Session() as sess:
    configSess = tf.ConfigProto(intra_op_parallelism_threads=config.jobs, 
                        inter_op_parallelism_threads=config.jobs, 
                        allow_soft_placement=True, 
                        device_count = {'CPU': config.jobs})
    with tf.Session(config = configSess) as sess:
        cache_dir = config.data_cache_dir
        if not os.path.isdir(cache_dir):
            raise Exception("Expected to find cache directory at {}".format(cache_dir))

        ## load in real dataset
        dataset_real = GTADataset_VOC([(config.data_dir_real, config.num_images_real, config.data_slug_real)], cache_dir=cache_dir, calc_val_mean=config.eval_mean)
        ##
        ## load in synthetic dataset
        dataset_synth = GTADataset_VOC([(config.data_dir_synth, config.num_images_synth, config.data_slug_synth)], cache_dir=cache_dir, calc_val_mean=config.eval_mean)
        #
        #pdb.set_trace()
        if not config.name:
            config.name = config.data_slug_synth#'gta'#dataset_synth.slug

        ## generate the network object
        mdl = STnet(sess=sess, config=config, dataset_real=dataset_real, dataset_synth=dataset_synth)
        mdl.run_model()
        #if mdl.phase == 'train':
        #    mdl.train()
        #elif mdl.phase == 'val':
        #    mdl.evaluate()
        #else:
        #    raise ValueError('Unsupported phase.')


if __name__ == '__main__':
    tf.app.run()
