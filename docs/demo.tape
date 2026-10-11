# VHS tape — re-record the walk-forward demo as GIF/MP4/WebM (deterministic, CI-friendly)
# Install: brew install vhs  (requires ttyd + ffmpeg)  |  Docker: ghcr.io/charmbracelet/vhs
Output docs/demo.gif
Output docs/demo.mp4
Output docs/demo.webm
Set Width 1280
Set Height 720
Set FontSize 22
Set Theme "Catppuccin Frappe"
Hide
Type "cd /home/md/src/pardo-evaluation-optimization-wfa-benchmark-2026 && python3 -m pytest tests/ -q && bash scripts/run_all.sh"
Enter
Sleep 2s
Show
Type "python3 experiments/03_walkforward.py --config config/experiment.yaml"
Enter
Sleep 3s
Type "ls -lh docs/*.png docs/*.gif results/*.csv | head -n 20"
Enter
Sleep 2s
