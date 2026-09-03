from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_height = 6.0
frame_thickness = 5.0
hole_diameter = 4.0
hole_spacing = 15.0
fillet_vertical = 1.5
fillet_bottom = 0.8

inner_length = base_length - 2 * frame_thickness
inner_width = base_width - 2 * frame_thickness

solid = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
solid = fillet(solid.edges().filter_by(Axis.Z), fillet_vertical)
bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = fillet(bottom_face.edges(), fillet_bottom)

frame = Pos(0, 0, base_thickness + frame_height/2) * Box(inner_length, inner_width, frame_height)
solid = solid + frame

cutout = Pos(0, 0, base_thickness + frame_height/2) * Box(inner_length - 2*frame_thickness, inner_width - 2*frame_thickness, frame_height)
solid = solid - cutout

hole_r = hole_diameter / 2
hole_h = base_thickness + frame_height + 10
for y in [-hole_spacing/2, hole_spacing/2]:
    solid = solid - Pos(-base_length/2, y, base_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
    solid = solid - Pos(base_length/2, y, base_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
for x in [-hole_spacing/2, hole_spacing/2]:
    solid = solid - Pos(x, -base_width/2, base_thickness/2) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)
    solid = solid - Pos(x, base_width/2, base_thickness/2) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)

part = solid
part.name = "base_plate_with_frame"
export_step(part, "output.step")