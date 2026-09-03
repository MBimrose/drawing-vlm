from build123d import *

base_width = 80.0
base_length = 80.0
base_thickness = 6.0
base_fillet = 2.0
frame_outer = 70.0
frame_inner = 60.0
frame_height = 10.0
frame_fillet = 1.5
chamfer_size = 0.5
hole_diameter = 4.0
hole_offset = 20.0
slot_width = 6.0
slot_length = 30.0
slot_depth = 4.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_length, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), base_fillet)

frame = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer, frame_outer, frame_height)
result = base + frame

inner_cut = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_inner, frame_inner, frame_height)
result = result - inner_cut

result = fillet(result.edges().filter_by(Axis.Z), frame_fillet)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

hole_positions = [
    (hole_offset, hole_offset),
    (-hole_offset, hole_offset),
    (-hole_offset, -hole_offset),
    (hole_offset, -hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, base_thickness + frame_height + 10)

slot = Pos(base_width/2 - slot_depth/2, 0, base_thickness/2) * Box(slot_depth, slot_length, slot_width)
result = result - slot

part = result
part.name = "base_with_frame"
export_step(part, "output.step")