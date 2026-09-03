from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_outer_length = 70.0
frame_outer_width = 50.0
frame_height = 12.0
frame_wall_thickness = 4.0
chamfer_distance = 1.0
hole_diameter = 4.0
hole_rows = 3
hole_cols = 4
hole_margin = 6.0

inner_length = frame_outer_length - 2 * frame_wall_thickness
inner_width = frame_outer_width - 2 * frame_wall_thickness

hole_spacing_x = (base_length - 2 * hole_margin) / (hole_cols - 1)
hole_spacing_y = (base_width - 2 * hole_margin) / (hole_rows - 1)

hole_points = [
    (-base_length / 2 + hole_margin + i * hole_spacing_x,
     -base_width / 2 + hole_margin + j * hole_spacing_y)
    for i in range(hole_cols)
    for j in range(hole_rows)
]

solid = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
solid = solid + Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer_length, frame_outer_width, frame_height)
solid = solid - Pos(0, 0, base_thickness + frame_height/2) * Box(inner_length, inner_width, frame_height)
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_distance)

for x, y in hole_points:
    solid = solid - Pos(x, y, (base_thickness + frame_height)/2) * Cylinder(hole_diameter/2, base_thickness + frame_height + 10)

part = solid
part.name = "base_plate_with_frame"
export_step(part, "output.step")