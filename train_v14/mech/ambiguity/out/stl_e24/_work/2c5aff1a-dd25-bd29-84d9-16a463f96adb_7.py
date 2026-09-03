from build123d import *

outer_radius = 45.0
inner_radius = 30.0
housing_length = 70.0
wall_thickness = outer_radius - inner_radius
pocket_width = 20.0
pocket_height = 30.0
pocket_depth = 10.0
pocket_offset = 15.0
fillet_radius = 3.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_rows = 2
hole_cols = 3
hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Line((inner_radius, 0), (outer_radius, 0))
            Line((outer_radius, 0), (outer_radius, housing_length))
            Line((outer_radius, housing_length), (inner_radius, housing_length))
            Line((inner_radius, housing_length), (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = fillet(top_face.edges(), fillet_radius)
solid_body = fillet(bottom_face.edges(), fillet_radius)

pocket = Pos(inner_radius - pocket_depth/2, 0, pocket_offset + pocket_height/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing
        z = (j - (hole_rows-1)/2) * hole_spacing + hole_offset
        hole = Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, housing_length + 20)
        solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_pocket_and_holes"
export_step(part, "output.step")