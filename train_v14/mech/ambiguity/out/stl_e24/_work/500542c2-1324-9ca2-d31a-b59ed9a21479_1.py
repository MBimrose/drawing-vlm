from build123d import *
import math

gear_base_radius = 30.0
gear_thickness = 5.0
tooth_width = 6.0
tooth_height = 8.0
tooth_overlap = 1.0
num_teeth = 18
central_hole_diameter = 6.0
chamfer_distance = 0.5

tooth_center_x = gear_base_radius + tooth_height/2 - tooth_overlap

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(gear_base_radius)
    extrude(amount=gear_thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    tooth = Rot(0, 0, angle) * Pos(tooth_center_x, 0, gear_thickness + tooth_height/2) * Box(tooth_height, tooth_width, tooth_height)
    solid_body = solid_body + tooth

solid_body = solid_body - Cylinder(central_hole_diameter/2, 100)

part = solid_body
part.name = "gear"
export_step(part, "output.step")