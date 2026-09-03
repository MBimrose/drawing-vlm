from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
rib_width = 5.0
rib_height = 7.0
hole_diameter = 4.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = (plate_length - 2 * rib_width) / (hole_cols + 1)
hole_spacing_y = (plate_width - 2 * rib_width) / (hole_rows + 1)
reinforcement_thickness = 4.0
reinforcement_height = 5.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, plate_thickness + rib_height/2) * (Box(plate_length, plate_width, rib_height) - Box(plate_length - 2*rib_width, plate_width - 2*rib_width, rib_height))
reinforcement = Pos(0, 0, plate_thickness + reinforcement_height/2) * Box(plate_length - 2*rib_width, reinforcement_thickness, reinforcement_height)

solid_body = base + rib + reinforcement

hole_r = hole_diameter / 2
hole_h = plate_thickness + rib_height + 10
hole_z = (plate_thickness + rib_height) / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, hole_z) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")