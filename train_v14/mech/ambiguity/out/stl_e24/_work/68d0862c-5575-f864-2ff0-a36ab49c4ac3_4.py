from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
corner_radius = 5.0
wall_thickness = 2.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 4.0
hole_diameter = 6.0
hole_offset_x = 20.0
hole_offset_y = 15.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)

for x, y in [(-hole_offset_x, -hole_offset_y), (hole_offset_x, hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 2)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "shelled_plate_with_pocket"
export_step(part, "output.step")