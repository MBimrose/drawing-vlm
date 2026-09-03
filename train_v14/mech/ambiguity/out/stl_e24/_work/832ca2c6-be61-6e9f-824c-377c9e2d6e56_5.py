from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_height = 10.0
frame_wall_thickness = 4.0
hole_diameter = 5.5
hole_spacing_x = 30.0
hole_spacing_y = 20.0
chamfer_size = 0.8

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
frame_outer = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_wall_thickness, base_width - 2*frame_wall_thickness, frame_height)

result = base + frame_outer - frame_inner

hole_positions = [
    (-hole_spacing_x, -hole_spacing_y),
    (0, -hole_spacing_y),
    (hole_spacing_x, -hole_spacing_y),
    (-hole_spacing_x, hole_spacing_y),
    (0, hole_spacing_y),
    (hole_spacing_x, hole_spacing_y),
]

for x, y in hole_positions:
    result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, base_thickness + frame_height + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")