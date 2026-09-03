from build123d import *
import math

outer_width = 80.0
outer_depth = 80.0
outer_height = 40.0
wall_thickness = 5.0
notch_width = 30.0
notch_height = 20.0
notch_depth = 10.0
hole_diameter = 3.0
hole_radius = hole_diameter / 2.0
hole_depth = wall_thickness + 2.0
hole_pattern_radius = (outer_width / 2.0) - wall_thickness - 5.0
chamfer_distance = 1.5

solid_body = Box(outer_width, outer_depth, outer_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

notch_box = Pos(-outer_width/2 + notch_depth/2, 0, 0) * Box(notch_depth, notch_width, notch_height)
solid_body = solid_body - notch_box

for i in range(4):
    angle = math.radians(i * 90)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    hole = Pos(px, py, outer_height/2 - hole_depth/2) * Cylinder(hole_radius, hole_depth)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "shelled_box_with_notch_and_holes"
export_step(part, "output.step")