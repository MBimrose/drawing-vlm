from build123d import *

outer_diameter = 30.0
spacer_height = 15.0
counterbore_diameter = 12.0
counterbore_depth = 4.0
through_hole_diameter = 5.0
chamfer_size = 0.8
tab_width = 6.0
tab_height = 3.0
tab_thickness = 2.0
side_hole_diameter = 5.0
side_hole_spacing = 6.0

solid_body = Cylinder(outer_diameter / 2, spacer_height)
solid_body = solid_body - Pos(0, 0, spacer_height / 2 - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)
solid_body = solid_body - Cylinder(through_hole_diameter / 2, spacer_height + 1)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

tab = Pos(outer_diameter / 2, 0, 0) * Box(tab_width, tab_thickness, tab_height)
solid_body = solid_body + tab

for y in [-side_hole_spacing / 2, side_hole_spacing / 2]:
    solid_body = solid_body - Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(side_hole_diameter / 2, outer_diameter + 1)

part = solid_body
part.name = "spacer_with_tab"
export_step(part, "output.step")