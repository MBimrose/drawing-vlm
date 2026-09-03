from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 6.0
frame_height = 7.0
frame_wall = 5.0
rib_height = 4.0
rib_width = 6.0
hole_diameter = 4.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = (base_length - 2 * frame_wall) / (hole_cols + 1)
hole_spacing_y = (base_width - 2 * frame_wall) / (hole_rows + 1)

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
frame = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
result = base + frame

cut_box = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_wall, base_width - 2*frame_wall, frame_height)
result = result - cut_box

rib = Pos(0, 0, base_thickness + rib_height/2) * Box(base_length - 2*frame_wall, rib_width, rib_height)
result = result + rib

hole_r = hole_diameter / 2
hole_h = base_thickness + frame_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_r, hole_h)

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")