from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 6.0
boss_radius = 12.0
boss_height = 5.0
hole_diameter = 4.0
hole_spacing_x = 40.0
hole_spacing_y = 12.0
chamfer_size = 0.5
notch_width = 8.0
notch_depth = 20.0

solid_body = Box(plate_length, plate_width, plate_thickness)

notch1 = Pos(-plate_length/2 + notch_width/2, 0, 0) * Box(notch_width, notch_depth, plate_thickness)
notch2 = Pos(plate_length/2 - notch_width/2, 0, 0) * Box(notch_width, notch_depth, plate_thickness)
solid_body = solid_body - notch1 - notch2

boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
]
for x, y in hole_positions:
    hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + boss_height + 10)
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")