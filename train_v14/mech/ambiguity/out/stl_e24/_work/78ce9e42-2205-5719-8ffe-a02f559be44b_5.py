from build123d import *

horizontal_leg_length = 60.0
vertical_leg_length = 50.0
leg_thickness = 8.0
bracket_depth = 8.0
inner_fillet_radius = 3.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
mount_hole_offset_from_top = 15.0
rib_width = 12.0
rib_height = 12.0
rib_thickness = bracket_depth
pocket_diameter = 22.0
pocket_depth = bracket_depth

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), inner_fillet_radius)

hole_y1 = vertical_leg_length - mount_hole_offset_from_top - mount_hole_spacing / 2
hole_y2 = vertical_leg_length - mount_hole_offset_from_top + mount_hole_spacing / 2
hole_x = leg_thickness / 2

for hx, hy in [(hole_x, hole_y1), (hole_x, hole_y2)]:
    solid_body = solid_body - Pos(hx, hy, bracket_depth / 2) * Cylinder(mount_hole_diameter / 2, bracket_depth + 1)

rib = Pos(leg_thickness + rib_width / 2, leg_thickness + rib_height / 2, bracket_depth / 2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

pocket = Pos(leg_thickness, leg_thickness, bracket_depth / 2) * Cylinder(pocket_diameter / 2, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")