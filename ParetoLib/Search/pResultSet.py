import os
import __builtin__
import time
import pickle
from itertools import chain, combinations_with_replacement, product
from multiprocessing import Pool, cpu_count

from ParetoLib.Geometry.Rectangle import *
from ParetoLib.Geometry.pRectangle import *
from ParetoLib.Search.ResultSet import *


class pResultSet(ResultSet):
    def __init__(self, border=list(), ylow=list(), yup=list(), xspace=Rectangle()):
        # type: (pResultSet, list, list, list, Rectangle) -> None
        # super(pResultSet, self).__init__(border, ylow, yup, xspace)
        ResultSet.__init__(self, border, ylow, yup, xspace)
        self.p = Pool(cpu_count())

    def __del__(self):
        # Stop multiprocessing
        self.p.close()
        self.p.join()

    # Vertex functions
    def verticesYup(self):
        # type: (pResultSet) -> set
        # vertices_list = (rect.vertices() for rect in self.yup)
        vertices_list = self.p.map(pvertices, self.yup)
        vertices = set()
        vertices = vertices.union(*vertices_list)
        return vertices

    def verticesYlow(self):
        # type: (pResultSet) -> set
        # vertices_list = (rect.vertices() for rect in self.ylow)
        vertices_list = self.p.map(pvertices, self.ylow)
        vertices = set()
        vertices = vertices.union(*vertices_list)
        return vertices

    def verticesBorder(self):
        # type: (pResultSet) -> set
        # vertices_list = (rect.vertices() for rect in self.border)
        vertices_list = self.p.map(pvertices, self.border)
        vertices = set()
        vertices = vertices.union(*vertices_list)
        return vertices

    # Volume functions
    def _overlappingVolume(self, pairs_of_rect):
        # type: (pResultSet, iter) -> float
        # remove pairs (recti, recti) from previous list
        #pairs_of_rect_filt = (pair for pair in pairs_of_rect if pair[0] != pair[1])
        #overlapping_rect = (r1.intersection(r2) for (r1, r2) in pairs_of_rect_filt)
        overlapping_rect = (r1.intersection(r2) for (r1, r2) in pairs_of_rect if r1.overlaps(r2))
        vol_overlapping_rect = self.p.imap_unordered(pvol, overlapping_rect)
        return sum(vol_overlapping_rect)

    def volumeYup(self):
        # type: (pResultSet) -> float
        vol_list = self.p.imap_unordered(pvol, self.yup)
        # vol_list = (rect.volume() for rect in self.yup)
        return sum(vol_list)

    def volumeYlow(self):
        # type: (pResultSet) -> float
        vol_list = self.p.imap_unordered(pvol, self.ylow)
        # vol_list = (rect.volume() for rect in self.ylow)
        return sum(vol_list)

    # By construction, overlapping of rectangles only happens in the boundary
    def volumeBorderExact(self):
        # type: (pResultSet) -> float
        vol_list = self.p.imap_unordered(pvol, self.border)
        # vol_list = (rect.volume() for rect in self.border)
        return sum(vol_list) - self.overlappingVolumeBorder()

    def memberYup(self, xpoint):
        # type: (pResultSet, tuple) -> bool
        # isMember = (rect.inside(xpoint) for rect in self.yup)
        args_member = ((rect, xpoint) for rect in self.yup)
        isMember = self.p.imap_unordered(pinside, args_member)
        # return any(isMember)
        return any(isMember) and not self.memberBorder(xpoint)

    def memberYlow(self, xpoint):
        # type: (pResultSet, tuple) -> bool
        # isMember = (rect.inside(xpoint) for rect in self.ylow)
        args_member = ((rect, xpoint) for rect in self.ylow)
        isMember = self.p.imap_unordered(pinside, args_member)
        # return any(isMember)
        return any(isMember) and not self.memberBorder(xpoint)

    def memberBorder(self, xpoint):
        # type: (pResultSet, tuple) -> bool
        # isMember = (rect.inside(xpoint) for rect in self.border)
        args_member = ((rect, xpoint) for rect in self.border)
        isMember = self.p.imap_unordered(pinside, args_member)
        return any(isMember)
