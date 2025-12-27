import FreeCAD as App
import Part

WIDTH = 60
HEIGHT = 40
DEPTH = 20
WALL = 2
FILLET = 1.5

def make_box():
    outer = Part.makeBox(WIDTH, DEPTH, HEIGHT)
    inner = Part.makeBox(WIDTH - 2*WALL,
                         DEPTH - 2*WALL,
                         HEIGHT - 2*WALL)
    inner.translate(App.Vector(WALL, WALL, WALL))
    shell = outer.cut(inner)
    shell = shell.makeFillet(FILLET, shell.Edges)
    return shell

doc = App.newDocument("GeneratedModel")
body = make_box()

part = doc.addObject("Part::Feature", "Enclosure")
part.Shape = body
part.Visibility = True

doc.recompute()
doc.saveAs("exports/enclosure.FCStd")
