# MongoDB initialization — runs once on first container boot.
// Creates Sentinel collections referenced in the project plan (Section 13).

db = db.getSiblingDB("sentinel");

const collections = [
  "deploys",
  "service_registry",
  "fault_catalogue",
  "inventory_items",
];

collections.forEach((name) => {
  if (!db.getCollectionNames().includes(name)) {
    db.createCollection(name);
    print(`Created collection: ${name}`);
  }
});

// Seed service registry with the toy-system topology for later investigator use.
db.service_registry.updateOne(
  { _id: "toy-system" },
  {
    $set: {
      services: [
        { name: "api-gateway", port: 8080, depends_on: ["orders-service"] },
        { name: "orders-service", port: 8081, depends_on: ["payments-service", "inventory-service"] },
        { name: "payments-service", port: 8082, depends_on: ["external-payment-mock"] },
        { name: "inventory-service", port: 8083, depends_on: ["mongodb"] },
        { name: "external-payment-mock", port: 8084, depends_on: [] },
      ],
      updated_at: new Date(),
    },
  },
  { upsert: true }
);

print("MongoDB init complete.");
