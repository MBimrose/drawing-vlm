from build123d import *

outer_diameter = 30.0
inner_diameter = 12.0
length = 15.0
counterbore_diameter = 18.0
counterbore_depth = 4.0
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_spacing = 6.0
tab_width = 4.0
tab_height = 3.0
tab_thickness = 2.0

solid_body = Cylinder(outer_diameter/2, length)
solid_body = solid_body - Cylinder(inner_diameter/2, length)
solid_body = solid_body - Pos(0, 0, length/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

hole_r = mount_hole_diameter / 2
hole_h = outer_diameter + 1
for y in [mount_hole_spacing/2, -mount_hole_spacing/2]:
    solid_body = solid_body - Pos(outer_diameter/2, y, 0) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
    solid_body = solid_body - Pos(-outer_diameter/2, y, 0) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)

tab = Pos(outer_diameter/2, 0, 0) * Box(tab_width, tab_thickness, tab_height)
solid_body = solid_body + tab

part = solid_body
part.name = "collar_with_tabs"
export_step(part, "output.step")