from build123d import *

chute_length = 80.0
chute_width = 50.0
chute_height = 30.0
wall_thickness = 2.0
slot_bottom_width = 40.0
slot_top_width = 20.0
fillet_radius = 1.0
rib_width = 5.0
rib_depth = 4.0
rib_height = 2.0
rib_spacing = 15.0

base = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as slot_bp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((-slot_bottom_width/2, 0), (slot_bottom_width/2, 0),
                     (slot_top_width/2, chute_height), (-slot_top_width/2, chute_height), close=True)
        make_face()
    extrude(amount=chute_length)
slot_solid = Pos(0, -chute_length/2, 0) * slot_bp.part
base = base - slot_solid

rib_count = int((chute_length - 2 * wall_thickness) // rib_spacing)
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, chute_height + rib_height/2) * Box(rib_width, rib_depth, rib_height)
    base = base + rib

part = base
part.name = "chute_with_ribs"
export_step(part, "output.step")