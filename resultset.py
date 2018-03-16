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

  # GNUPlot Graphics
  def toGNUPlotYup(self, xaxe=0, yaxe=1):
    print('set title \'Yup\'')
    for i, rect in enumerate(self.yup):
        print('set object ' + str(i+1) + ' ' + rect.toGnuPlot(xaxe, yaxe) + ' ' + rect.toGnuPlotColor("green"))

    #print('set ' + xspace.toGnuPlotXrange())
    #print('set ' + xspace.toGnuPlotYrange())
    print('set xzeroaxis')
    print('set yzeroaxis')

    print('plot x')

  def toGNUPlotYlow(self, xaxe=0, yaxe=1):
    print('set title \'Ylow\'')
    for i, rect in enumerate(self.ylow):
        print('set object ' + str(i+1) + ' ' + rect.toGnuPlot(xaxe, yaxe) + ' ' + rect.toGnuPlotColor("red"))

    #print('set ' + xspace.toGnuPlotXrange())
    #print('set ' + xspace.toGnuPlotYrange())
    print('set xzeroaxis')
    print('set yzeroaxis')

    print('plot x')

  def toGNUPlotBorder(self, xaxe=0, yaxe=1):
    print('set title \'Border\'')
    for i, rect in enumerate(self.border):
        print('set object ' + str(i+1) + ' ' + rect.toGnuPlot(xaxe, yaxe) + ' ' + rect.toGnuPlotColor("blu"))

    #print('set ' + xspace.toGnuPlotXrange())
    #print('set ' + xspace.toGnuPlotYrange())
    print('set xzeroaxis')
    print('set yzeroaxis')

    print('plot x')

  def toGNUPlot(self, xaxe=0, yaxe=1):
      print('set title \'Xspace\'')
      i = 0
      for rect in self.ylow:
          print('set object ' + str(i + 1) + ' ' + rect.toGnuPlot(xaxe, yaxe) + ' ' + rect.toGnuPlotColor("red"))
          i += 1

      for rect in self.yup:
          print('set object ' + str(i + 1) + ' ' + rect.toGnuPlot(xaxe, yaxe) + ' ' + rect.toGnuPlotColor("green"))
          i += 1

      for rect in self.border:
          print('set object ' + str(i + 1) + ' ' + rect.toGnuPlot(xaxe, yaxe) + ' ' + rect.toGnuPlotColor("blu"))
          i += 1

      #print('set ' + xspace.toGnuPlotXrange(xaxe))
      #print('set ' + xspace.toGnuPlotYrange(yaxe))
      print('set xzeroaxis')
      print('set yzeroaxis')

      print('plot x')

  # MatPlot Graphics
  def toMatPlotYup(self, xaxe=0, yaxe=1):
    patches = []
    for rect in self.yup:
        patches += [rect.toMatplot('green', xaxe, yaxe)]
    return patches

  def toMatPlotYlow(self, xaxe=0, yaxe=1):
    patches = []
    for rect in self.ylow:
        patches += [rect.toMatplot('red', xaxe, yaxe)]
    return patches

  def toMatPlotBorder(self, xaxe=0, yaxe=1):
    patches = []
    for rect in self.border:
        patches += [rect.toMatplot('blue', xaxe, yaxe)]
    return patches

  def toMatPlot(self, file='', xaxe=0, yaxe=1):
      fig1 = plt.figure()
      ax1 = fig1.add_subplot(111, aspect='equal')
      ax1.set_title('Approximation of the Pareto front')

      pathpatch_yup = self.toMatPlotYup(xaxe, yaxe)
      pathpatch_ylow = self.toMatPlotYlow(xaxe, yaxe)
      pathpatch_border = self.toMatPlotBorder(xaxe, yaxe)

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
      plt.show()
      return 0

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
