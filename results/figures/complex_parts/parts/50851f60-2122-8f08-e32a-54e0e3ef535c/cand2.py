from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 30.0
height = 20.0
groove_width = 12.0
groove_depth = 4.0
set_screw_diameter = 4.0
set_screw_depth = 8.0
chamfer_size = 1.0
slot_width = 8.0
slot_length = 40.0
slot_depth = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

groove = Pos(0, 0, height/2 - groove_depth/2) * Cylinder(outer_radius - groove_width/2, groove_depth)
solid_body = solid_body - groove

slot = Pos(0, 0, height/2 - slot_depth/2) * Box(slot_length, slot_width, slot_depth)
solid_body = solid_body - slot

for i in range(4):
    angle = math.radians(i * 90)
    px = (outer_radius - set_screw_depth/2) * math.cos(angle)
    py = (outer_radius - set_screw_depth/2) * math.sin(angle)
    hole = Pos(px, py, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
    solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "grooved_ring_with_slot"
export_step(part, "output.step")