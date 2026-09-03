from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 5.0
hole_diameter = 12.0
hole_spacing = 60.0
mount_hole_diameter = 4.0
mount_hole_spacing = 40.0
rib_width = 10.0
rib_height = 10.0
rib_thickness = 4.0
chamfer_size = 1.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])
vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_size)

rib = Pos(0, 0, outer_height/2) * Box(rib_width, rib_thickness, rib_height)
base = base + rib

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    base = base - Pos(x, 0, outer_height/2) * Cylinder(hole_diameter/2, outer_height)

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    base = base - Pos(0, y, outer_height/4) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length)

part = base
part.name = "hollow_box_with_rib_pockets_and_holes"
export_step(part, "output.step")