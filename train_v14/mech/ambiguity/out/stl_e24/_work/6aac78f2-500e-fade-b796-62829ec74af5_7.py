from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 10.0
wall_thickness = 1.0
chamfer_size = 2.0
notch_width = 10.0
notch_depth = 8.0
rib_length = 30.0
rib_width = 6.0
rib_height = 4.0
rib_offset = 20.0
slot_length = 40.0
slot_width = 5.0
slot_depth = 8.0
hole_diameter = 4.0
cbore_diameter = 6.0
cbore_depth = 2.0
hole_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-plate_length/2, -plate_width/2),
                (plate_length/2, -plate_width/2),
                (plate_length/2, plate_width/2),
                (-plate_length/2 + notch_width, plate_width/2),
                (-plate_length/2 + notch_width, plate_width/2 - notch_depth),
                (-plate_length/2, plate_width/2 - notch_depth),
                (-plate_length/2, -plate_width/2),
                close=True
            )
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

rib1 = Pos(rib_offset, 0, plate_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
rib2 = Pos(-rib_offset, 0, plate_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib1 + rib2

slot = Pos(0, plate_width/2 - slot_depth/2, plate_thickness/2) * Box(slot_length, slot_depth, slot_width)
solid_body = solid_body - slot

for y in [-hole_spacing/2, hole_spacing/2]:
    cbore = Pos(plate_length/2 - cbore_depth/2, y, plate_thickness/2) * Rot(0, 90, 0) * Cylinder(cbore_diameter/2, cbore_depth)
    shaft = Pos(0, y, plate_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, plate_length + 10)
    solid_body = solid_body - cbore - shaft

part = solid_body
part.name = "plate_with_notch_ribs_slot_holes"
export_step(part, "output.step")