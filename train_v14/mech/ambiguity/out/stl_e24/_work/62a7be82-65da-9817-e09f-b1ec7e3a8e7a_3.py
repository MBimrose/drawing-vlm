from build123d import *

outer_diameter = 80.0
thickness = 8.0
rib_height = 2.0
rib_width = 6.0
rib_margin = 5.0
set_screw_diameter = 4.0
set_screw_head_diameter = 7.0
set_screw_head_depth = 4.0
set_screw_offset_from_edge = 5.0
chamfer_size = 0.8
rib_chamfer = 0.5

outer_radius = outer_diameter / 2.0
rib_outer_radius = outer_radius - rib_margin
rib_inner_radius = rib_outer_radius - rib_width
set_screw_center_radius = outer_radius - set_screw_offset_from_edge

base = Pos(0, 0, thickness / 2) * Cylinder(outer_radius, thickness)
top_face = base.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
base = chamfer(top_edges, chamfer_size)

rib = Pos(0, 0, rib_height / 2) * (Cylinder(rib_outer_radius, rib_height) - Cylinder(rib_inner_radius, rib_height))
rib_top_face = rib.faces().sort_by(Axis.Z)[-1]
rib_top_edges = rib_top_face.edges()
rib = chamfer(rib_top_edges, rib_chamfer)

result = base + rib

shaft_hole = Pos(set_screw_center_radius, 0, thickness / 2) * Cylinder(set_screw_diameter / 2, thickness)
cbore_hole = Pos(set_screw_center_radius, 0, thickness - set_screw_head_depth / 2) * Cylinder(set_screw_head_diameter / 2, set_screw_head_depth)
result = result - shaft_hole - cbore_hole

part = result
part.name = "ribbed_disc_with_set_screw"
export_step(part, "output.step")