from build123d import *

leg_length = 60.0
leg_width = 20.0
thickness = 8.0
rib_height = 20.0
rib_width = 4.0
rib_thickness = 2.0
pocket_width = 12.0
pocket_depth = 5.0
pocket_offset = 10.0
hole_diameter = 4.0
hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length,0), (leg_length,leg_width), (leg_width,leg_width), (leg_width,leg_length), (0,leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

solid_body = solid_body + Pos(leg_length + rib_thickness/2, leg_width/2, thickness/2) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + Pos(leg_width/2, leg_length + rib_thickness/2, thickness/2) * Box(rib_width, rib_thickness, rib_height)

solid_body = solid_body - Pos(pocket_offset, pocket_offset, thickness - pocket_depth/2) * Box(pocket_width, pocket_width, pocket_depth)

solid_body = solid_body - Pos(leg_length, hole_offset, thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, 200)
solid_body = solid_body - Pos(hole_offset, leg_length, thickness/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, 200)

part = solid_body
part.name = "L_bracket_with_ribs_pocket_holes"
export_step(part, "output.step")