from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 8.0
rib_height = 6.0
rib_thickness = 4.0
hole_diameter = 7.0
hole_counterbore_diameter = 10.0
hole_counterbore_depth = 2.0
hole_spacing = 60.0
blind_hole_diameter = 4.0
blind_hole_depth = 6.0
chamfer_size = 1.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, plate_width/2 + rib_height/2, plate_thickness/2) * Box(plate_length, rib_height, rib_thickness)
solid_body = base + rib

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 10)
    solid_body = solid_body - Pos(x, 0, plate_thickness - hole_counterbore_depth/2) * Cylinder(hole_counterbore_diameter/2, hole_counterbore_depth)

solid_body = solid_body - Pos(0, 0, plate_thickness - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")