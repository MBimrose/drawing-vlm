from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_height = 8.0
frame_thickness = 4.0
pocket_margin = 6.0
pocket_depth = 3.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
fillet_radius_outer = 2.0
fillet_radius_inner = 1.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius_outer)

frame_outer = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_thickness, base_width - 2*frame_thickness, frame_height)
frame = frame_outer - frame_inner
frame = fillet(frame.edges().filter_by(Axis.Z), fillet_radius_inner)

result = base + frame

pocket_w = base_length - 2*frame_thickness - pocket_margin
pocket_h = base_width - 2*frame_thickness - pocket_margin
pocket = Pos(0, 0, base_thickness + frame_height - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)
result = result - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        hole = Pos(x, y, base_thickness + frame_height/2) * Cylinder(hole_diameter/2, base_thickness + frame_height + 10)
        result = result - hole

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")