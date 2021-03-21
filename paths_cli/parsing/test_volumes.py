import pytest
import mock

import yaml
import openpathsampling as paths

from paths_cli.parsing.volumes import *

class TestBuildCVVolume:
    def setup(self):
        self.yml = "\n".join(["type: cv-volume", "cv: {func}",
                              "lambda_min: 0", "lambda_max: 1"])

        self.mock_cv = mock.Mock(return_value=0.5)
        self.named_objs_dict = {
            'foo': {'name': 'foo',
                    'type': 'bar',
                    'func': 'foo_func'}
        }
        mock_named_objs = mock.MagicMock()
        mock_named_objs.__getitem__ = mock.Mock(return_value=self.mock_cv)
        mock_named_objs.descriptions = self.named_objs_dict

        self.named_objs = {
            'inline': ...,
            'external': mock_named_objs
        }
        self.func = {
            'inline': "\n  ".join(["name: foo", "type: mdtraj"]),  # TODO
            'external': 'foo'
        }

    def create_inputs(self, inline, periodic):
        yml = "\n".join(["type: cv-volume", "cv: {func}",
                         "lambda_min: 0", "lambda_max: 1"])

    def set_periodic(self, periodic):
        if periodic == 'periodic':
            self.named_objs_dict['foo']['period_max'] = 'np.pi'
            self.named_objs_dict['foo']['period_min'] = '-np.pi'

    @pytest.mark.parametrize('inline', ['external', 'external'])
    @pytest.mark.parametrize('periodic', ['periodic', 'nonperiodic'])
    def test_build_cv_volume(self, inline, periodic):
        self.set_periodic(periodic)
        yml = self.yml.format(func=self.func[inline])
        dct = yaml.load(yml, Loader=yaml.FullLoader)
        if inline =='external':
            patchloc = 'paths_cli.parsing.volumes.cv_parser.named_objs'
            with mock.patch.dict(patchloc, {'foo': self.mock_cv}):
                vol = build_cv_volume(dct)
        elif inline == 'internal':
            vol = build_cv_volume(dct)
        assert vol.collectivevariable(1) == 0.5
        expected_class = {
            'nonperiodic': paths.CVDefinedVolume,
            'periodic': paths.PeriodicCVDefinedVolume
        }[periodic]
        assert isinstance(vol, expected_class)


class TestBuildIntersectionVolume:
    def setup(self):
        self.yml = "\n".join([
            'type: intersection', 'name: inter', 'subvolumes:',
            '  - type: cv-volume',
        ])
        pass
