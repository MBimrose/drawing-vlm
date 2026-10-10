from build123d import *
import math

base_radius = 15.0
base_height = 40.0
flange_radius = 40.0
flange_thickness = 8.0
pocket_width = 20.0
pocket_depth = 10.0
pocket_height = 30.0
hole_diameter = 5.0
hole_count = 6
hole_circle_radius = 30.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (flange_radius, base_height))
            l3 = Line(l2 @ 1, (flange_radius, base_height + flange_thickness))
            l4 = Line(l3 @ 1, (0, base_height + flange_thickness))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

pocket = Pos(base_radius - pocket_depth/2, 0, pocket_height/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    hole = Pos(px, py, base_height + flange_thickness/2) * Cylinder(hole_diameter/2, base_height + flange_thickness + 10)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "revolved_flange_with_pocket"
export_step(part, "output.step")