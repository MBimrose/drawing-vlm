from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
slot_length = 20.0
slot_width = 5.0
slot_depth = 6.0
hole_diameter = 8.0
hole_offset_x = 15.0
gusset_height = 12.0
gusset_thickness = 6.0
fillet_radius = 1.0

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)

slot_cut = Pos(0, bracket_width/2 - slot_depth/2, 0) * Box(slot_length, slot_depth, slot_width)
base = base - slot_cut

hole_cut = Pos(hole_offset_x, 0, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)
base = base - hole_cut

with BuildPart() as gp:
    with BuildSketch(Plane.XZ.offset(bracket_width/2)) as sk:
        with BuildLine() as bl:
            Polyline((-gusset_height/2, 0), (gusset_height/2, 0), (0, gusset_thickness), close=True)
        make_face()
    extrude(amount=bracket_thickness)
gusset = gp.part

result = base + gusset
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "bracket"
export_step(part, "output.step")