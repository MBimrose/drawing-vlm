from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = 5.0
hole_diameter = 3.0
hole_offset_x = 20.0
hole_offset_y = 15.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[bottom_face])

rib = Pos(0, 0, -rib_height/2) * Box(outer_length - 2*wall_thickness, rib_thickness, rib_height)
base = base + rib

hole_r = hole_diameter / 2
hole_h = outer_height + rib_height + 10
for x, y in [(hole_offset_x, hole_offset_y), (-hole_offset_x, hole_offset_y),
             (hole_offset_x, -hole_offset_y), (-hole_offset_x, -hole_offset_y)]:
    base = base - Pos(x, y, outer_height/2) * Cylinder(hole_r, hole_h)

part = base
part.name = "shelled_box_with_rib_and_holes"
export_step(part, "output.step")