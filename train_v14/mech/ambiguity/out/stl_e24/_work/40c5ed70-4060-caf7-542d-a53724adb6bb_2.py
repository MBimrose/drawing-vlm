from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 3.0
pocket_length = 60.0
pocket_width = 30.0
pocket_depth = 12.0
chamfer_distance = 2.0
mount_hole_dia = 4.0
mount_hole_spacing = 30.0

solid = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = offset(solid, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid = solid - pocket

hole_r = mount_hole_dia / 2
hole_h = outer_length + 10
for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid = solid - Pos(outer_length/2, y, outer_height/2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
    solid = solid - Pos(-outer_length/2, y, outer_height/2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)

bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = chamfer(bottom_face.edges(), chamfer_distance)

part = solid
part.name = "hollow_box_with_pocket"
export_step(part, "output.step")