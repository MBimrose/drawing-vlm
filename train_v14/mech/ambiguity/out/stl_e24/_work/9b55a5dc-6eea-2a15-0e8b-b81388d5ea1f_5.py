from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 12.0
cavity_diameter = 30.0
cavity_depth = 6.0
mount_hole_diameter = 4.0
mount_hole_offset = 15.0
counterbore_diameter = 6.0
counterbore_depth = 4.0
fillet_radius = 3.0
chamfer_size = 0.8

solid_body = Box(plate_length, plate_width, plate_thickness)

cavity = Pos(0, 0, plate_thickness/2 - cavity_depth/2) * Cylinder(cavity_diameter/2, cavity_depth)
solid_body = solid_body - cavity

hole_x = plate_length/2 - mount_hole_offset
hole_y = plate_width/2 - mount_hole_offset
for x in [-hole_x, hole_x]:
    for y in [-hole_y, hole_y]:
        cbore = Pos(x, y, plate_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
        shaft = Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)
        solid_body = solid_body - cbore - shaft

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "plate_with_cavity_and_mounting_holes"
export_step(part, "output.step")