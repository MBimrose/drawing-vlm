from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 20.0
wall_thickness = 5.0
inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
fillet_radius = 3.0
hole_diameter = 5.0
hole_offset_x = 15.0
hole_offset_y = 15.0
counterbore_diameter = 10.0
counterbore_depth = 4.0

solid_body = Box(outer_length, outer_width, outer_height) - Box(inner_length, inner_width, outer_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole_positions = [
    (-outer_length/2 + hole_offset_x, -outer_width/2 + hole_offset_y),
    ( outer_length/2 - hole_offset_x, -outer_width/2 + hole_offset_y),
    (-outer_length/2 + hole_offset_x,  outer_width/2 - hole_offset_y),
    ( outer_length/2 - hole_offset_x,  outer_width/2 - hole_offset_y),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, outer_height)
    solid_body = solid_body - Pos(x, y, outer_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

part = solid_body
part.name = "hollow_box_with_counterbored_holes"
export_step(part, "output.step")