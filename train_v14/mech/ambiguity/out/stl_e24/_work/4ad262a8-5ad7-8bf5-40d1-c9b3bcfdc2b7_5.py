from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 6.0
frame_height = 7.0
frame_thickness = 5.0
rib_width = 5.0
rib_height = 4.0
hole_diameter = 4.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = 18.0
hole_spacing_y = 34.0
chamfer_size = 0.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)

frame_outer = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_thickness, base_width - 2*frame_thickness, frame_height)
frame = frame_outer - frame_inner

rib = Pos(0, 0, base_thickness + rib_height/2) * Box(base_length - 2*frame_thickness, rib_width, rib_height)

solid_body = base + frame + rib

start_x = -((hole_cols - 1) * hole_spacing_x) / 2
start_y = -((hole_rows - 1) * hole_spacing_y) / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        px = start_x + i * hole_spacing_x
        py = start_y + j * hole_spacing_y
        solid_body = solid_body - Pos(px, py, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, 30)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "base_plate_with_frame"
export_step(part, "output.step")