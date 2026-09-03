from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
thickness = 10.0
pocket_diameter = 30.0
pocket_depth = 4.0
blind_hole_diameter = 6.0
blind_hole_depth = 6.0
blind_hole_count = 6
blind_hole_radius = (outer_diameter/2 + inner_diameter/2)/2
chamfer_size = 1.5
slot_width = 5.0
slot_length = 20.0

solid_body = Cylinder(outer_diameter/2, thickness) - Cylinder(inner_diameter/2, thickness)
solid_body = chamfer(solid_body.edges(), chamfer_size)

pocket = Cylinder(pocket_diameter/2, pocket_depth)
solid_body = solid_body - Pos(0, 0, thickness - pocket_depth/2) * pocket

for i in range(blind_hole_count):
    angle = math.radians(i * 360.0 / blind_hole_count)
    px = blind_hole_radius * math.cos(angle)
    py = blind_hole_radius * math.sin(angle)
    hole = Cylinder(blind_hole_diameter/2, blind_hole_depth)
    solid_body = solid_body - Pos(px, py, thickness - blind_hole_depth/2) * hole

slot = Box(slot_length, slot_width, thickness)
solid_body = solid_body - Pos(outer_diameter/2 - slot_width/2, 0, 0) * slot

part = solid_body
part.name = "ring_with_pocket_holes_and_slot"
export_step(part, "output.step")