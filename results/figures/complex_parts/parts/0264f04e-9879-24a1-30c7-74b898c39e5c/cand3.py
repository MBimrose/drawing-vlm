from build123d import *

base_radius = 30.0
base_height = 15.0
middle_radius = 20.0
middle_height = 15.0
top_radius = 12.0
top_height = 20.0
pocket_width = 10.0
pocket_depth = 5.0
pocket_height = 8.0
hole_diameter = 5.0
hole_spacing = 40.0
fillet_radius = 2.0

total_height = base_height + middle_height + top_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1@1, (base_radius, base_height))
            l3 = Line(l2@1, (middle_radius, base_height))
            l4 = Line(l3@1, (middle_radius, base_height + middle_height))
            l5 = Line(l4@1, (top_radius, base_height + middle_height))
            l6 = Line(l5@1, (top_radius, total_height))
            l7 = Line(l6@1, (0, total_height))
            l8 = Line(l7@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(0, 0, total_height - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

for y in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(0, y, total_height/2) * Cylinder(hole_diameter/2, total_height + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "stepped_cylinder_with_pocket_and_holes"
export_step(part, "output.step")