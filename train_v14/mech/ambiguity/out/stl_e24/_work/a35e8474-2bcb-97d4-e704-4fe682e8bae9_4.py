from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
thickness = 8.0
depth = 12.0
fillet_radius = 4.0
slot_length = 20.0
slot_width = 6.0
slot_depth = 6.0
blind_hole_diameter = 6.0
blind_hole_depth = 10.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
rib_thickness = 4.0
rib_height = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, thickness),
                     (thickness, thickness), (thickness, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, fillet_radius)

slot_box = Box(slot_length, slot_width, slot_depth)
solid_body = solid_body - Pos(horizontal_leg_length - slot_length/2, thickness/2, slot_depth/2) * slot_box

blind_hole = Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - Pos(thickness/2, vertical_leg_length/2, depth - blind_hole_depth/2) * blind_hole

for x in [horizontal_leg_length/2 - mount_hole_spacing/2, horizontal_leg_length/2 + mount_hole_spacing/2]:
    mount_hole = Cylinder(mount_hole_diameter/2, depth)
    solid_body = solid_body - Pos(x, thickness/2, depth/2) * mount_hole

rib = Box(rib_thickness, rib_height, depth)
solid_body = solid_body + Pos(thickness/2, thickness/2, depth/2) * rib

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")