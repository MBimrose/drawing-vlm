from build123d import *

leg_length = 80.0
leg_height = 70.0
thickness = 8.0
depth = 12.0
pocket_diameter = 20.0
pocket_depth = 4.0
hole_diameter = 6.0
hole_margin = 10.0
hole_spacing = (leg_height - 2 * hole_margin) / 2
fillet_radius = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, leg_height), (thickness, leg_height),
                     (thickness, thickness), (leg_length + thickness, thickness),
                     (leg_length + thickness, 0), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part

# Pocket at inner corner (thickness, thickness)
solid_body = solid_body - Pos(thickness, thickness, depth - pocket_depth / 2) * Cylinder(pocket_diameter / 2, pocket_depth)

# Three through holes on vertical leg
for i in range(3):
    y = hole_margin + i * hole_spacing
    solid_body = solid_body - Pos(thickness / 2, y, depth / 2) * Cylinder(hole_diameter / 2, depth)

# Fillet inner corner edge (vertical edge at x=thickness, y=thickness)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
inner_edge = None
for e in vertical_edges:
    c = e.center()
    if abs(c.X - thickness) < 1 and abs(c.Y - thickness) < 1:
        inner_edge = e
        break
if inner_edge:
    solid_body = fillet([inner_edge], fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")