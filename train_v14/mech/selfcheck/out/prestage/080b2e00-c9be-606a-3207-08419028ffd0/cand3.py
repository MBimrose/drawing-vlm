from build123d import *

plate_width = 60.0
plate_depth = 45.0
plate_thickness = 5.0
corner_fillet_radius = 4.0
top_chamfer = 0.8
slot_width = 30.0
slot_height = 10.0
slot_offset_y = 15.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset_y = 15.0

solid = Box(plate_width, plate_depth, plate_thickness)
solid = fillet(solid.edges().filter_by(Axis.Z), corner_fillet_radius)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), top_chamfer)

slot_cut = Pos(0, slot_offset_y - plate_depth/2, 0) * Box(slot_width, slot_height, plate_thickness * 2)
solid = solid - slot_cut

hole_cut = Cylinder(hole_diameter/2, plate_thickness * 2)
for x in [-hole_spacing/2, hole_spacing/2]:
    solid = solid - Pos(x, hole_offset_y - plate_depth/2, 0) * hole_cut

part = solid
part.name = "plate_with_slot_and_holes"
export_step(part, "output.step")