#!/usr/bin/env bash
# The drawing renderer env on the cluster (login node; needs network): same pins as
# /srv/scratch/bimrose2/dw_venv on the serv boxes -- draftwright 0.4.23 with the VLM font patch
# (_core.py: _FONT_SIZE = 5.25; upstream 3.0), build123d 0.10.0, cadquery-ocp 7.8.1.1.post1.
# There is NO legacy fallback anywhere: a part that will not draw is a recorded failure.
set -uo pipefail
DV=/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm; cd $DV
export UV_CACHE_DIR=$DV/.uv_cache; UV=$(command -v uv || echo $HOME/.local/bin/uv); VP=$DV/dw_venv/bin/python
[ -x $VP ] || $UV venv dw_venv --python 3.11
$UV pip install --python $VP --quiet "draftwright==0.4.23" "build123d==0.10.0" "cadquery-ocp==7.8.1.1.post1" \
  "cairosvg==2.9.1" "ezdxf==1.4.4" "ocpsvg==0.5.0" "svgwrite==1.4.3" "trimesh==5.1.0" "numpy==2.4.6" "pillow==12.3.0" "lxml==6.1.3" || echo "install rc=$?"
CORE=$(ls dw_venv/lib/python3.11/site-packages/draftwright/_core.py)
grep -n "^_FONT_SIZE" $CORE
sed -i -E 's/^_FONT_SIZE = [0-9.]+.*/_FONT_SIZE = 5.25  # annotation text height (page-mm); upstream 3.0, raised to 5.25 for VLM legibility/' $CORE
grep -n "^_FONT_SIZE" $CORE
$VP -c "import draftwright, build123d, OCP, cairosvg; print('draftwright', draftwright.__version__, 'build123d', build123d.__version__)"
echo "DW VENV DONE $(date)"
