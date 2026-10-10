from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 2.0
height = 40.0
pocket_width = 15.0
pocket_height = 20.0
pocket_depth = 5.0
chamfer_size = 0.5
hole_diameter = 3.0
hole_count = 4
hole_radius = outer_diameter/2 - wall_thickness/2
rib_width = 10.0
rib_height = 5.0
rib_thickness = 2.0

outer_radius = outer_diameter/2
inner_radius = outer_radius - wall_thickness

solid_body = Pos(0, 0, height/2) * Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

pocket = Pos(outer_radius - pocket_depth/2, 0, height/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    hole = Pos(px, py, height/2) * Rot(0, 0, angle) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, wall_thickness + 0.2)
    solid_body = solid_body - hole

rib = Pos(0, outer_radius - rib_thickness/2, 0) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_pocket_holes_rib"
export_step(part, "output.step")