# Minimal Federated Learning Framework Using gRPC

This repository currently contains the first, monolithic prototype of a minimal
Federated Learning framework. Arithmetic expressions stand in for local machine
learning training so that registration, task distribution, result collection,
and aggregation can be validated without ML dependencies.

## Architecture

```text
Management Client
       ↓
Coordinator
       ↓
Participants
       ↓
Local computation
       ↓
Coordinator aggregation
```

The Coordinator owns jobs and aggregation. Participants only execute assigned
tasks and return local results. The Management Client drives the workflow.

## Example

```text
(12 * 5) + (30 / 6) - (8 * 4) + (15 + 7)
```

The final result is:

```text
55
```

Expressions are parsed with Python's AST module rather than evaluated with
`eval()`. Additive expressions are decomposed into signed tasks, while nested
expressions remain intact when splitting them would change arithmetic semantics.

## Running

From the repository root:

```powershell
python -m src.main
python -m pytest
```

Install the test dependency first if needed:

```powershell
python -m pip install -r requirements.txt
```

## Future evolution

The next phase will transform the Coordinator, Participants, and Management
Client into independent services communicating through gRPC and Protocol
Buffers. gRPC is not implemented in this prototype.
