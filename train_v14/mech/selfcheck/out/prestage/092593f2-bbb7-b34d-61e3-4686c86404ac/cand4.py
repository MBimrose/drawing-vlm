from build123d import *

bracket_length = 80
bracket_width = 40
bracket_thickness = 4
cutout_width = 20
cutout_height = 30
cutout_offset = 5
fillet_radius = 3
hole_diameter = 5
hole_spacing = 30
hole_edge_margin = 8
rib_thickness = 2
rib_height = 6
rib_length = bracket_width - 10

base = Box(bracket_length, bracket_width, bracket_thickness)

cutout_center_x = bracket_length/2 - cutout_offset - cutout_width/2
cutout = Pos(cutout_center_x, 0, 0) * Box(cutout_width, cutout_height, bracket_thickness)
cutout = fillet(cutout.edges().filter_by(Axis.Z), fillet_radius)

result = base - cutout

hole_x = -bracket_length/2 + hole_edge_margin
for y in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(hole_x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness)

rib = Pos(bracket_length/2 + rib_height/2, 0, 0) * Box(rib_height, rib_length, rib_thickness)
result = result + rib

part = result
part.name = "bracket"
export_step(part, "output.step")