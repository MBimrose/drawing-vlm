from build123d import *
import math

outer_diameter = 80.0
cap_height = 30.0
wall_thickness = 2.0
groove_width = 6.0
groove_depth = 1.5
vent_hole_diameter = 5.0
vent_hole_count = 4
vent_hole_offset = 5.0
rib_thickness = 4.0
rib_height = 10.0
rib_count = 8
chamfer_distance = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
groove_outer_radius = outer_radius - wall_thickness / 2.0
groove_inner_radius = groove_outer_radius - groove_width

solid_body = Cylinder(outer_radius, cap_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove_z = cap_height - groove_depth / 2
groove_cut = Pos(0, 0, groove_z) * (Cylinder(groove_outer_radius, groove_depth) - Cylinder(groove_inner_radius, groove_depth))
solid_body = solid_body - groove_cut

vent_radius = vent_hole_diameter / 2.0
vent_r = outer_radius - wall_thickness / 2.0 - vent_hole_offset
for i in range(vent_hole_count):
    a = math.radians(i * 360.0 / vent_hole_count)
    vent_cut = Pos(vent_r * math.cos(a), vent_r * math.sin(a), cap_height / 2) * Rot(0, 90, math.degrees(a)) * Cylinder(vent_radius, wall_thickness + 0.1)
    solid_body = solid_body - vent_cut

rib_r = inner_radius - rib_thickness / 2.0
for i in range(rib_count):
    a = math.radians(i * 360.0 / rib_count)
    rib = Pos(rib_r * math.cos(a), rib_r * math.sin(a), cap_height / 2) * Rot(0, 0, math.degrees(a)) * Box(rib_thickness, rib_height, wall_thickness)
    solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "hollow_cap_with_groove_vents_ribs"
export_step(part, "output.step")