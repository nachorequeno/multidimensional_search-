import os
import sys
import time
import pickle
from itertools import chain, combinations  # combinations_with_replacement
import zipfile
import tempfile
# import shutil

import matplotlib.pyplot as plt

from ParetoLib.Geometry.Rectangle import Rectangle
import ParetoLib.Search as RootSearch


class ResultSet:
    def __init__(self, border=list(), ylow=list(), yup=list(), xspace=Rectangle()):
        # type: (ResultSet, list, list, list, Rectangle) -> None
        # self.border = list(border) is required for forcing the creation of a local list.
        # If two ResultSets are created by making an empty call to ResultSet() (i.e., rs1, rs2),
        # then rs1.border and rs2.border will point to the same list. Modifications in rs1.border
        # will change rs2.border
        self.border = list(border)
        self.ylow = list(ylow)
        self.yup = list(yup)
        self.xspace = xspace

        self.filename_yup = 'up'
        self.filename_ylow = 'low'
        self.filename_border = 'border'
        self.filename_space = 'space'

    # Printers
    def to_str(self):
        # type: (ResultSet) -> str
        # _string = '('
        # for i, data in enumerate(self.low):
        #    _string += str(data)
        #    if i != dim(self.low) - 1:
        #        _string += ', '
        # _string += ')'
        _string = '<'
        _string += str(self.yup)
        _string += ', '
        _string += str(self.ylow)
        _string += ', '
        _string += str(self.border)
        _string += '>'
        return _string

    def __repr__(self):
        # type: (ResultSet) -> str
        return self.to_str()

    def __str__(self):
        # type: (ResultSet) -> str
        return self.to_str()

    # Equality functions
    def __eq__(self, other):
        # type: (ResultSet) -> bool
        return (other.border == self.border) and \
               (other.ylow == self.ylow) and \
               (other.yup == self.yup) and \
               (other.xspace == self.xspace)

    def __ne__(self, other):
        # type: (ResultSet) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (ResultSet) -> int
        return hash((self.border, self.ylow, self.yup, self.xspace))

    # Vertex functions
    def vertices_yup(self):
        # type: (ResultSet) -> set
        vertices_list = (rect.vertices() for rect in self.yup)
        vertices = set()
        vertices = vertices.union(*vertices_list)
        return vertices

    def vertices_ylow(self):
        # type: (ResultSet) -> set
        vertices_list = (rect.vertices() for rect in self.ylow)
        vertices = set()
        vertices = vertices.union(*vertices_list)
        return vertices

    def vertices_border(self):
        # type: (ResultSet) -> set
        vertices_list = (rect.vertices() for rect in self.border)
        vertices = set()
        vertices = vertices.union(*vertices_list)
        return vertices

    def vertices(self):
        # type: (ResultSet) -> set
        vertices = self.vertices_yup()
        vertices = vertices.union(self.vertices_ylow())
        vertices = vertices.union(self.vertices_border())
        return vertices

    # Simplification functions
    # After running simplify(), the number of cubes in the boundary and in each closure should decrease.
    # Besides, overlapping cubes in the boundary should also disappear, i.e.,
    # overlapping_volume_border() == 0 and overlapping_volume_total() == 0
    def simplify(self):
        # type: (ResultSet) -> None
        self.recalculate_border()
        self.fusion_rectangles_border()
        self.fusion_rectangles_ylow()
        self.fusion_rectangles_yup()

    def fusion_rectangles_yup(self):
        # type: (ResultSet) -> None
        len_before = float('inf')
        len_after = len(self.yup)
        while len_before > len_after:
            # len_before = len(self.yup)
            len_before = len_after
            for rect1 in self.yup:
                for rect2 in self.yup:
                    if rect1.is_concatenable(rect2):
                        rect1.concatenate_update(rect2)
                        self.yup.remove(rect2)
            len_after = len(self.yup)

    def fusion_rectangles_ylow(self):
        # type: (ResultSet) -> None
        len_before = float('inf')
        len_after = len(self.ylow)
        while len_before > len_after:
            len_before = len_after
            for rect1 in self.ylow:
                for rect2 in self.ylow:
                    if rect1.is_concatenable(rect2):
                        rect1.concatenate_update(rect2)
                        self.ylow.remove(rect2)
            len_after = len(self.ylow)

    def fusion_rectangles_border(self):
        # type: (ResultSet) -> None
        len_before = float('inf')
        len_after = len(self.border)
        while len_before > len_after:
            len_before = len_after
            for rect1 in self.border:
                for rect2 in self.border:
                    if rect1.is_concatenable(rect2):
                        rect1.concatenate_update(rect2)
                        self.border.remove(rect2)
            len_after = len(self.border)

    def recalculate_border(self):
        # type: (ResultSet) -> None
        # Given the space xspace, the upper (yup) and lower (ylow) closures of the Pareto front,
        # the boundary border is computed as border = xspace - yup - ylow

        new_border = {self.xspace}

        # Copy list
        closure_list = []
        closure_list.extend(self.yup)
        closure_list.extend(self.ylow)

        # Find cubes B of the upper/lower closures that intersect any cube A from the boundary
        # and remove from A the portion that intersects with B

        intersect_list = [(a, b) for a in new_border for b in closure_list if a.overlaps(b)]
        while len(intersect_list) > 0:
            a, b = intersect_list[0]

            new_border.remove(a)
            new_border = new_border.union(list(a - b))

            intersect_list = [(a, b) for a in new_border for b in closure_list if a.overlaps(b)]

        self.border = list(new_border)

    # Volume functions
    @staticmethod
    def _overlapping_volume(pairs_of_rect):
        # type: (iter) -> float
        # remove pairs (recti, recti) from previous list
        # pairs_of_rect_filt = (pair for pair in pairs_of_rect if pair[0] != pair[1])
        # overlapping_rect = (r1.intersection(r2) for (r1, r2) in pairs_of_rect_filt)
        overlapping_rect = (r1.intersection(r2) for (r1, r2) in pairs_of_rect if r1.overlaps(r2))
        vol_overlapping_rect = (rect.volume() for rect in overlapping_rect)
        return sum(vol_overlapping_rect)

    # By construction, overlapping of cubes should only happen in the boundary.
    # Therefore,
    # overlapping_volume_yup() == 0
    # overlapping_volume_ylow() == 0
    # overlapping_volume_border() >= 0
    # overlapping_volume_total() >= 0
    #
    # WARNING!
    # In some situations, some cubes of the border may also intersect cubes of upper (yup) or lower (ylow) closures.
    # This fact makes that:
    # overlapping_volume_total() != overlapping_volume_border()
    #
    # Does it happen because of the way cones crect and brect are calculated in Rectangle.py?
    # It seems to be an inherent problem of the functions for computing crect/brect because it sometimes generates
    # planes (2-dimensional) instead of cubes (n-dimensional) for spaces of n-dimension.

    def overlapping_volume_yup(self):
        # type: (ResultSet) -> float
        # self.yup = [rect1, rect2,..., rectn]
        # pairs_of_rect = [(rect1, rect1), (rect1, rect2),..., (rectn, rectn)]
        pairs_of_rect = combinations(self.yup, 2)
        # return self._overlapping_volume(pairs_of_rect)
        return ResultSet._overlapping_volume(pairs_of_rect)

    def overlapping_volume_ylow(self):
        # type: (ResultSet) -> float
        # self.ylow = [rect1, rect2,..., rectn]
        # pairs_of_rect = [(rect1, rect1), (rect1, rect2),..., (rectn, rectn)]
        pairs_of_rect = combinations(self.ylow, 2)
        # return self._overlapping_volume(pairs_of_rect)
        return ResultSet._overlapping_volume(pairs_of_rect)

    def overlapping_volume_border(self):
        # type: (ResultSet) -> float
        # self.border = [rect1, rect2,..., rectn]
        # pairs_of_rect = [(rect1, rect1), (rect1, rect2),..., (rectn, rectn)]
        pairs_of_rect = combinations(self.border, 2)
        # return self._overlapping_volume(pairs_of_rect)
        return ResultSet._overlapping_volume(pairs_of_rect)

    def overlapping_volume_total(self):
        # type: (ResultSet) -> float
        # total_rectangles = [rect1, rect2,..., rectn]
        # pairs_of_rect = [(rect1, rect1), (rect1, rect2),..., (rectn, rectn)]
        total_rectangles = []
        total_rectangles.extend(self.border)
        total_rectangles.extend(self.yup)
        total_rectangles.extend(self.ylow)
        pairs_of_rect = combinations(total_rectangles, 2)
        # return self._overlapping_volume(pairs_of_rect)
        return ResultSet._overlapping_volume(pairs_of_rect)

    def volume_yup(self):
        # type: (ResultSet) -> float
        # vol_list = p.map(Rectangle.volume, self.yup)
        vol_list = (rect.volume() for rect in self.yup)
        return sum(vol_list)

    def volume_ylow(self):
        # type: (ResultSet) -> float
        # vol_list = p.map(Rectangle.volume, self.ylow)
        vol_list = (rect.volume() for rect in self.ylow)
        return sum(vol_list)

    def volume_border(self):
        # type: (ResultSet) -> float
        vol_total = self.xspace.volume()
        vol_ylow = self.volume_ylow()
        vol_yup = self.volume_yup()
        return vol_total - vol_ylow - vol_yup

    def volume_border_2(self):
        # type: (ResultSet) -> float
        # vol_list = p.map(Rectangle.volume, self.border)
        vol_list = (rect.volume() for rect in self.border)
        return sum(vol_list) - self.overlapping_volume_total()

    def volume_total(self):
        # type: (ResultSet) -> float
        # vol_total = self.volume_ylow() + self.volume_yup() + self.volume_border()
        vol_total = self.xspace.volume()
        return vol_total

    def volume_report(self):
        # type: (ResultSet) -> str
        vol_report = ('Volume report (Ylow, Yup, Border, Total): ({0}, {1}, {2}, {3})\n'.format(
            str(self.volume_ylow()), str(self.volume_yup()), str(self.volume_border()),
            str(self.volume_total())))
        return vol_report

    # Membership functions
    def __contains__(self, xpoint):
        # type: (ResultSet, tuple) -> bool
        # xpoint is inside the upper/lower closure or in the border
        return self.member_border(xpoint) or \
               self.member_ylow(xpoint) or \
               self.member_yup(xpoint)

    def member_yup(self, xpoint):
        # type: (ResultSet, tuple) -> bool
        isMember = (rect.inside(xpoint) for rect in self.yup)
        return any(isMember)
        # return any(isMember) and not self.member_border(xpoint)

    def member_ylow(self, xpoint):
        # type: (ResultSet, tuple) -> bool
        isMember = (rect.inside(xpoint) for rect in self.ylow)
        return any(isMember)
        # return any(isMember) and not self.member_border(xpoint)

    def member_border(self, xpoint):
        # type: (ResultSet, tuple) -> bool
        # isMember = (rect.inside(xpoint) for rect in self.border)
        # return any(isMember)
        return self.member_space(xpoint) and not self.member_yup(xpoint) and not self.member_ylow(xpoint)

    def member_space(self, xpoint):
        # type: (ResultSet, tuple) -> bool
        # return xpoint in self.xspace
        return self.xspace.inside(xpoint)

    # Points of closure
    def get_points_yup(self, n):
        # type: (ResultSet, int) -> list
        m = int(n / len(self.yup))
        m = 1 if m < 1 else m
        # point_list = [rect.get_points(m) for rect in self.yup]
        point_list = (rect.get_points(m) for rect in self.yup)
        # Flatten list
        # Before
        # point_list = [ [] , [], ..., [] ]
        # After
        # point_list = [ ... ]
        merged = list(chain.from_iterable(point_list))
        return merged

    def get_points_ylow(self, n):
        # type: (ResultSet, int) -> list
        m = int(n / len(self.ylow))
        m = 1 if m < 1 else m
        # point_list = [rect.get_points(m) for rect in self.ylow]
        point_list = (rect.get_points(m) for rect in self.ylow)
        merged = list(chain.from_iterable(point_list))
        return merged

    def get_points_border(self, n):
        # type: (ResultSet, int) -> list
        m = int(n / len(self.border))
        m = 1 if m < 1 else m
        # point_list = [rect.get_points(m) for rect in self.border]
        point_list = (rect.get_points(m) for rect in self.border)
        merged = list(chain.from_iterable(point_list))
        return merged

    def get_points_space(self, n):
        # type: (ResultSet, int) -> list
        return self.xspace.get_points(n)

    # Maximum/minimum values for each parameter
    @staticmethod
    def _get_min_val_dimension_rect_list(i, rect_list):
        # type: (int, list) -> float
        min_cs = (rect.min_corner for rect in rect_list)
        mc_i = (mc[i] for mc in min_cs)
        return min(mc_i)

    def get_min_val_dimension_yup(self, i):
        # type: (ResultSet, int) -> float
        return ResultSet._get_min_val_dimension_rect_list(i, self.yup)

    def get_min_val_dimension_ylow(self, i):
        # type: (ResultSet, int) -> float
        return ResultSet._get_min_val_dimension_rect_list(i, self.ylow)

    def get_min_val_dimension_border(self, i):
        # type: (ResultSet, int) -> float
        return ResultSet._get_min_val_dimension_rect_list(i, self.border)

    @staticmethod
    def _get_max_val_dimension_rect_list(i, rect_list):
        # type: (int, list) -> float
        max_cs = (rect.max_corner for rect in rect_list)
        mc_i = (mc[i] for mc in max_cs)
        return max(mc_i)

    def get_max_val_dimension_yup(self, i):
        # type: (ResultSet, int) -> float
        return ResultSet._get_max_val_dimension_rect_list(i, self.yup)

    def get_max_val_dimension_ylow(self, i):
        # type: (ResultSet, int) -> float
        return ResultSet._get_max_val_dimension_rect_list(i, self.ylow)

    def get_max_val_dimension_border(self, i):
        # type: (ResultSet, int) -> float
        return ResultSet._get_max_val_dimension_rect_list(i, self.border)

    # MatPlot Graphics
    def plot_space_2D(self, xaxe=0, yaxe=1, opacity=1.0):
        # type: (ResultSet, int, int, float) -> list
        patch = [self.xspace.plot_2D('blue', xaxe, yaxe, opacity)]
        return patch

    def plot_yup_2D(self, xaxe=0, yaxe=1, opacity=1.0):
        # type: (ResultSet, int, int, float) -> list
        patch = [rect.plot_2D('green', xaxe, yaxe, opacity) for rect in self.yup]
        return patch

    def plot_ylow_2D(self, xaxe=0, yaxe=1, opacity=1.0):
        # type: (ResultSet, int, int, float) -> list
        patch = [rect.plot_2D('red', xaxe, yaxe, opacity) for rect in self.ylow]
        return patch

    def plot_border_2D(self, xaxe=0, yaxe=1, opacity=1.0):
        # type: (ResultSet, int, int, float) -> list
        patch = [rect.plot_2D('blue', xaxe, yaxe, opacity) for rect in self.border]
        return patch

    def plot_2D(self,
                filename='',
                xaxe=0,
                yaxe=1,
                var_names=list(),
                targetx=list(),
                targety=list(),
                blocking=False,
                sec=0.0,
                opacity=1.0):
        # type: (ResultSet, str, int, int, list, list, list, bool, float, float) -> plt
        fig1 = plt.figure()
        # ax1 = fig1.add_subplot(111, aspect='equal')
        ax1 = fig1.add_subplot(111)
        # ax1.set_title('Approximation of the Pareto front, Parameters (' + str(xaxe) + ', ' + str(yaxe) + ')')
        ax1.set_title('Approximation of the Pareto front')

        # The name of the inferred parameters using Pareto search are written in the axes of the graphic.
        # For instance, axe 0 represents parameter 'P0', axe 1 represents parameter 'P1', etc.
        # If parameter names are not provided (var_names is empty or smaller than 2D), then we use
        # lexicographic characters by default.
        var_names = [chr(i) for i in range(ord('a'), ord('z') + 1)] if len(var_names) <= 2 else var_names
        ax1.set_xlabel(var_names[xaxe % len(var_names)])
        ax1.set_ylabel(var_names[yaxe % len(var_names)])

        pathpatch_yup = self.plot_yup_2D(xaxe, yaxe, opacity)
        pathpatch_ylow = self.plot_ylow_2D(xaxe, yaxe, opacity)
        pathpatch_border = self.plot_border_2D(xaxe, yaxe, opacity)

        pathpatch = pathpatch_yup
        pathpatch += pathpatch_ylow
        pathpatch += pathpatch_border

        for pathpatch_i in pathpatch:
            ax1.add_patch(pathpatch_i)

        # Include the vertices of the rectangles of the ResultSet in the plotting
        # The inclusion of explicit points forces the autoscaling of the image
        rs_vertices = self.vertices()
        xs = [vi[0] for vi in rs_vertices]
        ys = [vi[1] for vi in rs_vertices]

        targetx += [min(xs), max(xs)]
        targety += [min(ys), max(ys)]

        plt.plot(targetx, targety, 'kp')
        # ax1.scatter(targetx, targety, c='k')
        # ax1.autoscale_view()

        #
        fig1.tight_layout()
        plt.tight_layout()
        #

        # plt.autoscale()
        plt.xscale('linear')
        plt.yscale('linear')

        plt.show(block=blocking)
        time.sleep(sec)

        if filename != '':
            fig1.savefig(filename, dpi=90, bbox_inches='tight')

        plt.close()
        return plt

    def plot_2D_light(self,
                      filename='',
                      xaxe=0,
                      yaxe=1,
                      var_names=list(),
                      targetx=list(),
                      targety=list(),
                      blocking=False,
                      sec=0.0,
                      opacity=1.0):
        # type: (ResultSet, str, int, int, list, list, list, bool, float, float) -> plt

        fig1 = plt.figure()
        # ax1 = fig1.add_subplot(111, aspect='equal')
        ax1 = fig1.add_subplot(111)
        # ax1.set_title('Approximation of the Pareto front, Parameters (' + str(xaxe) + ', ' + str(yaxe) + ')')
        ax1.set_title('Approximation of the Pareto front')

        # The name of the inferred parameters using Pareto search are written in the axes of the graphic.
        # For instance, axe 0 represents parameter 'P0', axe 1 represents parameter 'P1', etc.
        # If parameter names are not provided (var_names is empty or smaller than 2D), then we use
        # lexicographic characters by default.
        var_names = [chr(i) for i in range(ord('a'), ord('z') + 1)] if len(var_names) <= 2 else var_names
        ax1.set_xlabel(var_names[xaxe % len(var_names)])
        ax1.set_ylabel(var_names[yaxe % len(var_names)])

        pathpatch_yup = self.plot_yup_2D(xaxe, yaxe, opacity)
        pathpatch_ylow = self.plot_ylow_2D(xaxe, yaxe, opacity)
        pathpatch_border = self.plot_space_2D(xaxe, yaxe, 0.2)

        pathpatch = pathpatch_border
        pathpatch += pathpatch_ylow
        pathpatch += pathpatch_yup

        for pathpatch_i in pathpatch:
            ax1.add_patch(pathpatch_i)

        # Include the vertices of the rectangles of the ResultSet in the plotting
        # The inclusion of explicit points forces the autoscaling of the image
        rs_vertices = self.vertices()
        xs = [vi[0] for vi in rs_vertices]
        ys = [vi[1] for vi in rs_vertices]

        targetx += [min(xs), max(xs)]
        targety += [min(ys), max(ys)]

        plt.plot(targetx, targety, 'kp')
        # ax1.scatter(targetx, targety,  c='k')
        # ax1.autoscale_view()

        #
        fig1.tight_layout()
        plt.tight_layout()
        #

        # plt.autoscale()
        plt.xscale('linear')
        plt.yscale('linear')

        plt.show(block=blocking)
        time.sleep(sec)

        if filename != '':
            fig1.savefig(filename, dpi=90, bbox_inches='tight')

        plt.close()
        return plt

    def plot_space_3D(self, xaxe=0, yaxe=1, zaxe=2, opacity=1.0):
        # type: (ResultSet, int, int, int, float) -> list
        faces = [self.xspace.plot_3D('blue', xaxe, yaxe, zaxe, opacity)]
        return faces

    def plot_yup_3D(self, xaxe=0, yaxe=1, zaxe=2, opacity=1.0):
        # type: (ResultSet, int, int, int, float) -> list
        faces = [rect.plot_3D('green', xaxe, yaxe, zaxe, opacity) for rect in self.yup]
        return faces

    def plot_ylow_3D(self, xaxe=0, yaxe=1, zaxe=2, opacity=1.0):
        # type: (ResultSet, int, int, int, float) -> list
        faces = [rect.plot_3D('red', xaxe, yaxe, zaxe, opacity) for rect in self.ylow]
        return faces

    def plot_border_3D(self, xaxe=0, yaxe=1, zaxe=2, opacity=1.0):
        # type: (ResultSet, int, int, int, float) -> list
        faces = [rect.plot_3D('blue', xaxe, yaxe, zaxe, opacity) for rect in self.border]
        return faces

    def plot_3D(self,
                filename='',
                xaxe=0,
                yaxe=1,
                zaxe=2,
                var_names=list(),
                targetx=list(),
                targety=list(),
                targetz=list(),
                blocking=False,
                sec=0.0,
                opacity=1.0):
        # type: (ResultSet, str, int, int, int, list, list, list, list, bool, float, float) -> plt
        fig1 = plt.figure()
        # ax1 = fig1.add_subplot(111, aspect='equal', projection='3d')
        ax1 = fig1.add_subplot(111, projection='3d')
        ax1.set_title('Approximation of the Pareto front')

        # The name of the inferred parameters using Pareto search are written in the axes of the graphic.
        # For instance, axe 0 represents parameter 'P0', axe 1 represents parameter 'P1', etc.
        # If parameter names are not provided (var_names is empty or smaller than 2D), then we use
        # lexicographic characters by default.
        var_names = [chr(i) for i in range(ord('a'), ord('z') + 1)] if len(var_names) <= 3 else var_names
        ax1.set_xlabel(var_names[xaxe % len(var_names)])
        ax1.set_ylabel(var_names[yaxe % len(var_names)])
        ax1.set_zlabel(var_names[zaxe % len(var_names)])

        faces_yup = self.plot_yup_3D(xaxe, yaxe, zaxe, opacity)
        faces_ylow = self.plot_ylow_3D(xaxe, yaxe, zaxe, opacity)
        faces_border = self.plot_border_3D(xaxe, yaxe, zaxe, opacity)

        faces = faces_yup
        faces += faces_ylow
        faces += faces_border

        for faces_i in faces:
            ax1.add_collection3d(faces_i)

        # Include the vertices of the rectangles of the ResultSet in the plotting
        # The inclusion of explicit points forces the autoscaling of the image
        rs_vertices = self.vertices()
        xs = [vi[0] for vi in rs_vertices]
        ys = [vi[1] for vi in rs_vertices]
        zs = [vi[2] for vi in rs_vertices]

        targetx += [min(xs), max(xs)]
        targety += [min(ys), max(ys)]
        targetz += [min(zs), max(zs)]

        plt.plot(targetx, targety, targetz, 'kp')
        # ax1.scatter(targetx, targety, targetz, c='k')
        # ax1.autoscale_view()

        #
        fig1.tight_layout()
        plt.tight_layout()
        #

        # plt.autoscale()
        plt.xscale('linear')
        plt.yscale('linear')
        # plt.zscale('linear')

        plt.show(block=blocking)
        time.sleep(sec)

        if filename != '':
            fig1.savefig(filename, dpi=90, bbox_inches='tight')
        plt.close()
        return plt

    def plot_3D_light(self,
                      filename='',
                      xaxe=0,
                      yaxe=1,
                      zaxe=2,
                      var_names=list(),
                      targetx=list(),
                      targety=list(),
                      targetz=list(),
                      blocking=False,
                      sec=0.0,
                      opacity=1.0):
        # type: (ResultSet, str, int, int, int, list, list, list, list, bool, float, float) -> plt
        fig1 = plt.figure()
        # ax1 = fig1.add_subplot(111, aspect='equal', projection='3d')
        ax1 = fig1.add_subplot(111, projection='3d')
        ax1.set_title('Approximation of the Pareto front')

        # The name of the inferred parameters using Pareto search are written in the axes of the graphic.
        # For instance, axe 0 represents parameter 'P0', axe 1 represents parameter 'P1', etc.
        # If parameter names are not provided (var_names is empty or smaller than 2D), then we use
        # lexicographic characters by default.
        var_names = [chr(i) for i in range(ord('a'), ord('z') + 1)] if len(var_names) <= 3 else var_names
        ax1.set_xlabel(var_names[xaxe % len(var_names)])
        ax1.set_ylabel(var_names[yaxe % len(var_names)])
        ax1.set_zlabel(var_names[zaxe % len(var_names)])

        faces_yup = self.plot_yup_3D(xaxe, yaxe, zaxe, opacity)
        faces_ylow = self.plot_ylow_3D(xaxe, yaxe, zaxe, opacity)
        faces_border = self.plot_space_3D(xaxe, yaxe, zaxe, 0.2)

        faces = faces_border
        faces += faces_ylow
        faces += faces_yup

        for faces_i in faces:
            ax1.add_collection3d(faces_i)

        # Include the vertices of the rectangles of the ResultSet in the plotting
        # The inclusion of explicit points forces the autoscaling of the image
        rs_vertices = self.vertices()
        xs = [vi[0] for vi in rs_vertices]
        ys = [vi[1] for vi in rs_vertices]
        zs = [vi[2] for vi in rs_vertices]

        targetx += [min(xs), max(xs)]
        targety += [min(ys), max(ys)]
        targetz += [min(zs), max(zs)]

        plt.plot(targetx, targety, targetz, 'kp')
        # ax1.scatter(targetx, targety, targetz, c='k')
        # ax1.autoscale_view()

        #
        fig1.tight_layout()
        plt.tight_layout()
        #

        # plt.autoscale()
        plt.xscale('linear')
        plt.yscale('linear')
        # plt.zscale('linear')

        plt.show(block=blocking)
        time.sleep(sec)

        if filename != '':
            fig1.savefig(filename, dpi=90, bbox_inches='tight')
        plt.close()
        return plt

    # Saving/loading results
    def to_file_yup(self, f):
        # type: (ResultSet, str) -> None
        with open(f, 'wb') as output:
            pickle.dump(self.yup, output, pickle.HIGHEST_PROTOCOL)

    def to_file_ylow(self, f):
        # type: (ResultSet, str) -> None
        with open(f, 'wb') as output:
            pickle.dump(self.ylow, output, pickle.HIGHEST_PROTOCOL)

    def to_file_border(self, f):
        # type: (ResultSet, str) -> None
        with open(f, 'wb') as output:
            pickle.dump(self.border, output, pickle.HIGHEST_PROTOCOL)

    def to_file_space(self, f):
        # type: (ResultSet, str) -> None
        with open(f, 'wb') as output:
            pickle.dump(self.xspace, output, pickle.HIGHEST_PROTOCOL)

    def to_file(self, f):
        # type: (ResultSet, str) -> None
        # fname = os.path.basename(f)
        # name = os.path.splitext(fname)
        # ('file', '.ext')
        # basename = name[0]
        # extension = name[1]

        # Save each closure into a separated file, and, then, compress them in a single .zip
        tempdir = tempfile.mkdtemp()

        yup_name = os.path.join(tempdir, self.filename_yup)
        ylow_name = os.path.join(tempdir, self.filename_ylow)
        border_name = os.path.join(tempdir, self.filename_border)
        space_name = os.path.join(tempdir, self.filename_space)

        self.to_file_yup(yup_name)
        self.to_file_ylow(ylow_name)
        self.to_file_border(border_name)
        self.to_file_space(space_name)

        filename_list = (yup_name, ylow_name, border_name, space_name)
        zf = zipfile.ZipFile(f, mode='w', compression=zipfile.ZIP_DEFLATED)
        for outfile in filename_list:
            try:
                fname = os.path.basename(outfile)
                # Adding new file to the .zip
                zf.write(outfile, arcname=fname)
            except OSError:
                RootSearch.logger.error('Unexpected error when saving {0}: {1}'.format(outfile, sys.exc_info()[0]))
            os.remove(outfile)
        zf.close()

        # Remove temporary folder
        os.rmdir(tempdir)
        # shutil.rmtree(tempdir, ignore_errors=True)

    def from_file_yup(self, f):
        # type: (ResultSet, str) -> None
        self.yup = set()
        with open(f, 'rb') as inputfile:
            self.yup = pickle.load(inputfile)

    def from_file_ylow(self, f):
        # type: (ResultSet, str) -> None
        self.ylow = set()
        with open(f, 'rb') as inputfile:
            self.ylow = pickle.load(inputfile)

    def from_file_border(self, f):
        # type: (ResultSet, str) -> None
        self.border = set()
        with open(f, 'rb') as inputfile:
            self.border = pickle.load(inputfile)

    def from_file_space(self, f):
        # type: (ResultSet, str) -> None
        self.xspace = Rectangle()
        with open(f, 'rb') as inputfile:
            self.xspace = pickle.load(inputfile)

    def from_file(self, f):
        # type: (ResultSet, str) -> None
        # fname = os.path.basename(f)
        # name = os.path.splitext(fname)
        # ('file', '.ext')
        # basename = name[0]
        # extension = name[1]

        # Extracts all the files into a temporal folder.
        # Each file contains a closure.
        tempdir = tempfile.mkdtemp()

        zf = zipfile.ZipFile(f, mode='r')
        try:
            zf.extractall(tempdir)
        except KeyError:
            RootSearch.logger.error('Did not find {0} file'.format(f))
        else:
            zf.close()

        yup_name = os.path.join(tempdir, self.filename_yup)
        ylow_name = os.path.join(tempdir, self.filename_ylow)
        border_name = os.path.join(tempdir, self.filename_border)
        space_name = os.path.join(tempdir, self.filename_space)

        self.from_file_yup(yup_name)
        self.from_file_ylow(ylow_name)
        self.from_file_border(border_name)
        self.from_file_space(space_name)

        # Remove temporal files before removing the temporary folder
        filename_list = (yup_name, ylow_name, border_name, space_name)
        for infile in filename_list:
            if os.path.exists(infile):
                try:
                    os.remove(infile)
                except OSError:
                    RootSearch.logger.error('Unexpected error when removing {0}: {1}'.format(infile, sys.exc_info()[0]))

        # Remove temporary folder
        try:
            os.rmdir(tempdir)
        except OSError:
            RootSearch.logger.error('Unexpected error when removing folder {0}: {1}'.format(tempdir, sys.exc_info()[0]))
