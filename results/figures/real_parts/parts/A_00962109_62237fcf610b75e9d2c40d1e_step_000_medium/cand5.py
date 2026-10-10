from build123d import *
import math

central_radius = 12.0
lobe_radius = 15.0
lobe_offset = 28.0
thickness = 8.0
shell_thickness = 0.7
fillet_radius = 1.5

central = Cylinder(central_radius, thickness)
lobe = Cylinder(lobe_radius, thickness)

lobe0 = Pos(lobe_offset, 0, 0) * lobe
lobe1 = Pos(-lobe_offset/2, lobe_offset*0.8660254, 0) * lobe
lobe2 = Pos(-lobe_offset/2, -lobe_offset*0.8660254, 0) * lobe

base = central + lobe0 + lobe1 + lobe2
base = fillet(base.edges(), fillet_radius)
part = offset(base, amount=-shell_thickness)
part.name = "shelled_lobed_disk"
export_step(part, "output.step")