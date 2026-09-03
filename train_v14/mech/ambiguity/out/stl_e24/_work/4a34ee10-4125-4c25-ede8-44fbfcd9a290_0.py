from build123d import *
import math

outer_radius = 45.0
inner_radius = 30.0
ring_height = 12.0
groove_width = 4.0
groove_depth = 6.0
groove_spacing = 6.0
hole_diameter = 4.0
hole_count = 4
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, ring_height))
            l3 = Line(l2@1, (inner_radius, ring_height))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

groove1 = Pos(outer_radius - groove_width/2, 0, groove_spacing/2) * Box(groove_width, groove_depth, groove_spacing)
groove2 = Pos(outer_radius - groove_width/2, 0, ring_height - groove_spacing/2) * Box(groove_width, groove_depth, groove_spacing)
solid_body = solid_body - groove1 - groove2

hole_radius = (inner_radius + outer_radius) / 2
for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, ring_height/2) * Cylinder(hole_diameter/2, ring_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "ring_with_grooves_and_holes"
export_step(part, "output.step")