# Infrastructure: Dapr & Kafka Configuration

## Dapr Components
1. **Pub/Sub (Kafka):**
   - Name: `kafka-pubsub`
   - Type: `pubsub.kafka`
   - Broker: `redpanda.messaging.svc.cluster.local:9092` (Local K8s address)
   - Topics: `task-events`, `reminders`

2. **Cron Binding:**
   - Name: `reminder-cron`
   - Type: `bindings.cron`
   - Schedule: `*/5 * * * *` (Run every 5 minutes)

3. **State Store:**
   - Name: `statestore`
   - Type: `state.postgresql`
   - Connection: Connects to the SQLModel database (Neon or local).