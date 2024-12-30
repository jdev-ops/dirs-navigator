import os
import shutil
from pathlib import Path
from unittest import TestCase

from cattrs import structure
import cattrs

import pytest

from yaml import load, dump

from dirs_navigator import *
from dirs_navigator.navigator import normalize_path

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


# @pytest.mark.skip(reason="not able to execute the tests on runners due to resource constraints")
class TestLogic(TestCase):

    def setUp(self):
        pass

    def test_normalize(self):
        # res = normalize_path("~/src/")
        # self.assertEqual(res, f"{os.environ["HOME"]}/src/")
        # global_user = "/home/user/src/"
        # res = normalize_path(global_user)
        # self.assertEqual(res, global_user)
        pass
