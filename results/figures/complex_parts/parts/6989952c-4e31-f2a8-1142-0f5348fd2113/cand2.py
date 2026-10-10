from build123d import *
import math

outer_radius = 30.0
web_thickness = 10.0
flange_thickness = 15.0
web_length = 30.0
total_length = 2 * flange_thickness + web_length
hole_diameter = 6.0
hole_pattern_radius = 22.0
hole_count = 6
fillet_radius = 2.0
pocket_width = 12.0
pocket_depth = 8.0
pocket_height = 5.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, -total_length/2), (outer_radius, -total_length/2))
            l2 = Line(l1@1, (outer_radius, -total_length/2 + flange_thickness))
            l3 = Line(l2@1, (web_thickness, -total_length/2 + flange_thickness))
            l4 = Line(l3@1, (web_thickness, total_length/2 - flange_thickness))
            l5 = Line(l4@1, (outer_radius, total_length/2 - flange_thickness))
            l6 = Line(l5@1, (outer_radius, total_length/2))
            l7 = Line(l6@1, (0, total_length/2))
            l8 = Line(l7@1, (0, -total_length/2))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter/2, total_length + 2)

solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(0, 0, total_length/2 - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "flanged_web_with_holes"
export_step(part, "output.step")