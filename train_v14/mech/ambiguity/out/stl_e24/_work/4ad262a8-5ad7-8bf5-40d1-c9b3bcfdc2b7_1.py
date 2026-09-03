from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
frame_height = 7.0
frame_thickness = 5.0
rib_width = 6.0
rib_height = 4.0
hole_diameter = 4.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = 18.0
hole_spacing_y = 34.0
chamfer_size = 1.0
fillet_radius = 1.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

frame_outer = Pos(0, 0, plate_thickness + frame_height/2) * Box(plate_length, plate_width, frame_height)
frame_inner = Pos(0, 0, plate_thickness + frame_height/2) * Box(plate_length - 2*frame_thickness, plate_width - 2*frame_thickness, frame_height)
frame = frame_outer - frame_inner
frame = fillet(frame.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(0, 0, plate_thickness + rib_height/2) * Box(plate_length - 2*frame_thickness, rib_width, rib_height)

result = base + frame + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)

part = result
part.name = "plate_with_frame_rib_and_holes"
export_step(part, "output.step")