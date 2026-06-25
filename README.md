# Communication Protocol

A small UDP-based communication protocol demo that shows how a client request can be routed through a DNS-style dispatcher to a primary server, with a backup server taking over when the primary stops sending heartbeats.

The project runs locally on `127.0.0.1` and is intended as a networking and fault-tolerance exercise rather than a production service.

## What it demonstrates

- UDP socket communication in Python
- A DNS/router process that forwards client requests to the currently active server
- Primary/backup failover using heartbeat messages
- Backup promotion when the primary server becomes unavailable
- Recovery back to the primary after it has been stable for a configured period
- A simple test client for sending messages through the protocol

## Architecture

The system has four scripts:

| File | Role | Default port |
| --- | --- | --- |
| `NR_P2_dns.py` | DNS-style router that receives client messages and forwards them to the active server | `5000` |
| `NR_P2_primary.py` | Primary server that processes routed messages and sends heartbeats to the backup | `5001` |
| `NR_P2_backup.py` | Backup server that monitors primary heartbeats and becomes active after a timeout | `5002` |
| `test_client.py` | UDP client used to send test messages to the DNS/router | User-supplied |

Normal message flow:

1. The client sends a message to the DNS/router on port `5000`.
2. The DNS/router forwards the message to the active server with a `ROUTED: ` prefix.
3. The active server processes the message and returns it with a `RESPONSE: ` prefix.
4. The DNS/router strips the response prefix and sends the result back to the client.

When the primary server is active, responses are converted to uppercase. When the backup server is active, responses are converted to lowercase, making failover visible during testing.

## Failover behavior

The primary sends a `HEARTBEAT` message to the backup every 2 seconds. The backup tracks the last heartbeat time.

- If the backup does not receive a heartbeat for 5 seconds, it switches from `STANDBY` to `ACTIVE` and notifies the DNS/router with `PRIMARY_DOWN`.
- The DNS/router then routes future client requests to the backup server.
- If the primary starts sending heartbeats again, the backup begins a recovery timer.
- After 10 seconds of stable heartbeats, the backup returns to `STANDBY` and notifies the DNS/router with `PRIMARY_UP`.
- The DNS/router resumes routing traffic to the primary server.

## Requirements

- Python 3
- No external packages

The project only uses Python standard-library modules: `socket`, `threading`, `time`, and `sys`.

## How to run

Open three terminals from the repository root.

Terminal 1: start the DNS/router.

```bash
python3 NR_P2_dns.py
```

Terminal 2: start the backup server.

```bash
python3 NR_P2_backup.py
```

Terminal 3: start the primary server.

```bash
python3 NR_P2_primary.py
```

In a fourth terminal, send a test message to the DNS/router on port `5000`.

```bash
python3 test_client.py hello 5000
```

Expected output while the primary is active:

```text
Sent: hello to ('127.0.0.1', 5000)
Received: HELLO from ('127.0.0.1', 5000)
```

## Testing failover

1. Start `NR_P2_dns.py`, `NR_P2_backup.py`, and `NR_P2_primary.py`.
2. Send a message through the client and confirm the response is uppercase.
3. Stop the primary server process.
4. Wait at least 5 seconds for the backup to detect the missed heartbeat.
5. Send another message through the client.

Example:

```bash
python3 test_client.py HELLO 5000
```

Expected output while the backup is active:

```text
Sent: HELLO to ('127.0.0.1', 5000)
Received: hello from ('127.0.0.1', 5000)
```

To test recovery, restart `NR_P2_primary.py` and wait at least 10 seconds. The backup should return to standby, and future client messages should route to the primary again.

## Configuration

The main timing and port values are defined near the top of the server scripts:

```python
DNS_SERVER_PORT = 5000
PRIMARY_SERVER_PORT = 5001
BACKUP_SERVER_PORT = 5002
HEARTBEAT_TIMEOUT = 5
RECOVERY_TIME = 10
```

## Current limitations

- Runs on localhost only.
- Uses UDP, so delivery and ordering are not guaranteed.
- Does not replicate application state between primary and backup.
- Handles simple single-message request/response traffic.
- Has no authentication, encryption, or production-grade health checking.

## Resume framing

This project is a compact example of network programming and fault-tolerant system behavior in Python. The strongest resume angle is the primary/backup failover flow: heartbeat monitoring, DNS-style routing, backup promotion, and recovery to the primary after a stability window.