from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
length = 60.0
groove_width = 6.0
groove_depth = 3.0
keyway_width = 20.0
keyway_depth = 10.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
central_hole_diameter = 10.0
chamfer_size = 1.0
rib_thickness = 2.0
rib_height = 10.0
rib_count = 6

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Pos(0, 0, length/2) * Cylinder(outer_radius, length)
solid_body = solid_body - Pos(0, 0, length/2) * Cylinder(inner_radius, length)

groove = Pos(0, 0, length - groove_depth/2) * Cylinder(inner_radius - groove_width/2, groove_depth)
solid_body = solid_body - groove

keyway = Pos(outer_radius - keyway_depth/2, 0, 0) * Box(keyway_depth, keyway_width, wall_thickness)
solid_body = solid_body - keyway

solid_body = solid_body - Pos(0, 0, length/2) * Cylinder(central_hole_diameter/2, length)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, length/2) * Cylinder(mount_hole_diameter/2, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
    solid_body = solid_body - rib

part = solid_body
part.name = "hollow_cylinder_with_groove_keyway_and_ribs"
export_step(part, "output.step")