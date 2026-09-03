from build123d import *

outer_diameter = 80.0
height = 60.0
wall_thickness = 6.0
rib_thickness = 2.0
rib_height = 12.0
rib_count = 12
recess_diameter = 30.0
recess_depth = 8.0
through_hole_diameter = 10.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, height - recess_depth/2) * Cylinder(recess_diameter/2, recess_depth)
solid_body = solid_body - Pos(0, 0, height/2) * Cylinder(through_hole_diameter/2, height)

rib = Pos(inner_radius - rib_thickness/2, 0, height/2) * Box(rib_thickness, rib_height, height)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    solid_body = solid_body + Rot(0, 0, angle) * rib

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")