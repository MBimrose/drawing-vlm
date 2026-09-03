from build123d import *

outer_width = 60.0
outer_depth = 40.0
outer_height = 30.0
wall_thickness = 3.0
slot_width = 8.0
slot_height = 20.0
hole_diameter = 3.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
chamfer_size = 0.5
boss_width = 20.0
boss_depth = 10.0
boss_height = 5.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

slot_box = Box(slot_width, outer_depth + 10, slot_height)
solid_body = solid_body - Pos(0, 0, outer_height/2) * slot_box

slot_box_y = Box(outer_width + 10, slot_width, slot_height)
solid_body = solid_body - Pos(0, 0, outer_height/2) * slot_box_y

hole_cyl = Cylinder(hole_diameter/2, outer_height + 10)
for dx in [-hole_spacing_x/2, hole_spacing_x/2]:
    for dy in [-hole_spacing_y/2, hole_spacing_y/2]:
        solid_body = solid_body - Pos(dx, dy, outer_height/2) * hole_cyl

boss_box = Box(boss_width, boss_depth, boss_height)
solid_body = solid_body + Pos(0, 0, boss_height/2) * boss_box

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "shelled_box_with_slots_holes_boss"
export_step(part, "output.step")