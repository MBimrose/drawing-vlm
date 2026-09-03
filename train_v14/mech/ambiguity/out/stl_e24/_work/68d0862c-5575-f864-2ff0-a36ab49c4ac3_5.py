from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
corner_radius = 5.0
wall_thickness = 2.0
hole_diameter = 6.0
hole_offset_x = 20.0
hole_offset_y = 15.0
rib_width = 10.0
rib_height = 4.0
rib_length = plate_width - 2 * wall_thickness
pocket_width = 30.0
pocket_depth = 20.0
pocket_height = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_depth)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

for x, y in [(-hole_offset_x, -hole_offset_y), (hole_offset_x, hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 2)

rib = Pos(0, 0, plate_thickness - rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

pocket = Pos(0, 0, plate_thickness - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "shelled_plate_with_rib_and_pocket"
export_step(part, "output.step")