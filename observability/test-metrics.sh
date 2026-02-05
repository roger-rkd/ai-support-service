#!/bin/bash
# Test script to generate metrics for the AI Support Service

SERVICE_URL="${SERVICE_URL:-http://localhost:8000}"
NUM_REQUESTS="${NUM_REQUESTS:-10}"

echo "Testing AI Support Service Metrics"
echo "==================================="
echo "Service URL: $SERVICE_URL"
echo "Number of requests: $NUM_REQUESTS"
echo ""

# Test health endpoint
echo "1. Testing health endpoint..."
for i in $(seq 1 $NUM_REQUESTS); do
    response=$(curl -s -w "\n%{http_code}" "$SERVICE_URL/health")
    status=$(echo "$response" | tail -n 1)
    if [ "$status" = "200" ]; then
        echo "  ✓ Health check $i/$NUM_REQUESTS - OK"
    else
        echo "  ✗ Health check $i/$NUM_REQUESTS - Failed (HTTP $status)"
    fi
    sleep 0.5
done

echo ""
echo "2. Testing /ask endpoint..."

# Sample questions
questions=(
    "How do I reset my password?"
    "How do I update my billing information?"
    "What are your support hours?"
    "How can I contact technical support?"
    "How do I delete my account?"
)

for i in $(seq 1 $NUM_REQUESTS); do
    question_index=$((i % ${#questions[@]}))
    question="${questions[$question_index]}"

    echo "  Request $i/$NUM_REQUESTS: \"$question\""

    response=$(curl -s -w "\n%{http_code}" \
        -X POST "$SERVICE_URL/ask" \
        -H "Content-Type: application/json" \
        -d "{\"question\":\"$question\"}")

    status=$(echo "$response" | tail -n 1)

    if [ "$status" = "200" ]; then
        answer=$(echo "$response" | head -n -1 | jq -r '.answer' | cut -c1-80)
        echo "  ✓ Response: ${answer}..."
    else
        echo "  ✗ Failed (HTTP $status)"
    fi

    sleep 2
done

echo ""
echo "3. Viewing metrics..."
echo ""
curl -s "$SERVICE_URL/metrics" | grep -E "(ai_support_requests_total|ai_support_request_latency|ai_support_rag)" | head -20

echo ""
echo "==================================="
echo "Test complete!"
echo ""
echo "View metrics:"
echo "  Raw: $SERVICE_URL/metrics"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3000"
