from build123d import *

outer_radius = 45
inner_radius = 30
housing_length = 70
wall_thickness = outer_radius - inner_radius
fillet_radius = 3
pocket_width = 20
pocket_height = 30
pocket_depth = wall_thickness * 0.6
hole_diameter = 6
hole_offset_z = 15
rib_width = 10
rib_height = 15
rib_thickness = 5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, housing_length))
            l2 = Line(l1 @ 1, (inner_radius, housing_length))
            l3 = Line(l2 @ 1, (inner_radius, 0))
            l4 = Line(l3 @ 1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(outer_radius - pocket_depth/2, 0, housing_length/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

for x in [outer_radius - wall_thickness/2, -(outer_radius - wall_thickness/2)]:
    hole = Pos(x, 0, hole_offset_z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, housing_length)
    solid_body = solid_body - hole

rib = Pos(inner_radius - rib_thickness/2, 0, housing_length/2) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "housing_with_pocket_holes_rib"
export_step(part, "output.step")