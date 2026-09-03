from build123d import *

base_radius = 30.0
base_height = 15.0
shoulder_radius = 20.0
shoulder_height = 15.0
boss_radius = 12.0
boss_height = 20.0
fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0
pocket_width = 10.0
pocket_depth = 8.0
pocket_length = 30.0

base = Pos(0, 0, base_height/2) * Cylinder(base_radius, base_height)
shoulder = Pos(0, 0, base_height + shoulder_height/2) * Cylinder(shoulder_radius, shoulder_height)
boss = Pos(0, 0, base_height + shoulder_height + boss_height/2) * Cylinder(boss_radius, boss_height)

solid_body = base + shoulder + boss

shoulder_edges = [e for e in solid_body.edges() if abs(e.center().Z - base_height) < 0.1]
solid_body = fillet(shoulder_edges, fillet_radius)

boss_edges = [e for e in solid_body.edges() if abs(e.center().Z - (base_height + shoulder_height)) < 0.1]
solid_body = fillet(boss_edges, fillet_radius)

hole_h = base_height + shoulder_height + boss_height + 10
for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(0, y, hole_h/2) * Cylinder(mount_hole_diameter/2, hole_h)

pocket = Pos(shoulder_radius - pocket_depth/2, 0, base_height + shoulder_height/2) * Box(pocket_depth, pocket_width, pocket_length)
solid_body = solid_body - pocket

part = solid_body
part.name = "stepped_cylinder_with_holes_and_pocket"
export_step(part, "output.step")