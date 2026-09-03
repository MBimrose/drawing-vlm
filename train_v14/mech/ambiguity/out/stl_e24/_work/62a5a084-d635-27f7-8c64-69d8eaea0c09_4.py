from build123d import *
import math

outer_diameter = 30.0
inner_diameter = 12.0
body_height = 20.0
rib_height = 8.0
rib_thickness = 2.0
rib_count = 3
counterbore_diameter = 10.0
counterbore_depth = 4.0
through_hole_diameter = 6.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=body_height)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, body_height / 2) * Cylinder(inner_diameter / 2, body_height)

rib_radius = outer_diameter / 2 - rib_thickness / 2
for i in range(rib_count):
    angle_deg = i * 360.0 / rib_count
    angle_rad = math.radians(angle_deg)
    px = rib_radius * math.cos(angle_rad)
    py = rib_radius * math.sin(angle_rad)
    rib = Pos(px, py, rib_height / 2) * Rot(0, 0, angle_deg) * Box(rib_thickness, body_height, rib_height)
    solid_body = solid_body + rib

cb_x = outer_diameter / 2 - counterbore_depth / 2
solid_body = solid_body - Pos(cb_x, 0, body_height / 2) * Rot(0, 90, 0) * Cylinder(counterbore_diameter / 2, counterbore_depth)
solid_body = solid_body - Pos(outer_diameter / 2, 0, body_height / 2) * Rot(0, 90, 0) * Cylinder(through_hole_diameter / 2, outer_diameter)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "ribbed_cylinder_with_counterbore"
export_step(part, "output.step")