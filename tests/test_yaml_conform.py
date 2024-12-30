import os
import shutil
from pathlib import Path
from unittest import TestCase

from cattrs import structure
import cattrs

import pytest

from yaml import load, dump

from dirs_navigator import *

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


# @pytest.mark.skip(reason="not able to execute the tests on runners due to resource constraints")
class TestYamlConform(TestCase):
    user_dir = "/home/user/src"
    user_id = "user_id"

    def setUp(self):
        self.root_group = load(open("tests/data/job.yml"), Loader=Loader)
        self.node1 = load(open("tests/data/.navigator_1.yml"), Loader=Loader)
        self.node2 = load(open("tests/data/.navigator_2.yml"), Loader=Loader)

    def tearDown(self):
        pass

    def test_deserialize_ok(self):
        # Given
        # Then
        # self.assertTrue(True), ""
        root = converter.structure(self.root_group, RootGroup)
        match root:
            case RootGroup(git_working_trees=[WorkTree(path=path, tag=tag)], base_paths=base_paths):
                self.assertEqual(path, "~/src/a/intelygenz/src/trinity/base")
                self.assertEqual(tag, "base")
                self.assertEqual(base_paths, ["~/src/a/intelygenz/src"])

        node1 = converter.structure(self.node1, Node)
        node1.cwd = self.user_dir

        match node1:
            case Node(paths, expansions, excludes, includes=includes, cwd=cwd, tag=tag):
                self.assertEqual(paths, ["git-dependencies2"])
                self.assertEqual(includes, ["demos", "ds-trinity"])
                self.assertEqual(expansions, None)
                self.assertEqual(excludes, None)
                self.assertEqual(tag, "nav1")
                self.assertEqual(cwd, self.user_dir)

        node2 = converter.structure(self.node2, Node)

        match node2:
            case Node(base_paths=paths, expansions=[Expansion(path, level,tag=expansion_tag)], excludes=excludes, includes=includes,cwd=cwd,tag=tag):
                self.assertEqual(path, "PHALP-deps")
                self.assertEqual(level, 2)
                self.assertEqual(excludes, ["base", "pypi"])
                self.assertEqual(paths, None)
                self.assertEqual(includes, None)
                self.assertEqual(cwd, None)
                self.assertEqual(tag, "nav2")
                self.assertEqual(expansion_tag, "phalp-deps")

        # clean up
