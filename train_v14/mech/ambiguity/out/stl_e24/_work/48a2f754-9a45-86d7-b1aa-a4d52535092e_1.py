from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 12.0
pocket_length = 40.0
pocket_width = 12.0
pocket_depth = 6.0
hole_diameter = 6.4
hole_spacing_x = 30.0
hole_spacing_y = 10.0
fillet_radius = 2.0
rib_height = 4.0
rib_thickness = 3.0
rib_spacing = 15.0

solid_body = Box(arm_length, arm_width, arm_thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(0, arm_width/2 - pocket_depth/2, arm_thickness/2) * Box(pocket_length, pocket_depth, pocket_width)
solid_body = solid_body - pocket

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, arm_thickness * 2)

rib_count = int((arm_length - 2 * rib_spacing) // rib_spacing) + 1
rib_positions = [(-arm_length/2 + rib_spacing + i * rib_spacing) for i in range(rib_count)]
for x in rib_positions:
    rib = Pos(x, 0, -arm_thickness/2 + rib_height/2) * Box(rib_thickness, arm_width - 2*fillet_radius, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "arm_with_pocket_holes_and_ribs"
export_step(part, "output.step")