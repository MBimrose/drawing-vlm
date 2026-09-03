from build123d import *

bracket_length = 80.0
bracket_width = 50.0
bracket_thickness = 8.0
rib_height = 3.0
rib_width = 3.0
rib_spacing = 8.0
rib_count = 8
slot_length = 60.0
slot_width = 4.0
hole_diameter = 6.0
hole_offset_x = 15.0
hole_offset_y = 12.0
chamfer_distance = 0.5

solid_body = Box(bracket_length, bracket_width, bracket_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, bracket_width / 2 + rib_height / 2, 0) * Box(rib_width, rib_height, bracket_thickness)
    solid_body = solid_body + rib

slot = Box(slot_length, slot_width, bracket_thickness)
solid_body = solid_body - slot

hole_positions = [
    (-bracket_length / 2 + hole_offset_x, -bracket_width / 2 + hole_offset_y),
    (bracket_length / 2 - hole_offset_x, -bracket_width / 2 + hole_offset_y),
    (-bracket_length / 2 + hole_offset_x, bracket_width / 2 - hole_offset_y),
    (bracket_length / 2 - hole_offset_x, bracket_width / 2 - hole_offset_y),
]
for hx, hy in hole_positions:
    solid_body = solid_body - Pos(hx, hy, 0) * Cylinder(hole_diameter / 2, bracket_thickness)

part = solid_body
part.name = "bracket_with_ribs"
export_step(part, "output.step")