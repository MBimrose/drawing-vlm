from build123d import *

base_length = 80.0
base_width = 80.0
base_thickness = 5.0
frame_height = 6.0
frame_wall_thickness = 4.0
frame_outer_length = base_length
frame_outer_width = base_width
frame_inner_length = base_length - 2 * frame_wall_thickness
frame_inner_width = base_width - 2 * frame_wall_thickness
hole_diameter = 5.0
hole_depth = base_thickness + frame_height - 2.0
hole_spacing_x = 18.0
hole_spacing_y = 18.0
chamfer_size = 0.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
frame = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer_length, frame_outer_width, frame_height)
inner_cut = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_inner_length, frame_inner_width, frame_height)
result = base + frame - inner_cut

hole_positions = [
    (-hole_spacing_x, -hole_spacing_y),
    (0, -hole_spacing_y),
    (hole_spacing_x, -hole_spacing_y),
    (-hole_spacing_x, 0),
    (0, 0),
    (hole_spacing_x, 0),
    (-hole_spacing_x, hole_spacing_y),
    (0, hole_spacing_y),
    (hole_spacing_x, hole_spacing_y),
]

for x, y in hole_positions:
    result = result - Pos(x, y, base_thickness + frame_height - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")