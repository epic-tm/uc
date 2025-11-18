Ultimate Completionist - packaged web UI + achievement generator
--------------------------------------------------

Files included:
- index.html
- style.css
- script.js            (copied from your upload or placeholder)
- data/data.js         (sample achievements and shards)
- data/achievements.json (sample JSON for generator)
- assets/icons/*       (small icons and any placeholder images found in container)
- assets/achievement/* (9-slice fallbacks used by generator)
- generator.py         (Python script to create achievement PNGs)
- uc_package.zip       (this archive)

Usage (web UI):
1. Open index.html in a browser (serve via a local web server for full functionality, e.g. 'python -m http.server').
2. Edit data/data.js to add your ACHIEVEMENTS, or load from an external JSON file.

Usage (generator):
1. Ensure Pillow is installed: pip install pillow requests
2. Run generator.py to generate single achievements or batch from data/achievements.json:
   python generator.py
   (or import generator.generate_all_from_json in your own scripts)

Notes:
- generator.py supports a RAW_BASE constant if you want to load assets directly from a GitHub repo's raw paths.
- If 9-slice images are not provided, the generator draws a fallback rounded-panel background automatically.

