from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 12.0
corner_radius = 8.0
slot_width = 10.0
slot_depth = 8.0
slot_length = plate_length - 2 * corner_radius
mount_hole_diameter = 6.0
mount_hole_offset = 8.0
chamfer_distance = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-plate_length/2, -plate_width/2), (plate_length/2, -plate_width/2))
            a1 = ThreePointArc(l1@1, (plate_length/2 + corner_radius, 0), (plate_length/2, plate_width/2))
            l2 = Line(a1@1, (-plate_length/2, plate_width/2))
            a2 = ThreePointArc(l2@1, (-plate_length/2 - corner_radius, 0), (-plate_length/2, -plate_width/2))
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

slot_box = Pos(0, 0, plate_thickness - slot_depth/2) * Box(slot_length, slot_width, slot_depth)
solid_body = solid_body - slot_box

hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    hole = Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_slot_and_holes"
export_step(part, "output.step")