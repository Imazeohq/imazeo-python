# SDK release procedure (`imazeo` on PyPI)

Independent repository: [manishbalodia/imazeo-python](https://github.com/manishbalodia/imazeo-python).  
PyPI project: [`imazeo`](https://pypi.org/project/imazeo/).  
Supported API prefix: `v1`. SemVer lives in this repo (`pyproject.toml` + `src/imazeo/version.py`).

Do not publish automatically from CI until a protected release workflow is added.
Never overwrite a published version; ship a patch instead.

## Pre-publish checks

```powershell
cd D:\projects\imazeo\sdk-python
python scripts\check-release.py
python -m pip install ".[dev]" build twine
python -m pytest
python -m build
python -m twine check dist\*
```

Optional: `pip-audit` on the installed package environment.

Confirm the wheel/sdist contain the intended files (no API keys or `.env`).

## Manual publish (first release `1.0.0`)

1. Create empty GitHub repo `manishbalodia/imazeo-python` and push this tree to `main`.
2. Clean `main`, equal to the revision you verified.
3. `git tag v1.0.0` and push `main` + `v1.0.0`.
4. Create a PyPI account (or log in), enable 2FA, and create an **API token**
   (project-scoped after first upload, or account token for the first publish).
5. Publish:
   ```powershell
   python -m twine upload dist\*
   ```
   Or Trusted Publishing from GitHub Actions once configured.
6. Verify: `pip index versions imazeo` / https://pypi.org/project/imazeo/

## After publish

Record the Git revision and check results. Smoke-install in a temp venv:

```powershell
python -m venv .venv-smoke
.\.venv-smoke\Scripts\Activate.ps1
pip install imazeo==1.0.0
```

If the release is bad, yank per PyPI policy and ship a reviewed patch — do not
reupload the same version.
