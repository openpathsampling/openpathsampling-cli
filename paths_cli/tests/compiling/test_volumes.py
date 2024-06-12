import pytest
from unittest import mock
from paths_cli.tests.compiling.utils import mock_compiler
from paths_cli.compiling.plugins import CVCompilerPlugin
from paths_cli.compiling.core import Parameter

import yaml
import numpy as np
import openpathsampling as paths
from openpathsampling.experimental.storage.collective_variables import \
        CoordinateFunctionCV
from openpathsampling.tests.test_helpers import make_1d_traj

from paths_cli.compiling.volumes import *

class TestBuildCVVolume:
    def setup_method(self):
        self.yml = "\n".join(["type: cv-volume", "cv: {func}",
                              "lambda_min: 0", "lambda_max: 1"])

        self.named_objs_dict = {
            'foo': {'name': 'foo',
                    'type': 'bar',
                    'func': 'foo_func'}
        }

        self.func = {
            'inline': "\n  " + "\n  ".join([
                "name: foo",
                "type: fake_type",
                "input_data: bar",
            ]),
            'external': 'foo'
        }

    def set_periodic(self, periodic):
        if periodic == 'periodic':
            self.named_objs_dict['foo']['period_max'] = 'np.pi'
            self.named_objs_dict['foo']['period_min'] = '-np.pi'

    @pytest.mark.parametrize('inline', ['external', 'inline'])
    @pytest.mark.parametrize('periodic', ['periodic', 'nonperiodic'])
    def test_build_cv_volume(self, inline, periodic):
        self.set_periodic(periodic)
        yml = self.yml.format(func=self.func[inline])
        dct = yaml.load(yml, Loader=yaml.FullLoader)
        period_min, period_max = {'periodic': (-np.pi, np.pi),
                                  'nonperiodic': (None, None)}[periodic]
        mock_cv = CoordinateFunctionCV(lambda s: s.xyz[0][0],
                                       period_min=period_min,
                                       period_max=period_max).named('foo')

        patch_loc = 'paths_cli.compiling.root_compiler._COMPILERS'

        if inline =='external':
            compilers = {
                'cv': mock_compiler('cv', named_objs={'foo': mock_cv})
            }
        elif inline == 'inline':
            fake_plugin = CVCompilerPlugin(
                name="fake_type",
                parameters=[Parameter('input_data', str)],
                builder=lambda input_data: mock_cv
            )
            compilers = {
                'cv': mock_compiler(
                    'cv',
                    type_dispatch={'fake_type': fake_plugin}
                )
            }
        else:  # -no-cov-
            raise RuntimeError("Should never get here")

        with mock.patch.dict(patch_loc, compilers):
            vol = build_cv_volume(dct)

        in_state = make_1d_traj([0.5])[0]
        assert vol.collectivevariable(in_state) == 0.5
        assert vol(in_state)
        out_state = make_1d_traj([2.0])[0]
        assert vol.collectivevariable(out_state) == 2.0
        assert not vol(out_state)
        if_periodic = make_1d_traj([7.0])[0]
        assert (vol(if_periodic) == (periodic == 'periodic'))
        expected_class = {
            'nonperiodic': paths.CVDefinedVolume,
            'periodic': paths.PeriodicCVDefinedVolume
        }[periodic]
        assert isinstance(vol, expected_class)


class TestBuildCombinationVolume:
    def setup_method(self):
        from  openpathsampling.experimental.storage.collective_variables \
                import CollectiveVariable
        self.cv = CollectiveVariable(lambda s: s.xyz[0][0]).named('foo')

    def _vol_and_yaml(self, lambda_min, lambda_max, name):
        yml = ['- type: cv-volume', '  cv: foo',
               f"  lambda_min: {lambda_min}",
               f"  lambda_max: {lambda_max}"]
        vol = paths.CVDefinedVolume(self.cv, lambda_min,
                                    lambda_max).named(name)
        description = {'name': name,
                       'type': 'cv-volume',
                       'cv': 'foo',
                       'lambda_min': lambda_min,
                       'lambda_max': lambda_max}
        return vol, yml, description

    @pytest.mark.parametrize('combo', ['union', 'intersection'])
    @pytest.mark.parametrize('inline', [True, False])
    def test_build_combo_volume(self, combo, inline):
        vol_A, yaml_A, desc_A = self._vol_and_yaml(0.0, 0.55, "A")
        vol_B, yaml_B, desc_B = self._vol_and_yaml(0.45, 1.0, "B")
        if inline:
            named_volumes_dict = {}
            descriptions = {}
            subvol_yaml = ['  ' + line for line in yaml_A + yaml_B]
        else:
            named_volumes_dict = {v.name: v for v in [vol_A, vol_B]}
            descriptions = {"A": desc_A, "B": desc_B}
            subvol_yaml = ['  - A', '  - B']

        yml = "\n".join([f"type: {combo}", "name: bar", "subvolumes:"]
                        + subvol_yaml)

        combo_class = {'union': paths.UnionVolume,
                       'intersection': paths.IntersectionVolume}[combo]
        builder = {'union': build_union_volume,
                   'intersection': build_intersection_volume}[combo]

        true_vol = combo_class(vol_A, vol_B)
        dct = yaml.load(yml, yaml.FullLoader)
        compiler = {
            'cv': mock_compiler('cv', named_objs={'foo': self.cv}),
            'volume': mock_compiler(
                'volume',
                type_dispatch={'cv-volume': build_cv_volume},
                named_objs=named_volumes_dict
            ),
        }
        with mock.patch.dict('paths_cli.compiling.root_compiler._COMPILERS',
                             compiler):
            vol = builder(dct)

        traj = make_1d_traj([0.5, 2.0, 0.2])
        assert vol(traj[0])
        assert not vol(traj[1])
        assert vol(traj[2]) == (combo == 'union')
