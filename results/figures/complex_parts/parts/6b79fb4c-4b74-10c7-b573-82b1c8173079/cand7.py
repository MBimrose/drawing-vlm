from build123d import *

channel_width = 80.0
channel_height = 40.0
wall_thickness = 5.0
length = 100.0
slot_width = 20.0
slot_height = 30.0
slot_offset_from_end = 10.0
chamfer_size = 2.0
hole_diameter = 8.0
hole_center_x = wall_thickness / 2
hole_center_z = channel_height / 2
pattern_hole_diameter = 3.0
pattern_spacing = 12.0
pattern_rows = 3
pattern_cols = 4

outer = Box(channel_width, length, channel_height)
inner = Pos(wall_thickness / 2, 0, 0) * Box(channel_width - wall_thickness, length, channel_height - 2 * wall_thickness)
result = outer - inner

slot_center_x = channel_width / 2 - slot_offset_from_end - slot_width / 2
slot = Pos(slot_center_x, 0, channel_height / 2 - wall_thickness / 2) * Box(slot_width, slot_height, wall_thickness)
result = result - slot

top_face = result.faces().sort_by(Axis.Z)[-1]
chamfer_edges = top_face.edges().filter_by(Axis.Y)
result = chamfer(chamfer_edges, chamfer_size)

result = result - Pos(hole_center_x, 0, hole_center_z - channel_height / 2) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, channel_width)

for i in range(pattern_cols):
    for j in range(pattern_rows):
        y = (i - (pattern_cols - 1) / 2) * pattern_spacing
        z = (j - (pattern_rows - 1) / 2) * pattern_spacing
        result = result - Pos(-channel_width / 2 + wall_thickness / 2, y, z) * Rot(0, 90, 0) * Cylinder(pattern_hole_diameter / 2, channel_width)

part = result
part.name = "C_channel_with_slot_and_holes"
export_step(part, "output.step")