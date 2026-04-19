#!/bin/bash
OUTDIR="/rscratch/yuezhouhu/realtime-video.paper/figures/teaser_frames"
TARGET="/rscratch/yuezhouhu/realtime-video.target/outputs/target_only"
DRAFT="/rscratch/yuezhouhu/realtime-video.draft/outputs/draft_only"
RSVG="/rscratch/yuezhouhu/realtime-video/outputs/reward_fixed_-0.7"

for idx in 003 004 000; do
  for f in 0 8 16 24; do
    ffmpeg -y -loglevel error -i "$TARGET/prompt_${idx}.mp4" -vf "select=eq(n\,$f)" -vframes 1 "$OUTDIR/target_${idx}_f${f}.png"
    ffmpeg -y -loglevel error -i "$DRAFT/prompt_${idx}.mp4" -vf "select=eq(n\,$f)" -vframes 1 "$OUTDIR/draft_${idx}_f${f}.png"
    ffmpeg -y -loglevel error -i "$RSVG/prompt_${idx}.mp4" -vf "select=eq(n\,$f)" -vframes 1 "$OUTDIR/rsvg_${idx}_f${f}.png"
  done
done
echo "Done: $(ls $OUTDIR/*.png | wc -l) frames extracted"
