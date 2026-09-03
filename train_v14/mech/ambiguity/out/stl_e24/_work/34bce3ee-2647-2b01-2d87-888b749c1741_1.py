from build123d import *

base_width = 80.0
base_length = 80.0
base_thickness = 6.0
frame_outer_width = 70.0
frame_outer_length = 70.0
frame_height = 10.0
frame_wall_thickness = 5.0
slot_width = 30.0
slot_depth = 5.0
hole_diameter = 4.0
hole_offset = 10.0
chamfer_size = 0.5
fillet_radius = 1.5

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_length, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

frame = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer_width, frame_outer_length, frame_height)
frame = frame - Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer_width - 2*frame_wall_thickness, frame_outer_length - 2*frame_wall_thickness, frame_height)
frame = chamfer(frame.edges().filter_by(Axis.Z), chamfer_size)

result = base + frame

slot = Pos(frame_outer_width/2 - slot_depth/2, 0, base_thickness/2) * Box(slot_depth, slot_width, slot_depth)
result = result - slot

hole_positions = [
    (frame_outer_width/2 - hole_offset, frame_outer_length/2 - hole_offset),
    (-frame_outer_width/2 + hole_offset, frame_outer_length/2 - hole_offset),
    (-frame_outer_width/2 + hole_offset, -frame_outer_length/2 + hole_offset),
    (frame_outer_width/2 - hole_offset, -frame_outer_length/2 + hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, frame_height)

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")