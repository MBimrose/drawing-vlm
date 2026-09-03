from build123d import *
import math

outer_radius = 45.0
plate_thickness = 5.0
boss_radius = 15.0
boss_height = 2.0
central_hole_diameter = 9.0
slot_width = 6.0
slot_length = 20.0
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_radius = outer_radius - 12.0
rib_width = 10.0
rib_height = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=plate_thickness)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Cylinder(central_hole_diameter/2, plate_thickness + 1)

slot_center_x = outer_radius - slot_length / 2.0
solid_body = solid_body - Pos(slot_center_x, 0, plate_thickness/2) * Box(slot_width, slot_length, plate_thickness + 1)

solid_body = solid_body + Pos(0, 0, boss_height/2) * Cylinder(boss_radius, boss_height)

rib_center_x = (boss_radius + outer_radius) / 2.0
rib_length = outer_radius - boss_radius
solid_body = solid_body + Pos(rib_center_x, 0, rib_height/2) * Box(rib_width, rib_length, rib_height)

for i in range(3):
    angle = math.radians(i * 120.0)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_boss_and_rib"
export_step(part, "output.step")