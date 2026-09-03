from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
corner_radius = 5.0
wall_thickness = 2.0
rib_width = 4.0
rib_height = 3.0
rib_spacing = 10.0
hole_diameter = 6.0
hole_offset_x = 20.0
hole_offset_y = 15.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, corner_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib_count_x = int((plate_length - 2 * wall_thickness) // (rib_width + rib_spacing))
rib_count_y = int((plate_width - 2 * wall_thickness) // (rib_width + rib_spacing))

for i in range(rib_count_x):
    for j in range(rib_count_y):
        x = -plate_length/2 + wall_thickness + rib_width/2 + i * (rib_width + rib_spacing)
        y = -plate_width/2 + wall_thickness + rib_width/2 + j * (rib_width + rib_spacing)
        rib = Pos(x, y, rib_height/2) * Box(rib_width, rib_width, rib_height)
        solid_body = solid_body + rib

hole_positions = [
    (-plate_length/2 + hole_offset_x, -plate_width/2 + hole_offset_y),
    (plate_length/2 - hole_offset_x, plate_width/2 - hole_offset_y)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 2)

part = solid_body
part.name = "ribbed_plate"
export_step(part, "output.step")