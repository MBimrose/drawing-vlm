from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 2.0
height = 30.0
rib_count = 8
rib_width = 4.0
rib_height = 10.0
rib_thickness = 2.0
vent_slot_width = 6.0
vent_slot_length = 30.0
vent_slot_depth = 4.0
chamfer_size = 0.5
mount_hole_dia = 5.0
mount_hole_spacing = 40.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
solid_body = chamfer(solid_body.edges(), chamfer_size)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius - rib_thickness/2, 0, height/2) * Box(rib_width, rib_height, rib_thickness)
    solid_body = solid_body + rib

vent_slot = Pos(0, outer_radius - vent_slot_depth/2, height/2) * Box(vent_slot_width, vent_slot_depth, vent_slot_length)
solid_body = solid_body - vent_slot

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, outer_radius - wall_thickness/2, height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_dia/2, wall_thickness + 0.1)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")