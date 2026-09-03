from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
leg_thickness = 10.0
bracket_thickness = 12.0
fillet_radius = 2.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 6.0
pocket_offset_from_top = 10.0
mount_hole_diameter = 6.0
mount_hole_offset = 40.0
rib_thickness = 4.0
rib_height = 20.0
rib_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (horizontal_leg_length, 0))
            l2 = Line(l1 @ 1, (horizontal_leg_length, leg_thickness))
            l3 = Line(l2 @ 1, (leg_thickness, leg_thickness))
            l4 = Line(l3 @ 1, (leg_thickness, vertical_leg_length))
            l5 = Line(l4 @ 1, (0, vertical_leg_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

pocket_cx = leg_thickness / 2
pocket_cy = vertical_leg_length - pocket_offset_from_top - pocket_height / 2
pocket_cz = bracket_thickness - pocket_depth / 2
solid_body = solid_body - Pos(pocket_cx, pocket_cy, pocket_cz) * Box(pocket_width, pocket_height, pocket_depth)

hole_r = mount_hole_diameter / 2
hole_h = bracket_thickness + 1
solid_body = solid_body - Pos(mount_hole_offset, leg_thickness / 2, 0) * Cylinder(hole_r, hole_h)
solid_body = solid_body - Pos(leg_thickness / 2, mount_hole_offset, 0) * Cylinder(hole_r, hole_h)

with BuildPart() as rib_p:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_bl:
            rl1 = Line((leg_thickness, leg_thickness), (leg_thickness + rib_thickness, leg_thickness))
            rl2 = Line(rl1 @ 1, (leg_thickness, leg_thickness + rib_height))
            rl3 = Line(rl2 @ 1, (leg_thickness, leg_thickness))
        make_face()
    extrude(amount=rib_offset)

solid_body = solid_body + rib_p.part

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")