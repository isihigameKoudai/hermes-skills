# biome → oxlint / oxfmt mapping

Concrete mapping used when migrating a biome project to the Oxc toolchain. Rule names are exact oxlint rule IDs; the disable-comment conversion uses the same table.

## biome rule → oxlint rule

| biome (`lint/<group>/<rule>`) | oxlint rule |
| --- | --- |
| `style/noNonNullAssertion` | `typescript/no-non-null-assertion` |
| `suspicious/noExplicitAny` | `typescript/no-explicit-any` |
| `suspicious/noArrayIndexKey` | `react/no-array-index-key` |
| `a11y/useMediaCaption` | `jsx-a11y/media-has-caption` |
| `a11y/useKeyWithClickEvents` | `jsx-a11y/click-events-have-key-events` |
| `a11y/noStaticElementInteractions` | `jsx-a11y/no-static-element-interactions` |
| `correctness/useHookAtTopLevel` | `react-hooks/rules-of-hooks` |
| `style/useImportType` | `typescript/consistent-type-imports` |
| `correctness/useExhaustiveDependencies` | `react-hooks/exhaustive-deps` |
| `a11y/useValidAnchor` | `jsx-a11y/anchor-is-valid` |
| `performance/noAccumulatingSpread` | *(no oxlint equivalent — drop the comment)* |

Note: biome's `preset: recommended` maps only loosely to oxlint's default `correctness` category. `typescript/no-non-null-assertion`, `no-explicit-any`, and `react/no-array-index-key` are NOT enabled by default in oxlint — enable them explicitly at `warn` to avoid a coverage regression. `useHookAtTopLevel` (biome correctness = error) maps to `react-hooks/rules-of-hooks` at `error`.

## oxlint plugins

`options.typeAware: true` (and optionally `typeCheck: true`) require a type backend: `tsrs` or `oxlint-tsgolint`. Plugins are NOT additive in `.oxlintrc.json` — setting `plugins` overwrites the default set, so list all you want: `["typescript", "unicorn", "oxc", "react", "jsx-a11y"]`. Default-on plugins are `typescript`, `unicorn`, `oxc`; `react` and `jsx-a11y` are off by default.

## disable-comment conversion

- line: `// biome-ignore lint/<g>/<r>: <reason>` → `// oxlint-disable-next-line <oxrule> -- <reason>`
- JSX: `{/* biome-ignore lint/<g>/<r>: <reason> */}` → `{/* oxlint-disable-next-line <oxrule> -- <reason> */}`
- rules with no equivalent: delete the comment (the rule is no longer enforced).
- trailing/stacked comments (`let // biome-ignore ...` on the line before the `!`) convert 1:1 — a stacked pair becomes two `oxlint-disable-next-line` lines, one of which is then redundant and shows up under `--report-unused-disable-directives` (harmless).

## biome formatter → oxfmt options

`oxfmt --migrate=biome` generates this automatically. Manual equivalent:

| biome | oxfmt |
| --- | --- |
| `quoteStyle: single` | `singleQuote: true` |
| `semicolons: always` | `semi: true` |
| `trailingCommas: all` | `trailingComma: "all"` |
| `indentStyle: tab` + `indentWidth: 2` | `useTabs: true`, `tabWidth: 2` |
| `lineWidth: 80` | `printWidth: 80` |

biome's `files.includes` negatives (`!**/dist/`, `!**/*.gen.*`, …) become oxfmt `ignorePatterns`. Add `**/*.md`, `**/*.html`, `**/*.yaml`, `**/*.yml` on top because oxfmt formats those and biome did not.
