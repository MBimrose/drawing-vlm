from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 8.0
fillet_radius = 2.0
pin_hole_diameter = 5.0
pin_hole_offset = 25.0
pocket_length = 40.0
pocket_width = 12.0
pocket_depth = 4.0
relief_hole_diameter = 8.0
relief_hole_offset = 10.0
rib_height = 3.0
rib_width = 6.0
rib_thickness = 2.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(leaf_length, leaf_width)
    extrude(amount=leaf_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

pin_x = -leaf_length / 2 + pin_hole_offset
solid_body = solid_body - Pos(pin_x, 0, leaf_thickness / 2) * Cylinder(pin_hole_diameter / 2, leaf_thickness * 2)

pocket_z = leaf_thickness - pocket_depth / 2
solid_body = solid_body - Pos(0, 0, pocket_z) * Box(pocket_length, pocket_width, pocket_depth)

relief_y_positions = [leaf_width / 2 - relief_hole_offset, -leaf_width / 2 + relief_hole_offset]
for y in relief_y_positions:
    solid_body = solid_body - Pos(0, y, 0) * Cylinder(relief_hole_diameter / 2, leaf_thickness * 2)

rib_z = -rib_height / 2
solid_body = solid_body + Pos(0, 0, rib_z) * Box(rib_width, rib_thickness, rib_height)

part = solid_body
part.name = "leaf_with_holes_and_rib"
export_step(part, "output.step")