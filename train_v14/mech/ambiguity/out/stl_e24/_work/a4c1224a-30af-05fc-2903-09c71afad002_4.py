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
chamfer_distance = 0.5
rib_width = 20.0
rib_length = 30.0
rib_thickness = 2.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

frame = Pos(0, 0, base_thickness + frame_height/2) * (Cylinder(frame_outer_radius, frame_height) - Cylinder(frame_inner_radius, frame_height))

rib = Pos(0, 0, rib_thickness/2) * Box(rib_width, rib_length, rib_thickness)

result = base + frame + rib

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    ( hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2,  hole_spacing_y/2),
    ( hole_spacing_x/2,  hole_spacing_y/2),
]
for x, y in hole_positions:
    result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, 100)

part = result
part.name = "base_with_frame_rib_and_holes"
export_step(part, "output.step")