#!/usr/bin/env node
/** Keep pyproject.toml version and SDK_VERSION in sync after release-it bumps package.json. */
import { readFileSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const version = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8')).version;

const pyprojectPath = join(root, 'pyproject.toml');
const pyproject = readFileSync(pyprojectPath, 'utf8');
const nextPyproject = pyproject.replace(
  /^version\s*=\s*"[^"]+"/m,
  `version = "${version}"`,
);
if (!nextPyproject.includes(`version = "${version}"`)) {
  console.error('sync-sdk-version: failed to update pyproject.toml');
  process.exit(1);
}
writeFileSync(pyprojectPath, nextPyproject, 'utf8');

const versionPyPath = join(root, 'src', 'imazeo', 'version.py');
const versionPy = readFileSync(versionPyPath, 'utf8');
const nextVersionPy = versionPy.replace(
  /SDK_VERSION:\s*Final\s*=\s*"[^"]+"/,
  `SDK_VERSION: Final = "${version}"`,
);
if (!nextVersionPy.includes(`SDK_VERSION: Final = "${version}"`)) {
  console.error('sync-sdk-version: failed to update version.py');
  process.exit(1);
}
writeFileSync(versionPyPath, nextVersionPy, 'utf8');

const add = spawnSync(
  'git',
  ['add', 'pyproject.toml', 'src/imazeo/version.py', 'package.json'],
  {
    cwd: root,
    stdio: 'inherit',
    shell: false,
  },
);
if (add.status !== 0) process.exit(add.status ?? 1);
console.log(`sync-sdk-version: ${version}`);
