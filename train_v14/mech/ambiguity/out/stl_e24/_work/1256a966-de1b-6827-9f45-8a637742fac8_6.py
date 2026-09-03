from build123d import *

bracket_length = 80.0
bracket_width = 50.0
bracket_thickness = 8.0
rib_height = 6.0
rib_width = 4.0
rib_spacing = 10.0
rib_count = int((bracket_length - 20) / rib_spacing)
hole_diameter = 6.0
hole_offset_x = 15.0
hole_offset_y = 12.0
chamfer_distance = 0.5
slot_width = 4.0
slot_length = bracket_length - 20.0

solid = Box(bracket_length, bracket_width, bracket_thickness)
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_distance)

for i in range(rib_count):
    x_pos = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x_pos, bracket_width / 2, 0) * Box(rib_width, rib_height, bracket_thickness)
    solid = solid + rib

hole_positions = [
    (-bracket_length / 2 + hole_offset_x, -bracket_width / 2 + hole_offset_y),
    (bracket_length / 2 - hole_offset_x, -bracket_width / 2 + hole_offset_y),
    (-bracket_length / 2 + hole_offset_x, bracket_width / 2 - hole_offset_y),
    (bracket_length / 2 - hole_offset_x, bracket_width / 2 - hole_offset_y),
]
for x, y in hole_positions:
    solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter / 2, bracket_thickness * 2)

slot = Box(slot_length, slot_width, bracket_thickness * 2)
solid = solid - slot

part = solid
part.name = "bracket_with_ribs"
export_step(part, "output.step")