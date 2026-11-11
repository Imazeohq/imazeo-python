# SDK release procedure (`imazeo` on PyPI)

Independent repository: [Imazeohq/imazeo-python](https://github.com/Imazeohq/imazeo-python).  
PyPI package: [`imazeo`](https://pypi.org/project/imazeo/).  
Supported API prefix: `v1`. SemVer lives in `pyproject.toml`, `SDK_VERSION`, and `package.json`
(kept in sync by the release script).

Never overwrite a published version; ship a patch instead.

## One-time: Trusted Publishing

On pypi.org (personal account that owns the project) → **imazeo** → **Publishing**:

| Field | Value |
| --- | --- |
| Owner | `Imazeohq` |
| Repository | `imazeo-python` |
| Workflow name | `publish.yml` |
| Environment | leave empty |

## Release (PowerShell)

Commit your work on `main` first (clean working tree required). One-time: `npm install`.

```powershell
$env:RELEASE_MODE = "true"
npm run release
```

You will be prompted for version bump and GitHub Release.  
This syncs versions, commits, tags `vX.Y.Z`, and pushes.  
**Publish PyPI** then uploads with OIDC.

## Release from GitHub only

If the version bump is already on `main`:

1. **Releases** → Draft a new release → tag `vX.Y.Z` → Publish  
   or
2. **Actions** → **Publish PyPI** → **Run workflow**

## After publish

Verify: https://pypi.org/project/imazeo/
