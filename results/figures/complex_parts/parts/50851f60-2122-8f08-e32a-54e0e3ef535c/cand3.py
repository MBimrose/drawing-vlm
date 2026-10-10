from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 30.0
height = 20.0
groove_width = 6.0
groove_depth = 2.0
slot_width = 4.0
slot_height = 12.0
slot_count = 6
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius

result = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

groove = Pos(0, 0, height/2 - groove_depth/2) * Cylinder(inner_radius - groove_width/2, groove_depth)
result = result - groove

for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = (outer_radius - wall_thickness/2) * math.cos(angle)
    py = (outer_radius - wall_thickness/2) * math.sin(angle)
    slot = Pos(px, py, 0) * Box(wall_thickness, slot_width, slot_height)
    result = result - slot

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "hollow_cylinder_with_groove_and_slots"
export_step(part, "output.step")