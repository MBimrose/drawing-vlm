from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 2.0
height = 40.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 5.0
pocket_hole_diameter = 3.0
mount_hole_diameter = 3.0
mount_hole_count = 4
chamfer_size = 0.5
plate_thickness = 2.0
plate_width = 70.0
plate_height = 30.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Pos(0, 0, height/2) * Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

pocket = Pos(0, 0, height - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

pocket_hole = Pos(0, 0, height/2) * Rot(90, 0, 0) * Cylinder(pocket_hole_diameter/2, height + 10)
solid_body = solid_body - pocket_hole

for i in range(mount_hole_count):
    angle = i * 360.0 / mount_hole_count
    hole = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness/2, 0, height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, wall_thickness + 2)
    solid_body = solid_body - hole

plate = Pos(0, outer_radius + plate_thickness/2, 0) * Box(plate_width, plate_thickness, plate_height)
solid_body = solid_body + plate

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "cylindrical_shell_with_pocket_and_plate"
export_step(part, "output.step")