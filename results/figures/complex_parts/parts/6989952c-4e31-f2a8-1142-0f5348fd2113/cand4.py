from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 20.0
length = 60.0
flange_thickness = 15.0
fillet_radius = 2.0
hole_diameter = 6.0
hole_count = 6
hole_circle_radius = (outer_diameter/2) - 8.0
pocket_width = 20.0
pocket_length = 30.0
pocket_depth = 5.0

outer_radius = outer_diameter/2.0
inner_radius = inner_diameter/2.0
half_length = length/2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, -half_length), (outer_radius, -half_length))
            l2 = Line(l1@1, (outer_radius, -half_length + flange_thickness))
            l3 = Line(l2@1, (inner_radius, -half_length + flange_thickness))
            l4 = Line(l3@1, (inner_radius, half_length - flange_thickness))
            l5 = Line(l4@1, (outer_radius, half_length - flange_thickness))
            l6 = Line(l5@1, (outer_radius, half_length))
            l7 = Line(l6@1, (0, half_length))
            l8 = Line(l7@1, (0, -half_length))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter/2, length + 2)

solid_body = solid_body - Pos(0, 0, half_length - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "flanged_shaft_with_holes_and_pocket"
export_step(part, "output.step")