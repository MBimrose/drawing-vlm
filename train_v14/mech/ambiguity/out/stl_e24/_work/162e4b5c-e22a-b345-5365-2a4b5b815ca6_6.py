from build123d import *

length = 80.0
width = 30.0
thickness = 10.0
split_gap = 0.5
bearing_diameter = 20.0
bearing_depth = 8.0
chamfer_size = 1.0
tab_length = 12.0
tab_width = 8.0
tab_thickness = 4.0
mount_hole_diameter = 4.0
mount_hole_spacing = 15.0

solid_body = Box(length, width, thickness)

tab = Pos(-length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, thickness)
solid_body = solid_body + tab

split_cut = Box(split_gap, width, thickness - 2*chamfer_size)
solid_body = solid_body - split_cut

bearing_pocket = Pos(length/2 - bearing_depth/2, 0, -thickness/2 + bearing_depth/2) * Cylinder(bearing_diameter/2, bearing_depth)
solid_body = solid_body - bearing_pocket

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(-length/4, y, 0) * Cylinder(mount_hole_diameter/2, thickness)
    solid_body = solid_body - hole

left_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
solid_body = chamfer(left_edges, chamfer_size)

right_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
solid_body = chamfer(right_edges, chamfer_size)

part = solid_body
part.name = "split_bearing_block"
export_step(part, "output.step")