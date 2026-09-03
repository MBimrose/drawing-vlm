from build123d import *

length = 80.0
width = 30.0
thickness = 6.0
fillet_radius = 1.0
chamfer_dist = 0.7
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset = 10.0
boss_diameter = 12.0
boss_height = 2.0

solid_body = Pos(0, 0, length/2) * Box(width, thickness, length)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Y), chamfer_dist)

hole_positions = [hole_offset + i * hole_spacing for i in range(4)]
for x in hole_positions:
    solid_body = solid_body - Pos(x, 0, length/2) * Cylinder(hole_diameter/2, length + 10)

boss = Pos(0, thickness/2 + boss_height/2, 0) * Rot(90, 0, 0) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "bar_with_holes_and_boss"
export_step(part, "output.step")