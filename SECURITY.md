# Security model

## Supported versions

The project is currently in the design/pre-alpha stage; there are no supported public versions yet.

## Security principles

### Isolate probe data

ScoreFence must create a separate temporary collection, schema, namespace, or tenant. Writing probes into a customer collection is forbidden by default.

### Least-privilege credentials

Credentials should permit only:

- creating a temporary namespace;
- writing and reading controlled probe records;
- deleting the created namespace.

If the backend supports a pre-provisioned sandbox, permission to create production collections is not required.

### No customer content

The vector-retrieval pack uses synthetic vectors and technical IDs. Every future probe pack must use synthetic or explicitly supplied non-production fixtures by default. ScoreFence must not read customer documents, transactions, profiles, or model inputs to validate a score contract.

### Probe-pack review

A probe pack is executable test logic and must declare the data it creates, queries it sends, capabilities it requires, and cleanup behavior it expects. Packs must not introduce hidden network calls, download external datasets at runtime, or widen target permissions beyond their declared capabilities.

### Cleanup is mandatory

Cleanup runs in `finally` and is confirmed using a read-after-delete or metadata check when the backend permits it.

If cleanup cannot be confirmed:

- the report receives finding `SF302`;
- the exit code signals an environment failure;
- the namespace ID is shown to the operator;
- secrets remain redacted.

### Secret redaction

Logs and reports must never contain:

- API tokens;
- database passwords;
- Authorization headers;
- signed URLs;
- connection strings containing credentials.

### SSRF and target restrictions

If ScoreFence is offered as a hosted service, arbitrary target URLs create an SSRF risk. The runner must apply a tenant-scoped allowlist and reuse an already validated target configuration instead of accepting an arbitrary raw URL.

## Threats outside the MVP

ScoreFence is not:

- a prompt-injection scanner;
- a data-loss prevention system;
- a target-system vulnerability scanner;
- an authorization auditor;
- proof of deletion for customer data.

## Reporting a vulnerability

No security contact is defined until the public repository owner is chosen. Before publication, this section must be replaced with a real private disclosure channel and response expectations.
