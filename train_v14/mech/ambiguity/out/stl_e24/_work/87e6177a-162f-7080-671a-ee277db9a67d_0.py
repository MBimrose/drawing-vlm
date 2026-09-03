from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
height = 60.0
slot_width = 2.0
slot_depth = 10.0
slot_count = 8
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Pos(0, 0, height/2) * Cylinder(outer_radius, height)
solid_body = solid_body - Pos(0, 0, height/2) * Cylinder(inner_radius, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

slot_radius = outer_radius - wall_thickness/2.0
for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    slot = Pos(px, py, slot_depth/2) * Box(slot_width, wall_thickness, slot_depth)
    solid_body = solid_body - slot

part = solid_body
part.name = "hollow_cylinder_with_slots"
export_step(part, "output.step")