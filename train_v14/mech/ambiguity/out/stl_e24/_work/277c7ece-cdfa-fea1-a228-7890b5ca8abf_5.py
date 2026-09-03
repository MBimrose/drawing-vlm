from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 8.0
frame_height = 6.0
frame_wall_thickness = 4.0
pocket_margin = 5.0
pocket_depth = 3.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
num_holes_x = 3
num_holes_y = 2
rib_thickness = 3.0
rib_width = 6.0
rib_height = 4.0
fillet_radius_outer = 2.0
fillet_radius_inner = 1.5

result = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius_outer)

frame = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
result = result + frame
inner_cut = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_wall_thickness, base_width - 2*frame_wall_thickness, frame_height)
result = result - inner_cut
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius_inner)

pocket = Pos(0, 0, base_thickness + frame_height - pocket_depth/2) * Box(base_length - 2*pocket_margin, base_width - 2*pocket_margin, pocket_depth)
result = result - pocket

for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = (i - (num_holes_x-1)/2) * hole_spacing_x
        y = (j - (num_holes_y-1)/2) * hole_spacing_y
        hole = Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, base_thickness + frame_height + 20)
        result = result - hole

rib1 = Pos(-base_length/4, 0, rib_height/2) * Box(rib_thickness, rib_width, rib_height)
rib2 = Pos(base_length/4, 0, rib_height/2) * Box(rib_thickness, rib_width, rib_height)
result = result + rib1 + rib2

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")