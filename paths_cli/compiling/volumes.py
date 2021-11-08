import operator
import functools

from paths_cli.compiling.core import Parameter
from paths_cli.compiling.tools import custom_eval_float
from paths_cli.compiling.plugins import VolumeCompilerPlugin, CategoryPlugin
from paths_cli.compiling.root_compiler import compiler_for
from paths_cli.compiling.json_type import (
    json_type_ref, json_type_eval, json_type_list
)


# TODO: extra function for volumes should not be necessary as of OPS 2.0
def cv_volume_build_func(**dct):
    import openpathsampling as paths
    cv = dct['cv']
    builder = paths.CVDefinedVolume
    if cv.period_min is not None or cv.period_max is not None:
        builder = paths.PeriodicCVDefinedVolume
        dct['period_min'] = cv.period_min
        dct['period_max'] = cv.period_max

    dct['collectivevariable'] = dct.pop('cv')
    # TODO: wrap this with some logging
    return builder(**dct)


CV_VOLUME_PLUGIN = VolumeCompilerPlugin(
    builder=cv_volume_build_func,
    parameters=[
        Parameter('cv', compiler_for('cv'), json_type=json_type_ref('cv'),
                  description="CV that defines this volume"),
        Parameter('lambda_min', custom_eval_float,
                  json_type=json_type_eval("Float"),
                  description="Lower bound for this volume"),
        Parameter('lambda_max', custom_eval_float,
                  json_type=json_type_eval("Float"),
                  description="Upper bound for this volume")
    ],
    description=("A volume defined by an allowed range of values for the "
                 "given CV."),
    name='cv-volume',
)

build_cv_volume = CV_VOLUME_PLUGIN


INTERSECTION_VOLUME_PLUGIN = VolumeCompilerPlugin(
    builder=lambda subvolumes: functools.reduce(operator.__and__,
                                                subvolumes),
    parameters=[
        Parameter('subvolumes', compiler_for('volume'),
                  json_type=json_type_list(json_type_ref('volume')),
                  description="List of the volumes to intersect")
    ],
    description=("A volume determined by the intersection of its "
                 "constituent volumes; i.e., to be in this volume a point "
                 "must be in *all* the constituent volumes."),
    name='intersection',
)

build_intersection_volume = INTERSECTION_VOLUME_PLUGIN


UNION_VOLUME_PLUGIN = VolumeCompilerPlugin(
    builder=lambda subvolumes: functools.reduce(operator.__or__,
                                                subvolumes),
    parameters=[
        Parameter('subvolumes', compiler_for('volume'),
                  json_type=json_type_list(json_type_ref('volume')),
                  description="List of the volumes to join into a union")
    ],
    description=("A volume defined by the union of its constituent "
                 "volumes; i.e., a point that is in *any* of the "
                 "constituent volumes is also in this volume."),
    name='union',
)

build_union_volume = UNION_VOLUME_PLUGIN


VOLUME_COMPILER = CategoryPlugin(VolumeCompilerPlugin, aliases=['state',
                                                                'states'])
