from build123d import *

outer_radius = 45.0
inner_radius = 30.0
housing_length = 70.0
fillet_radius = 4.0
pocket_width = 20.0
pocket_height = 30.0
pocket_depth = 5.0
pocket_offset_z = 20.0
hole_diameter = 6.0
hole_spacing = 30.0
hole_offset_z = 15.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, housing_length))
            l3 = Line(l2@1, (inner_radius, housing_length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = fillet(bottom_face.edges(), fillet_radius)

pocket = Pos(inner_radius - pocket_depth/2, 0, pocket_offset_z + pocket_height/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

for x in [-hole_spacing, 0, hole_spacing]:
    hole = Pos(x, 0, hole_offset_z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, housing_length)
    solid_body = solid_body - hole

part = solid_body
part.name = "housing_with_pocket_and_holes"
export_step(part, "output.step")