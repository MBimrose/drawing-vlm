from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
corner_radius = 5.0
wall_thickness = 2.0
pocket_depth = plate_thickness - wall_thickness
pocket_length = plate_length - 2 * wall_thickness
pocket_width = plate_width - 2 * wall_thickness
hole_diameter = 6.0
hole_offset_x = 20.0
hole_offset_y = 15.0
rib_height = 2.0
rib_width = 10.0
rib_length = plate_length - 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)

pocket = Pos(0, 0, plate_thickness - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for x, y in [(-hole_offset_x, -hole_offset_y), (hole_offset_x, hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, plate_thickness / 2) * Cylinder(hole_diameter / 2, plate_thickness)

rib = Pos(0, 0, rib_height / 2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_holes_and_rib"
export_step(part, "output.step")