from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
thickness = 10.0
rib_width = 6.0
rib_height = 30.0
rib_thickness = 4.0
pocket_width = 20.0
pocket_depth = 6.0
pocket_offset_from_end = 15.0
counterbore_diameter = 8.0
counterbore_depth = 4.0
through_hole_diameter = 4.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, thickness),
                     (thickness, thickness), (thickness, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

rib = Pos(thickness/2, vertical_leg_length/2, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

pocket_center_x = horizontal_leg_length - pocket_offset_from_end - pocket_width/2
pocket = Pos(pocket_center_x, thickness/2, thickness - pocket_depth/2) * Box(pocket_width, pocket_depth, pocket_depth)
solid_body = solid_body - pocket

cbore = Pos(thickness/2, vertical_leg_length/2, thickness - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - cbore

thru = Pos(thickness/2, vertical_leg_length/2, thickness/2) * Cylinder(through_hole_diameter/2, thickness)
solid_body = solid_body - thru

for i in range(2):
    x = horizontal_leg_length/2 + (i - 0.5) * mount_hole_spacing
    hole = Pos(x, 0, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)
    solid_body = solid_body - hole

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")