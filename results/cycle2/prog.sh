#!/bin/bash
# progress: rows done + start-IoU band of the last 20 rows, cluster pool and serv-20 rp2 pool
C=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/cycle2/search
b() { python3 -c "
import json,sys
rs=[json.loads(l) for l in sys.stdin]; t=rs[-20:]
print(len(rs),'last20 start mean',round(sum(r['start_iou'] for r in t)/max(1,len(t)),3),'min',round(min(r['start_iou'] for r in t),3),'crossed',sum(r['best_iou']>=0.75>r['start_iou'] for r in rs))"; }
date; echo -n "cluster "; cat $C/gts_all.jsonl | b
echo -n "rp2     "; timeout 30 ssh -o BatchMode=yes wpk-serv-20.mechse.illinois.edu cat /srv/scratch/bimrose2/cycle2/search/gts_rp2.jsonl | b
