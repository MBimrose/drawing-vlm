from build123d import *

base_radius = 30.0
shoulder_radius = 20.0
neck_radius = 12.0
base_height = 15.0
shoulder_height = 15.0
neck_height = 20.0
pocket_width = 20.0
pocket_depth = 10.0
pocket_height = 5.0
hole_diameter = 5.0
hole_spacing = 40.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1@1, (base_radius, base_height))
            l3 = Line(l2@1, (shoulder_radius, base_height))
            l4 = Line(l3@1, (shoulder_radius, base_height + shoulder_height))
            l5 = Line(l4@1, (neck_radius, base_height + shoulder_height))
            l6 = Line(l5@1, (neck_radius, base_height + shoulder_height + neck_height))
            l7 = Line(l6@1, (0, base_height + shoulder_height + neck_height))
            l8 = Line(l7@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

top_z = base_height + shoulder_height + neck_height
pocket = Pos(0, 0, top_z - pocket_height / 2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

for x, y in [(0, -hole_spacing / 2), (0, hole_spacing / 2)]:
    hole = Pos(x, y, top_z / 2) * Cylinder(hole_diameter / 2, top_z + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "revolved_stepped_cylinder_with_pocket_and_holes"
export_step(part, "output.step")