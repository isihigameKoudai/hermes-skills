# Benchmarking the new toolchain against ESLint

Use when the ask is "how much faster is oxlint than ESLint" on a repo that has no ESLint installed, or to add ESLint as a comparison baseline. This is a temporary sandbox exercise: install, measure, then revert `package.json`/`pnpm-lock.yaml` so nothing lands in the PR.

## Install (version pins matter — see SKILL.md pitfalls)

```sh
pnpm add -D eslint@^9 typescript-eslint @eslint/js \
  eslint-plugin-react eslint-plugin-react-hooks eslint-plugin-jsx-a11y
# if the repo is on TypeScript 7 (typescript-eslint peers on <6.1):
pnpm add -D typescript@~5.9.0
```

Skip `eslint-plugin-unicorn` unless it configures cleanly: its flat `recommended` config has thrown a rule-schema validation error on eslint 9.39.x (`unicorn/logical-assignment-operators`). For a speed benchmark, rule-set parity with oxlint's unicorn plugin is secondary — drop a crashing plugin rather than fight it.

## Flat config template (`eslint.config.mjs`)

Type-aware (the relevant mode when the new tool is type-aware):

```js
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import jsxA11y from 'eslint-plugin-jsx-a11y';

export default tseslint.config(
  { ignores: ['dist/**', 'node_modules/**', 'public/**', 'vite.config.ts', '**/*.gen.*'] },
  js.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,
  react.configs.flat.recommended,
  react.configs.flat['jsx-runtime'],
  reactHooks.configs.flat.recommended,
  jsxA11y.flatConfigs.recommended,
  { languageOptions: { parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname } } },
);
```

Non-type-aware: swap `...tseslint.configs.recommendedTypeChecked` for `...tseslint.configs.recommended` and drop the `parserOptions` block.

Config export names drift between plugin majors — verify before writing: `node -e "import('eslint-plugin-X').then(m => console.log(Object.keys(m.default.configs)))"`.

## Run

```sh
# type-aware (eslint exits 1 on findings — hyperfine needs --ignore-failure)
hyperfine --warmup 1 --runs 3 --ignore-failure 'pnpm exec eslint src utils'
# non-type-aware
hyperfine --warmup 2 --runs 5 --ignore-failure 'pnpm exec eslint -c eslint.config.nontype.mjs src utils'
```

For the oxlint side, reuse the repo's config (type-aware) and a copy with `options.typeAware` removed (non-type-aware), so both modes are compared fairly. Scope both to the same files (`src utils`).

## Reference numbers (304-file TS/React repo, 4 vCPU)

| mode | ESLint | oxlint | speedup |
| --- | --- | --- | --- |
| type-aware | ~43 s | ~1.8 s | ~24× |
| non-type-aware | ~14 s | ~0.3 s | ~45× |

Order-of-magnitude references only — they drift with plugin/rule versions and hardware. Report them as such, never as constants.

## Cleanup

```sh
rm eslint.config*.mjs
git checkout -- package.json pnpm-lock.yaml
pnpm install --frozen-lockfile   # restore the repo's real toolchain (e.g. TypeScript 7)
git status --short               # confirm clean
```
