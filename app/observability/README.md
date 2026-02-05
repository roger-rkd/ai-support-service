# Observability Module

This module provides Prometheus metrics for monitoring the AI Support Service.

## Metrics

### Request Metrics

**`ai_support_requests_total`** (Counter)
- Total number of requests to the AI support service
- Labels: `endpoint`, `method`, `status`
- Example: `ai_support_requests_total{endpoint="/ask",method="POST",status="success"}`

**`ai_support_request_failures_total`** (Counter)
- Total number of failed requests
- Labels: `endpoint`, `error_type`
- Example: `ai_support_request_failures_total{endpoint="/ask",error_type="ValueError"}`

**`ai_support_request_latency_seconds`** (Histogram)
- Request latency in seconds
- Labels: `endpoint`
- Buckets: 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, +Inf

### RAG Pipeline Metrics

**`ai_support_rag_pipeline_latency_seconds`** (Histogram)
- Total RAG pipeline processing latency
- Buckets: 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, +Inf

**`ai_support_rag_retrieval_latency_seconds`** (Histogram)
- Document retrieval latency
- Buckets: 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, +Inf

**`ai_support_rag_generation_latency_seconds`** (Histogram)
- Answer generation latency (LLM call)
- Buckets: 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, +Inf

**`ai_support_documents_retrieved`** (Histogram)
- Number of documents retrieved per query
- Buckets: 1, 2, 3, 4, 5, 10, 20, 50, +Inf

## Accessing Metrics

Metrics are exposed at the `/metrics` endpoint in Prometheus text format:

```bash
curl http://localhost:8000/metrics
```

## Prometheus Configuration

Add this job to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'ai-support-service'
    scrape_interval: 15s
    static_configs:
      - targets: ['ai-support-service:8000']
    metrics_path: '/metrics'
```

For Kubernetes deployments:

```yaml
scrape_configs:
  - job_name: 'ai-support-service-k8s'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - default
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: ai-support-service
      - source_labels: [__meta_kubernetes_pod_ip]
        action: replace
        target_label: __address__
        replacement: $1:8000
```

## Example Queries

### Request Rate
```promql
# Requests per second
rate(ai_support_requests_total[5m])

# Success rate
rate(ai_support_requests_total{status="success"}[5m])
  /
rate(ai_support_requests_total[5m])

# Error rate
rate(ai_support_requests_total{status="error"}[5m])
```

### Latency
```promql
# 95th percentile latency
histogram_quantile(0.95,
  rate(ai_support_request_latency_seconds_bucket[5m])
)

# Average RAG pipeline latency
rate(ai_support_rag_pipeline_latency_seconds_sum[5m])
  /
rate(ai_support_rag_pipeline_latency_seconds_count[5m])
```

### RAG Performance
```promql
# Retrieval vs Generation latency
rate(ai_support_rag_retrieval_latency_seconds_sum[5m])
  /
rate(ai_support_rag_generation_latency_seconds_sum[5m])

# Average documents retrieved
rate(ai_support_documents_retrieved_sum[5m])
  /
rate(ai_support_documents_retrieved_count[5m])
```

### Errors
```promql
# Total errors by type
sum by (error_type) (
  rate(ai_support_request_failures_total[5m])
)

# Error rate percentage
100 * rate(ai_support_request_failures_total[5m])
  /
rate(ai_support_requests_total[5m])
```

## Alerts

Example Prometheus alert rules:

```yaml
groups:
  - name: ai_support_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          rate(ai_support_request_failures_total[5m])
            /
          rate(ai_support_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            rate(ai_support_request_latency_seconds_bucket[5m])
          ) > 30
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "95th percentile latency is {{ $value }}s"

      - alert: SlowRAGPipeline
        expr: |
          histogram_quantile(0.95,
            rate(ai_support_rag_pipeline_latency_seconds_bucket[5m])
          ) > 20
        for: 5m
        labels:
          severity: info
        annotations:
          summary: "RAG pipeline is slow"
          description: "95th percentile RAG latency is {{ $value }}s"
```

## Grafana Dashboard

Import the dashboard from `observability/grafana-dashboard.json` for visualization.

Key panels:
- Request rate and success rate
- Latency percentiles (p50, p95, p99)
- RAG pipeline breakdown
- Error rates by type
- Documents retrieved per query

## Development

### Adding New Metrics

1. Define the metric in `metrics.py`:
```python
from prometheus_client import Counter

my_metric = Counter(
    'ai_support_my_metric_total',
    'Description of my metric',
    ['label1', 'label2']
)
```

2. Record the metric in your code:
```python
from app.observability import metrics

metrics.my_metric.labels(label1="value1", label2="value2").inc()
```

### Testing Metrics

```python
import pytest
from app.observability import metrics

def test_request_count():
    # Reset metrics
    metrics.request_count.clear()

    # Record a request
    metrics.record_request(endpoint="/test", method="GET", status="success")

    # Verify
    assert metrics.request_count.labels(
        endpoint="/test",
        method="GET",
        status="success"
    )._value.get() == 1
```
