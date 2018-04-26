import __builtin__
import time
import pickle
from itertools import chain

import matplotlib.pyplot as plt


class ResultSet:
    suffix_Yup = 'up'
    suffix_Ylow = 'low'
    suffix_Border = 'border'

    def __init__(self, border=set(), ylow=set(), yup=set()):
        # type: (ResultSet, set, set, set) -> None
        self.border = border
        self.ylow = ylow
        self.yup = yup

    # Printers
    def toStr(self):
        # type: (ResultSet) -> str
        # _string = "("
        # for i, data in enumerate(self.l):
        #    _string += str(data)
        #    if i != dim(self.l) - 1:
        #        _string += ", "
        # _string += ")"
        _string = "<"
        _string += str(self.yup)
        _string += ', '
        _string += str(self.ylow)
        _string += ', '
        _string += str(self.border)
        _string += ">"
        return _string

    def __repr__(self):
        # type: (ResultSet) -> str
        return self.toStr()

    def __str__(self):
        # type: (ResultSet) -> str
        return self.toStr()

    # Equality functions
    def __eq__(self, other):
        # type: (ResultSet) -> bool
        return (other.yup == self.yup) and \
               (other.ylow == self.ylow) and \
               (other.border == self.border)

    def __ne__(self, other):
        # type: (ResultSet) -> bool
        return not self.__eq__(other)

    # Vertex functions
    def verticesYup(self):
        # type: (ResultSet) -> set
        vertices = set()
        for rect in self.yup:
            vertices = vertices.union(set(rect.vertices()))
        return vertices

    def verticesYlow(self):
        # type: (ResultSet) -> set
        vertices = set()
        for rect in self.ylow:
            vertices = vertices.union(set(rect.vertices()))
        return vertices

    def verticesBorder(self):
        # type: (ResultSet) -> set
        vertices = set()
        for rect in self.border:
            vertices = vertices.union(set(rect.vertices()))
        return vertices

    def vertices(self):
        # type: (ResultSet) -> set
        vertices = self.verticesYup()
        vertices = vertices.union(self.verticesYlow())
        vertices = vertices.union(self.verticesBorder())
        return vertices

    # Volume functions
    def VolumeYup(self):
        # type: (ResultSet) -> float
        vol = 0.0
        for rect in self.yup:
            vol = vol + rect.volume()
        return vol

    def VolumeYlow(self):
        # type: (ResultSet) -> float
        vol = 0.0
        for rect in self.ylow:
            vol = vol + rect.volume()
        return vol

    def VolumeBorder(self):
        # type: (ResultSet) -> float
        vol = 0.0
        for rect in self.border:
            vol = vol + rect.volume()
        return vol

    # Membership functions
    def MemberYup(self, xpoint):
        # type: (ResultSet, tuple) -> bool
        isMember = False
        for rect in self.yup:
            isMember = isMember or (xpoint in rect)
        return isMember

    def MemberYlow(self, xpoint):
        # type: (ResultSet, tuple) -> bool
        isMember = False
        for rect in self.ylow:
            isMember = isMember or (xpoint in rect)
        return isMember

    def MemberBorder(self, xpoint):
        # type: (ResultSet, tuple) -> bool
        isMember = False
        for rect in self.border:
            isMember = isMember or (xpoint in rect)
        return isMember

    # Points of closure
    def getPointsYup(self, n):
        # type: (ResultSet, int) -> list
        m = n / len(self.yup)
        m = 1 if m < 1 else m
        point_list = [rect.getPoints(m) for rect in self.yup]
        # Flatten list
        # Before
        # point_list = [ [] , [], ..., [] ]
        # After
        # point_list = [ ... ]
        merged = list(chain.from_iterable(point_list))
        return merged

    def getPointsYlow(self, n):
        # type: (ResultSet, int) -> list
        m = n / len(self.ylow)
        m = 1 if m < 1 else m
        point_list = [rect.getPoints(m) for rect in self.ylow]
        merged = list(chain.from_iterable(point_list))
        return merged

    def getPointsBorder(self, n):
        # type: (ResultSet, int) -> list
        m = n / len(self.border)
        m = 1 if m < 1 else m
        point_list = [rect.getPoints(m) for rect in self.border]
        merged = list(chain.from_iterable(point_list))
        return merged

    # MatPlot Graphics
    def toMatPlotYup2D(self, xaxe=0, yaxe=1, opacity=1.0):
        # type: (ResultSet, int, int, float) -> list
        patches = [rect.toMatplot2D('green', xaxe, yaxe, opacity) for rect in self.yup]
        return patches

    def toMatPlotYlow2D(self, xaxe=0, yaxe=1, opacity=1.0):
        # type: (ResultSet, int, int, float) -> list
        patches = [rect.toMatplot2D('red', xaxe, yaxe, opacity) for rect in self.ylow]
        return patches

    def toMatPlotBorder2D(self, xaxe=0, yaxe=1, opacity=1.0):
        # type: (ResultSet, int, int, float) -> list
        patches = [rect.toMatplot2D('blue', xaxe, yaxe, opacity) for rect in self.border]
        return patches

    def toMatPlot2D(self,
                  filename='',
                  xaxe=0,
                  yaxe=1,
                  targetx=[],
                  targety=[],
                  blocking=False,
                  sec=0.0,
                  opacity=1.0):
        # type: (ResultSet, str, int, int, list, list, bool, float, float) -> plt
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111, aspect='equal')
        ax1.set_title('Approximation of the Pareto front (x,y): (' + str(xaxe) + ', ' + str(yaxe) + ')')

        pathpatch_yup = self.toMatPlotYup2D(xaxe, yaxe, opacity)
        pathpatch_ylow = self.toMatPlotYlow2D(xaxe, yaxe, opacity)
        pathpatch_border = self.toMatPlotBorder2D(xaxe, yaxe, opacity)

        pathpatch = pathpatch_yup
        pathpatch += pathpatch_ylow
        pathpatch += pathpatch_border

        for pathpatch_i in pathpatch:
            ax1.add_patch(pathpatch_i)
        ax1.autoscale_view()

        # Include the vertices of the rectangles of the ResultSet in the plotting
        # The inclusion of explicit points forces the autoscaling of the image
        rs_vertices = self.vertices()
        xs = [vi[0] for vi in rs_vertices]
        ys = [vi[1] for vi in rs_vertices]

        targetx += [__builtin__.min(xs), __builtin__.max(xs)]
        targety += [__builtin__.min(ys), __builtin__.max(ys)]

        plt.plot(targetx, targety, 'kp')
        plt.autoscale()
        plt.show(block=blocking)
        if sec > 0:
            time.sleep(sec)

        if filename != '':
            fig1.savefig(filename, dpi=90, bbox_inches='tight')

        plt.close()
        return plt

    def toMatPlotYup3D(self, xaxe=0, yaxe=1, zaxe=2, opacity=1.0):
        # type: (ResultSet, int, int, int, float) -> list
        faces = [rect.toMatplot3D('green', xaxe, yaxe, zaxe, opacity) for rect in self.yup]
        return faces

    def toMatPlotYlow3D(self, xaxe=0, yaxe=1, zaxe=2, opacity=1.0):
        # type: (ResultSet, int, int, int, float) -> list
        faces = [rect.toMatplot3D('red', xaxe, yaxe, zaxe, opacity) for rect in self.ylow]
        return faces

    def toMatPlotBorder3D(self, xaxe=0, yaxe=1, zaxe=2, opacity=1.0):
        # type: (ResultSet, int, int, int, float) -> list
        faces = [rect.toMatplot3D('blue', xaxe, yaxe, zaxe, opacity) for rect in self.border]
        return faces

    def toMatPlot3D(self,
                  filename='',
                  xaxe=0,
                  yaxe=1,
                  zaxe=2,
                  targetx=[],
                  targety=[],
                  targetz=[],
                  blocking=False,
                  sec=0.0,
                  opacity=1.0):
        # type: (ResultSet, str, int, int, int, list, list, list, bool, float, float) -> plt
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111, aspect='equal', projection='3d')
        ax1.set_title('Approximation of the Pareto front (x,y,z): ('
                      + str(xaxe) + ', ' + str(yaxe) + ', ' + str(zaxe) + ')')

        faces_yup = self.toMatPlotYup3D(xaxe, yaxe, zaxe, opacity)
        faces_ylow = self.toMatPlotYlow3D(xaxe, yaxe, zaxe, opacity)
        faces_border = self.toMatPlotBorder3D(xaxe, yaxe, zaxe, opacity)

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

        targetx += [__builtin__.min(xs), __builtin__.max(xs)]
        targety += [__builtin__.min(ys), __builtin__.max(ys)]
        targetz += [__builtin__.min(zs), __builtin__.max(zs)]

        ax1.scatter(targetx, targety, targetz, c='k')
        #ax1.autoscale_view()
        #ax1.autoscale(enable=True, tight=True)

        plt.show(block=blocking)
        if sec > 0:
            time.sleep(sec)
        if filename != '':
            fig1.savefig(filename, dpi=90, bbox_inches='tight')
        plt.close()
        return plt


    # Saving/loading results
    def toFileYup(self, f):
        # type: (ResultSet, str) -> None
        with open(f, 'wb') as output:
            for rect in self.yup:
                pickle.dump(rect, output, pickle.HIGHEST_PROTOCOL)

    def toFileYlow(self, f):
        # type: (ResultSet, str) -> None
        with open(f, 'wb') as output:
            for rect in self.ylow:
                pickle.dump(rect, output, pickle.HIGHEST_PROTOCOL)

    def toFileBorder(self, f):
        # type: (ResultSet, str) -> None
        with open(f, 'wb') as output:
            for rect in self.border:
                pickle.dump(rect, output, pickle.HIGHEST_PROTOCOL)

    def toFile(self, f):
        # type: (ResultSet, str) -> None
        self.toFileYup(f + self.suffix_Yup)
        self.toFileYlow(f + self.suffix_Ylow)
        self.toFileBorder(f + self.suffix_Border)

    def fromFileYup(self, f):
        # type: (ResultSet, str) -> None
        self.yup = set()
        with open(f, 'rb') as inputfile:
            self.yup = pickle.load(inputfile)

    def fromFileYlow(self, f):
        # type: (ResultSet, str) -> None
        self.ylow = set()
        with open(f, 'rb') as inputfile:
            self.ylow = pickle.load(inputfile)

    def fromFileBorder(self, f):
        # type: (ResultSet, str) -> None
        self.border = set()
        with open(f, 'rb') as inputfile:
            self.border = pickle.load(inputfile)

    def fromFile(self, f):
        # type: (ResultSet, str) -> None
        self.fromFileYup(f + self.suffix_Yup)
        self.fromFileYlow(f + self.suffix_Ylow)
        self.fromFileBorder(f + self.suffix_Border)
