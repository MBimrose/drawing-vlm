from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
housing_height = 55.0
rib_count = 12
rib_width = 8.0
rib_height = housing_height - 10.0
rib_thickness = 4.0
vent_slot_width = 12.0
vent_slot_length = 30.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0
chamfer_distance = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, housing_height) - Cylinder(inner_radius, housing_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

vent_cut = Pos(0, 0, housing_height - wall_thickness / 2) * Box(vent_slot_length, vent_slot_width, wall_thickness)
solid_body = solid_body - vent_cut

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius - rib_thickness / 2.0, 0, rib_height / 2.0) * Box(rib_thickness, rib_width, rib_height)
    solid_body = solid_body + rib

for x, y in [(-mount_hole_spacing / 2, -mount_hole_spacing / 2),
             (mount_hole_spacing / 2, -mount_hole_spacing / 2),
             (-mount_hole_spacing / 2, mount_hole_spacing / 2),
             (mount_hole_spacing / 2, mount_hole_spacing / 2)]:
    solid_body = solid_body - Pos(x, y, housing_height / 2) * Cylinder(mount_hole_diameter / 2, housing_height)

part = solid_body
part.name = "ribbed_housing_with_vent"
export_step(part, "output.step")