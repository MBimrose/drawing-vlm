from build123d import *
import math

inner_radius = 10.0
outer_radius = 18.0
height = 30.0
rib_thickness = 2.0
rib_height = 10.0
rib_base = 5.0
rib_count = 6
hole_diameter = 4.0
hole_depth = 16.0
hole_radius = 14.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((inner_radius, 0), (outer_radius, 0), (outer_radius, height), (inner_radius, height), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_thickness/2, 0, rib_base + rib_height/2) * Cylinder(rib_thickness/2, rib_height)
    solid_body = solid_body + rib

for i in range(3):
    angle = i * 120.0
    x = hole_radius * math.cos(math.radians(angle))
    y = hole_radius * math.sin(math.radians(angle))
    hole = Pos(x, y, height - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "revolved_ring_with_ribs_and_holes"
export_step(part, "output.step")