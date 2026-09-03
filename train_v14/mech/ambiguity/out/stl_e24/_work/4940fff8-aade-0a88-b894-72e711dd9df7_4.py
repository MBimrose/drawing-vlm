from build123d import *

base_width = 80.0
base_length = 80.0
base_thickness = 5.0
frame_height = 6.0
frame_wall_thickness = 4.0
hole_diameter = 5.0
hole_spacing_x = 18.0
hole_spacing_y = 18.0
hole_rows = 3
hole_cols = 3
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 2.0
chamfer_size = 0.5

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_length, base_thickness)
frame = Pos(0, 0, base_thickness + frame_height/2) * Box(base_width, base_length, frame_height)
solid_body = base + frame

inner_cut = Pos(0, 0, base_thickness + frame_height/2) * Box(base_width - 2*frame_wall_thickness, base_length - 2*frame_wall_thickness, frame_height)
solid_body = solid_body - inner_cut

pocket = Pos(0, 0, base_thickness + frame_height - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        hole = Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, base_thickness + frame_height + 1)
        solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "base_plate_with_frame"
export_step(part, "output.step")