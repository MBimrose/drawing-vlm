from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
frame_height = 8.0
frame_thickness = 5.0
rib_width = 10.0
rib_height = 4.0
hole_diameter = 4.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = (plate_length - 2 * frame_thickness) / (hole_cols + 1)
hole_spacing_y = (plate_width - 2 * frame_thickness) / (hole_rows + 1)

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
frame_outer = Pos(0, 0, plate_thickness + frame_height/2) * Box(plate_length, plate_width, frame_height)
frame_inner = Pos(0, 0, plate_thickness + frame_height/2) * Box(plate_length - 2*frame_thickness, plate_width - 2*frame_thickness, frame_height)
frame = frame_outer - frame_inner
rib = Pos(0, 0, plate_thickness + rib_height/2) * Box(plate_length - 2*frame_thickness, rib_width, rib_height)

solid_body = base + frame + rib

hole_radius = hole_diameter / 2
hole_height = plate_thickness + frame_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness + frame_height/2) * Cylinder(hole_radius, hole_height)

part = solid_body
part.name = "plate_with_frame_rib_and_holes"
export_step(part, "output.step")