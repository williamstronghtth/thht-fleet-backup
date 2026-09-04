# Task: Rework THHT Community Pages V2 Design

**From:** Ryan Chen (Software Engineer)
**Priority:** High — Chris requested this directly
**Date:** 2026-06-08

## Context

We built community pages for 5 NH towns (Hollis, Amherst, Mont Vernon, Milford, Nashua) and deployed them to WordPress at thehooverhometeam.com. Chris wants the V2 design reworked by you since you're the marketing/design expert.

## What Exists Now

- **Landing page:** thehooverhometeam.com/communities/
- **Town pages:** /communities/hollis-nh/, /communities/amherst-nh/, /communities/mont-vernon-nh/, /communities/milford-nh/, /communities/nashua-nh/
- **Deploy script:** `thht-communities/scripts/deploy-v2.py` (in your workspace)

## Current V2 Features
- Hero images with gradient overlays (Unsplash stock photos)
- Quick stats bar (population, median home price, income, school rating)
- GEO-optimized content sections (About, Why Live Here)
- Google Places data baked in (restaurants, coffee, shopping, parks, beauty & wellness)
- Schools section with Primary/Middle/High filter tabs and ratings table
- Explore-more community grid with thumbnails
- CTA sections

## Design Inspiration
Chris shared screenshots of the **Meyer Lucas team's Jupiter FL community pages** as the target design quality. Their pages have:
- Professional hero imagery with text overlays
- Rich GEO content
- School listings with filter tabs
- Clean, modern real estate aesthetic

## What Chris Wants
A design rework — better layout, typography, colors, visual hierarchy, and overall marketing polish. You have full creative control as the marketing/design expert.

## Technical Notes
- Pages are deployed via Python script that pushes HTML to WordPress REST API
- CSS is inline (embedded in the HTML content) using `thht-v2__*` class namespace
- Google Fonts: currently using Playfair Display (headlines) + Lato (body)
- The script fetches Google Places data at deploy time and bakes it into the HTML
- WordPress credentials and API key are in the deploy script
- To test changes, run: `GOOGLE_PLACES_API_KEY=<key> python3 scripts/deploy-v2.py`

## Deliverable
Update the HTML/CSS in `deploy-v2.py` to create a more polished, professional design. The script structure (fetching places, deploying to WP) should stay the same — just rework the visual design and content layout.

When done, let me know and I'll review + deploy, or you can deploy directly with the script.
