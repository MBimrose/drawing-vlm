from build123d import *

plate_length = 100.0
plate_width = 30.0
plate_thickness = 5.0
slot_length = 30.0
slot_width = 10.0
hole_diameter = 5.1
hole_spacing = 20.0
num_holes = 4
chamfer_distance = 2.0
rib_height = 2.0
rib_width = 5.0
rib_length = 20.0

solid_body = Box(plate_length, plate_width, plate_thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

slot = Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - slot

hole_positions = [
    (-((num_holes - 1) * hole_spacing) / 2 + i * hole_spacing, 0)
    for i in range(num_holes)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness)

rib_z = -plate_thickness / 2 - rib_height / 2
rib1 = Pos(-plate_length / 2 + rib_length / 2, -plate_width / 2 + rib_width / 2, rib_z) * Box(rib_length, rib_width, rib_height)
rib2 = Pos(plate_length / 2 - rib_length / 2, -plate_width / 2 + rib_width / 2, rib_z) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_slot_holes_and_ribs"
export_step(part, "output.step")