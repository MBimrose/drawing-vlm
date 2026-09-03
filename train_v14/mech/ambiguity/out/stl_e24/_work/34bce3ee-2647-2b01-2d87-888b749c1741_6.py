from build123d import *

base_width = 80.0
base_length = 80.0
base_thickness = 6.0
frame_outer_size = 70.0
frame_inner_size = 60.0
frame_height = 10.0
fillet_radius_base = 1.5
fillet_radius_frame = 2.0
chamfer_distance = 0.5
hole_diameter = 4.0
hole_offset = 20.0
slot_width = 12.0
slot_length = 30.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_length, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius_base)

frame_outer = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer_size, frame_outer_size, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_inner_size, frame_inner_size, frame_height)
frame = frame_outer - frame_inner
frame = fillet(frame.edges().filter_by(Axis.Z), fillet_radius_frame)

result = base + frame

for x, y in [(hole_offset, hole_offset), (-hole_offset, hole_offset), (-hole_offset, -hole_offset), (hole_offset, -hole_offset)]:
    result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, frame_height)

slot = Pos(frame_outer_size/2, 0, base_thickness + frame_height/2) * Box(slot_width, slot_length, frame_height)
result = result - slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "base_with_frame"
export_step(part, "output.step")