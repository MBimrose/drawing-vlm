from build123d import *
import math

outer_diameter = 80.0
thickness = 10.0
central_hole_diameter = 20.0
slot_width = 6.0
slot_length = 20.0
slot_offset = 5.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
slot_center_radius = outer_radius - slot_offset - slot_width / 2.0

solid_body = Cylinder(outer_radius, thickness)
solid_body = solid_body - Cylinder(central_hole_diameter / 2, thickness)

for i in range(4):
    angle = math.radians(i * 90)
    px = slot_center_radius * math.cos(angle)
    py = slot_center_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Box(slot_width, slot_length, thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")