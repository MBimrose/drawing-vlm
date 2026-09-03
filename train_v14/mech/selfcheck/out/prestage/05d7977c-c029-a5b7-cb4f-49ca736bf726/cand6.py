from build123d import *

base_width = 60.0
base_length = 40.0
base_thickness = 8.0
boss_diameter = 20.0
boss_height = 12.0
hole_diameter = 6.0
hole_offset = 15.0
fillet_radius = 2.0
chamfer_distance = 0.5
rib_width = 5.0
rib_height = 4.0
rib_spacing = 20.0
pocket_width = 12.0
pocket_length = 8.0
pocket_depth = 2.0

solid = Pos(0, 0, base_thickness/2) * Box(base_width, base_length, base_thickness)
solid = solid + Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)

for x, y in [(hole_offset, hole_offset), (-hole_offset, hole_offset), (hole_offset, -hole_offset), (-hole_offset, -hole_offset)]:
    solid = solid - Pos(x, y, boss_height/2) * Cylinder(hole_diameter/2, boss_height + 10)

solid = solid - Pos(0, 0, boss_height - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)

rib = Box(rib_width, base_length - 2*rib_spacing, rib_height)
solid = solid + Pos(-base_width/2 + rib_spacing, 0, rib_height/2) * rib
solid = solid + Pos(base_width/2 - rib_spacing, 0, rib_height/2) * rib

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_distance)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = fillet(top_face.edges(), fillet_radius)

part = solid
part.name = "base_plate_with_boss"
export_step(part, "output.step")