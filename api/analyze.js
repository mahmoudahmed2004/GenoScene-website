import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const model = require("../model/phenotype-model.json");
const MAX_SAMPLES = 25;
const MIN_RECOGNIZED_FEATURES = 10;

function json(data, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

function dense(input, layer, useRelu) {
  const output = layer.biases.slice();

  for (let inputIndex = 0; inputIndex < input.length; inputIndex += 1) {
    const value = input[inputIndex];
    const weights = layer.weights[inputIndex];
    for (let outputIndex = 0; outputIndex < output.length; outputIndex += 1) {
      output[outputIndex] += value * weights[outputIndex];
    }
  }

  return useRelu ? output.map((value) => Math.max(0, value)) : output;
}

function normalize(values) {
  const clipped = values.map((value) =>
    Number.isFinite(value) ? Math.max(0, value) : 0,
  );
  const total = clipped.reduce((sum, value) => sum + value, 0);

  if (total <= Number.EPSILON) {
    return clipped.map(() => 1 / clipped.length);
  }

  return clipped.map((value) => value / total);
}

function isNumericFeatureValue(value) {
  return value !== null && value !== undefined && String(value).trim() !== ""
    && Number.isFinite(Number(value));
}

function prepareFeatures(sample) {
  return model.features.map((feature, index) => {
    const parsed = Number(sample[feature]);
    const value = isNumericFeatureValue(sample[feature])
      ? Math.min(2, Math.max(0, parsed))
      : model.imputer_median[index];
    return (value - model.scaler_mean[index]) / model.scaler_scale[index];
  });
}

function predictSample(sample, fallbackId) {
  const recognizedFeatures = model.features.filter((feature) =>
    isNumericFeatureValue(sample[feature]),
  ).length;
  let layerValues = prepareFeatures(sample);
  model.layers.forEach((layer, index) => {
    layerValues = dense(layerValues, layer, index < model.layers.length - 1);
  });

  const probabilities = {};
  const predictions = {};
  let offset = 0;

  for (const [trait, classes] of Object.entries(model.target_groups)) {
    const values = normalize(layerValues.slice(offset, offset + classes.length));
    probabilities[trait] = Object.fromEntries(
      classes.map((className, index) => [className, values[index]]),
    );

    const topIndex = values.indexOf(Math.max(...values));
    predictions[trait] = {
      top: classes[topIndex],
      confidence: values[topIndex],
      confidence_pct: Math.round(values[topIndex] * 10000) / 100,
    };
    offset += classes.length;
  }

  return {
    sample_id: String(sample.sampleid ?? sample.sampleId ?? fallbackId),
    recognized_features: recognizedFeatures,
    total_model_features: model.features.length,
    probabilities,
    predictions,
  };
}

export async function handleRequest(request) {
  if (request.method === "GET") {
    return json({
      status: "ok",
      model: {
        type: model.model_type,
        trained_at: model.trained_at,
        training_rows: model.training_rows,
        feature_count: model.features.length,
        metrics: model.metrics,
      },
    });
  }

  if (request.method !== "POST") {
    return json({ success: false, error: "Method not allowed." }, 405);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ success: false, error: "Request body must be valid JSON." }, 400);
  }

  const samples = Array.isArray(body?.samples) ? body.samples : [];
  if (samples.length === 0) {
    return json({ success: false, error: "At least one SNP sample is required." }, 400);
  }
  if (samples.length > MAX_SAMPLES) {
    return json(
      { success: false, error: `A maximum of ${MAX_SAMPLES} samples is allowed per request.` },
      400,
    );
  }

  const invalidIndex = samples.findIndex((sample) => {
    if (!sample || typeof sample !== "object") return true;
    return model.features.filter((feature) => isNumericFeatureValue(sample[feature])).length
      < MIN_RECOGNIZED_FEATURES;
  });
  if (invalidIndex !== -1) {
    return json(
      {
        success: false,
        error: `Sample ${invalidIndex + 1} must contain at least ${MIN_RECOGNIZED_FEATURES} recognized numeric SNP markers.`,
      },
      400,
    );
  }

  const results = samples.map((sample, index) =>
    predictSample(sample && typeof sample === "object" ? sample : {}, body.sample_id ?? index + 1),
  );

  return json({
    success: true,
    count: results.length,
    results,
    model: {
      trained_at: model.trained_at,
      training_rows: model.training_rows,
      metrics: model.metrics,
    },
  });
}

export default {
  fetch: handleRequest,
};
