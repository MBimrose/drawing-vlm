from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_outer_length = 70.0
frame_outer_width = 50.0
frame_height = 12.0
frame_wall_thickness = 4.0
chamfer_size = 1.0
hole_diameter = 4.0
hole_rows = 3
hole_cols = 4
hole_margin = 6.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

frame = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer_length, frame_outer_width, frame_height)
result = base + frame

inner_cut = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer_length - 2*frame_wall_thickness, frame_outer_width - 2*frame_wall_thickness, frame_height)
result = result - inner_cut

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

x_start = -base_length/2 + hole_margin
x_end = base_length/2 - hole_margin
y_start = -base_width/2 + hole_margin
y_end = base_width/2 - hole_margin
x_spacing = (x_end - x_start) / (hole_cols - 1)
y_spacing = (y_end - y_start) / (hole_rows - 1)

total_height = base_thickness + frame_height
for i in range(hole_cols):
    for j in range(hole_rows):
        x = x_start + i * x_spacing
        y = y_start + j * y_spacing
        result = result - Pos(x, y, total_height/2) * Cylinder(hole_diameter/2, total_height)

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")