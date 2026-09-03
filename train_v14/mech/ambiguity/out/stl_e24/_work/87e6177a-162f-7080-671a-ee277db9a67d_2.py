from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
length = 60.0
groove_width = 2.0
groove_depth = 2.0
groove_length = 30.0
groove_spacing = 12.0
num_grooves = 6
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Pos(0, 0, length/2) * Cylinder(outer_radius, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_edges = solid_body.edges().sort_by(Axis.Z)[-2:]
solid_body = chamfer(top_edges, chamfer_size)

for i in range(num_grooves):
    angle_deg = i * 360.0 / num_grooves
    groove = Rot(0, 0, angle_deg) * Pos(outer_radius - groove_depth/2, 0, 0) * Box(groove_width, groove_depth, groove_length)
    solid_body = solid_body - groove

part = solid_body
part.name = "grooved_cylinder"
export_step(part, "output.step")