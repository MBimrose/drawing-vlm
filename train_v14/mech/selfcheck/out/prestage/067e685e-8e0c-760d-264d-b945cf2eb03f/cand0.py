from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 5.0
rib_width = 4.0
rib_height = 3.0
rib_spacing = 10.0
fillet_radius = 2.5
chamfer_distance = 0.5
hole_diameter = 4.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0

solid_body = Box(leaf_length, leaf_width, leaf_thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

rib1 = Pos(-rib_spacing/2, 0, leaf_thickness/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)
rib2 = Pos(rib_spacing/2, 0, leaf_thickness/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body + rib1 + rib2

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, leaf_thickness + rib_height + 10)

part = solid_body
part.name = "leaf_with_ribs_and_holes"
export_step(part, "output.step")