# Sequence Diagram Report

## Diagram

```
Sequence Diagram:
Customer -> OrderSystem: PlaceOrder(item: Milk, quantity: 2)
OrderSystem -> Order: CreateOrder(id: 123, items: [Milk])
Order -> PaymentGateway: ProcessPayment(amount: 50)
```
