from build123d import *

outer_width = 80.0
outer_depth = 60.0
outer_height = 30.0
wall_thickness = 2.0
recess_width = 40.0
recess_depth = 30.0
recess_height = 8.0
mount_hole_diameter = 4.0
mount_hole_offset_x = 30.0
mount_hole_offset_y = 20.0
chamfer_size = 1.0

base = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[bottom_face])

recess = Pos(0, 0, outer_height - recess_height/2) * Box(recess_width, recess_depth, recess_height)
base = base - recess

hole_r = mount_hole_diameter / 2
for x, y in [(-mount_hole_offset_x, -mount_hole_offset_y),
             (mount_hole_offset_x, -mount_hole_offset_y),
             (-mount_hole_offset_x, mount_hole_offset_y),
             (mount_hole_offset_x, mount_hole_offset_y)]:
    base = base - Pos(x, y, outer_height/2) * Cylinder(hole_r, outer_height)

vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_size)

part = base
part.name = "shelled_box_with_recess_and_holes"
export_step(part, "output.step")