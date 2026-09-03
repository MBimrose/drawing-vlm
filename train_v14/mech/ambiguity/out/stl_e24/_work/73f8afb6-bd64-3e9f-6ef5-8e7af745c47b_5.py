from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
length = 30.0
inner_diameter = outer_diameter - 2 * wall_thickness
tab_width = 20.0
tab_height = 10.0
tab_thickness = 8.0
hole_diameter = 5.0
hole_spacing = 14.0
chamfer_size = 0.8
fillet_radius = 0.5

outer_cyl = Cylinder(outer_diameter / 2, length)
inner_cyl = Cylinder(inner_diameter / 2, length)
shell = outer_cyl - inner_cyl
shell = chamfer(shell.edges(), chamfer_size)
shell = fillet(shell.edges(), fillet_radius)

tab = Pos(outer_diameter / 2 + tab_thickness / 2 - 0.5, 0, 0) * Box(tab_thickness, tab_width, tab_height)

hole1 = Pos(outer_diameter / 2 + tab_thickness / 2 - 0.5, -hole_spacing / 2, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, tab_thickness + 1)
hole2 = Pos(outer_diameter / 2 + tab_thickness / 2 - 0.5, hole_spacing / 2, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, tab_thickness + 1)

tab_with_holes = tab - hole1 - hole2
part = shell + tab_with_holes
part.name = "shell_with_tab"
export_step(part, "output.step")