# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""ParResultSet.

The result of the discovery process of the Pareto front is saved in
an object of the *ResultSet* class. This object is a data structure
composed of three elements: the upper closure (*X1*), the lower
closure (*X2*), and the gap between X1 and X2 representing the
precision error of the learning process.
The size of this gap depends on the accuracy of the learning process,
which can be tuned by the EPS and DELTA parameters during the
invocation of the learning method.

The ResultSet class provides functions for:
- Testing the membership of a new point *y* to any of the closures.
- Plotting 2D and 3D spaces
- Exporting/Importing the results to text and binary files.
"""

from multiprocessing import Pool, cpu_count
from itertools import combinations

from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Geometry.ParRectangle import pvertices, pinside, pvol

from ParetoLib.Search.ResultSet import ResultSet


class ParResultSet(ResultSet):
    def __init__(self, border=list(), ylow=list(), yup=list(), xspace=Rectangle()):
        # type: (ParResultSet, iter, iter, iter, Rectangle) -> None
        # super(ParResultSet, self).__init__(border, ylow, yup, xspace)
        ResultSet.__init__(self, border, ylow, yup, xspace)
        self.p = Pool(cpu_count())

    def __del__(self):
        # Stop multiprocessing
        self.p.close()
        self.p.join()

    # Vertex functions
    def vertices_yup(self):
        # type: (ParResultSet) -> set
        # vertices_list = (rect.vertices() for rect in self.yup)
        vertices_list = self.p.map(pvertices, self.yup)
        vertices = set()
        vertices = vertices.union(*vertices_list)
        return vertices

    def vertices_ylow(self):
        # type: (ParResultSet) -> set
        # vertices_list = (rect.vertices() for rect in self.ylow)
        vertices_list = self.p.map(pvertices, self.ylow)
        vertices = set()
        vertices = vertices.union(*vertices_list)
        return vertices

    def vertices_border(self):
        # type: (ParResultSet) -> set
        # vertices_list = (rect.vertices() for rect in self.border)
        vertices_list = self.p.map(pvertices, self.border)
        vertices = set()
        vertices = vertices.union(*vertices_list)
        return vertices

    # Volume functions
    def _overlapping_volume(self, pairs_of_rect):
        # type: (ParResultSet, iter) -> float
        # remove pairs (recti, recti) from previous list
        # pairs_of_rect_filt = (pair for pair in pairs_of_rect if pair[0] != pair[1])
        # overlapping_rect = (r1.intersection(r2) for (r1, r2) in pairs_of_rect_filt)
        overlapping_rect = (r1.intersection(r2) for (r1, r2) in pairs_of_rect if r1.overlaps(r2))
        vol_overlapping_rect = self.p.imap_unordered(pvol, overlapping_rect)
        return sum(vol_overlapping_rect)

    def overlapping_volume_yup(self):
        # type: (ParResultSet) -> float
        # self.yup_2D = [rect1, rect2,..., rectn]
        # pairs_of_rect = [(rect1, rect1), (rect1, rect2),..., (rectn, rectn)]
        pairs_of_rect = combinations(self.yup, 2)
        return self._overlapping_volume(pairs_of_rect)
        # return ParResultSet._overlapping_volume(pairs_of_rect)

    def overlapping_volume_ylow(self):
        # type: (ParResultSet) -> float
        # self.ylow_2D = [rect1, rect2,..., rectn]
        # pairs_of_rect = [(rect1, rect1), (rect1, rect2),..., (rectn, rectn)]
        pairs_of_rect = combinations(self.ylow, 2)
        return self._overlapping_volume(pairs_of_rect)
        # return ParResultSet._overlapping_volume(pairs_of_rect)

    def overlapping_volume_border(self):
        # type: (ParResultSet) -> float
        # self.border_2D = [rect1, rect2,..., rectn]
        # pairs_of_rect = [(rect1, rect1), (rect1, rect2),..., (rectn, rectn)]
        pairs_of_rect = combinations(self.border, 2)
        return self._overlapping_volume(pairs_of_rect)
        # return ParResultSet._overlapping_volume(pairs_of_rect)

    def overlapping_volume_total(self):
        # type: (ParResultSet) -> float
        # total_rectangles = [rect1, rect2,..., rectn]
        # pairs_of_rect = [(rect1, rect1), (rect1, rect2),..., (rectn, rectn)]
        total_rectangles = []
        total_rectangles.extend(self.border)
        total_rectangles.extend(self.yup)
        total_rectangles.extend(self.ylow)
        pairs_of_rect = combinations(total_rectangles, 2)
        return self._overlapping_volume(pairs_of_rect)
        # return ParResultSet._overlapping_volume(pairs_of_rect)

    def volume_yup(self):
        # type: (ParResultSet) -> float
        vol_list = self.p.imap_unordered(pvol, self.yup)
        # vol_list = (rect.volume() for rect in self.yup)
        return sum(vol_list)

    def volume_ylow(self):
        # type: (ParResultSet) -> float
        vol_list = self.p.imap_unordered(pvol, self.ylow)
        # vol_list = (rect.volume() for rect in self.ylow)
        return sum(vol_list)

    def volume_border_2(self):
        # type: (ParResultSet) -> float
        vol_list = self.p.imap_unordered(pvol, self.border)
        # vol_list = (rect.volume() for rect in self.border)
        return sum(vol_list) - self.overlapping_volume_total()

    # Membership functions
    def member_yup(self, xpoint):
        # type: (ParResultSet, tuple) -> bool
        # isMember = (rect.inside(xpoint) for rect in self.yup)
        args_member = ((rect, xpoint) for rect in self.yup)
        isMember = self.p.imap_unordered(pinside, args_member)
        return any(isMember)
        # return any(isMember) and not self.member_border(xpoint)

    def member_ylow(self, xpoint):
        # type: (ParResultSet, tuple) -> bool
        # isMember = (rect.inside(xpoint) for rect in self.ylow)
        args_member = ((rect, xpoint) for rect in self.ylow)
        isMember = self.p.imap_unordered(pinside, args_member)
        return any(isMember)
        # return any(isMember) and not self.member_border(xpoint)

    def member_border(self, xpoint):
        # type: (ParResultSet, tuple) -> bool
        # isMember = (rect.inside(xpoint) for rect in self.border)
        args_member = ((rect, xpoint) for rect in self.border)
        isMember = self.p.imap_unordered(pinside, args_member)
        return any(isMember)
