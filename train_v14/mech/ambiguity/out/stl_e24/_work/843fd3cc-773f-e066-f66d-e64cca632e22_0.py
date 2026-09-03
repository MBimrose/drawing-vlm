from build123d import *
import math

outer_radius = 45.0
plate_thickness = 5.0
central_hole_diameter = 9.0
slot_width = 6.0
slot_length = 20.0
slot_center_radius = 30.0
mount_hole_diameter = 5.0
mount_hole_radius = 35.0
mount_hole_count = 3
chamfer_distance = 0.6
boss_radius = 10.0
boss_height = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = solid_body + Pos(0, 0, boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Cylinder(central_hole_diameter/2, plate_thickness + 1)
solid_body = solid_body - Pos(slot_center_radius, 0, plate_thickness/2) * Box(slot_width, slot_length, plate_thickness + 1)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")