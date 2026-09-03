from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_outer_length = 70.0
frame_outer_width = 50.0
frame_height = 12.0
frame_wall_thickness = 5.0
inner_length = frame_outer_length - 2 * frame_wall_thickness
inner_width = frame_outer_width - 2 * frame_wall_thickness
hole_diameter = 4.0
hole_spacing = 6.0
hole_count = 9
chamfer_size = 0.8
fillet_radius = 1.2

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), 1.2)

frame = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer_length, frame_outer_width, frame_height)
result = base + frame

inner_cut = Pos(0, 0, base_thickness + frame_height/2) * Box(inner_length, inner_width, frame_height)
result = result - inner_cut

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    hole = Pos(x, 0, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, 30)
    result = result - hole

part = result
part.name = "base_with_frame_and_holes"
export_step(part, "output.step")