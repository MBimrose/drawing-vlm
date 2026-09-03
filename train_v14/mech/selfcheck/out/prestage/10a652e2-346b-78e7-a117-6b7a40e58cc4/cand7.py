from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
leg_thickness = 10.0
bracket_depth = 20.0
rib_thickness = 5.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset = 10.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as l:
            Polyline((0,0), (leg_length_long, 0), (leg_length_long, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length_short),
                     (0, leg_length_short), close=True)
        make_face()
    extrude(amount=bracket_depth)

with BuildPart() as p_rib:
    with BuildSketch() as s_rib:
        with BuildLine() as l_rib:
            Polyline((0,0), (rib_thickness, 0), (0, rib_thickness), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part + p_rib.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

hole_r = hole_diameter / 2
hole_h = bracket_depth + 2
for i in range(4):
    x = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, bracket_depth/2) * Cylinder(hole_r, hole_h)

for i in range(4):
    y = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(0, y, bracket_depth/2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")