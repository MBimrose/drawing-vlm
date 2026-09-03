from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
slot_stem_width = 6.0
slot_stem_length = 30.0
slot_top_width = 20.0
slot_top_thickness = 6.0
hole_diameter = 4.0
hole_offset_from_slot = 15.0
gusset_height = 12.0
gusset_width = 20.0

solid_body = Box(plate_length, plate_width, plate_thickness)

slot_stem = Box(slot_stem_width, slot_stem_length, plate_thickness + 2)
slot_top = Pos(0, slot_stem_length/2 - slot_top_thickness/2, 0) * Box(slot_top_width, slot_top_thickness, plate_thickness + 2)
solid_body = solid_body - slot_stem - slot_top

hole_positions = [
    (-slot_stem_length/2 - hole_offset_from_slot, 0),
    (slot_stem_length/2 + hole_offset_from_slot, 0),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 2)

with BuildPart() as gp:
    with BuildSketch(Plane.XY.offset(-plate_thickness/2)) as gs:
        with BuildLine() as gl:
            Polyline((0, -gusset_width/2), (0, gusset_width/2), (-gusset_height, 0), close=True)
        make_face()
    extrude(amount=plate_thickness)
gusset = gp.part

solid_body = solid_body + Pos(plate_length/2, 0, 0) * gusset
solid_body = solid_body + Pos(-plate_length/2, 0, 0) * mirror(gusset, about=Plane.YZ)

part = solid_body
part.name = "plate_with_slot_holes_and_gussets"
export_step(part, "output.step")