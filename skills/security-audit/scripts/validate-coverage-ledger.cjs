#!/usr/bin/env node
/*
 * Validate a coverage-ledger.json against the security-audit coverage contract.
 * Zero dependencies. Usage: node validate-coverage-ledger.cjs <path-to-ledger.json>
 *
 * Enforces: required unit fields, status/prior_status enums, canonical
 * coverage_id shape, duplicate/collision detection, lexicographic sort,
 * state-table invariants, and check-object ownership.
 */

"use strict";

const fs = require("fs");

const STATUSES = ["planned", "not_applicable", "out_of_scope", "in_progress", "covered", "candidate", "blocked", "deferred"];
const ATTEMPT_STATUSES = ["covered", "candidate", "blocked"];
const PRIOR_STATUSES = [
  "new", "prior_confirmed_same_source", "prior_confirmed_changed_source",
  "prior_needs_validation", "prior_deferred", "prior_blocked",
  "prior_out_of_scope", "prior_covered_same_source",
  "prior_covered_changed_source", "prior_rejected_claim_changed", "none",
];
const REQUIRED_FIELDS = [
  "coverage_id", "canonical_refs", "surface", "boundary", "subsystem", "attack_class",
  "starting_paths", "ordinary_attack_class_block", "selected_companion_blocks",
  "excluded_blocks", "prior_status", "attempts", "wave", "status", "agent_id",
  "reviewed_paths", "local_checks", "result_fingerprints", "unresolved",
];
const ATTEMPT_FIELDS = ["wave", "status", "agent_id", "reviewed_paths", "local_checks", "result_fingerprints", "unresolved", "reassignment_reason"];
const FINGERPRINT_RE = /^[A-Za-z0-9][A-Za-z0-9._:/@+-]*$/;
const AGENT_ID_RE = /^[a-z0-9][a-z0-9_-]{0,63}$/;
const METHODS = ["source", "local"];

function add(errors, msg) { errors.push(msg); }
function nonEmpty(v) { return typeof v === "string" && v.trim().length > 0; }
function isArr(v) { return Array.isArray(v); }

function checkCheck(c, at, errors) {
  if (!c || !AGENT_ID_RE.test(c.agent_id || "")) add(errors, `${at}.agent_id: must match ${AGENT_ID_RE}`);
  if (!isArr(c.reviewed_paths) || c.reviewed_paths.length === 0) add(errors, `${at}.reviewed_paths: must be a non-empty array`);
  else c.reviewed_paths.forEach((p, i) => { if (!nonEmpty(p)) add(errors, `${at}.reviewed_paths[${i}]: must be a non-empty string`); });
  if (!nonEmpty(c.invariant)) add(errors, `${at}.invariant: must be a non-empty string`);
  if (!METHODS.includes(c.method)) add(errors, `${at}.method: must be one of ${METHODS.join("|")}`);
  if (!nonEmpty(c.result)) add(errors, `${at}.result: must be a non-empty string`);
  if (c.method === "source") {
    if (c.artifact !== null) add(errors, `${at}.artifact: a source-only check must use null`);
  } else {
    const owned = `agents/${c.agent_id}/artifacts/`;
    if (typeof c.artifact !== "string" || !c.artifact.startsWith(owned)) {
      add(errors, `${at}.artifact: a local check must reference its own ${owned}... path`);
    }
  }
}

function checkState(u, at, errors) {
  const st = u.status;
  if (st === "planned") {
    if (u.agent_id !== null) add(errors, `${at}: a planned unit must be unassigned`);
    if (u.reviewed_paths.length || u.local_checks.length) add(errors, `${at}: a planned unit must have no evidence`);
  } else if (["not_applicable", "out_of_scope", "deferred"].includes(st)) {
    if (u.agent_id !== null) add(errors, `${at}: a ${st} unit must be unassigned`);
    if (u.reviewed_paths.length || u.local_checks.length) add(errors, `${at}: a ${st} unit must have no evidence`);
    if (u.unresolved.length === 0) add(errors, `${at}: a ${st} unit must record a reason`);
  } else if (st === "in_progress") {
    if (!AGENT_ID_RE.test(u.agent_id || "")) add(errors, `${at}: an in_progress unit needs an owner`);
    if (u.reviewed_paths.length || u.local_checks.length) add(errors, `${at}: an in_progress unit must have no evidence yet`);
  } else if (st === "blocked") {
    if (!AGENT_ID_RE.test(u.agent_id || "")) add(errors, `${at}: a blocked unit needs an owner`);
    if (!u.reviewed_paths.length || !u.local_checks.length) add(errors, `${at}: a blocked unit must carry partial evidence`);
    if (u.unresolved.length === 0) add(errors, `${at}: a blocked unit must record a blocker`);
  } else if (st === "covered") {
    if (!AGENT_ID_RE.test(u.agent_id || "")) add(errors, `${at}: a covered unit needs an owner`);
    if (!u.reviewed_paths.length || !u.local_checks.length) add(errors, `${at}: a covered unit must carry evidence`);
    if (u.result_fingerprints.length) add(errors, `${at}: a covered unit must have no result fingerprints`);
  } else if (st === "candidate") {
    if (!AGENT_ID_RE.test(u.agent_id || "")) add(errors, `${at}: a candidate unit needs an owner`);
    if (!u.reviewed_paths.length || !u.local_checks.length) add(errors, `${at}: a candidate unit must carry evidence`);
    if (u.result_fingerprints.length === 0) add(errors, `${at}: a candidate unit must have result fingerprints`);
  }
  if (st !== "candidate" && u.result_fingerprints.length) {
    add(errors, `${at}: result fingerprints only allowed on candidate units`);
  }
}

function checkUnit(u, i, errors, seen, prev) {
  const at = `$[${i}]`;
  if (!u || typeof u !== "object") { add(errors, `${at}: must be an object`); return; }

  for (const f of REQUIRED_FIELDS) {
    if (!Object.prototype.hasOwnProperty.call(u, f)) add(errors, `${at}.${f}: required field missing`);
  }

  if (nonEmpty(u.coverage_id)) {
    if (seen.has(u.coverage_id)) add(errors, `${at}.coverage_id: duplicate coverage ID`);
    seen.add(u.coverage_id);
    if (prev !== null && prev > u.coverage_id) add(errors, `${at}: units must be sorted lexicographically by coverage_id`);
  }
  if (!isArr(u.starting_paths) || u.starting_paths.length === 0) add(errors, `${at}.starting_paths: must be a non-empty array`);
  if (!PRIOR_STATUSES.includes(u.prior_status)) add(errors, `${at}.prior_status: must be one of ${PRIOR_STATUSES.join("|")}`);
  if (!STATUSES.includes(u.status)) add(errors, `${at}.status: must be one of ${STATUSES.join("|")}`);
  if (!Number.isInteger(u.wave) || u.wave < 1) add(errors, `${at}.wave: must be a positive integer`);
  if (u.agent_id !== null && !AGENT_ID_RE.test(u.agent_id)) add(errors, `${at}.agent_id: must match ${AGENT_ID_RE}`);

  if (!isArr(u.reviewed_paths)) add(errors, `${at}.reviewed_paths: must be an array`);
  if (!isArr(u.local_checks)) add(errors, `${at}.local_checks: must be an array`);
  if (!isArr(u.result_fingerprints)) add(errors, `${at}.result_fingerprints: must be an array`);
  else u.result_fingerprints.forEach((fp, j) => { if (!FINGERPRINT_RE.test(fp || "")) add(errors, `${at}.result_fingerprints[${j}]: invalid fingerprint`); });
  if (!isArr(u.unresolved)) add(errors, `${at}.unresolved: must be an array`);
  if (!isArr(u.selected_companion_blocks)) add(errors, `${at}.selected_companion_blocks: must be an array`);
  if (!isArr(u.excluded_blocks)) add(errors, `${at}.excluded_blocks: must be an array`);
  if (!isArr(u.attempts)) add(errors, `${at}.attempts: must be an array`);
  else {
    u.attempts.forEach((a, j) => {
      const p = `${at}.attempts[${j}]`;
      for (const f of ATTEMPT_FIELDS) {
        if (!Object.prototype.hasOwnProperty.call(a || {}, f)) add(errors, `${p}.${f}: required field missing`);
      }
      if (a && !ATTEMPT_STATUSES.includes(a.status)) add(errors, `${p}.status: must be one of ${ATTEMPT_STATUSES.join("|")}`);
      if (a && (!Number.isInteger(a.wave) || a.wave < 1 || a.wave >= u.wave)) add(errors, `${p}.wave: must be a positive integer below the unit's wave`);
    });
  }

  u.local_checks.forEach((c, j) => checkCheck(c, `${at}.local_checks[${j}]`, errors));

  // reviewed-path ownership: every unit-level path must have a check owner,
  // and every check-owned path must appear in the unit aggregate.
  const ownedPaths = new Set();
  u.local_checks.forEach((c) => c.reviewed_paths.forEach((p) => ownedPaths.add(p)));
  u.reviewed_paths.forEach((p) => { if (!ownedPaths.has(p)) add(errors, `${at}: reviewed path "${p}" has no check owner`); });
  const unitPaths = new Set(u.reviewed_paths);
  u.local_checks.forEach((c) => c.reviewed_paths.forEach((p) => { if (!unitPaths.has(p)) add(errors, `${at}: check-owned path "${p}" absent from the unit aggregate`); }));

  checkState(u, at, errors);
}

function main() {
  const inputPath = process.argv[2];
  if (!inputPath) {
    console.error("Usage: node validate-coverage-ledger.cjs <coverage-ledger.json>");
    process.exit(2);
  }
  let raw;
  try { raw = fs.readFileSync(inputPath, "utf8"); }
  catch (e) { console.error(`Cannot read ${inputPath}: ${e.message}`); process.exit(2); }
  let data;
  try { data = JSON.parse(raw); }
  catch (e) { console.error(`Not valid JSON: ${e.message}`); process.exit(1); }
  if (!Array.isArray(data)) {
    console.error("$: expected a top-level array");
    process.exit(1);
  }

  const errors = [];
  const seen = new Set();
  let prev = null;
  data.forEach((u, i) => checkUnit(u, i, errors, seen, prev) || (prev = u && u.coverage_id));

  if (errors.length === 0) {
    console.log(`PASS: ${data.length} coverage units valid`);
    process.exit(0);
  }
  errors.forEach((e) => console.error(`ERROR: ${e}`));
  console.error(`FAIL: ${errors.length} validation error(s)`);
  process.exit(1);
}

main();
