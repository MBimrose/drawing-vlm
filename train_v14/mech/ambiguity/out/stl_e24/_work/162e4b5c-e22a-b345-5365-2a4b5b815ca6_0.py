from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
bearing_diameter = 20.0
bearing_depth = 8.0
split_groove_width = 30.0
split_groove_depth = 2.0
mount_hole_diameter = 4.0
mount_hole_spacing = 20.0
chamfer_distance = 1.0
fillet_radius = 0.5
rib_height = 3.0
rib_width = 5.0
rib_offset = 10.0

solid_body = Box(jaw_length, jaw_width, jaw_thickness)

bearing_cut = Pos(jaw_length/2 - bearing_depth/2, 0, -jaw_thickness/2 + bearing_depth/2) * Cylinder(bearing_diameter/2, bearing_depth)
solid_body = solid_body - bearing_cut

groove_cut = Pos(0, 0, -jaw_thickness/2 + split_groove_depth/2) * Box(split_groove_depth, split_groove_width, split_groove_depth)
solid_body = solid_body - groove_cut

for y in [-jaw_width/4, jaw_width/4]:
    hole = Pos(-jaw_length/2 + mount_hole_spacing, y, 0) * Cylinder(mount_hole_diameter/2, jaw_thickness)
    solid_body = solid_body - hole

rib = Pos(-jaw_length/2 + rib_offset, 0, -jaw_thickness/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body + rib

left_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
solid_body = chamfer(left_edges, chamfer_distance)

right_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
solid_body = fillet(right_edges, fillet_radius)

part = solid_body
part.name = "jaw_with_bearing_seat"
export_step(part, "output.step")