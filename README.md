# \# Media Library

# 

# A command-line tool for browsing and searching my physical media collection —

# VHS, DVD, and Blu-ray movies plus TV series on disc — cataloged from actual

# shelf photos.

# 

# \## What it does

# 

# \- Search the collection by title

# \- Filter by format (VHS / DVD / Blu-ray)

# \- List what's missing from partially-owned franchises (Harry Potter, Star

# &#x20; Wars, James Bond, and more)

# \- Quick stats on the whole collection at a glance

# 

# \## Usage

# 

# \\`\\`\\`

# python media\_library.py                # list everything

# python media\_library.py search harry    # search by title

# python media\_library.py format dvd      # filter by format

# python media\_library.py have            # only what I own

# python media\_library.py need            # only what's missing

# python media\_library.py stats           # counts by format and status

# \\`\\`\\`

# 

# \## Data

# 

# Everything lives in `media.json` — one entry per title, with format,

# category (movie/tv), status (have/need), and collection grouping for

# partially-owned franchises.

