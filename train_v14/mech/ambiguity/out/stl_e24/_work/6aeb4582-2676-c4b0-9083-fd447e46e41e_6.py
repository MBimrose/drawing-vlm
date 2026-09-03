from build123d import *

rod_length = 60.0
rod_diameter = 10.0
hole_diameter = 6.0
tab_width = 12.0
tab_height = 8.0
tab_thickness = 4.0
tab_hole_diameter = 3.0
tab_hole_spacing = 6.0
chamfer_size = 0.5

rod = Rot(0, 90, 0) * Cylinder(rod_diameter/2, rod_length)
hole = Rot(0, 90, 0) * Cylinder(hole_diameter/2, rod_length + 10)
rod = rod - hole

tab = Pos(rod_length/2, 0, 0) * Box(tab_thickness, tab_width, tab_height)
tab_face = tab.faces().sort_by(Axis.X)[-1]
tab = chamfer(tab_face.edges(), chamfer_size)

for y in [-tab_hole_spacing/2, tab_hole_spacing/2]:
    tab = tab - Pos(rod_length/2, y, 0) * Rot(0, 90, 0) * Cylinder(tab_hole_diameter/2, tab_thickness + 10)

part = rod + tab
part.name = "rod_with_tab"
export_step(part, "output.step")