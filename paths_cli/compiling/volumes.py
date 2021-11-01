import operator
import functools

from paths_cli.compiling.core import Parameter
from paths_cli.compiling.tools import custom_eval
from paths_cli.compiling.plugins import VolumeCompilerPlugin, CategoryPlugin
from paths_cli.compiling.root_compiler import compiler_for


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
        Parameter('cv', compiler_for('cv'),
                  description="CV that defines this volume"),
        Parameter('lambda_min', custom_eval,
                  description="Lower bound for this volume"),
        Parameter('lambda_max', custom_eval,
                  description="Upper bound for this volume")
    ],
    name='cv-volume',
)

build_cv_volume = CV_VOLUME_PLUGIN

# jsonschema type for combination volumes
VOL_ARRAY_TYPE = {
    'type': 'array',
    'items': {"$ref": "#/definitions/volume_type"}
}


INTERSECTION_VOLUME_PLUGIN = VolumeCompilerPlugin(
    builder=lambda subvolumes: functools.reduce(operator.__and__,
                                                subvolumes),
    parameters=[
        Parameter('subvolumes', compiler_for('volume'),
                  json_type=VOL_ARRAY_TYPE,
                  description="List of the volumes to intersect")
    ],
    name='intersection',
)

build_intersection_volume = INTERSECTION_VOLUME_PLUGIN


UNION_VOLUME_PLUGIN = VolumeCompilerPlugin(
    builder=lambda subvolumes: functools.reduce(operator.__or__,
                                                subvolumes),
    parameters=[
        Parameter('subvolumes', compiler_for('volume'),
                  json_type=VOL_ARRAY_TYPE,
                  description="List of the volumes to join into a union")
    ],
    name='union',
)

build_union_volume = UNION_VOLUME_PLUGIN


VOLUME_COMPILER = CategoryPlugin(VolumeCompilerPlugin, aliases=['state',
                                                                'states'])
