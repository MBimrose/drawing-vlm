from build123d import *

arm_length = 80.0
outer_diameter = 20.0
inner_diameter = 8.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
pocket_width = 12.0
pocket_height = 10.0
pocket_depth = 6.0
pocket_offset_from_end = 20.0
groove_width = 4.0
groove_depth = 2.0
groove_offset_from_end = 30.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, arm_length) - Cylinder(inner_radius, arm_length)

pocket_center_z = arm_length - pocket_offset_from_end - pocket_height / 2.0
pocket_box = Pos(0, outer_radius - pocket_depth / 2.0, pocket_center_z) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket_box

groove_center_z = arm_length - groove_offset_from_end - groove_width / 2.0
groove_box = Pos(0, outer_radius - groove_depth / 2.0, groove_center_z) * Box(groove_width, groove_depth, groove_depth)
solid_body = solid_body - groove_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "hollow_arm_with_pocket_and_groove"
export_step(part, "output.step")