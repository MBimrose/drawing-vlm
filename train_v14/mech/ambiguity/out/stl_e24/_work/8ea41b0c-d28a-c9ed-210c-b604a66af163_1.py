from build123d import *

bracket_width = 80.0
bracket_height = 60.0
bracket_thickness = 5.0
notch_width = 10.0
notch_depth = 8.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset_y = 15.0
slot_width = 12.0
slot_length = 30.0
slot_offset_y = 15.0
rib_height = 10.0
rib_thickness = 4.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-bracket_width/2, -bracket_height/2),
                (bracket_width/2, -bracket_height/2),
                (bracket_width/2, bracket_height/2 - notch_depth),
                (bracket_width/2 - notch_width, bracket_height/2 - notch_depth),
                (bracket_width/2 - notch_width, bracket_height/2),
                (bracket_width/2, bracket_height/2),
                (-bracket_width/2, bracket_height/2),
                close=True
            )
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

for x, y in [(-hole_spacing/2, hole_offset_y), (hole_spacing/2, hole_offset_y), (0, hole_offset_y + hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)

slot_center_y = -bracket_height/2 + slot_offset_y + slot_length/2
solid_body = solid_body - Pos(0, slot_center_y, 0) * Box(slot_width, slot_length, bracket_thickness * 2)

rib1 = Pos(-bracket_width/2 + rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, bracket_thickness)
rib2 = Pos(bracket_width/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, bracket_thickness)
solid_body = solid_body + rib1 + rib2

solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")