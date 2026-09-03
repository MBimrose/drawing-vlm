from build123d import *

vertical_leg_height = 70.0
horizontal_leg_length = 80.0
thickness = 8.0
depth = 12.0
fillet_radius = 4.0
pocket_radius = 8.0
pocket_depth = 4.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_count = 3

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_height), (thickness, vertical_leg_height),
                     (thickness, thickness), (horizontal_leg_length + thickness, thickness),
                     (horizontal_leg_length + thickness, 0), close=True)
        make_face()
    extrude(amount=depth)

solid = p.part
inner_edge = solid.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
solid = fillet([inner_edge], fillet_radius)

pocket = Pos(horizontal_leg_length / 2, thickness / 2, depth - pocket_depth / 2) * Cylinder(pocket_radius, pocket_depth)
solid = solid - pocket

for i in range(hole_count):
    y = vertical_leg_height / 2 + (i - (hole_count - 1) / 2) * hole_spacing
    hole = Pos(thickness / 2, y, depth / 2) * Cylinder(hole_diameter / 2, depth)
    solid = solid - hole

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")