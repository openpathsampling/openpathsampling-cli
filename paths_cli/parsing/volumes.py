import operator
import functools

from .core import Parser, InstanceBuilder, custom_eval, Parameter
from .cvs import cv_parser

class CVVolumeInstanceBuilder(InstanceBuilder):
    # subclass to handle periodic cv volumes
    # TODO: this will be removed after OPS 2.0 is released
    def select_builder(self, dct):
        import openpathsampling as paths
        cv = dct['cv']
        builder = paths.CVDefinedVolume
        if cv.period_min is not None:
            builder = paths.PeriodicCVDefinedVolume
        if cv.period_max is not None:
            builder = paths.PeriodicCVDefinedVolume
        return builder

def cv_volume_remapper(dct):
    dct['collectivevariable'] = dct.pop('cv')
    return dct

build_cv_volume = CVVolumeInstanceBuilder(
    builder=None,
    # attribute_table={
        # 'cv': cv_parser,
        # 'lambda_min': custom_eval,
        # 'lambda_max': custom_eval,
    # },
    attribute_table=None,
    remapper=cv_volume_remapper,
    parameters=[
        Parameter('cv', cv_parser,
                  description="CV that defines this volume"),
        Parameter('lambda_min', custom_eval,
                  description="Lower bound for this volume"),
        Parameter('lambda_max', custom_eval,
                  description="Upper bound for this volume")
    ],
    name='cv-volume',
    object_type='volume'
)

def _use_parser(dct):
    # this is a hack to get around circular definitions
    return volume_parser(dct)

# jsonschema type for combination volumes
VOL_ARRAY_TYPE = {
    'type': 'array',
    'items': {"$ref": "#/definitions/volume_type"}
}

build_intersection_volume = InstanceBuilder(
    builder=lambda subvolumes: functools.reduce(operator.__and__,
                                                subvolumes),
    # attribute_table={'subvolumes': _use_parser},
    attribute_table=None,
    parameters=[
        Parameter('subvolumes', _use_parser,
                  json_type=VOL_ARRAY_TYPE,
                  description="List of the volumes to intersect")
    ],
    name='intersection',
    object_type='volume'
)

build_union_volume = InstanceBuilder(
    builder=lambda subvolumes: functools.reduce(operator.__or__,
                                                subvolumes),
    # attribute_table={'subvolumes': _use_parser},
    attribute_table=None,
    parameters=[
        Parameter('subvolumes', _use_parser,
                  json_type=VOL_ARRAY_TYPE,
                  description="List of the volumes to join into a union")
    ],
    name='union',
    object_type='volume'
)

TYPE_MAPPING = {
    'cv-volume': build_cv_volume,
    'intersection': build_intersection_volume,
}

volume_parser = Parser(TYPE_MAPPING, label="volumes")

