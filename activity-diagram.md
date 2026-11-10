# Activity Diagram Report

## Diagram

```
Activity Diagram:
StartOrderProcessing -> CheckInventory
CheckInventory -> ProcessPayment (if inventoryAvailable AND NOT blacklisted)
CheckInventory -> NotifyCustomer (if NOT (inventoryAvailable AND NOT blacklisted))
ProcessPayment -> CompleteOrder
NotifyCustomer -> EndOrderProcessing
```

## Analysis

- Start node(s): StartOrderProcessing

### Cycles
- No cycles detected

### Unreachable Steps
- None

### Sinks (no outgoing edges)
- Warning: 'CompleteOrder' has no outgoing edges and does not look final

### Topological Order

StartOrderProcessing -> CheckInventory -> ProcessPayment -> NotifyCustomer -> CompleteOrder -> EndOrderProcessing
