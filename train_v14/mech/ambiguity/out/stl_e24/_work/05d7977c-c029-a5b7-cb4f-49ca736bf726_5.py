from build123d import *

base_length = 60.0
base_width = 40.0
base_thickness = 8.0
boss_diameter = 20.0
boss_height = 12.0
fillet_radius = 2.0
chamfer_distance = 0.5
hole_diameter = 6.0
hole_offset = 15.0
rib_width = 4.0
rib_height = 6.0
rib_thickness = 2.0
rib_offset = 10.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
boss = Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

hole_positions = [
    (hole_offset, hole_offset),
    (-hole_offset, hole_offset),
    (-hole_offset, -hole_offset),
    (hole_offset, -hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

rib1 = Pos(-base_length/2 + rib_offset, 0, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
rib2 = Pos(base_length/2 - rib_offset, 0, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
result = result + rib1 + rib2

part = result
part.name = "base_with_boss_ribs"
export_step(part, "output.step")