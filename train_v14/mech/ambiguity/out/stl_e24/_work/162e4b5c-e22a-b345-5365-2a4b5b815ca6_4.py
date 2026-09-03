from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
bearing_diameter = 20.0
bearing_depth = 8.0
bearing_offset = 10.0
split_gap = 0.5
chamfer_distance = 1.0
mount_hole_diameter = 4.0
mount_hole_spacing = 15.0
mount_hole_offset = 20.0
rib_height = 4.0
rib_thickness = 2.0
rib_offset = 5.0

solid_body = Pos(0, 0, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)

bearing_x = arm_length/2 - bearing_offset
bearing_cut = Pos(bearing_x, 0, bearing_depth/2) * Cylinder(bearing_diameter/2, bearing_depth)
solid_body = solid_body - bearing_cut

hole_x = -arm_length/2 + mount_hole_offset
for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(hole_x, y, arm_thickness/2) * Cylinder(mount_hole_diameter/2, arm_thickness)
    solid_body = solid_body - hole

rib_x = -arm_length/2 + rib_offset + rib_thickness/2
rib = Pos(rib_x, 0, rib_height/2) * Box(rib_thickness, arm_width - 2*rib_offset, rib_height)
solid_body = solid_body + rib

left_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
solid_body = chamfer(left_edges, chamfer_distance)

split_cut = Pos(0, 0, arm_thickness/4) * Box(split_gap, arm_width, arm_thickness/2)
solid_body = solid_body - split_cut

part = solid_body
part.name = "arm_with_bearing_and_rib"
export_step(part, "output.step")