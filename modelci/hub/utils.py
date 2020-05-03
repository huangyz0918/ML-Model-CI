import re
from collections import defaultdict
from enum import unique, Enum
from pathlib import Path
from typing import Union

import numpy as np
import tensorflow as tf
import torch

from modelci.persistence.bo import Framework, Engine, ModelVersion
from modelci.utils.trtis_objects import DataType, ModelInputFormat


def parse_path(path: Path):
    """Obtain filename, framework and engine from saved path.
    """

    if re.match(r'^.*?[!/]*/[a-z]+-[a-z]+/\d+$', str(path.with_suffix(''))):
        filename = path.name
        architecture = path.parent.parent.stem
        info = path.parent.name.split('-')
        framework = Framework[info[0].upper()]
        engine = Engine[info[1].upper()]
        version = ModelVersion(Path(filename).stem)
        return {
            'architecture': architecture,
            'framework': framework,
            'engine': engine,
            'version': version,
            'filename': filename
        }
    else:
        raise ValueError('Incorrect model path pattern')


def generate_path(model_name: str, framework: Framework, engine: Engine, version: Union[ModelVersion, str, int]):
    """Generate saved path from model
    """
    model_name = str(model_name)
    if not isinstance(framework, Framework):
        raise ValueError(f'Expecting framework type to be `Framework`, but got {type(framework)}')
    if not isinstance(engine, Engine):
        raise ValueError(f'Expecting engine type to be `Engine`, but got {type(engine)}')
    if not isinstance(version, ModelVersion):
        version = ModelVersion(str(version))

    return Path.home() / '.modelci' / model_name / f'{framework.name.lower()}-{engine.name.lower()}' / str(version)


def GiB(val):
    return val * 1 << 30


def type_to_trt_type(tensor_type: type):
    mapper = defaultdict(
        lambda: DataType.TYPE_INVALID, {
            bool: DataType.TYPE_BOOL,
            int: DataType.TYPE_INT32,
            float: DataType.TYPE_FP32,
            str: DataType.TYPE_STRING,
            torch.bool: DataType.TYPE_BOOL,
            torch.uint8: DataType.TYPE_UINT8,
            torch.int: DataType.TYPE_INT32,
            torch.int8: DataType.TYPE_INT8,
            torch.int16: DataType.TYPE_INT16,
            torch.int32: DataType.TYPE_INT32,
            torch.int64: DataType.TYPE_INT64,
            torch.float: DataType.TYPE_FP32,
            torch.float16: DataType.TYPE_FP16,
            torch.float32: DataType.TYPE_FP32,
            torch.float64: DataType.TYPE_FP64,
            tf.bool: DataType.TYPE_BOOL,
            tf.uint8: DataType.TYPE_UINT8,
            tf.uint16: DataType.TYPE_UINT16,
            tf.uint32: DataType.TYPE_UINT32,
            tf.uint64: DataType.TYPE_UINT64,
            tf.int8: DataType.TYPE_INT8,
            tf.int16: DataType.TYPE_INT16,
            tf.int32: DataType.TYPE_INT32,
            tf.int64: DataType.TYPE_INT64,
            tf.float16: DataType.TYPE_FP16,
            tf.float32: DataType.TYPE_FP32,
            tf.float64: DataType.TYPE_FP64,
            tf.string: DataType.TYPE_STRING
        }
    )

    return mapper[tensor_type]


def model_dtype_to_np(model_dtype):
    mapper = {
        DataType.TYPE_INVALID: None,
        DataType.TYPE_BOOL: np.bool,
        DataType.TYPE_UINT8: np.uint8,
        DataType.TYPE_UINT16: np.uint16,
        DataType.TYPE_UINT32: np.uint32,
        DataType.TYPE_UINT64: np.uint64,
        DataType.TYPE_INT8: np.int8,
        DataType.TYPE_INT16: np.int16,
        DataType.TYPE_INT32: np.int32,
        DataType.TYPE_INT64: np.int64,
        DataType.TYPE_FP16: np.float16,
        DataType.TYPE_FP32: np.float32,
        DataType.TYPE_FP64: np.float64,
        DataType.TYPE_STRING: np.dtype(object)
    }

    if isinstance(model_dtype, int):
        model_dtype = DataType(model_dtype)
    elif isinstance(model_dtype, str):
        model_dtype = DataType[model_dtype]
    elif not isinstance(model_dtype, DataType):
        raise TypeError(
            f'model_dtype is expecting one of the type: `int`, `str`, or `DataType` but got {type(model_dtype)}'
        )
    return mapper[model_dtype]


@unique
class TensorRTPlatform(Enum):
    """TensorRT platform type for model configuration
    """
    TENSORRT_PLAN = 0
    TENSORFLOW_GRAPHDEF = 1
    TENSORFLOW_SAVEDMODEL = 2
    CAFFE2_NETDEF = 3
    ONNXRUNTIME_ONNX = 4
    PYTORCH_LIBTORCH = 5
    CUSTOM = 6


TensorRTModelInputFormat = ModelInputFormat
