from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
t_slot_stem_width = 6.0
t_slot_stem_length = 20.0
t_slot_top_width = 30.0
t_slot_top_thickness = 6.0
gusset_height = 12.0
gusset_width = 20.0
chamfer_size = 0.5
hole_diameter = 4.0
hole_spacing = 60.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

stem = Box(t_slot_stem_width, t_slot_stem_length, plate_thickness)
top_bar = Pos(0, t_slot_stem_length/2 + t_slot_top_thickness/2, 0) * Box(t_slot_top_width, t_slot_top_thickness, plate_thickness)
solid_body = solid_body - stem - top_bar

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness)

with BuildPart() as gp:
    with BuildSketch(Plane.XY.offset(-plate_thickness/2)) as sk:
        with BuildLine() as bl:
            Polyline((0, -gusset_width/2), (gusset_height, 0), (0, gusset_width/2), close=True)
        make_face()
    extrude(amount=plate_thickness)
gusset = gp.part

solid_body = solid_body + Pos(plate_length/2, 0, 0) * gusset
solid_body = solid_body + Pos(-plate_length/2, 0, 0) * mirror(gusset, about=Plane.YZ)

part = solid_body
part.name = "plate_with_tslot_gussets"
export_step(part, "output.step")