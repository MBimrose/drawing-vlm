from build123d import *

bracket_length = 80.0
bracket_width = 50.0
bracket_thickness = 8.0
rib_height = 6.0
rib_width = 4.0
rib_spacing = 10.0
hole_diameter = 6.0
hole_offset_x = 15.0
hole_offset_y = 12.0
slot_length = 60.0
slot_width = 4.0
chamfer_size = 0.5

solid_body = Box(bracket_length, bracket_width, bracket_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

hole_positions = [
    (-bracket_length/2 + hole_offset_x, -bracket_width/2 + hole_offset_y),
    ( bracket_length/2 - hole_offset_x, -bracket_width/2 + hole_offset_y),
    (-bracket_length/2 + hole_offset_x,  bracket_width/2 - hole_offset_y),
    ( bracket_length/2 - hole_offset_x,  bracket_width/2 - hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness)

solid_body = solid_body - Box(slot_length, slot_width, bracket_thickness)

num_ribs = int((bracket_length - 2*hole_offset_x) // rib_spacing) + 1
for i in range(num_ribs):
    x_pos = -bracket_length/2 + hole_offset_x + i * rib_spacing
    rib = Pos(x_pos, bracket_width/2, 0) * Box(rib_width, rib_height, bracket_thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "bracket_with_ribs"
export_step(part, "output.step")