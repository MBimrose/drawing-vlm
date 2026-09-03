from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
rib_height = 4.0
rib_thickness = 4.0
rib_spacing = 10.0
hole_diameter = 8.0
hole_offset = 10.0
chamfer_size = 1.0
fillet_radius = 0.8
mount_hole_diameter = 4.0
mount_hole_spacing = 25.0

solid_body = Box(arm_length, arm_width, arm_thickness)

rib1 = Pos(0, rib_spacing/2 + rib_thickness/2, arm_thickness/2 + rib_height/2) * Box(arm_length - 2*hole_offset, rib_thickness, rib_height)
rib2 = Pos(0, -(rib_spacing/2 + rib_thickness/2), arm_thickness/2 + rib_height/2) * Box(arm_length - 2*hole_offset, rib_thickness, rib_height)
solid_body = solid_body + rib1 + rib2

hole_center_x = arm_length/2 - hole_offset
solid_body = solid_body - Pos(hole_center_x, 0, 0) * Cylinder(hole_diameter/2, arm_thickness + rib_height + 20)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, arm_width + 20)

min_x_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = chamfer(min_x_face.edges(), chamfer_size)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "arm_with_ribs"
export_step(part, "output.step")