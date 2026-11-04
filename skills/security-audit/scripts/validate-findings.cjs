#!/usr/bin/env node
/*
 * Validate a findings.json against the security-audit record contract.
 * Zero dependencies. Usage: node validate-findings.cjs <path-to-findings.json>
 *
 * Enforces, beyond the JSON shape: fingerprint uniqueness and sort order,
 * entrypoint→sink trace ordering, positive line numbers, per-verdict
 * forbidden fields, and the rule that overall severity never exceeds impact.
 */

"use strict";

const fs = require("fs");
const path = require("path");

const VERDICTS = ["confirmed", "needs_validation", "rejected"];
const TRACE_KINDS = ["entrypoint", "propagation", "sink"];
const CONDITION_KINDS = [
  "authentication_level", "authorization_role", "user_interaction",
  "system_configuration", "network_routing", "environmental_dependency",
  "data_state", "timing_dependency", "third_party_dependency",
];
const SEVERITY_LEVELS = ["informational", "low", "medium", "high", "critical"];
const SEVERITY_RANK = new Map(SEVERITY_LEVELS.map((v, i) => [v, i]));
const CONFIDENCE_LEVELS = ["low", "medium", "high"];
const FINGERPRINT_RE = /^[A-Za-z0-9][A-Za-z0-9._:/@+-]*$/;

const FORBIDDEN = {
  confirmed: ["claimed_root_cause", "blockers", "validation_plan", "reason"],
  needs_validation: ["severity", "execution", "remediation", "reason", "root_cause"],
  rejected: ["severity", "execution", "remediation", "blockers", "validation_plan", "root_cause"],
};

function nonEmpty(v) {
  return typeof v === "string" && v.trim().length > 0;
}

function posInt(v) {
  return Number.isInteger(v) && v >= 1;
}

function add(errors, msg) {
  errors.push(msg);
}

function checkCommon(f, at, errors) {
  if (!nonEmpty(f.fingerprint)) add(errors, `${at}.fingerprint: must be a non-empty string`);
  else if (!FINGERPRINT_RE.test(f.fingerprint)) add(errors, `${at}.fingerprint: must match ${FINGERPRINT_RE}`);
  if (!nonEmpty(f.title)) add(errors, `${at}.title: must be a non-empty string`);
  if (!nonEmpty(f.description)) add(errors, `${at}.description: must be a non-empty string`);

  if (!Array.isArray(f.trace) || f.trace.length === 0) {
    add(errors, `${at}.trace: must be a non-empty array`);
  } else {
    f.trace.forEach((t, i) => {
      const p = `${at}.trace[${i}]`;
      if (!t || !TRACE_KINDS.includes(t.kind)) add(errors, `${p}.kind: must be one of ${TRACE_KINDS.join("|")}`);
      if (!nonEmpty(t.file)) add(errors, `${p}.file: must be a non-empty string`);
      if (!posInt(t.line)) add(errors, `${p}.line: must be a positive integer`);
      if (!nonEmpty(t.scope)) add(errors, `${p}.scope: must be a non-empty string`);
      if (!nonEmpty(t.description)) add(errors, `${p}.description: must be a non-empty string`);
    });
    if (f.trace.length === 1) {
      if (!["entrypoint", "sink"].includes(f.trace[0].kind)) {
        add(errors, `${at}.trace[0].kind: a single-step trace must be entrypoint or sink`);
      }
    } else {
      if (f.trace[0].kind !== "entrypoint") add(errors, `${at}.trace[0].kind: first step of a multi-step trace must be entrypoint`);
      if (f.trace[f.trace.length - 1].kind !== "sink") add(errors, `${at}.trace[last].kind: last step of a multi-step trace must be sink`);
      for (let i = 1; i < f.trace.length - 1; i++) {
        if (f.trace[i].kind !== "propagation") add(errors, `${at}.trace[${i}].kind: intermediate steps must be propagation`);
      }
    }
  }

  if (!Array.isArray(f.evidence) || f.evidence.length === 0) {
    add(errors, `${at}.evidence: must be a non-empty array`);
  } else {
    f.evidence.forEach((e, i) => {
      const p = `${at}.evidence[${i}]`;
      if (!nonEmpty(e.file)) add(errors, `${p}.file: must be a non-empty string`);
      if (!posInt(e.line)) add(errors, `${p}.line: must be a positive integer`);
      if (!nonEmpty(e.description)) add(errors, `${p}.description: must be a non-empty string`);
    });
  }
}

function checkForbidden(f, verdict, at, errors) {
  for (const field of FORBIDDEN[verdict]) {
    if (Object.prototype.hasOwnProperty.call(f, field)) {
      add(errors, `${at}.${field}: not allowed on a ${verdict} record`);
    }
  }
}

function checkConfirmed(f, at, errors) {
  for (const field of ["root_cause", "intended_behavior"]) {
    if (!nonEmpty(f[field])) add(errors, `${at}.${field}: must be a non-empty string`);
  }
  if (!Array.isArray(f.conditions)) {
    add(errors, `${at}.conditions: must be an array`);
  } else {
    f.conditions.forEach((c, i) => {
      if (!c || !CONDITION_KINDS.includes(c.kind)) add(errors, `${at}.conditions[${i}].kind: must be one of ${CONDITION_KINDS.join("|")}`);
      if (!c || !nonEmpty(c.description)) add(errors, `${at}.conditions[${i}].description: must be a non-empty string`);
    });
  }

  const x = f.execution;
  if (!x || !nonEmpty(x.attacker_perspective)) add(errors, `${at}.execution.attacker_perspective: must be a non-empty string`);
  if (!x || !Array.isArray(x.payloads) || x.payloads.length === 0) add(errors, `${at}.execution.payloads: must be a non-empty array`);
  if (!x || !Array.isArray(x.instructions) || x.instructions.length === 0) add(errors, `${at}.execution.instructions: must be a non-empty array`);
  if (!x || !nonEmpty(x.observed_result)) add(errors, `${at}.execution.observed_result: must be a non-empty string`);

  const r = f.remediation;
  if (!r || !nonEmpty(r.strategy)) add(errors, `${at}.remediation.strategy: must be a non-empty string`);
  if (r && r.code_changes != null) {
    if (!Array.isArray(r.code_changes)) add(errors, `${at}.remediation.code_changes: must be an array`);
    else r.code_changes.forEach((cc, i) => {
      if (!nonEmpty(cc.file_name)) add(errors, `${at}.remediation.code_changes[${i}].file_name: must be a non-empty string`);
      if (typeof cc.fixed_code !== "string") add(errors, `${at}.remediation.code_changes[${i}].fixed_code: must be a string`);
    });
  }

  const s = f.severity;
  if (!s) {
    add(errors, `${at}.severity: required on a confirmed record`);
  } else {
    for (const axis of ["likelihood", "impact"]) {
      const a = s[axis];
      if (!a || !SEVERITY_LEVELS.includes(a.score)) add(errors, `${at}.severity.${axis}.score: must be one of ${SEVERITY_LEVELS.join("|")}`);
      if (!a || !nonEmpty(a.reason)) add(errors, `${at}.severity.${axis}.reason: must be a non-empty string`);
    }
    if (!SEVERITY_LEVELS.includes(s.overall_severity)) add(errors, `${at}.severity.overall_severity: must be one of ${SEVERITY_LEVELS.join("|")}`);
    else if (s.impact && SEVERITY_LEVELS.includes(s.impact.score)) {
      if (SEVERITY_RANK.get(s.overall_severity) > SEVERITY_RANK.get(s.impact.score)) {
        add(errors, `${at}.severity.overall_severity: cannot exceed demonstrated impact (${s.impact.score})`);
      }
    }
  }

  const c = f.confidence;
  if (!c || !CONFIDENCE_LEVELS.includes(c.score)) add(errors, `${at}.confidence.score: must be one of ${CONFIDENCE_LEVELS.join("|")}`);
  if (!c || !nonEmpty(c.reason)) add(errors, `${at}.confidence.reason: must be a non-empty string`);
}

function checkNeedsValidation(f, at, errors) {
  if (!nonEmpty(f.claimed_root_cause)) add(errors, `${at}.claimed_root_cause: must be a non-empty string`);
  if (!Array.isArray(f.blockers) || f.blockers.length === 0) {
    add(errors, `${at}.blockers: must be a non-empty array`);
  } else {
    f.blockers.forEach((b, i) => { if (!nonEmpty(b)) add(errors, `${at}.blockers[${i}]: must be a non-empty string`); });
  }
  const vp = f.validation_plan || {};
  const hasLocal = nonEmpty(vp.local);
  const hasDeployment = nonEmpty(vp.deployment);
  if (!hasLocal && !hasDeployment) add(errors, `${at}.validation_plan: at least one of local/deployment must be a non-empty string`);
}

function checkRejected(f, at, errors) {
  if (!nonEmpty(f.claimed_root_cause)) add(errors, `${at}.claimed_root_cause: must be a non-empty string`);
  if (!nonEmpty(f.reason)) add(errors, `${at}.reason: must be a non-empty string`);
}

function main() {
  const inputPath = process.argv[2];
  if (!inputPath) {
    console.error("Usage: node validate-findings.cjs <findings.json>");
    process.exit(2);
  }
  let raw;
  try {
    raw = fs.readFileSync(inputPath, "utf8");
  } catch (e) {
    console.error(`Cannot read ${inputPath}: ${e.message}`);
    process.exit(2);
  }
  let data;
  try {
    data = JSON.parse(raw);
  } catch (e) {
    console.error(`Not valid JSON: ${e.message}`);
    process.exit(1);
  }
  if (!Array.isArray(data)) {
    console.error("$: expected a top-level array");
    process.exit(1);
  }

  const errors = [];
  const seen = new Set();
  let prevFingerprint = null;

  data.forEach((f, i) => {
    const at = `$[${i}]`;
    if (!f || typeof f !== "object") { add(errors, `${at}: must be an object`); return; }
    if (!VERDICTS.includes(f.verdict)) { add(errors, `${at}.verdict: must be one of ${VERDICTS.join("|")}`); return; }

    checkCommon(f, at, errors);
    checkForbidden(f, f.verdict, at, errors);

    if (f.verdict === "confirmed") checkConfirmed(f, at, errors);
    else if (f.verdict === "needs_validation") checkNeedsValidation(f, at, errors);
    else checkRejected(f, at, errors);

    if (nonEmpty(f.fingerprint)) {
      if (seen.has(f.fingerprint)) add(errors, `${at}.fingerprint: duplicate of an earlier record`);
      seen.add(f.fingerprint);
      if (prevFingerprint !== null && prevFingerprint > f.fingerprint) {
        add(errors, `${at}: findings must be sorted lexicographically by fingerprint`);
      }
      prevFingerprint = f.fingerprint;
    }
  });

  if (errors.length === 0) {
    console.log(`PASS: ${data.length} findings valid`);
    process.exit(0);
  }
  errors.forEach((e) => console.error(`ERROR: ${e}`));
  console.error(`FAIL: ${errors.length} validation error(s)`);
  process.exit(1);
}

main();
