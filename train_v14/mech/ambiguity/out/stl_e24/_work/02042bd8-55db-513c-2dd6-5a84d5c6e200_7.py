from build123d import *

outer_width = 80.0
outer_depth = 60.0
outer_height = 30.0
wall_thickness = 2.0
pocket_width = 40.0
pocket_depth = 30.0
pocket_depth_height = 10.0
chamfer_size = 1.0
mount_hole_diameter = 4.0
mount_hole_spacing = 40.0
mount_hole_offset = 5.0
rib_width = 10.0
rib_height = 10.0
rib_thickness = 4.0
vent_diameter = 12.0
vent_offset = 10.0

solid = Box(outer_width, outer_depth, outer_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = offset(solid, amount=-wall_thickness, openings=[top_face])

pocket_cut = Pos(0, 0, outer_height/2 - pocket_depth_height/2) * Box(pocket_width, pocket_depth, pocket_depth_height)
solid = solid - pocket_cut

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, -outer_height/2 + wall_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid = solid + rib

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(-outer_width/2, y, -outer_height/2 + mount_hole_offset) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_width)
    solid = solid - hole

for x in [-outer_width/2 + vent_offset, outer_width/2 - vent_offset]:
    vent = Pos(x, 0, 0) * Cylinder(vent_diameter/2, outer_height)
    solid = solid - vent

part = solid
part.name = "hollow_box_with_pocket_ribs_and_holes"
export_step(part, "output.step")