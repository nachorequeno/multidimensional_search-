import os
import tempfile as tf
import unittest
import pytest
import copy

from ParetoLib.Geometry.Rectangle import Rectangle

from ParetoLib.Search.ParResultSet import ParResultSet
from ParetoLib.Search.ResultSet import ResultSet
from ParetoLib.Search.Search import create_2D_space, create_3D_space


class ResultSetTestCase(unittest.TestCase):

    def setUp(self):
        # type: (ResultSetTestCase) -> None
        self.files_to_clean = set()

        # Set of rectangles calculated by doc/example/example2d.py
        # Search2D stopped after 5 steps
        self.border_2D = [Rectangle((0.624992370605469, 0.249996185186319), (0.75, 0.375001907290425)),
                          Rectangle((0.125001907348633, 0.749992370605469), (0.250003814697266, 0.875003814930096)),
                          Rectangle((0.749992370605469, 0.125001907348633), (0.875003814930096, 0.250003814697266)),
                          Rectangle((0.5, 0.374994277546644), (0.625, 0.500007629394531)),
                          Rectangle((0.0, 0.874996185302734), (0.12500953685958, 1.0)),
                          Rectangle((0.874996185302734, 0.0), (1.0, 0.12500953685958)),
                          Rectangle((0.249996185186319, 0.5), (0.500007629394531, 0.75))]

        self.ylow_2D = [Rectangle((0.0, 0.0), (0.5, 0.5)),
                        Rectangle((0.5, 0.0), (0.749992370605469, 0.249996185186319)),
                        Rectangle((0.0, 0.5), (0.249996185186319, 0.749992370605469)),
                        Rectangle((0.749992370605469, 0.0), (0.874996185302734, 0.125001907348633)),
                        Rectangle((0.0, 0.749992370605469), (0.125001907348633, 0.874996185302734)),
                        Rectangle((0.5, 0.249996185186319), (0.624992370605469, 0.374994277546644))]

        self.yup_2D = [Rectangle((0.500007629394531, 0.500007629394531), (1.0, 1.0)),
                       Rectangle((0.75, 0.250003814697266), (1.0, 0.500007629394531)),
                       Rectangle((0.250003814697266, 0.75), (0.500007629394531, 1.0)),
                       Rectangle((0.875003814930096, 0.12500953685958), (1.0, 0.250003814697266)),
                       Rectangle((0.12500953685958, 0.875003814930096), (0.250003814697266, 1.0)),
                       Rectangle((0.625, 0.375001907290425), (0.75, 0.500007629394531))]

        self.xspace_2D = create_2D_space(0.0, 0.0, 1.0, 1.0)

        self.rs_2D = ResultSet(self.border_2D, self.ylow_2D, self.yup_2D, self.xspace_2D)
        self.rs2 = ResultSet()

        # Set of rectangles calculated by doc/example/example3d.py
        # Search3D stopped after 5 steps
        self.border_3D = [Rectangle((0.5, 0.5, 0.0), (0.500007629394531, 0.500007629394531, 0.500007629394531)),
                          Rectangle((0.5, 0.5, 0.0), (1.0, 0.500007629394531, 7.629510947e-06)),
                          Rectangle((0.5, 0.5, 0.0), (0.500007629394531, 1.0, 7.629510947e-06)),
                          Rectangle((0.0, 0.499999999883584, 0.999992370605469),
                                    (0.500007629394531, 0.500007629394531, 1.0)),
                          Rectangle((0.499999999883584, 0.0, 0.999992370605469),
                                    (0.500007629394531, 0.500007629394531, 1.0)),
                          Rectangle((0.499999999883584, 0.499999999883584, 0.5),
                                    (0.500007629394531, 0.500007629394531, 1.0)),
                          Rectangle((0.5, 0.5, 0.0), (0.500007629394531, 1.0, 0.500007629394531)),
                          Rectangle((0.5, 0.5, 0.0), (1.0, 0.500007629394531, 0.500007629394531)),
                          Rectangle((0.5, 0.5, 0.0), (1.0, 1.0, 7.629510947e-06)),
                          Rectangle((0.0, 0.0, 0.999992370605469), (0.500007629394531, 0.500007629394531, 1.0)),
                          Rectangle((0.499999999883584, 0.0, 0.5), (0.500007629394531, 0.500007629394531, 1.0)),
                          Rectangle((0.0, 0.499999999883584, 0.5), (0.500007629394531, 0.500007629394531, 1.0)),
                          Rectangle((0.5, 0.249996185186319, 0.5), (0.75, 0.500007629394531, 0.75)),
                          Rectangle((0.749992370605469, 0.0, 0.5), (1.0, 0.250003814697266, 0.75)),
                          Rectangle((0.5, 0.0, 0.749992370605469), (0.75, 0.250003814697266, 1.0)),
                          Rectangle((0.5, 0.0, 0.249996185186319), (0.75, 0.250003814697266, 0.500007629394531)),
                          Rectangle((0.5, 0.249996185186319, 0.0), (0.75, 0.500007629394531, 0.250003814697266)),
                          Rectangle((0.249996185186319, 0.5, 0.0), (0.500007629394531, 0.75, 0.250003814697266)),
                          Rectangle((0.0, 0.5, 0.249996185186319), (0.250003814697266, 0.75, 0.500007629394531)),
                          Rectangle((0.749992370605469, 0.0, 0.0), (1.0, 0.250003814697266, 0.250003814697266)),
                          Rectangle((0.0, 0.749992370605469, 0.0), (0.250003814697266, 1.0, 0.250003814697266)),
                          Rectangle((0.5, 0.249996185186319, 0.749992370605469), (0.75, 0.500007629394531, 1.0)),
                          Rectangle((0.749992370605469, 0.249996185186319, 0.5), (1.0, 0.500007629394531, 0.75)),
                          Rectangle((0.749992370605469, 0.0, 0.749992370605469), (1.0, 0.250003814697266, 1.0)),
                          Rectangle((0.5, 0.249996185186319, 0.249996185186319),
                                    (0.75, 0.500007629394531, 0.500007629394531)),
                          Rectangle((0.249996185186319, 0.5, 0.249996185186319),
                                    (0.500007629394531, 0.75, 0.500007629394531)),
                          Rectangle((0.749992370605469, 0.249996185186319, 0.0),
                                    (1.0, 0.500007629394531, 0.250003814697266)),
                          Rectangle((0.749992370605469, 0.0, 0.249996185186319),
                                    (1.0, 0.250003814697266, 0.500007629394531)),
                          Rectangle((0.0, 0.749992370605469, 0.249996185186319),
                                    (0.250003814697266, 1.0, 0.500007629394531)),
                          Rectangle((0.249996185186319, 0.749992370605469, 0.0),
                                    (0.500007629394531, 1.0, 0.250003814697266)),
                          Rectangle((0.0, 0.5, 0.5), (0.500007629394531, 1.0, 1.0))]

        self.ylow_3D = [Rectangle((0.0, 0.0, 0.0), (0.5, 0.5, 0.5)),
                        Rectangle((0.0, 0.5, 0.0), (0.249996185186319, 0.749992370605469, 0.249996185186319)),
                        Rectangle((0.0, 0.0, 0.5), (0.499999999883584, 0.499999999883584, 0.999992370605469)),
                        Rectangle((0.5, 0.0, 0.0), (0.749992370605469, 0.249996185186319, 0.249996185186319)),
                        Rectangle((0.5, 0.0, 0.5), (0.749992370605469, 0.249996185186319, 0.749992370605469)),
                        Rectangle((0.5, 0.5, 0.0), (0.5, 0.5, 0.0))]

        self.yup_3D = [Rectangle((0.500007629394531, 0.500007629394531, 7.629510947e-06), (1.0, 1.0, 1.0)),
                       Rectangle((0.250003814697266, 0.75, 0.250003814697266),
                                 (0.500007629394531, 1.0, 0.500007629394531)),
                       Rectangle((0.500007629394531, 0.500007629394531, 1.0),
                                 (0.500007629394531, 0.500007629394531, 1.0)),
                       Rectangle((0.75, 0.250003814697266, 0.250003814697266),
                                 (1.0, 0.500007629394531, 0.500007629394531)),
                       Rectangle((0.75, 0.250003814697266, 0.75), (1.0, 0.500007629394531, 1.0))]

        self.xspace_3D = create_3D_space(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        self.rs_3D = ResultSet(self.border_3D, self.ylow_3D, self.yup_3D, self.xspace_3D)

    def tearDown(self):
        # type: (ResultSetTestCase) -> None
        for filename in self.files_to_clean:
            if os.path.isfile(filename):
                os.remove(filename)

    def add_file_to_clean(self, filename):
        # type: (ResultSetTestCase) -> None
        self.files_to_clean.add(filename)

    def test_files_2D(self):
        # type: (ResultSetTestCase) -> None
        tmpfile = tf.NamedTemporaryFile(delete=False)
        nfile = tmpfile.name

        self.rs_2D.to_file(nfile)
        self.rs2.from_file(nfile)

        self.assertTrue(self.rs_2D == self.rs2)

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(nfile)

    def test_files_3D(self):
        # type: (ResultSetTestCase) -> None
        tmpfile = tf.NamedTemporaryFile(delete=False)
        nfile = tmpfile.name

        self.rs_3D.to_file(nfile)
        self.rs2.from_file(nfile)

        self.assertTrue(self.rs_3D == self.rs2)

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(nfile)

    def test_vertices_2D(self):
        # type: (ResultSetTestCase) -> None

        s1 = {(0.250003814697266, 1.0), (0.875003814930096, 0.12500953685958), (0.12500953685958, 1.0),
              (0.75, 0.250003814697266), (0.625, 0.375001907290425), (0.75, 0.375001907290425),
              (0.250003814697266, 0.875003814930096), (0.625, 0.500007629394531), (1.0, 0.12500953685958),
              (0.500007629394531, 0.500007629394531), (0.250003814697266, 0.75), (0.75, 0.500007629394531),
              (0.12500953685958, 0.875003814930096), (1.0, 0.250003814697266), (0.500007629394531, 1.0),
              (0.500007629394531, 0.75), (1.0, 1.0), (0.875003814930096, 0.250003814697266),
              (1.0, 0.500007629394531)}

        s2 = {(0.125001907348633, 0.874996185302734), (0.5, 0.5), (0.249996185186319, 0.5), (0.0, 0.749992370605469),
              (0.0, 0.5), (0.874996185302734, 0.125001907348633), (0.749992370605469, 0.249996185186319),
              (0.624992370605469, 0.249996185186319), (0.125001907348633, 0.749992370605469), (0.749992370605469, 0.0),
              (0.5, 0.0), (0.624992370605469, 0.374994277546644), (0.0, 0.874996185302734), (0.5, 0.249996185186319),
              (0.0, 0.0), (0.5, 0.374994277546644), (0.874996185302734, 0.0), (0.749992370605469, 0.125001907348633),
              (0.249996185186319, 0.749992370605469)}

        s3 = {(0.0, 0.874996185302734), (0.75, 0.375001907290425), (0.249996185186319, 0.75),
              (0.875003814930096, 0.250003814697266), (0.624992370605469, 0.375001907290425),
              (0.125001907348633, 0.749992370605469), (0.874996185302734, 0.0),
              (0.749992370605469, 0.250003814697266),
              (0.249996185186319, 0.5), (0.500007629394531, 0.5), (0.500007629394531, 0.75),
              (0.250003814697266, 0.749992370605469), (0.5, 0.374994277546644), (0.12500953685958, 1.0),
              (0.250003814697266, 0.875003814930096), (0.125001907348633, 0.875003814930096),
              (0.5, 0.500007629394531),
              (0.75, 0.249996185186319), (1.0, 0.0), (0.0, 1.0), (0.624992370605469, 0.249996185186319),
              (0.625, 0.500007629394531), (1.0, 0.12500953685958), (0.625, 0.374994277546644),
              (0.12500953685958, 0.874996185302734), (0.749992370605469, 0.125001907348633),
              (0.875003814930096, 0.125001907348633), (0.874996185302734, 0.12500953685958)}

        self.assertEqual(s1, self.rs_2D.vertices_yup())
        self.assertEqual(s2, self.rs_2D.vertices_ylow())
        self.assertEqual(s3, self.rs_2D.vertices_border())
        self.assertEqual(s1.union(s2).union(s3), self.rs_2D.vertices())

    def test_vertices_3D(self):
        # type: (ResultSetTestCase) -> None

        s1 = {(0.75, 0.500007629394531, 0.500007629394531), (0.250003814697266, 1.0, 0.500007629394531),
               (0.500007629394531, 1.0, 7.629510947e-06), (1.0, 0.250003814697266, 0.250003814697266),
               (0.75, 0.250003814697266, 0.75), (0.500007629394531, 0.75, 0.500007629394531),
               (0.75, 0.500007629394531, 1.0), (1.0, 1.0, 7.629510947e-06), (1.0, 0.500007629394531, 1.0),
               (1.0, 1.0, 1.0), (1.0, 0.500007629394531, 0.75), (0.250003814697266, 0.75, 0.500007629394531),
               (1.0, 0.500007629394531, 7.629510947e-06), (1.0, 0.250003814697266, 0.75),
               (0.500007629394531, 1.0, 0.500007629394531), (0.500007629394531, 1.0, 1.0),
               (1.0, 0.500007629394531, 0.500007629394531), (0.500007629394531, 1.0, 0.250003814697266),
               (0.75, 0.250003814697266, 1.0), (0.250003814697266, 0.75, 0.250003814697266),
               (0.500007629394531, 0.500007629394531, 1.0), (1.0, 0.250003814697266, 1.0),
               (0.500007629394531, 0.500007629394531, 7.629510947e-06), (1.0, 0.500007629394531, 0.250003814697266),
               (0.75, 0.500007629394531, 0.75), (0.500007629394531, 0.75, 0.250003814697266),
               (0.75, 0.250003814697266, 0.250003814697266), (1.0, 0.250003814697266, 0.500007629394531),
               (0.250003814697266, 1.0, 0.250003814697266), (0.75, 0.500007629394531, 0.250003814697266),
               (0.75, 0.250003814697266, 0.500007629394531)}

        s2 = {(0.749992370605469, 0.0, 0.749992370605469), (0.5, 0.0, 0.749992370605469),
               (0.749992370605469, 0.249996185186319, 0.5), (0.0, 0.0, 0.5), (0.749992370605469, 0.0, 0.5),
               (0.0, 0.5, 0.5), (0.499999999883584, 0.0, 0.999992370605469),
               (0.749992370605469, 0.249996185186319, 0.249996185186319), (0.0, 0.0, 0.0),
               (0.5, 0.249996185186319, 0.5),
               (0.0, 0.5, 0.249996185186319), (0.5, 0.249996185186319, 0.249996185186319),
               (0.0, 0.749992370605469, 0.249996185186319), (0.749992370605469, 0.0, 0.0),
               (0.249996185186319, 0.749992370605469, 0.0), (0.5, 0.0, 0.5),
               (0.5, 0.249996185186319, 0.749992370605469),
               (0.249996185186319, 0.749992370605469, 0.249996185186319),
               (0.499999999883584, 0.499999999883584, 0.999992370605469), (0.5, 0.0, 0.249996185186319),
               (0.249996185186319, 0.5, 0.249996185186319), (0.0, 0.0, 0.999992370605469),
               (0.5, 0.249996185186319, 0.0),
               (0.249996185186319, 0.5, 0.0), (0.0, 0.5, 0.0), (0.0, 0.749992370605469, 0.0), (0.5, 0.5, 0.5),
               (0.499999999883584, 0.499999999883584, 0.5), (0.749992370605469, 0.249996185186319, 0.749992370605469),
               (0.749992370605469, 0.0, 0.249996185186319), (0.0, 0.499999999883584, 0.999992370605469),
               (0.499999999883584, 0.0, 0.5), (0.5, 0.0, 0.0), (0.0, 0.499999999883584, 0.5), (0.5, 0.5, 0.0),
               (0.749992370605469, 0.249996185186319, 0.0)}

        s3 = {(0.749992370605469, 0.0, 0.250003814697266), (0.249996185186319, 0.749992370605469, 0.0),
               (0.75, 0.500007629394531, 0.250003814697266), (1.0, 0.500007629394531, 0.75),
               (1.0, 0.249996185186319, 0.5), (1.0, 0.249996185186319, 0.250003814697266), (1.0, 0.0, 0.5),
               (0.749992370605469, 0.249996185186319, 0.0), (0.749992370605469, 0.250003814697266, 0.250003814697266),
               (1.0, 0.250003814697266, 0.749992370605469), (1.0, 1.0, 7.629510947e-06),
               (0.500007629394531, 0.500007629394531, 0.500007629394531),
               (0.250003814697266, 0.749992370605469, 0.250003814697266), (0.250003814697266, 1.0, 0.0),
               (0.500007629394531, 0.5, 1.0), (0.5, 0.249996185186319, 0.500007629394531),
               (0.499999999883584, 0.0, 0.5),
               (0.749992370605469, 0.250003814697266, 0.5), (0.75, 0.0, 0.249996185186319),
               (0.5, 0.250003814697266, 0.249996185186319), (0.500007629394531, 1.0, 0.0),
               (1.0, 0.250003814697266, 0.500007629394531), (0.749992370605469, 0.0, 0.500007629394531),
               (0.749992370605469, 0.250003814697266, 0.500007629394531), (0.249996185186319, 1.0, 0.0),
               (0.749992370605469, 0.0, 1.0), (0.5, 0.500007629394531, 0.0),
               (0.749992370605469, 0.249996185186319, 0.75),
               (0.249996185186319, 0.5, 0.0), (0.250003814697266, 0.75, 0.249996185186319), (1.0, 0.0, 1.0),
               (0.5, 0.0, 0.749992370605469), (0.0, 0.5, 1.0), (1.0, 0.250003814697266, 0.250003814697266),
               (0.749992370605469, 0.250003814697266, 0.75), (0.0, 0.749992370605469, 0.249996185186319),
               (0.75, 0.500007629394531, 1.0), (1.0, 0.0, 0.500007629394531),
               (0.75, 0.249996185186319, 0.749992370605469), (1.0, 1.0, 0.0),
               (0.500007629394531, 0.749992370605469, 0.0),
               (0.499999999883584, 0.0, 0.999992370605469), (0.500007629394531, 0.499999999883584, 1.0),
               (0.5, 0.500007629394531, 1.0), (0.5, 1.0, 7.629510947e-06),
               (0.250003814697266, 0.749992370605469, 0.500007629394531), (0.5, 0.500007629394531, 0.75),
               (0.0, 0.499999999883584, 1.0), (1.0, 0.249996185186319, 0.0), (0.749992370605469, 0.0, 0.0),
               (1.0, 0.250003814697266, 1.0), (0.75, 0.500007629394531, 0.5),
               (0.500007629394531, 0.5, 0.500007629394531),
               (0.75, 0.500007629394531, 0.249996185186319), (0.500007629394531, 0.5, 7.629510947e-06),
               (0.0, 1.0, 0.500007629394531), (0.0, 0.5, 0.500007629394531),
               (0.75, 0.500007629394531, 0.749992370605469),
               (0.500007629394531, 0.75, 0.500007629394531), (0.500007629394531, 0.749992370605469, 0.250003814697266),
               (0.500007629394531, 0.5, 0.250003814697266), (0.0, 1.0, 0.250003814697266),
               (0.749992370605469, 0.500007629394531, 0.250003814697266), (0.75, 0.249996185186319, 0.75),
               (1.0, 0.500007629394531, 7.629510947e-06), (0.500007629394531, 0.500007629394531, 0.0),
               (0.500007629394531, 0.0, 0.999992370605469), (0.749992370605469, 0.249996185186319, 0.250003814697266),
               (1.0, 0.500007629394531, 0.0), (0.749992370605469, 0.0, 0.5),
               (0.0, 0.499999999883584, 0.999992370605469),
               (0.249996185186319, 0.75, 0.500007629394531), (1.0, 0.5, 0.500007629394531),
               (0.500007629394531, 1.0, 1.0),
               (0.5, 0.249996185186319, 0.749992370605469), (0.500007629394531, 0.5, 0.5),
               (0.499999999883584, 0.0, 1.0),
               (0.5, 0.0, 1.0), (0.75, 0.250003814697266, 1.0),
               (0.749992370605469, 0.250003814697266, 0.249996185186319),
               (0.0, 0.749992370605469, 0.0), (0.5, 0.249996185186319, 0.0),
               (0.749992370605469, 0.249996185186319, 0.5),
               (0.0, 0.75, 0.500007629394531), (1.0, 0.249996185186319, 0.75),
               (0.75, 0.249996185186319, 0.250003814697266), (0.5, 1.0, 0.0), (0.749992370605469, 0.0, 0.75),
               (0.499999999883584, 0.500007629394531, 0.5), (1.0, 0.0, 0.749992370605469), (0.0, 0.0, 1.0),
               (1.0, 0.500007629394531, 0.250003814697266), (0.500007629394531, 0.75, 0.250003814697266),
               (0.5, 0.500007629394531, 0.5), (0.500007629394531, 0.500007629394531, 0.5), (0.75, 0.0, 1.0),
               (0.0, 1.0, 0.0), (0.75, 0.249996185186319, 0.500007629394531), (1.0, 0.5, 7.629510947e-06),
               (0.75, 0.0, 0.749992370605469), (0.0, 0.500007629394531, 0.5),
               (0.0, 0.749992370605469, 0.500007629394531),
               (0.5, 0.5, 0.500007629394531), (0.75, 0.249996185186319, 0.5),
               (0.75, 0.500007629394531, 0.500007629394531), (0.75, 0.249996185186319, 1.0),
               (0.749992370605469, 0.500007629394531, 0.0), (0.500007629394531, 0.499999999883584, 0.5),
               (0.0, 0.5, 0.5),
               (0.749992370605469, 0.250003814697266, 0.749992370605469), (0.250003814697266, 1.0, 0.249996185186319),
               (0.249996185186319, 0.75, 0.250003814697266), (0.0, 0.500007629394531, 1.0),
               (0.250003814697266, 0.749992370605469, 0.249996185186319), (1.0, 0.250003814697266, 0.0),
               (0.75, 0.249996185186319, 0.249996185186319), (0.499999999883584, 0.499999999883584, 1.0),
               (0.0, 0.749992370605469, 0.250003814697266), (0.249996185186319, 0.5, 0.500007629394531),
               (0.5, 0.249996185186319, 0.75), (0.5, 0.0, 0.249996185186319), (1.0, 0.500007629394531, 0.5),
               (0.5, 0.0, 0.500007629394531), (0.499999999883584, 0.500007629394531, 0.999992370605469),
               (0.5, 0.249996185186319, 0.249996185186319), (1.0, 0.250003814697266, 0.5), (0.5, 0.5, 7.629510947e-06),
               (0.250003814697266, 1.0, 0.250003814697266), (1.0, 0.500007629394531, 0.500007629394531),
               (0.249996185186319, 0.749992370605469, 0.250003814697266), (0.500007629394531, 1.0, 0.500007629394531),
               (0.500007629394531, 0.499999999883584, 0.999992370605469), (0.0, 0.75, 0.249996185186319),
               (0.249996185186319, 0.75, 0.0), (0.75, 0.250003814697266, 0.249996185186319),
               (0.500007629394531, 0.75, 0.0), (0.749992370605469, 0.500007629394531, 0.75),
               (0.500007629394531, 0.5, 0.0), (0.5, 0.500007629394531, 0.749992370605469),
               (0.749992370605469, 0.500007629394531, 0.5), (0.250003814697266, 0.5, 0.500007629394531),
               (0.5, 0.249996185186319, 0.5), (0.749992370605469, 0.250003814697266, 1.0),
               (0.749992370605469, 0.250003814697266, 0.0), (0.499999999883584, 0.500007629394531, 1.0),
               (0.500007629394531, 0.0, 1.0), (0.249996185186319, 0.5, 0.250003814697266),
               (0.5, 0.500007629394531, 0.250003814697266), (0.5, 0.5, 0.0),
               (0.5, 0.500007629394531, 0.500007629394531),
               (0.500007629394531, 1.0, 0.250003814697266), (0.0, 1.0, 1.0), (0.0, 0.5, 0.249996185186319),
               (1.0, 0.5, 0.0), (0.500007629394531, 0.0, 0.5), (0.249996185186319, 1.0, 0.250003814697266),
               (1.0, 0.0, 0.250003814697266), (0.5, 1.0, 0.500007629394531), (0.0, 0.499999999883584, 0.5),
               (0.5, 0.250003814697266, 0.500007629394531), (1.0, 0.250003814697266, 0.249996185186319),
               (0.75, 0.500007629394531, 0.0), (0.75, 0.249996185186319, 0.0), (1.0, 0.0, 0.0),
               (0.5, 0.500007629394531, 7.629510947e-06), (0.5, 0.250003814697266, 0.749992370605469),
               (0.500007629394531, 1.0, 0.5), (0.249996185186319, 0.75, 0.249996185186319),
               (0.75, 0.0, 0.500007629394531), (0.5, 0.500007629394531, 0.249996185186319),
               (0.500007629394531, 0.5, 0.249996185186319), (1.0, 0.0, 0.75),
               (0.249996185186319, 0.5, 0.249996185186319),
               (0.500007629394531, 1.0, 7.629510947e-06), (0.0, 0.0, 0.999992370605469),
               (0.500007629394531, 0.500007629394531, 0.999992370605469), (1.0, 0.0, 0.249996185186319),
               (0.5, 0.249996185186319, 1.0), (0.0, 1.0, 0.5), (0.75, 0.250003814697266, 0.749992370605469),
               (0.75, 0.250003814697266, 0.500007629394531), (0.0, 0.500007629394531, 0.999992370605469),
               (0.500007629394531, 0.500007629394531, 1.0), (0.250003814697266, 0.75, 0.500007629394531),
               (0.250003814697266, 1.0, 0.500007629394531), (0.75, 0.500007629394531, 0.75),
               (0.500007629394531, 0.75, 0.249996185186319), (0.749992370605469, 0.0, 0.249996185186319),
               (0.0, 1.0, 0.249996185186319), (0.5, 0.249996185186319, 0.250003814697266),
               (0.499999999883584, 0.499999999883584, 0.5), (0.250003814697266, 0.749992370605469, 0.0),
               (1.0, 0.250003814697266, 0.75), (0.5, 0.250003814697266, 1.0),
               (0.250003814697266, 0.5, 0.249996185186319),
               (0.749992370605469, 0.0, 0.749992370605469)}

        self.assertEqual(s1, self.rs_3D.vertices_yup())
        self.assertEqual(s2, self.rs_3D.vertices_ylow())
        self.assertEqual(s3, self.rs_3D.vertices_border())
        self.assertEqual(s1.union(s2).union(s3), self.rs_3D.vertices())

    def test_min_max_dimension_values_2D(self):
        # type: (ResultSetTestCase) -> None
        # d = 2
        d = self.yup_2D[0].dim()
        self.assertEqual(2.0, d)

        for i in range(d):
            self.assertEqual(0.12500953685958, self.rs_2D.get_min_val_dimension_yup(i))
            self.assertEqual(0.0, self.rs_2D.get_min_val_dimension_ylow(i))
            self.assertEqual(0.0, self.rs_2D.get_min_val_dimension_border(i))

            self.assertEqual(1.0, self.rs_2D.get_max_val_dimension_yup(i))
            self.assertEqual(0.874996185302734, self.rs_2D.get_max_val_dimension_ylow(i))
            self.assertEqual(1.0, self.rs_2D.get_max_val_dimension_border(i))

    def test_min_max_dimension_values_3D(self):
        # type: (ResultSetTestCase) -> None
        # d = 3
        d = self.yup_3D[0].dim()
        self.assertEqual(3.0, d)

        self.assertEqual(self.rs_3D.get_min_val_dimension_yup(0), 0.250003814697266)
        self.assertEqual(self.rs_3D.get_min_val_dimension_yup(1), 0.250003814697266)
        self.assertEqual(self.rs_3D.get_min_val_dimension_yup(2), 7.629510947e-06)
        self.assertEqual(self.rs_3D.get_min_val_dimension_ylow(0), 0.0)
        self.assertEqual(self.rs_3D.get_min_val_dimension_ylow(1), 0.0)
        self.assertEqual(self.rs_3D.get_min_val_dimension_ylow(2), 0.0)
        self.assertEqual(self.rs_3D.get_min_val_dimension_border(0), 0.0)
        self.assertEqual(self.rs_3D.get_min_val_dimension_border(1), 0.0)
        self.assertEqual(self.rs_3D.get_min_val_dimension_border(2), 0.0)

        self.assertEqual(self.rs_3D.get_max_val_dimension_yup(0), 1.0)
        self.assertEqual(self.rs_3D.get_max_val_dimension_yup(1), 1.0)
        self.assertEqual(self.rs_3D.get_max_val_dimension_yup(2), 1.0)
        self.assertEqual(self.rs_3D.get_max_val_dimension_ylow(0), 0.749992370605469)
        self.assertEqual(self.rs_3D.get_max_val_dimension_ylow(1), 0.749992370605469)
        self.assertEqual(self.rs_3D.get_max_val_dimension_ylow(2), 0.999992370605469)
        self.assertEqual(self.rs_3D.get_max_val_dimension_border(0), 1.0)
        self.assertEqual(self.rs_3D.get_max_val_dimension_border(1), 1.0)
        self.assertEqual(self.rs_3D.get_max_val_dimension_border(2), 1.0)

    def test_volume_2D(self):
        # type: (ResultSetTestCase) -> None

        self.assertEqual(0.0, self.rs_2D.overlapping_volume_yup())
        self.assertEqual(0.0, self.rs_2D.overlapping_volume_ylow())
        self.assertAlmostEqual(3.492557355327832e-10, self.rs_2D.overlapping_volume_border())
        self.assertAlmostEqual(3.492557355327832e-10, self.rs_2D.overlapping_volume_total())

        # May differ in the last decimals because of arithmetic precision
        self.assertAlmostEqual(0.42186760904587917, self.rs_2D.volume_yup())
        self.assertAlmostEqual(0.42186951636540826, self.rs_2D.volume_ylow())
        self.assertAlmostEqual(0.15626287458871257, self.rs_2D.volume_border())
        self.assertAlmostEqual(self.rs_2D.volume_border(), self.rs_2D.volume_border_2())

        # Simplify the current result set (i.e., fusion of contiguous rectangles).
        # Overlapping should disappear
        # Volume should remain identical to previous computations.
        # rs_sim = copy.deepcopy(self.rs_2D)
        rs_sim = ResultSet(self.border_2D, self.ylow_2D, self.yup_2D, self.xspace_2D)
        rs_sim.simplify()
        rs_sim.fusion()

        self.assertEqual(0.0, rs_sim.overlapping_volume_yup())
        self.assertEqual(0.0, rs_sim.overlapping_volume_ylow())
        self.assertEqual(0.0, rs_sim.overlapping_volume_border())
        self.assertEqual(0.0, rs_sim.overlapping_volume_total())

        # May differ in the last decimals because of arithmetic precision
        self.assertAlmostEqual(rs_sim.volume_yup(), self.rs_2D.volume_yup())
        self.assertAlmostEqual(rs_sim.volume_ylow(), self.rs_2D.volume_ylow())
        self.assertAlmostEqual(rs_sim.volume_border(), self.rs_2D.volume_border())
        self.assertAlmostEqual(rs_sim.volume_border_2(), self.rs_2D.volume_border_2())
        self.assertAlmostEqual(rs_sim.volume_border(), rs_sim.volume_border_2())
        # self.assertEqual(0.1562628745887126, rs_sim.volume_border_2())

    def test_volume_3D(self):
        # type: (ResultSetTestCase) -> None

        self.assertEqual(0.0, self.rs_3D.overlapping_volume_yup())
        self.assertEqual(0.0, self.rs_3D.overlapping_volume_ylow())
        self.assertAlmostEqual(1.7168407867280266e-05, self.rs_3D.overlapping_volume_border())
        self.assertAlmostEqual(2.0029416264500524e-05, self.rs_3D.overlapping_volume_total())

        # May differ in the last decimals because of arithmetic precision
        self.assertAlmostEqual(0.2968666554443193, self.rs_3D.volume_yup())
        self.assertAlmostEqual(0.2968699931807370, self.rs_3D.volume_ylow())
        self.assertAlmostEqual(0.4062633513749437, self.rs_3D.volume_border())
        self.assertAlmostEqual(self.rs_3D.volume_border(), self.rs_3D.volume_border_2())
        # self.assertAlmostEqual(0.4062633501234191, self.rs_3D.volume_border_2())

        # Simplify the current result set (i.e., fusion of contiguous rectangles).
        # Overlapping should disappear
        # Volume should remain identical to previous computations.
        # rs_sim = copy.deepcopy(self.rs_3D)
        rs_sim = ResultSet(self.border_3D, self.ylow_3D, self.yup_3D, self.xspace_3D)
        rs_sim.simplify()
        rs_sim.fusion()

        self.assertEqual(0.0, rs_sim.overlapping_volume_yup())
        self.assertEqual(0.0, rs_sim.overlapping_volume_ylow())
        self.assertEqual(0.0, rs_sim.overlapping_volume_border())
        self.assertEqual(0.0, rs_sim.overlapping_volume_total())

        # May differ in the last decimals because of arithmetic precision
        self.assertAlmostEqual(0.34374141701118816, rs_sim.volume_yup())
        self.assertAlmostEqual(0.3124945163472164, rs_sim.volume_ylow())
        self.assertAlmostEqual(0.3437640666415955, rs_sim.volume_border())
        self.assertAlmostEqual(0.3437640666415954, rs_sim.volume_border_2())
        self.assertAlmostEqual(rs_sim.volume_border(), rs_sim.volume_border_2())

    def test_points_2D(self):
        # type: (ResultSetTestCase) -> None
        n = 10
        for r in self.rs_2D.get_points_yup(n):
            self.assertTrue(self.rs_2D.member_yup(r))

        for r in self.rs_2D.get_points_ylow(n):
            self.assertTrue(self.rs_2D.member_ylow(r))

        for r in self.rs_2D.get_points_border(n):
            self.assertTrue(self.rs_2D.member_border(r))

        for r in self.rs_2D.get_points_space(n):
            self.assertTrue(self.rs_2D.member_space(r))

    def test_points_3D(self):
        # type: (ResultSetTestCase) -> None
        n = 10
        for r in self.rs_3D.get_points_yup(n):
            self.assertTrue(self.rs_3D.member_yup(r))
            # self.assertTrue(self.rs_3D.member_yup(r), 'Point {0} not in Yup {1}, in Border? {2}'.format(str(r), str(self.rs_3D.yup), str(self.rs_3D.member_border(r))))

        for r in self.rs_3D.get_points_ylow(n):
            self.assertTrue(self.rs_3D.member_ylow(r))

        for r in self.rs_3D.get_points_border(n):
            self.assertTrue(self.rs_3D.member_border(r))

        for r in self.rs_3D.get_points_space(n):
            self.assertTrue(self.rs_3D.member_space(r))

    @pytest.mark.skipif(
        'DISPLAY' not in os.environ,
        reason='Display is not defined'
    )
    def test_plot_2D(self):
        # type: (ResultSetTestCase) -> None
        tmpfile = tf.NamedTemporaryFile(delete=False)
        nfile = tmpfile.name

        # Plot 2D by screen
        self.rs_2D.plot_2D(sec=1.0)
        self.rs_2D.plot_2D_light(sec=1.0)
        self.rs_2D.plot_2D_pareto(sec=1.0)

        # Plot 2D by file
        self.rs_2D.plot_2D(sec=1.0, filename=nfile)
        self.rs_2D.plot_2D_light(sec=1.0, filename=nfile)
        self.rs_2D.plot_2D_pareto(sec=1.0, filename=nfile)

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(nfile)

    @pytest.mark.skipif(
        'DISPLAY' not in os.environ,
        reason='Display is not defined'
    )
    def test_plot_3D(self):
        # type: (ResultSetTestCase) -> None
        tmpfile = tf.NamedTemporaryFile(delete=False)
        nfile = tmpfile.name

        # Plot 3D by screen
        self.rs_3D.plot_3D(sec=1.0)
        self.rs_3D.plot_3D_light(sec=1.0)
        self.rs_3D.plot_3D_pareto(sec=1.0)

        # Plot 3D by file
        self.rs_3D.plot_3D(sec=1.0, filename=nfile)
        self.rs_3D.plot_3D_light(sec=1.0, filename=nfile)
        self.rs_3D.plot_3D_pareto(sec=1.0, filename=nfile)

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(nfile)


################
# ParResultSet #
################

class ParResultSetTestCase(ResultSetTestCase):
    def setUp(self):
        # type: (ParResultSetTestCase) -> None
        super(ParResultSetTestCase, self).setUp()
        self.rs = ParResultSet(self.border_2D, self.ylow_2D, self.yup_2D, self.xspace_2D)
        self.rs2 = ParResultSet()

        self.rs_3D = ParResultSet(self.border_3D, self.ylow_3D, self.yup_3D, self.xspace_3D)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
