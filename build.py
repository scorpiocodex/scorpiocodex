#!/usr/bin/env python3
"""Regenerate assets/generated/*.svg from data/profile.json and live GitHub data.

    python3 build.py           write the images
    python3 build.py --check   render and validate only (used on pull requests)

Needs Python 3.10+ and no third-party packages. Locally it uses your `gh` login;
in GitHub Actions it uses GITHUB_TOKEN.
"""
import sys

from profilegen.build import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
