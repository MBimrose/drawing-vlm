from build123d import *

channel_length = 90.0
channel_outer_width = 30.0
channel_outer_height = 20.0
wall_thickness = 2.0
rib_thickness = 1.0
rib_spacing = 15.0
step_count = 3
step_height = 4.0
step_thickness = 2.0
chamfer_distance = 1.5

outer = Pos(0, 0, channel_outer_height/2) * Box(channel_length, channel_outer_width, channel_outer_height)
top_face = outer.faces().sort_by(Axis.Z)[-1]
hollow = offset(outer, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, channel_outer_width/2 - wall_thickness/2, (channel_outer_height - wall_thickness)/2) * Box(rib_thickness, channel_length, channel_outer_height - wall_thickness)
rib_mirrored = mirror(rib, about=Plane.YZ)
ribs = rib + rib_mirrored

steps = None
for i in range(step_count):
    step_z = wall_thickness + i * step_height
    step_width = channel_outer_width - 2*wall_thickness - i*step_thickness
    step = Pos(0, step_width/2, step_z/2) * Box(step_thickness, channel_length - 10, step_z)
    if steps is None:
        steps = step
    else:
        steps = steps + step

result = hollow + ribs - steps
top_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_distance)

part = result
part.name = "channel_with_ribs_and_steps"
export_step(part, OUTPUT_PATH)