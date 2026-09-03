from build123d import *

outer_width = 80.0
outer_length = 60.0
outer_height = 12.0
wall_thickness = 2.0
boss_diameter = 20.0
boss_height = 8.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 4.0
hole_diameter = 3.0
hole_offset = 10.0
fillet_radius = 1.5
chamfer_distance = 1.0

base = Box(outer_width, outer_length, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

boss = Pos(0, 0, outer_height/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
base = base + boss

pocket = Pos(0, 0, outer_height/2 + boss_height - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
base = base - pocket

hole_r = hole_diameter / 2
hole_h = outer_height + boss_height + 10
for x in [-(outer_width/2 - hole_offset), outer_width/2 - hole_offset]:
    for y in [-(outer_length/2 - hole_offset), outer_length/2 - hole_offset]:
        base = base - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

bottom_face = base.faces().sort_by(Axis.Z)[0]
base = chamfer(bottom_face.edges(), chamfer_distance)

part = base
part.name = "shelled_box_with_boss_pocket_holes"
export_step(part, "output.step")