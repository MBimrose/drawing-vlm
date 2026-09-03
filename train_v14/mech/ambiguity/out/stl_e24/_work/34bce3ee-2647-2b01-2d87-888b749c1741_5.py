from build123d import *

base_width = 80.0
base_length = 80.0
base_thickness = 6.0
frame_outer = 70.0
frame_inner = 60.0
frame_height = 10.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_height = 4.0
hole_diameter = 5.0
hole_offset = 5.0
chamfer_size = 0.5
fillet_base = 1.5
fillet_frame = 2.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_length, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_base)

frame = Pos(0, 0, base_thickness + frame_height/2) * (Box(frame_outer, frame_outer, frame_height) - Box(frame_inner, frame_inner, frame_height))
frame = fillet(frame.edges().filter_by(Axis.Z), fillet_frame)

result = base + frame

pocket = Pos(base_width/2 - pocket_height/2, 0, base_thickness/2) * Box(pocket_height, pocket_width, pocket_depth)
result = result - pocket

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

hole_r = hole_diameter / 2
hole_h = base_thickness + frame_height + 2
hole_z = (base_thickness + frame_height) / 2
for x, y in [(frame_outer/2 - hole_offset, frame_outer/2 - hole_offset),
             (frame_outer/2 - hole_offset, -(frame_outer/2 - hole_offset)),
             (-(frame_outer/2 - hole_offset), frame_outer/2 - hole_offset),
             (-(frame_outer/2 - hole_offset), -(frame_outer/2 - hole_offset))]:
    result = result - Pos(x, y, hole_z) * Cylinder(hole_r, hole_h)

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")