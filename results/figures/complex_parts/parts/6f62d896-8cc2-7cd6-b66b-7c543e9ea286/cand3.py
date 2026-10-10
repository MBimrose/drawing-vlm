from build123d import *

outer_diameter = 70.0
inner_diameter = 30.0
thickness = 10.0
central_hole_diameter = 8.0
counterbore_diameter = 9.0
counterbore_depth = 4.0
chamfer_distance = 0.5
rib_width = 5.0
rib_height = 3.0
rib_thickness = 2.0
pocket_width = 12.0
pocket_height = 6.0
pocket_depth = 2.0
fillet_radius = 0.3

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2)
    extrude(amount=thickness)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, thickness / 2) * Cylinder(central_hole_diameter / 2, thickness)
solid_body = solid_body - Pos(0, 0, thickness - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

rib = Pos(outer_diameter / 2 + rib_thickness / 2, 0, thickness / 2) * Box(rib_thickness, rib_height, rib_width)
solid_body = solid_body + rib

pocket = Pos(0, 0, thickness - pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "ring_with_rib_and_pocket"
export_step(part, "output.step")