from build123d import *
import math

outer_radius = 40.0
wall_thickness = 2.0
height = 30.0
base_thickness = 5.0
plate_thickness = 2.0
plate_height = 20.0
chamfer_size = 0.5
hole_diameter = 3.0
hole_rows = 2
hole_cols = 4
hole_spacing_z = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

base = Pos(0, 0, -base_thickness/2) * Cylinder(outer_radius, base_thickness)
solid_body = solid_body + base

plate = Pos(0, outer_radius + plate_thickness/2, 0) * Box(2*outer_radius, plate_thickness, plate_height)
plate_edges = plate.edges().filter_by(Axis.Z)
plate = chamfer(plate_edges, chamfer_size)
solid_body = solid_body + plate

for i in range(hole_cols):
    angle = i * 360.0 / hole_cols
    for j in range(hole_rows):
        z_pos = j * hole_spacing_z
        hole = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness/2, 0, z_pos) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, wall_thickness + 0.2)
        solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_plate_and_holes"
export_step(part, "output.step")