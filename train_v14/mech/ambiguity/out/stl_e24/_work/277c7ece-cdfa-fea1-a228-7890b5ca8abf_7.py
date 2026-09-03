from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 6.0
frame_height = 8.0
frame_thickness = 4.0
fillet_radius = 2.0
inner_fillet_radius = 1.5
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

frame_outer = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_thickness, base_width - 2*frame_thickness, frame_height)
frame = frame_outer - frame_inner

result = base + frame
result = fillet(result.edges().filter_by(Axis.Z), inner_fillet_radius)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, 30)

part = result
part.name = "base_with_frame_and_holes"
export_step(part, "output.step")