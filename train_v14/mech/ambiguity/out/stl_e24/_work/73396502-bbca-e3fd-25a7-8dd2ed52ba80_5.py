from build123d import *

length = 80.0
width = 30.0
thickness = 10.0
rib_width = 20.0
rib_height = 2.0
rib_length = width - 6.0
fillet_radius = 2.0
chamfer_distance = 0.5
hole_diameter = 3.3
hole_offset_x = 20.0
hole_offset_y = 12.0

base = Pos(0, 0, thickness/2) * Box(length, width, thickness)
rib = Pos(0, 0, thickness - rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = base + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

hole_positions = [
    (-hole_offset_x, -hole_offset_y),
    (hole_offset_x, -hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (hole_offset_x, hole_offset_y)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness + 1)

part = solid_body
part.name = "ribbed_plate_with_holes"
export_step(part, "output.step")