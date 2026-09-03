from build123d import *

bracket_length = 80.0
bracket_width = 60.0
bracket_thickness = 10.0
wall_thickness = 1.0
chamfer_distance = 2.0
notch_width = 10.0
notch_depth = 8.0
rib_width = 6.0
rib_height = 4.0
rib_offset = 12.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 6.0
mount_hole_diameter = 4.0
mount_hole_cbore_diameter = 6.0
mount_hole_cbore_depth = 2.0
mount_hole_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-bracket_length/2, -bracket_width/2),
                (bracket_length/2, -bracket_width/2),
                (bracket_length/2, bracket_width/2 - notch_depth),
                (bracket_length/2 - notch_width, bracket_width/2 - notch_depth),
                (bracket_length/2 - notch_width, bracket_width/2),
                (-bracket_length/2, bracket_width/2),
                close=True
            )
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

rib = Pos(0, rib_offset, bracket_thickness/2) * Box(bracket_length - 2*wall_thickness, rib_width, rib_height)
solid_body = solid_body + rib

pocket = Pos(bracket_length/2 - pocket_depth/2, 0, bracket_thickness/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    cbore = Pos(bracket_length/2 - mount_hole_cbore_depth/2, y, bracket_thickness/2) * Rot(0, 90, 0) * Cylinder(mount_hole_cbore_diameter/2, mount_hole_cbore_depth)
    solid_body = solid_body - cbore
    shaft = Pos(0, y, bracket_thickness/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, bracket_length + 10)
    solid_body = solid_body - shaft

part = solid_body
part.name = "bracket"
export_step(part, "output.step")