#!/bin/sh
# Ledge numbers, free from GitHub: repo traffic (14 days) + release download counts.
R=Saidileepkumarmukkamala/ledge; export GH_TOKEN=$(gh auth token --user Saidileepkumarmukkamala)
echo "== repo views (14d)";   gh api repos/$R/traffic/views  --jq '"\(.count) views, \(.uniques) unique visitors"'
echo "== repo clones (14d)";  gh api repos/$R/traffic/clones --jq '"\(.count) clones, \(.uniques) unique"'
echo "== top referrers";      gh api repos/$R/traffic/popular/referrers --jq '.[] | "\(.referrer): \(.count)"'
echo "== downloads per release asset"
gh api repos/$R/releases --jq '.[] | .tag_name as $t | .assets[] | "\($t) \(.name): \(.download_count)"'
echo "== stars"; gh api repos/$R --jq '.stargazers_count'
