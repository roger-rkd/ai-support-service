# Observability Setup

Complete observability stack for the AI Support Service with Prometheus and Grafana.

## Quick Start

### Local Development

Start Prometheus and Grafana:

```bash
cd observability
docker-compose up -d
```

Access:
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

The AI Support Service should be running on `localhost:8000` for metrics to be scraped.

### Kubernetes

If using Prometheus Operator:

```bash
kubectl apply -f k8s/servicemonitor.yaml
```

## Architecture

```
┌─────────────────────┐
│  AI Support Service │
│   (Port 8000)       │
│   /metrics endpoint │
└──────────┬──────────┘
           │
           │ scrapes every 15s
           ▼
┌─────────────────────┐
│    Prometheus       │
│   (Port 9090)       │
│  Stores metrics     │
└──────────┬──────────┘
           │
           │ queries
           ▼
┌─────────────────────┐
│     Grafana         │
│   (Port 3000)       │
│  Visualizes data    │
└─────────────────────┘
```

## Metrics Available

See [app/observability/README.md](../app/observability/README.md) for complete metrics documentation.

### Key Metrics

- **Request metrics**: Success/error rates, latency percentiles
- **RAG pipeline**: Retrieval and generation timing
- **Document retrieval**: Number of documents per query
- **Errors**: Detailed error tracking by type

## Grafana Dashboard

The dashboard is automatically provisioned when using docker-compose.

To import manually:
1. Open Grafana (http://localhost:3000)
2. Login (admin/admin)
3. Go to Dashboards → Import
4. Upload `grafana-dashboard.json`

Dashboard includes:
- Request rate and success rate
- Latency percentiles (p50, p95, p99)
- RAG pipeline performance breakdown
- Error rates by type
- Documents retrieved statistics
- Real-time statistics panels

## Configuration Files

### docker-compose.yml
Orchestrates Prometheus and Grafana containers with proper networking and volumes.

### prometheus.yml
Prometheus configuration:
- Scrape interval: 15s
- Targets: AI Support Service on `host.docker.internal:8000`
- Self-monitoring enabled

### grafana-datasource.yml
Automatic Prometheus datasource configuration for Grafana.

### grafana-dashboard.json
Pre-built dashboard with all key metrics visualized.

## Testing Metrics

Generate sample traffic:

```bash
# Health check
for i in {1..10}; do
  curl http://localhost:8000/health
  sleep 1
done

# Ask questions
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I reset my password?"}'

curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I update my billing information?"}'
```

View metrics:
```bash
# Raw Prometheus metrics
curl http://localhost:8000/metrics

# Prometheus UI
open http://localhost:9090

# Grafana dashboard
open http://localhost:3000
```

## Example Queries

Access Prometheus (http://localhost:9090) and try these queries:

### Request Rate
```promql
rate(ai_support_requests_total[5m])
```

### Success Rate
```promql
rate(ai_support_requests_total{status="success"}[5m])
  /
rate(ai_support_requests_total[5m])
```

### P95 Latency
```promql
histogram_quantile(0.95,
  rate(ai_support_request_latency_seconds_bucket[5m])
)
```

### RAG Pipeline Breakdown
```promql
rate(ai_support_rag_retrieval_latency_seconds_sum[5m])
  /
rate(ai_support_rag_retrieval_latency_seconds_count[5m])
```

## Kubernetes Deployment

### With Prometheus Operator

1. Deploy ServiceMonitor:
```bash
kubectl apply -f k8s/servicemonitor.yaml
```

2. Verify scraping:
```bash
# Check ServiceMonitor
kubectl get servicemonitor ai-support-service

# Check if Prometheus is scraping
kubectl port-forward svc/prometheus-operated 9090:9090
# Open http://localhost:9090/targets
```

### Manual Prometheus Configuration

Add to your Prometheus ConfigMap:

```yaml
scrape_configs:
  - job_name: 'ai-support-service'
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
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
```

## Alerts

Example alert rules (save as `alerts.yml`):

```yaml
groups:
  - name: ai_support_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: |
          (
            rate(ai_support_request_failures_total[5m])
            /
            rate(ai_support_requests_total[5m])
          ) > 0.05
        for: 5m
        labels:
          severity: warning
          service: ai-support-service
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            rate(ai_support_request_latency_seconds_bucket[5m])
          ) > 30
        for: 5m
        labels:
          severity: warning
          service: ai-support-service
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }}s (threshold: 30s)"

      - alert: ServiceDown
        expr: up{job="ai-support-service"} == 0
        for: 2m
        labels:
          severity: critical
          service: ai-support-service
        annotations:
          summary: "AI Support Service is down"
          description: "Service has been down for more than 2 minutes"
```

Add to `prometheus.yml`:
```yaml
rule_files:
  - 'alerts.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

## Troubleshooting

### Metrics not showing in Prometheus

1. Check if service is running:
```bash
curl http://localhost:8000/metrics
```

2. Check Prometheus targets:
```bash
# Open http://localhost:9090/targets
# Status should be "UP"
```

3. Check Prometheus logs:
```bash
docker logs prometheus
```

### Grafana not showing data

1. Verify Prometheus datasource:
   - Grafana → Configuration → Data Sources
   - Test the Prometheus connection

2. Check time range:
   - Ensure you have data for the selected time range
   - Try "Last 5 minutes"

3. Generate some traffic:
```bash
for i in {1..20}; do
  curl http://localhost:8000/health
  sleep 1
done
```

### Docker network issues

If using `host.docker.internal` doesn't work:

1. Find your host IP:
```bash
# Linux/Mac
ip addr show | grep inet

# Windows
ipconfig
```

2. Update `prometheus.yml`:
```yaml
- targets: ['192.168.x.x:8000']  # Use your actual IP
```

3. Restart Prometheus:
```bash
docker-compose restart prometheus
```

## Production Considerations

1. **Persistent Storage**: The docker-compose setup uses volumes for data persistence

2. **Security**:
   - Change Grafana admin password
   - Implement authentication for Prometheus
   - Use TLS for all connections

3. **Retention**: Configure Prometheus retention:
```yaml
command:
  - '--storage.tsdb.retention.time=30d'
  - '--storage.tsdb.retention.size=50GB'
```

4. **High Availability**:
   - Run multiple Prometheus instances
   - Use Thanos for long-term storage
   - Configure Grafana with multiple data sources

5. **Alerting**:
   - Set up Alertmanager
   - Configure notification channels (Slack, PagerDuty, etc.)
   - Test alert rules regularly

## Cleanup

```bash
# Stop services
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v
```

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [prometheus-client Python Library](https://github.com/prometheus/client_python)
- [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)
