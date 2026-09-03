from build123d import *

base_width = 80.0
base_length = 80.0
base_thickness = 6.0
base_fillet = 1.5
frame_outer = 70.0
frame_inner = 60.0
frame_height = 10.0
frame_fillet = 2.0
chamfer_size = 0.5
hole_diameter = 4.0
hole_offset = 10.0
slot_width = 30.0
slot_depth = 4.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_length, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), base_fillet)

frame_outer_solid = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer, frame_outer, frame_height)
frame_inner_solid = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_inner, frame_inner, frame_height)
frame = frame_outer_solid - frame_inner_solid
frame = fillet(frame.edges().filter_by(Axis.Z), frame_fillet)

result = base + frame

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

hole_positions = [
    (hole_offset - base_width/2, hole_offset - base_length/2),
    (base_width/2 - hole_offset, hole_offset - base_length/2),
    (hole_offset - base_width/2, base_length/2 - hole_offset),
    (base_width/2 - hole_offset, base_length/2 - hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, base_thickness + frame_height + 2)

slot = Pos(base_width/2 - slot_depth/2, 0, base_thickness/2) * Box(slot_depth, slot_width, slot_depth)
result = result - slot

part = result
part.name = "base_with_frame"
export_step(part, "output.step")