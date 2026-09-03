from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 12.0
wall_thickness = 2.0
boss_diameter = 20.0
boss_height = 8.0
fillet_radius = 1.5
chamfer_distance = 1.0
hole_diameter = 5.0
hole_offset_x = 20.0
hole_offset_y = 15.0

solid_body = Box(outer_length, outer_width, outer_height)
solid_body = solid_body - Pos(0, 0, wall_thickness/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, outer_height - wall_thickness)
solid_body = solid_body + Pos(0, 0, outer_height/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

hole_positions = [
    (-outer_length/2 + hole_offset_x, -outer_width/2 + hole_offset_y),
    ( outer_length/2 - hole_offset_x, -outer_width/2 + hole_offset_y),
    (-outer_length/2 + hole_offset_x,  outer_width/2 - hole_offset_y),
    ( outer_length/2 - hole_offset_x,  outer_width/2 - hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, outer_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "hollow_box_with_boss"
export_step(part, "output.step")