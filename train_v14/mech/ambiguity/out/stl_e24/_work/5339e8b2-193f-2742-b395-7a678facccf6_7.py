from build123d import *

horizontal_leg_length = 80.0
vertical_leg_height = 40.0
leg_width = 20.0
bracket_thickness = 8.0
rib_width = 5.0
rib_height = 6.0
rib_thickness = 2.0
hole_diameter = 5.0
counterbore_diameter = 9.0
counterbore_depth = 4.0
hole_spacing = 15.0
hole_offset_from_inner = 10.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, vertical_leg_height + leg_width),
                     (0, vertical_leg_height + leg_width), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(leg_width/2, leg_width/2, bracket_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

for i in range(4):
    x = hole_offset_from_inner + i * hole_spacing
    y = leg_width / 2
    solid_body = solid_body - Pos(x, y, bracket_thickness - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
    solid_body = solid_body - Pos(x, y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")