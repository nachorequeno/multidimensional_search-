import matplotlib.pyplot as plt
import pickle
import time

class ResultSet:
  suffix_Yup = 'up'
  suffix_Ylow = 'low'
  suffix_Border = 'border'

  def __init__(self, border, ylow, yup):
     self.border = border
     self.ylow = ylow
     self.yup = yup


  # Volume functions
  def VolumeYup(self):
      # type: (_) -> float
      vol = 0.0
      for rect in self.yup:
          vol = vol + rect.volume()
      return vol

  def VolumeYlow(self):
      # type: (_) -> float
      vol = 0.0
      for rect in self.ylow:
          vol = vol + rect.volume()
      return vol

  def VolumeBorder(self):
      # type: (_) -> float
      vol = 0.0
      for rect in self.border:
          vol = vol + rect.volume()
      return vol

  # Membership functions
  def MemberYup(self, xpoint):
      # type: (_, tuple) -> bool
      isMember = False
      for rect in self.yup:
          isMember = isMember or (xpoint in rect)
      return isMember

  def MemberYlow(self, xpoint):
      # type: (_, tuple) -> bool
      isMember = False
      for rect in self.ylow:
          isMember = isMember or (xpoint in rect)
      return isMember

  def MemberBorder(self, xpoint):
      # type: (_, tuple) -> bool
      isMember = False
      for rect in self.border:
          isMember = isMember or (xpoint in rect)
      return isMember

  # MatPlot Graphics
  def toMatPlotYup(self, xaxe=0, yaxe=1, opacity=1.0):
    patches = []
    for rect in self.yup:
        patches += [rect.toMatplot('green', xaxe, yaxe, opacity)]
    return patches

  def toMatPlotYlow(self, xaxe=0, yaxe=1, opacity=1.0):
    patches = []
    for rect in self.ylow:
        patches += [rect.toMatplot('red', xaxe, yaxe, opacity)]
    return patches

  def toMatPlotBorder(self, xaxe=0, yaxe=1, opacity=1.0):
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
                sec=0,
                opacity=1.0):
      fig1 = plt.figure()
      ax1 = fig1.add_subplot(111, aspect='equal')
      ax1.set_title('Approximation of the Pareto front (x,y): (' + str(xaxe) + ', ' + str(yaxe) + ')')

      pathpatch_yup = self.toMatPlotYup(xaxe, yaxe, opacity)
      pathpatch_ylow = self.toMatPlotYlow(xaxe, yaxe, opacity)
      pathpatch_border = self.toMatPlotBorder(xaxe, yaxe, opacity)

      pathpatch = pathpatch_yup
      pathpatch += pathpatch_ylow
      pathpatch += pathpatch_border

      #print('Pathpatch: ')
      #print(pathpatch)
      for pathpatch_i in pathpatch:
          ax1.add_patch(pathpatch_i)
          ## ax1.autoscale_view()
          ## plt.show()
          ## time.sleep(1)
      ax1.autoscale_view()

      if file != '':
          fig1.savefig(file, dpi=90, bbox_inches='tight')
      plt.plot(targetx, targety, 'kp')
      plt.show(block=blocking)
      if sec > 0:
          time.sleep(sec)
      plt.close()
      return plt

  # Saving/loading results
  def toFileYup(self, file):
    with open(file, 'wb') as output:
        for rect in self.yup:
            pickle.dump(rect, output, pickle.HIGHEST_PROTOCOL)
    return 0

  def toFileYlow(self, file):
    with open(file, 'wb') as output:
        for rect in self.ylow:
            pickle.dump(rect, output, pickle.HIGHEST_PROTOCOL)
    return 0

  def toFileBorder(self, file):
    with open(file, 'wb') as output:
        for rect in self.border:
            pickle.dump(rect, output, pickle.HIGHEST_PROTOCOL)
    return 0

  def toFile(self, file):
      self.toFileYup(file + self.suffix_Yup)
      self.toFileYlow(file + self.suffix_Ylow)
      self.toFileBorder(file + self.suffix_Border)

  def fromFileYup(self, file):
    self.yup = set()
    with open(file, 'rb') as input:
         self.yup = pickle.load(input)
    return 0

  def fromFileYlow(self, file):
    self.ylow = set()
    with open(file, 'rb') as input:
        self.ylow = pickle.load(input)
    return 0

  def fromFileBorder(self, file):
    self.border = set()
    with open(file, 'rb') as input:
        self.border = pickle.load(input)
    return 0

  def fromFile(self, file):
      self.fromFileYup(file+self.suffix_Yup)
      self.fromFileYlow(file+self.suffix_Ylow)
      self.fromFileBorder(file+self.suffix_Border)
