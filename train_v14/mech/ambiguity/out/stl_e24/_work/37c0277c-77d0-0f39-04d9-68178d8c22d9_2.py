from build123d import *

outer_diameter = 50.0
inner_diameter = 21.0
thickness = 10.0
keyway_width = 6.0
keyway_depth = 4.0
chamfer_size = 0.5
mounting_hole_diameter = 4.5
mounting_hole_spacing = 30.0

solid_body = Cylinder(outer_diameter/2, thickness)
solid_body = solid_body - Cylinder(inner_diameter/2, thickness)

keyway_center_x = inner_diameter/2 + keyway_depth/2
solid_body = solid_body - Pos(keyway_center_x, 0, 0) * Box(keyway_width, keyway_depth, thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

for x in [-mounting_hole_spacing/2, mounting_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mounting_hole_diameter/2, thickness)

part = solid_body
part.name = "flanged_shaft_with_keyway"
export_step(part, "output.step")