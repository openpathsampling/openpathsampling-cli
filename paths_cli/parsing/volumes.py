import operator
import functools

from .core import Parser, InstanceBuilder, custom_eval, Parameter
from .cvs import cv_parser
from paths_cli.parsing.plugins import VolumeParserPlugin

# TODO: extra function for volumes should not be necessary as of OPS 2.0
def cv_volume_build_func(**dct):
    # TODO: this should take dict, not kwargs
    import openpathsampling as paths
    cv = dct['cv']
    builder = paths.CVDefinedVolume
    if cv.period_min is not None or cv.period_max is not None:
        builder = paths.PeriodicCVDefinedVolume

    dct['collectivevariable'] = dct.pop('cv')
    # TODO: wrap this with some logging
    return builder(**dct)

build_cv_volume = VolumeParserPlugin(
    builder=cv_volume_build_func,
    parameters=[
        Parameter('cv', cv_parser,
                  description="CV that defines this volume"),
        Parameter('lambda_min', custom_eval,
                  description="Lower bound for this volume"),
        Parameter('lambda_max', custom_eval,
                  description="Upper bound for this volume")
    ],
    name='cv-volume',
)

def _use_parser(dct):
    # this is a hack to get around circular definitions
    return volume_parser(dct)

# jsonschema type for combination volumes
VOL_ARRAY_TYPE = {
    'type': 'array',
    'items': {"$ref": "#/definitions/volume_type"}
}

build_intersection_volume = VolumeParserPlugin(
    builder=lambda subvolumes: functools.reduce(operator.__and__,
                                                subvolumes),
    parameters=[
        Parameter('subvolumes', _use_parser,
                  json_type=VOL_ARRAY_TYPE,
                  description="List of the volumes to intersect")
    ],
    name='intersection',
)

build_union_volume = VolumeParserPlugin(
    builder=lambda subvolumes: functools.reduce(operator.__or__,
                                                subvolumes),
    parameters=[
        Parameter('subvolumes', _use_parser,
                  json_type=VOL_ARRAY_TYPE,
                  description="List of the volumes to join into a union")
    ],
    name='union',
)

TYPE_MAPPING = {
    'cv-volume': build_cv_volume,
    'intersection': build_intersection_volume,
}

volume_parser = Parser(TYPE_MAPPING, label="volumes")

