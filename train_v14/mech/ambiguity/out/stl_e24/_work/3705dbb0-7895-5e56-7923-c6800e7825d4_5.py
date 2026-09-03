from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
pocket_length = 60.0
pocket_width = 40.0
pocket_depth = 5.0
hole_diameter = 1.5
hole_spacing_x = 10.0
hole_spacing_y = 10.0
hole_rows = 4
hole_cols = 7
chamfer_size = 0.5
rib_thickness = 2.0
rib_height = 4.0
mount_hole_dia = 3.0
mount_hole_offset = 10.0

solid = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = offset(solid, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, 0, wall_thickness + pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid = solid - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid = solid - Pos(x, y, outer_height/2) * Cylinder(hole_diameter/2, outer_height + 10)

rib1 = Pos(0, outer_width/2 - wall_thickness - rib_thickness/2, wall_thickness + rib_height/2) * Box(outer_length - 2*wall_thickness, rib_thickness, rib_height)
rib2 = Pos(0, -(outer_width/2 - wall_thickness - rib_thickness/2), wall_thickness + rib_height/2) * Box(outer_length - 2*wall_thickness, rib_thickness, rib_height)
solid = solid + rib1 + rib2

solid = solid - Pos(outer_length/2, 0, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, outer_length + 10)
solid = solid - Pos(-outer_length/2, 0, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, outer_length + 10)

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

part = solid
part.name = "hollow_box_with_pocket_and_ribs"
export_step(part, "output.step")