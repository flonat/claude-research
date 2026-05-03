#!/bin/bash
# paper-book-deploy.sh — one-shot wrapper for /paper-book deploy
#
# Builds both public and private variants of a paper-book, rsyncs each to
# its target on the VPS, updates atlas frontmatter, regenerates the root
# index, and purges Cloudflare cache.
#
# Usage:
#   paper-book-deploy.sh <book-dir> [public|private|both]
#
# Defaults to "both". Examples:
#   paper-book-deploy.sh /Volumes/SSD/Dropbox/Research/OR/quiver-ea/paper-acm-gecco/book
#   paper-book-deploy.sh ./book public        # public only
#   paper-book-deploy.sh ./book private       # private only
#
# Requires:
#   - 1Password service account env at /Volumes/Secrets/1password-service-account.env
#   - SSH access to VPS (rsync target)
#   - npm + Python 3 in PATH

set -euo pipefail

TM="${TM:-$HOME/Task-Management}"

if [ $# -lt 1 ]; then
    echo "usage: $0 <book-dir> [public|private|both]" >&2
    exit 2
fi

BOOK_DIR="$(cd "$1" && pwd)"
VARIANT="${2:-both}"

if [ ! -d "$BOOK_DIR" ]; then
    echo "book-dir does not exist: $BOOK_DIR" >&2
    exit 1
fi

# Resolve slug from project directory name (book-dir is paper-<venue>/book)
SLUG="$(basename "$(dirname "$(dirname "$BOOK_DIR")")")"
echo "[deploy] book=$BOOK_DIR  slug=$SLUG  variant=$VARIANT"

deploy_one() {
    local v="$1"
    local target_path
    if [ "$v" = "public" ]; then
        target_path="/opt/user/data/books/$SLUG/"
    else
        target_path="/opt/user/data/books/private/$SLUG/"
    fi
    echo
    echo "─── building $v ───"
    python3 "$TM/.scripts/build_book_variant.py" "$BOOK_DIR" "$v"
    echo "─── rsync $v → vps:$target_path ───"
    rsync -avz --delete "$BOOK_DIR/_build-$v/html/" "vps:$target_path" \
        | tail -3
}

case "$VARIANT" in
    public|private)
        deploy_one "$VARIANT"
        ;;
    both)
        deploy_one public
        deploy_one private
        ;;
    *)
        echo "unknown variant: $VARIANT (expected public|private|both)" >&2
        exit 2
        ;;
esac

echo
echo "─── update atlas frontmatter (book_url) ───"
python3 "$TM/.scripts/update_atlas_book_url.py" \
    --slug "$SLUG" \
    --url "https://books.user.com/$SLUG/"

echo
echo "─── regen root index ───"
python3 "$TM/.scripts/gen_books_index.py" --out /tmp/books-index.html --rsync

echo
echo "─── purge Cloudflare edge cache ───"
# shellcheck disable=SC1091
source /Volumes/Secrets/1password-service-account.env
CF_TOKEN="$(op read "op://Research/Claude Code/CLOUDFLARE_API_TOKEN")"
curl -sf -X POST "https://api.cloudflare.com/client/v4/zones/4ac4b9388b993f5c83e44ffd81857eac/purge_cache" \
    -H "Authorization: Bearer $CF_TOKEN" \
    -H "Content-Type: application/json" \
    --data '{"hosts":["books.user.com"]}' \
    | python3 -c "import sys,json; print('  purge:', json.load(sys.stdin).get('success'))"

echo
echo "─── smoke test ───"
echo -n "  public  → "
curl -s -o /dev/null -w "%{http_code}\n" --resolve books.user.com:443:104.21.22.163 \
    "https://books.user.com/$SLUG/"
echo -n "  private → "
curl -s -o /dev/null -w "%{http_code} (302 = Access-protected as expected)\n" \
    --resolve books.user.com:443:104.21.22.163 \
    "https://books.user.com/private/$SLUG/"

echo
echo "✓ deployed: https://books.user.com/$SLUG/  +  /private/$SLUG/"
