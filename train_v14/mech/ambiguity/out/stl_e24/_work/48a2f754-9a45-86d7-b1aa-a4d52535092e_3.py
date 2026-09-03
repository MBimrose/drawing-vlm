from build123d import *

base_length = 80.0
base_width = 20.0
base_height = 12.0
groove_width = 12.0
groove_depth = 6.0
groove_length = 60.0
hole_diameter = 6.4
hole_spacing_x = 30.0
hole_spacing_y = 10.0
fillet_radius = 2.0
rib_height = 4.0
rib_thickness = 3.0

solid_body = Box(base_length, base_width, base_height)

groove = Pos(0, base_width/2 - groove_depth/2, base_height/2) * Box(groove_width, groove_depth, groove_length)
solid_body = solid_body - groove

solid_body = fillet(solid_body.edges(), fillet_radius)

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, base_height * 2)

rib = Pos(0, -base_width/2 + rib_thickness/2, base_height/2) * Box(base_length, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "base_with_groove_holes_and_rib"
export_step(part, "output.step")