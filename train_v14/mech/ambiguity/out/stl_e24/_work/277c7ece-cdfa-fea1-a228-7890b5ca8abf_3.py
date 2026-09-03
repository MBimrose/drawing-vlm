from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 6.0
frame_height = 8.0
frame_thickness = 4.0
pocket_depth = 2.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
num_holes_x = 3
num_holes_y = 2
fillet_radius = 2.0
inner_fillet_radius = 1.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

pocket = Pos(0, 0, base_thickness - pocket_depth/2) * Box(base_length - 2*frame_thickness, base_width - 2*frame_thickness, pocket_depth)
base = base - pocket

frame = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
result = base + frame

inner_cut = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_thickness, base_width - 2*frame_thickness, frame_height)
result = result - inner_cut

result = fillet(result.edges().filter_by(Axis.Z), inner_fillet_radius)

for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = (i - (num_holes_x-1)/2) * hole_spacing_x
        y = (j - (num_holes_y-1)/2) * hole_spacing_y
        hole = Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, 30)
        result = result - hole

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")