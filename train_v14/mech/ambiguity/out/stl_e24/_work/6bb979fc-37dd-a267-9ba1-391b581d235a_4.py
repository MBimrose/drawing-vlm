from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_height = 5.0
rib_thickness = 2.0
rib_offset = 5.0
tab_width = 10.0
tab_height = 6.0
tab_thickness = 3.0
tab_offset = 4.0
pocket_depth = 1.0
pocket_width = 4.0
pocket_length = tab_width - 2.0
hole_diameter = 4.0
hole_margin = 5.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

rib = Pos(0, -outer_width/2 - rib_thickness/2, rib_offset + rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
solid_body = solid_body + rib

tab = Pos(0, outer_width/2 + tab_thickness/2, tab_offset + tab_height/2) * Box(tab_width, tab_thickness, tab_height)
solid_body = solid_body + tab

pocket = Pos(0, outer_width/2 + tab_thickness - pocket_depth/2, tab_offset + tab_height/2) * Box(pocket_length, pocket_depth, pocket_width)
solid_body = solid_body - pocket

for x, y in [(-outer_length/2 + hole_margin, -outer_width/2 + hole_margin),
             (outer_length/2 - hole_margin, -outer_width/2 + hole_margin),
             (-outer_length/2 + hole_margin, outer_width/2 - hole_margin),
             (outer_length/2 - hole_margin, outer_width/2 - hole_margin)]:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(hole_diameter/2, outer_height)

part = solid_body
part.name = "hollow_box_with_rib_tab"
export_step(part, "output.step")