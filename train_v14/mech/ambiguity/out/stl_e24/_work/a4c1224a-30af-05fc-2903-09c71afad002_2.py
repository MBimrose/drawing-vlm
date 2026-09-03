from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_outer_radius = 30.0
frame_inner_radius = 25.0
frame_height = 8.0
hole_diameter = 4.0
hole_offset_x = 20.0
hole_offset_y = 15.0
chamfer_size = 0.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
frame = Pos(0, 0, base_thickness + frame_height/2) * (Cylinder(frame_outer_radius, frame_height) - Cylinder(frame_inner_radius, frame_height))
result = base + frame

hole_r = hole_diameter / 2
hole_h = base_thickness + frame_height + 10
for x, y in [(hole_offset_x, hole_offset_y), (-hole_offset_x, hole_offset_y), (hole_offset_x, -hole_offset_y), (-hole_offset_x, -hole_offset_y)]:
    result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_r, hole_h)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "base_with_frame_and_holes"
export_step(part, "output.step")