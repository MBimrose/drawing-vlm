from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 80.0
leg_thickness = 8.0
bracket_depth = 20.0
wall_thickness = 4.0
rib_width = 6.0
rib_height = 6.0
rib_depth = 12.0
fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_cbore_diameter = 8.0
mount_hole_cbore_depth = 3.0
mount_hole_spacing = 30.0
pocket_width = 20.0
pocket_height = 30.0
pocket_depth = wall_thickness
notch_width = 10.0
notch_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_leg_length,0), (horizontal_leg_length,leg_thickness),
                     (leg_thickness,leg_thickness), (leg_thickness,vertical_leg_length),
                     (0,vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

rib = Pos(leg_thickness/2, leg_thickness/2, rib_depth/2) * Box(rib_width, rib_height, rib_depth)
solid_body = solid_body + rib

hole_y = leg_thickness / 2
hole_x1 = horizontal_leg_length / 2 - mount_hole_spacing / 2
hole_x2 = horizontal_leg_length / 2 + mount_hole_spacing / 2

for hx, hy in [(hole_x1, hole_y), (hole_x2, hole_y)]:
    solid_body = solid_body - Pos(hx, hy, 0) * Cylinder(mount_hole_diameter/2, bracket_depth + 1)
    solid_body = solid_body - Pos(hx, hy, 0) * Cylinder(mount_hole_cbore_diameter/2, mount_hole_cbore_depth)

pocket = Pos(wall_thickness/2, vertical_leg_length - pocket_height/2, bracket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

notch = Pos(horizontal_leg_length - notch_width/2, leg_thickness/2, bracket_depth - notch_depth/2) * Box(notch_width, leg_thickness, notch_depth)
solid_body = solid_body - notch

part = solid_body
part.name = "L_Bracket_Mount"
export_step(part, "output.step")