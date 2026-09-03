from build123d import *

base_width = 60.0
base_depth = 30.0
base_thickness = 8.0
base_fillet = 1.5
shaft_radius = 5.0
shaft_length = 30.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_rows = 2
hole_columns = 3

base = Box(base_width, base_depth, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), base_fillet)

shaft = Pos(0, 0, base_thickness/2 + shaft_length/2) * Cylinder(shaft_radius, shaft_length)
solid_body = base + shaft

hole_r = hole_diameter / 2
hole_h = base_thickness + shaft_length + 20
hole_z = base_thickness/2 + shaft_length/2
for i in range(hole_columns):
    for j in range(hole_rows):
        x = (i - (hole_columns-1)/2) * hole_spacing
        y = (j - (hole_rows-1)/2) * hole_spacing
        solid_body = solid_body - Pos(x, y, hole_z) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "base_with_shaft_and_holes"
export_step(part, "output.step")