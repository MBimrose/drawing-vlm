from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 4.0
rib_height = 2.0
rib_offset = 5.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 15.0
hole_rows = 3
hole_cols = 4
countersink_diameter = 6.0
countersink_angle = 82.0
fillet_radius = 0.8

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Pos(0, 0, plate_thickness) * Box(plate_length - 2 * rib_offset, rib_width, rib_height)
rib2 = Pos(0, 0, plate_thickness) * Box(rib_width, plate_width - 2 * rib_offset, rib_height)
solid_body = base + rib1 + rib2

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness + rib_height + 10)

solid_body = solid_body - Pos(0, 0, plate_thickness + rib_height) * CounterSinkHole(countersink_diameter / 2, countersink_diameter, plate_thickness + rib_height, countersink_angle)

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")