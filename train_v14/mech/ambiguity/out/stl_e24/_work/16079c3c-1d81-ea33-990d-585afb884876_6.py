from build123d import *

length = 80.0
width = 30.0
thickness = 6.0
fillet_radius = 1.0
chamfer_distance = 0.7
hole_diameter = 4.0
hole_offset = 10.0
pocket_width = 12.0
pocket_height = 20.0
pocket_depth = 4.0
boss_diameter = 12.0
boss_height = 2.0
rib_width = 4.0
rib_height = 2.0

solid_body = Box(width, thickness, length)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Y), chamfer_distance)

for x_pos in [-length/2 + hole_offset, length/2 - hole_offset]:
    solid_body = solid_body - Pos(x_pos, 0, 0) * Cylinder(hole_diameter/2, length + 10)

solid_body = solid_body - Pos(0, thickness/2 - pocket_depth/2, 0) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body + Pos(0, thickness/2 + boss_height/2, -length/2 + boss_diameter/2) * Rot(90, 0, 0) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + Pos(0, -thickness/2 + rib_height/2, 0) * Box(rib_width, rib_height, length)

part = solid_body
part.name = "plate_with_features"
export_step(part, "output.step")