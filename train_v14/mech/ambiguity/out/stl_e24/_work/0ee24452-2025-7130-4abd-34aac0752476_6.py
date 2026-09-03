from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 60.0
thickness = 8.0
width = 20.0
gusset_thickness = 4.0
gusset_base = 10.0
hole_diameter = 5.0
hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as s1:
        with BuildLine() as l1:
            Polyline((0,0), (horizontal_leg_length, 0), (horizontal_leg_length, thickness),
                     (thickness, thickness), (thickness, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=width)
    with BuildSketch() as s2:
        with BuildLine() as l2:
            Polyline((0, vertical_leg_length), (gusset_base, vertical_leg_length), (0, vertical_leg_length - gusset_base), close=True)
        make_face()
    extrude(amount=gusset_thickness)

solid_body = p.part
hole_x = hole_offset
hole_z = width / 2
solid_body = solid_body - Pos(hole_x, vertical_leg_length, hole_z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, 200)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")