import time
import __builtin__

import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class ResultSet:
    suffix_Yup = 'up'
    suffix_Ylow = 'low'
    suffix_Border = 'border'

    def __init__(self, border=set(), ylow=set(), yup=set()):
        # type: (ResultSet, set, set, set) -> None
        self.border = border
        self.ylow = ylow
        self.yup = yup

    # TODO
    # Vertex functions
    def verticesYup(self):
        # type: (ResultSet) -> set
        #vertices_list = [rect.vertices() for rect in self.yup]
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

    # MatPlot Graphics
    def toMatPlotYup(self, xaxe=0, yaxe=1, opacity=1.0):
        # type: (ResultSet, int, int, float) -> list
        patches = []
        for rect in self.yup:
            patches += [rect.toMatplot('green', xaxe, yaxe, opacity)]
        return patches

    def toMatPlotYlow(self, xaxe=0, yaxe=1, opacity=1.0):
        # type: (ResultSet, int, int, float) -> list
        patches = []
        for rect in self.ylow:
            patches += [rect.toMatplot('red', xaxe, yaxe, opacity)]
        return patches

    def toMatPlotBorder(self, xaxe=0, yaxe=1, opacity=1.0):
        # type: (ResultSet, int, int, float) -> list
        patches = []
        for rect in self.border:
            patches += [rect.toMatplot('blue', xaxe, yaxe, opacity)]
        return patches

    def toMatPlot(self,
                  file='',
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

        pathpatch_yup = self.toMatPlotYup(xaxe, yaxe, opacity)
        pathpatch_ylow = self.toMatPlotYlow(xaxe, yaxe, opacity)
        pathpatch_border = self.toMatPlotBorder(xaxe, yaxe, opacity)

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

        if file != '':
            fig1.savefig(file, dpi=90, bbox_inches='tight')

        plt.close()
        return plt

    def toMatPlotYup3D(self, xaxe=0, yaxe=1, zaxe=2, opacity=1.0):
        # type: (ResultSet, int, int, int, float) -> list
        faces = []
        for rect in self.yup:
            faces += [rect.toMatplot3D('green', xaxe, yaxe, zaxe, opacity)]
        return faces

    def toMatPlotYlow3D(self, xaxe=0, yaxe=1, zaxe=2, opacity=1.0):
        # type: (ResultSet, int, int, int, float) -> list
        faces = []
        for rect in self.ylow:
            faces += [rect.toMatplot3D('red', xaxe, yaxe, zaxe, opacity)]
        return faces

    def toMatPlotBorder3D(self, xaxe=0, yaxe=1, zaxe=2, opacity=1.0):
        # type: (ResultSet, int, int, int, float) -> list
        faces = []
        for rect in self.border:
            faces += [rect.toMatplot3D('blue', xaxe, yaxe, zaxe, opacity)]
        return faces

    def toMatPlot3D(self,
                  file='',
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
        if file != '':
            fig1.savefig(file, dpi=90, bbox_inches='tight')
        plt.close()
        return plt


    # Saving/loading results
    def toFileYup(self, file):
        # type: (ResultSet, str) -> None
        with open(file, 'wb') as output:
            for rect in self.yup:
                pickle.dump(rect, output, pickle.HIGHEST_PROTOCOL)

    def toFileYlow(self, file):
        # type: (ResultSet, str) -> None
        with open(file, 'wb') as output:
            for rect in self.ylow:
                pickle.dump(rect, output, pickle.HIGHEST_PROTOCOL)

    def toFileBorder(self, file):
        # type: (ResultSet, str) -> None
        with open(file, 'wb') as output:
            for rect in self.border:
                pickle.dump(rect, output, pickle.HIGHEST_PROTOCOL)

    def toFile(self, file):
        # type: (ResultSet, str) -> None
        self.toFileYup(file + self.suffix_Yup)
        self.toFileYlow(file + self.suffix_Ylow)
        self.toFileBorder(file + self.suffix_Border)

    def fromFileYup(self, file):
        # type: (ResultSet, str) -> None
        self.yup = set()
        with open(file, 'rb') as input:
            self.yup = pickle.load(input)

    def fromFileYlow(self, file):
        # type: (ResultSet, str) -> None
        self.ylow = set()
        with open(file, 'rb') as input:
            self.ylow = pickle.load(input)

    def fromFileBorder(self, file):
        # type: (ResultSet, str) -> None
        self.border = set()
        with open(file, 'rb') as input:
            self.border = pickle.load(input)

    def fromFile(self, file):
        # type: (ResultSet, str) -> None
        self.fromFileYup(file + self.suffix_Yup)
        self.fromFileYlow(file + self.suffix_Ylow)
        self.fromFileBorder(file + self.suffix_Border)
