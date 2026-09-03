from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_height = 8.0
frame_wall_thickness = 5.0
rib_width = 8.0
rib_height = 2.0
hole_diameter = 4.0
hole_offset = 12.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0
chamfer_size = 0.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
frame = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
result = base + frame

inner_cut = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_wall_thickness, base_width - 2*frame_wall_thickness, frame_height)
result = result - inner_cut

rib = Pos(0, 0, -rib_height/2) * Box(base_length - 2*frame_wall_thickness, rib_width, rib_height)
result = result + rib

hole_positions = [
    (hole_offset, hole_offset),
    (base_length - hole_offset, hole_offset),
    (hole_offset, base_width - hole_offset),
    (base_length - hole_offset, base_width - hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, (base_thickness + frame_height)/2) * Cylinder(hole_diameter/2, base_thickness + frame_height + 10)

pocket = Pos(0, 0, base_thickness + frame_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "frame_with_rib_and_pocket"
export_step(part, "output.step")