#!/bin/bash

# WBF Newsletter Send Script
# Uses Himalaya to send emails to subscribers

SUBSCRIBERS_FILE="${HOME}/Desktop/WBF/subscribers.json"
ACCOUNT="wbf"
SUBJECT="${1:-Work Brings Freedom Dispatch}"
BODY_FILE="${2}"

if [ ! -f "$SUBSCRIBERS_FILE" ]; then
    echo "Error: Subscribers file not found at $SUBSCRIBERS_FILE"
    exit 1
fi

if [ -z "$BODY_FILE" ] || [ ! -f "$BODY_FILE" ]; then
    echo "Usage: $0 \"Subject Line\" /path/to/email-body.txt"
    echo ""
    echo "Example:"
    echo "  $0 \"April Newsletter - Banned Books Vol. 3\" ~/Desktop/WBF/newsletter.txt"
    exit 1
fi

# Extract emails from subscribers.json
EMAILS=$(cat "$SUBSCRIBERS_FILE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for sub in data:
        print(sub['email'])
except:
    pass
")

if [ -z "$EMAILS" ]; then
    echo "No subscribers found."
    exit 0
fi

TOTAL=$(echo "$EMAILS" | wc -l | tr -d ' ')
echo "Found $TOTAL subscribers"
echo "Subject: $SUBJECT"
echo "Body file: $BODY_FILE"
echo ""
read -p "Press Enter to send, or Ctrl+C to cancel..."

# Send to each subscriber
COUNT=0
for EMAIL in $EMAILS; do
    COUNT=$((COUNT + 1))
    echo "[$COUNT/$TOTAL] Sending to $EMAIL..."
    
    himalaya message send \
        --account "$ACCOUNT" \
        <<EOF
From: dispatch@workbringsfreedom.com
To: $EMAIL
Subject: $SUBJECT
$(cat "$BODY_FILE")
EOF
    
    if [ $? -eq 0 ]; then
        echo "  ✓ Sent"
    else
        echo "  ✗ Failed (see /tmp/wbf-newsletter-errors.log)"
    fi
    
    # Small delay to avoid rate limiting
    sleep 2
done

echo ""
echo "Done! $COUNT emails sent."
