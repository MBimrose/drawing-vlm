from build123d import *

base_length = 80.0
base_width = 80.0
base_thickness = 6.0
base_fillet = 1.5
frame_outer = 60.0
frame_inner = 50.0
frame_height = 10.0
frame_fillet = 2.0
hole_diameter = 5.0
hole_offset = 20.0
slot_width = 30.0
slot_height = 10.0
chamfer_size = 0.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), base_fillet)

frame = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer, frame_outer, frame_height)
frame = frame - Pos(0, 0, base_thickness + frame_height/2) * Box(frame_inner, frame_inner, frame_height)
frame = fillet(frame.edges().filter_by(Axis.Z), frame_fillet)

result = base + frame

for x, y in [(-hole_offset, -hole_offset), (hole_offset, -hole_offset), (-hole_offset, hole_offset), (hole_offset, hole_offset)]:
    result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, frame_height)

slot = Pos(base_length/2, 0, base_thickness/2) * Box(base_length, slot_width, slot_height)
result = result - slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "base_with_frame"
export_step(part, "output.step")