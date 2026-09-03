from build123d import *

bracket_length = 80.0
bracket_width = 50.0
bracket_thickness = 8.0
slot_length = 60.0
slot_width = 4.0
hole_diameter = 6.0
hole_offset_x = 15.0
hole_offset_y = 12.0
rib_height = 3.0
rib_width = 3.0
rib_spacing = 8.0
chamfer_size = 0.5

result = Box(bracket_length, bracket_width, bracket_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

slot = Box(slot_length, slot_width, bracket_thickness + 2)
result = result - slot

hole_positions = [
    (-bracket_length/2 + hole_offset_x, -bracket_width/2 + hole_offset_y),
    (bracket_length/2 - hole_offset_x, -bracket_width/2 + hole_offset_y),
    (-bracket_length/2 + hole_offset_x, bracket_width/2 - hole_offset_y),
    (bracket_length/2 - hole_offset_x, bracket_width/2 - hole_offset_y),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness + 2)

num_ribs = int((bracket_length - 2 * rib_spacing) // rib_spacing) + 1
rib_x_positions = [-bracket_length/2 + rib_spacing + i * rib_spacing for i in range(num_ribs)]
for x in rib_x_positions:
    rib = Pos(x, bracket_width/2 + rib_height/2, 0) * Box(rib_width, rib_height, bracket_thickness)
    result = result + rib

part = result
part.name = "bracket_with_ribs"
export_step(part, "output.step")