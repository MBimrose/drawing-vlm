from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 8.0
groove_width = 6.0
groove_depth = 2.0
set_screw_diameter = 4.0
set_screw_head_diameter = 7.0
set_screw_head_angle = 90.0
chamfer_distance = 0.8
boss_diameter = 12.0
boss_height = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part

groove_radius = (outer_diameter / 2) - (groove_width / 2)
groove = Pos(0, 0, thickness - groove_depth / 2) * Cylinder(groove_radius, groove_depth)
solid_body = solid_body - groove

boss = Pos(0, 0, boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

csk_radius = set_screw_head_diameter / 2
csk_height = csk_radius / math.tan(math.radians(set_screw_head_angle / 2))
hole_depth = thickness + 1

hole_x = (outer_diameter / 2) - (set_screw_head_diameter / 2) - 2.0
hole_y = 0.0

shaft = Pos(hole_x, hole_y, thickness - hole_depth / 2) * Cylinder(set_screw_diameter / 2, hole_depth)
csk_cone = Pos(hole_x, hole_y, thickness - csk_height / 2) * Cone(0, csk_radius, csk_height)
solid_body = solid_body - shaft - csk_cone

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "ring_with_groove_boss_and_setscrew"
export_step(part, "output.step")