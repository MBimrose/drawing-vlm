from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 76.0
height = 30.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
central_hole_diameter = 20.0
groove_width = 4.0
groove_depth = 2.0
chamfer_distance = 0.5
mount_hole_diameter = 3.0
mount_hole_count = 4
mount_hole_radius = outer_diameter / 2.0 - wall_thickness / 2.0
slot_width = 10.0
slot_height = 12.0
slot_depth = wall_thickness + 0.5
rib_thickness = 2.0
rib_width = outer_diameter - 2 * wall_thickness
rib_height = height - 4.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Pos(0, 0, height / 2) * Cylinder(outer_radius, height)
result = result - Pos(0, 0, height / 2) * Cylinder(inner_radius, height)
result = result - Pos(0, 0, height / 2) * Cylinder(central_hole_diameter / 2, height)

groove = Pos(0, 0, height - groove_depth / 2) * Cylinder(inner_radius - groove_width / 2, groove_depth)
result = result - groove

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    hole = Pos(px, py, height / 2) * Rot(0, 0, angle) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, outer_diameter)
    result = result - hole

slot = Pos(0, outer_radius - slot_depth / 2, height / 4) * Box(slot_width, slot_depth, slot_height)
result = result - slot

rib = Pos(0, outer_radius + rib_thickness / 2, 0) * Box(rib_width, rib_thickness, rib_height)
result = result + rib

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "hollow_cylinder_with_mounts"
export_step(part, "output.step")