cd /projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm
MAXTOK=30000 EFFORT=75 bash train_v14/serv19/dsv41_eval_serv19.sh runs/dsv41_gen_pilot_think pilot_think think
MAXTOK=30000 EFFORT=75 bash train_v14/serv19/dsv41_eval_serv19.sh runs/dsv41_gen_think_2n/step_1300 gen2n_step_1300 think
bash train_v14/serv19/dsv41_rep_eval_serv19.sh runs/dsv41_rep_r32 rep_r32
