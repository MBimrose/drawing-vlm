from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 8.0
corner_fillet_radius = 3.0
recess_diameter = 30.0
recess_depth = 2.0
hole_diameter = 8.0
hole_spacing_x = 30.0
hole_spacing_y = 24.0
rib_width = 10.0
rib_height = 30.0
rib_thickness = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

solid_body = solid_body - Pos(0, 0, plate_thickness - recess_depth/2) * Cylinder(recess_diameter/2, recess_depth)

for x, y in [(-hole_spacing_x/2, -hole_spacing_y/2), (hole_spacing_x/2, -hole_spacing_y/2),
             (-hole_spacing_x/2, hole_spacing_y/2), (hole_spacing_x/2, hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

rib = Pos(0, 0, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_rib"
export_step(part, "output.step")