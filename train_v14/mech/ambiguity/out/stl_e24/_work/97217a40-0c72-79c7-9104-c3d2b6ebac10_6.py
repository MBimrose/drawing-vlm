from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 6.0
rib_width = 10.0
rib_length = plate_length - 2.0
hole_diameter = 12.0
mount_hole_diameter = 5.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0
chamfer_distance = 1.0
shell_thickness = 2.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, plate_thickness + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = base + rib

solid_body = solid_body - Pos(0, 0, (plate_thickness + rib_height)/2) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, (plate_thickness + rib_height)/2) * Cylinder(mount_hole_diameter/2, plate_thickness + rib_height + 10)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-shell_thickness, openings=[bottom_face])

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")