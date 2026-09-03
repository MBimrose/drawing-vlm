from build123d import *

horizontal_length = 80.0
vertical_length = 70.0
thickness = 8.0
width = 12.0
fillet_radius = 3.0
clearance_hole_diameter = 6.0
mount_hole_diameter = 4.0
slot_width = 6.0
slot_length = 20.0
slot_depth = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_length, 0), (horizontal_length, thickness),
                     (thickness, thickness), (thickness, vertical_length), (0, vertical_length), close=True)
        make_face()
    extrude(amount=width)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - thickness) < 1e-3 and abs(e.center().Y - thickness) < 1e-3]
solid_body = fillet(inner_edges, fillet_radius)

solid_body = solid_body - Pos(thickness/2, vertical_length/2, width/2) * Cylinder(clearance_hole_diameter/2, width + 10)

for x, y in [(horizontal_length/3, thickness/2), (2*horizontal_length/3, thickness/2)]:
    solid_body = solid_body - Pos(x, y, width/2) * Cylinder(mount_hole_diameter/2, width + 10)

slot_box = Pos(horizontal_length - slot_length/2, thickness/2, slot_depth/2) * Box(slot_length, slot_width, slot_depth)
solid_body = solid_body - slot_box

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")