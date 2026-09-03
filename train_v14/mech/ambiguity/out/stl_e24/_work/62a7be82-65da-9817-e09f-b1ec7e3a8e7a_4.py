from build123d import *

outer_radius = 40.0
disc_thickness = 8.0
rib_width = 6.0
rib_height = 4.0
rib_offset = 5.0
hole_diameter = 4.0
cbore_diameter = 7.0
cbore_depth = 4.0
hole_offset = 35.0
chamfer_size = 0.8
pocket_width = 20.0
pocket_depth = 3.0
pocket_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=disc_thickness)

solid_body = p.part

rib = Pos(rib_offset + (outer_radius - rib_offset) / 2, 0, disc_thickness / 2) * Box(outer_radius - rib_offset, rib_width, rib_height)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Pos(hole_offset, 0, disc_thickness / 2) * Cylinder(hole_diameter / 2, disc_thickness + 1)
solid_body = solid_body - Pos(hole_offset, 0, disc_thickness - cbore_depth / 2) * Cylinder(cbore_diameter / 2, cbore_depth)

solid_body = solid_body - Pos(pocket_offset, 0, disc_thickness - pocket_depth / 2) * Box(pocket_width, pocket_width, pocket_depth)

part = solid_body
part.name = "disc_with_rib_and_pocket"
export_step(part, "output.step")