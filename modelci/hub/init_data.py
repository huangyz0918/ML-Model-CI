import argparse
import os

import tensorflow as tf
from torchvision import models

from modelci.controller import job_executor
from modelci.hub.converter import TFSConverter
from modelci.hub.manager import register_model
from modelci.hub.utils import generate_path
from modelci.types.bo import Framework, IOShape, ModelVersion, Engine
from modelci.types.trtis_objects import ModelInputFormat

os.environ['CUDA_VISIBLE_DEVICES'] = '1'


class ModelExporter(object):
    """Export pre-trained model given name and register the exported model into Model DB.

    The exported will auto generate possible model family members and perform registration.

    TODO:
        1. engine, dataset,
        2. collect and filled the accuracy / registration code for
            - ResNet101
            - DenseNet121
            - MobileNet
            - VGG16
    """

    @staticmethod
    def ResNet50(framework: Framework, version: str = '1'):
        """Export, generate model family and register ResNet50

        Arguments:
            framework (Framework): Framework name.
            version (str): Model version.
        """
        if framework == Framework.TENSORFLOW:
            model = tf.keras.applications.ResNet50()
            # converting to trt

            if not export_trt:
                tfs_dir = generate_path(
                    model_name='ResNet50', framework=framework, engine=Engine.TFS, version=str(version)
                )
                TFSConverter.from_tf_model(model, tfs_dir)
                model = str(tfs_dir.with_suffix('.zip'))

            register_model(
                model,
                dataset='imagenet',
                acc=0.76,
                task='image classification',
                inputs=[IOShape([-1, 224, 224, 3], dtype=float, name='input_1', format=ModelInputFormat.FORMAT_NHWC)],
                outputs=[IOShape([-1, 1000], dtype=float, name='probs')],
                architecture='ResNet50',
                framework=framework,
                version=ModelVersion(version),
                convert=export_trt,
            )
        elif framework == Framework.PYTORCH:
            model = models.resnet50(pretrained=True)
            register_model(
                model,
                dataset='imagenet',
                acc=0.76,
                task='image classification',
                inputs=[IOShape([-1, 3, 224, 224], dtype=float, name='INPUT__0', format=ModelInputFormat.FORMAT_NCHW)],
                outputs=[IOShape([-1, 1000], dtype=float, name='probs')],
                architecture='ResNet50',
                framework=framework,
                version=ModelVersion(version),
            )
        else:
            raise ValueError('Framework not supported.')

    @staticmethod
    def ResNet101(framework: Framework, version: str = "1"):
        if framework == Framework.TENSORFLOW:
            model = tf.keras.applications.ResNet101()
            register_model(
                model,
                dataset='imagenet',
                acc=...,  # TODO: to be filled
                task='image classification',
                inputs=[IOShape([-1, 224, 224, 3], dtype=float, name='input_1', format=ModelInputFormat.FORMAT_NHWC)],
                outputs=[IOShape([-1, 1000], dtype=float, name='probs')],
                architecture='ResNet101',
                framework=framework,
                version=ModelVersion(version)
            )
        elif framework == Framework.PYTORCH:
            model = models.resnet101(pretrained=True)
            register_model(
                model,
                dataset='imagenet',
                acc=...,  # TODO
                task='image classification',
                inputs=[IOShape([-1, 3, 224, 224], dtype=float, name='INPUT__0', format=ModelInputFormat.FORMAT_NCHW)],
                outputs=[IOShape([-1, 1000], dtype=float, name='probs')],
                architecture='ResNet101',
                framework=framework,
                version=ModelVersion(version)
            )
        else:
            raise ValueError('Framework not supported.')

    @staticmethod
    def DenseNet121(framework: Framework, version: str = '1'):
        if framework == Framework.TENSORFLOW:
            model = tf.keras.applications.DenseNet121()
        elif framework == Framework.PYTORCH:
            model = models.densenet121(pretrained=True)
        else:
            raise ValueError('Framework not supported.')

    @staticmethod
    def MobileNet(framework: Framework, version: str = "1"):
        if framework == Framework.TENSORFLOW:
            model = tf.keras.applications.MobileNet()
        else:
            raise ValueError('Framework not supported.')

    @staticmethod
    def VGG16(framework: Framework, version: str = "1"):
        if framework == Framework.TENSORFLOW:
            model = tf.keras.applications.VGG16()
        elif framework == Framework.PYTORCH:
            model = models.vgg16(pretrained=True)
        else:
            raise ValueError('Framework not supported.')


def export_model(args):
    model_name = args.model.lower()
    framework = Framework[args.framework.upper()]

    if model_name == 'resnet50':
        ModelExporter.ResNet50(framework)
    elif model_name == 'resnet101':
        ModelExporter.ResNet101(framework)
    elif model_name == 'vgg16':
        ModelExporter.VGG16(framework)
    elif model_name == 'densenet121':
        ModelExporter.DenseNet121(framework)
    elif model_name == 'mobilenet':
        ModelExporter.MobileNet(framework)
    else:
        exit('Model Not Found.')

    print(f'Model {args.model} is exported.')

    job_executor.finish()
    job_executor.join()
    print(f'Finish profiling {args.model}.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initialize Model Database.')
    subparsers = parser.add_subparsers(help='export model')

    exporter_parser = subparsers.add_parser('export', help='Export a model')
    exporter_parser.add_argument('--model', type=str, required=True, help='model name')
    exporter_parser.add_argument('--framework', type=str, required=True, help='model framework')
    exporter_parser.add_argument(
        '--trt', action='store_true',
        help='Flag for exporting TensorRT. Please make sure you have TensorRT installed in your machine.'
    )
    exporter_parser.set_defaults(func=export_model)

    args = parser.parse_args()
    export_trt = args.trt
    args.func(args)
