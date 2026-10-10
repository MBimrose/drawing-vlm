DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV; O=results/cycle2/rp4
rm -rf $O/tier_rp2; .venv/bin/python train_v14/geom/pack_repair_shards.py --bo $O/rp2_inputs.json --png-dir $O/png_rp2 \
  --bench train_v14/mech/benchmarks/data/rft_realpool_v2 --targets $O/rp2_targets.json --out $O/tier_rp2 --per-shard 500
