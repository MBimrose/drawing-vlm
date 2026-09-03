from build123d import *

outer_width = 80.0
outer_depth = 60.0
outer_height = 30.0
wall_thickness = 2.0
pocket_width = 40.0
pocket_depth = 30.0
pocket_height = 10.0
front_chamfer = 1.0
mount_hole_diameter = 3.0
mount_hole_spacing = 20.0
mount_hole_offset = 5.0
rib_thickness = 2.0
rib_height = outer_height - 2 * wall_thickness
rib_count = 3
rib_spacing = (outer_width - 2 * wall_thickness) / (rib_count + 1)

solid = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)
bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = offset(solid, amount=-wall_thickness, openings=[bottom_face])

pocket = Pos(0, 0, outer_height - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid = solid - pocket

front_face = solid.faces().sort_by(Axis.Y)[-1]
solid = chamfer(front_face.edges(), front_chamfer)

hole_r = mount_hole_diameter / 2
for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    z = outer_height/2 + mount_hole_offset
    hole = Pos(outer_width/2, y, z) * Rot(0, 90, 0) * Cylinder(hole_r, outer_width)
    solid = solid - hole

for i in range(rib_count):
    x = (i - (rib_count-1)/2) * rib_spacing
    rib = Pos(x, 0, wall_thickness + rib_height/2) * Box(rib_thickness, outer_depth - 2*wall_thickness, rib_height)
    solid = solid + rib

part = solid
part.name = "hollow_box_with_pocket_ribs"
export_step(part, "output.step")