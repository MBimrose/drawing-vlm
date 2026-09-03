from build123d import *
import math

outer_radius = 45.0
plate_thickness = 5.0
central_hole_dia = 9.0
rib_inner_radius = 15.0
rib_outer_radius = 22.5
rib_height = 2.0
slot_width = 6.0
slot_length = 20.0
slot_offset = 30.0
mount_hole_dia = 5.0
mount_hole_radius = 30.0
chamfer_size = 0.6

base_plate = Cylinder(outer_radius, plate_thickness)
rib = Cylinder(rib_outer_radius, rib_height) - Cylinder(rib_inner_radius, rib_height)
result = base_plate + rib

result = result - Cylinder(central_hole_dia / 2, plate_thickness * 2)

slot = Pos(slot_offset, 0, 0) * Box(slot_width, slot_length, plate_thickness * 2)
result = result - slot

for i in range(2):
    angle = math.radians(i * 120)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    result = result - Pos(px, py, 0) * Cylinder(mount_hole_dia / 2, plate_thickness * 2)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "flanged_plate_with_rib"
export_step(part, "output.step")