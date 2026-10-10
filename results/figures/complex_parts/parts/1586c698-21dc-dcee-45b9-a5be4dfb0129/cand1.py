from build123d import *

channel_length = 90.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 2.0
gusset_thickness = 3.0
hole_diameter = 5.0
hole_offset_from_end = 10.0
chamfer_size = 0.5
rib_thickness = 1.0
rib_height = channel_height - 2 * wall_thickness

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(rib_thickness, channel_length, rib_height)
base = base + rib

with BuildPart() as gp:
    with BuildSketch(Plane.YZ.offset(channel_length/2)) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (gusset_thickness, 0))
            l2 = Line(l1@1, (gusset_thickness, channel_height))
            l3 = Line(l2@1, (0, channel_height))
            l4 = Line(l3@1, (0, 0))
        make_face()
    extrude(amount=-gusset_thickness)
base = base + gp.part

for x in [-channel_length/2 + hole_offset_from_end, channel_length/2 - hole_offset_from_end]:
    base = base - Pos(x, channel_width/2, channel_height/2) * Cylinder(hole_diameter/2, channel_height)

top_edges = base.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
base = chamfer(top_edges, chamfer_size)

part = base
part.name = "channel_with_gusset"
export_step(part, "output.step")