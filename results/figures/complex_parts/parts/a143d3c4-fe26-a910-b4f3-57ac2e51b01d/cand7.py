from build123d import *
import math

base_radius = 15.0
top_radius = 40.0
height = 40.0
rim_thickness = 8.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_height = 25.0
chamfer_size = 1.0
hole_diameter = 5.0
hole_count = 6
hole_radius = 30.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (top_radius, height))
            l3 = Line(l2 @ 1, (top_radius, height + rim_thickness))
            l4 = Line(l3 @ 1, (0, height + rim_thickness))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

pocket = Pos(pocket_depth / 2, 0, height / 2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, height + rim_thickness / 2) * Cylinder(hole_diameter / 2, height + rim_thickness + 10)

part = solid_body
part.name = "revolved_cone_with_pocket_and_holes"
export_step(part, "output.step")