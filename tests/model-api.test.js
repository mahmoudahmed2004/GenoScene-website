import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { handleRequest } from "../api/analyze.js";

function testSample() {
  const [headerLine, rowLine] = readFileSync(
    new URL("../TEST.csv", import.meta.url),
    "utf8",
  )
    .trim()
    .split(/\r?\n/);
  const headers = headerLine.split(",");
  const values = rowLine.split(",");
  return Object.fromEntries(headers.map((header, index) => [header, values[index]]));
}

test("health endpoint exposes trained model metadata", async () => {
  const response = await handleRequest(new Request("http://localhost/api/analyze"));
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.status, "ok");
  assert.equal(body.model.feature_count, 40);
  assert.ok(body.model.metrics.overall_mae < 0.02);
});

test("predicts normalized phenotype probabilities from SNP values", async () => {
  const request = new Request("http://localhost/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sample_id: "TEST-SAMPLE", samples: [testSample()] }),
  });
  const response = await handleRequest(request);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.success, true);
  assert.equal(body.results[0].sample_id, "SAMPLE1");
  assert.equal(body.results[0].recognized_features, 40);

  for (const probabilities of Object.values(body.results[0].probabilities)) {
    const total = Object.values(probabilities).reduce((sum, value) => sum + value, 0);
    assert.ok(Math.abs(total - 1) < 1e-9);
    assert.ok(Object.values(probabilities).every((value) => value >= 0 && value <= 1));
  }
});

test("rejects requests without samples", async () => {
  const request = new Request("http://localhost/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ samples: [] }),
  });
  const response = await handleRequest(request);

  assert.equal(response.status, 400);
});

test("rejects samples without enough recognized numeric SNPs", async () => {
  const request = new Request("http://localhost/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ samples: [{ sampleid: "INVALID", rs_unknown_A: 2 }] }),
  });
  const response = await handleRequest(request);
  const body = await response.json();

  assert.equal(response.status, 400);
  assert.match(body.error, /recognized numeric SNP markers/);
});
