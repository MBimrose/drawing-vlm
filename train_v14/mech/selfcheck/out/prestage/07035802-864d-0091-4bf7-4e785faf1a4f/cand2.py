from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_outer_length = 70.0
frame_outer_width = 50.0
frame_height = 12.0
frame_wall_thickness = 4.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 6.0
hole_diameter = 4.0
hole_rows = 3
hole_cols = 4
hole_margin = 6.0
chamfer_distance = 1.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
frame = Pos(0, 0, base_thickness + frame_height/2) * Box(frame_outer_length, frame_outer_width, frame_height)
result = base + frame

inner_cut = Pos(0, 0, base_thickness + frame_height/2) * Box(
    frame_outer_length - 2*frame_wall_thickness,
    frame_outer_width - 2*frame_wall_thickness,
    frame_height
)
result = result - inner_cut

pocket = Pos(0, 0, base_thickness + frame_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

hole_spacing_x = (base_length - 2 * hole_margin) / (hole_cols - 1)
hole_spacing_y = (base_width - 2 * hole_margin) / (hole_rows - 1)
hole_r = hole_diameter / 2
hole_h = base_thickness + frame_height + 10

for i in range(hole_cols):
    for j in range(hole_rows):
        x = -base_length/2 + hole_margin + i * hole_spacing_x
        y = -base_width/2 + hole_margin + j * hole_spacing_y
        result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_r, hole_h)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")