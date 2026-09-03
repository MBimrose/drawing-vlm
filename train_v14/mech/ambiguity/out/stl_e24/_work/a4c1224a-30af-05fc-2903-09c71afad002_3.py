from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_outer_radius = 30.0
frame_inner_radius = 25.0
frame_height = 8.0
hole_diameter = 4.0
hole_spacing_x = 40.0
hole_spacing_y = 30.0
chamfer_size = 0.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

frame_outer = Pos(0, 0, base_thickness + frame_height/2) * Cylinder(frame_outer_radius, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height/2) * Cylinder(frame_inner_radius, frame_height)
frame = frame_outer - frame_inner

result = base + frame

hole_r = hole_diameter / 2
hole_h = base_thickness + frame_height + 2
for x in [-hole_spacing_x/2, hole_spacing_x/2]:
    for y in [-hole_spacing_y/2, hole_spacing_y/2]:
        result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_r, hole_h)

part = result
part.name = "base_with_frame_and_holes"
export_step(part, "output.step")