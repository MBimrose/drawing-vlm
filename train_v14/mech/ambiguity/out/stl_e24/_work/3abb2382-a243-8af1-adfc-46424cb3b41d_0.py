from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_height = 8.0
frame_wall_thickness = 5.0
hole_diameter = 4.0
hole_offset = 12.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 3.0
chamfer_size = 0.5
rib_height = 2.0
rib_width = 8.0
rib_length = base_length - 2 * frame_wall_thickness - 10.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
frame_outer = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_wall_thickness, base_width - 2*frame_wall_thickness, frame_height)
frame = frame_outer - frame_inner
result = base + frame

hole_positions = [
    (hole_offset, hole_offset),
    (base_length - hole_offset, hole_offset),
    (hole_offset, base_width - hole_offset),
    (base_length - hole_offset, base_width - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, (base_thickness + frame_height)/2) * Cylinder(hole_diameter/2, base_thickness + frame_height + 10)

result = result - Pos(0, 0, base_thickness + frame_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

rib = Pos(0, 0, -rib_height/2) * Box(rib_length, rib_width, rib_height)
result = result + rib

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")