from build123d import *

plate_length = 80.0
plate_width = 80.0
plate_thickness = 5.0
rib_height = 6.0
rib_thickness = 4.0
hole_diameter = 5.0
hole_spacing = 18.0
chamfer_distance = 0.5

base = Box(plate_length, plate_width, plate_thickness)
rib_outer = Box(plate_length, plate_width, rib_height)
rib_inner = Box(plate_length - 2 * rib_thickness, plate_width - 2 * rib_thickness, rib_height)
rib = Pos(0, 0, plate_thickness / 2 + rib_height / 2) * (rib_outer - rib_inner)
solid_body = base + rib

for i in range(3):
    for j in range(3):
        x = (i - 1) * hole_spacing
        y = (j - 1) * hole_spacing
        solid_body = solid_body - Pos(x, y, plate_thickness / 2 + rib_height / 2) * Cylinder(hole_diameter / 2, plate_thickness + rib_height + 1)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")