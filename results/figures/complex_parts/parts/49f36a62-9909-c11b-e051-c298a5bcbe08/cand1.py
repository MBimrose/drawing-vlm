from build123d import *

outer_diameter = 38.0
inner_diameter = 19.6
height = 15.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
pocket_width = 12.0
pocket_length = 8.0
pocket_depth = 2.0
chamfer_size = 0.5
mount_hole_diameter = 4.0
rib_thickness = 1.0
rib_height = 2.0

solid_body = Cylinder(outer_diameter / 2.0, height)
solid_body = solid_body - Cylinder(inner_diameter / 2.0, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

pocket = Pos(0, 0, height - pocket_depth / 2.0) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

solid_body = solid_body - Cylinder(mount_hole_diameter / 2.0, height)

rib = Pos(0, 0, height / 2.0 + rib_height / 2.0) * Box(rib_thickness, outer_diameter - 2 * wall_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_pocket_and_rib"
export_step(part, "output.step")