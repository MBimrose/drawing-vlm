from build123d import *

plate_length = 60.0
plate_width = 40.0
plate_thickness = 8.0
boss_diameter = 20.0
boss_height = 12.0
hole_diameter = 6.0
hole_spacing = 30.0
fillet_radius = 2.0
chamfer_distance = 0.5
pocket_depth = 4.0
pocket_width = 12.0
pocket_length = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
    with BuildSketch() as s2:
        Circle(boss_diameter / 2)
    extrude(amount=boss_height)

solid_body = p.part

for x, y in [(-hole_spacing/2, -hole_spacing/2), (hole_spacing/2, -hole_spacing/2),
             (-hole_spacing/2, hole_spacing/2), (hole_spacing/2, hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

solid_body = solid_body - Pos(0, 0, boss_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

part = solid_body
part.name = "plate_with_boss"
export_step(part, "output.step")