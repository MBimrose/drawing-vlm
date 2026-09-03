from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
thickness = 8.0
extrude_depth = 15.0
inner_fillet_radius = 4.0
hole_diameter = 6.0
counterbore_diameter = 10.0
counterbore_depth = 3.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (thickness, vertical_leg_length),
                     (thickness, thickness), (horizontal_leg_length, thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part

inner_edge = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 1e-3 and abs(e.center().Y - thickness) < 1e-3][0]
solid_body = fillet([inner_edge], inner_fillet_radius)

solid_body = solid_body - Pos(horizontal_leg_length - thickness/2, thickness/2, extrude_depth - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

hole_r = hole_diameter / 2
hole_h = extrude_depth + 10
for x, y in [(thickness/2, vertical_leg_length/3), (thickness/2, 2*vertical_leg_length/3), (horizontal_leg_length - thickness/2, thickness/2)]:
    solid_body = solid_body - Pos(x, y, extrude_depth/2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")