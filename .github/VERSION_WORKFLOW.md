# Auto Version Bump & Release Workflow

Workflow otomatis untuk bump version, create tag, dan release saat push ke GitHub.

## 🚀 Cara Kerja

### Otomatis (Auto Version Bump)

Workflow `version-bump.yml` akan otomatis berjalan saat:
- ✅ Push ke branch `main` (kecuali file markdown, docs, examples)
- ✅ Skip jika commit message mengandung `[skip version]`

**Version Bump Detection:**
- `feat:` atau `feature:` → **Minor** bump (1.0.0 → 1.1.0)
- `fix:` atau `bugfix:` → **Patch** bump (1.0.0 → 1.0.1)
- `break:` atau `breaking:` → **Major** bump (1.0.0 → 2.0.0)
- Default → **Patch** bump (1.0.0 → 1.0.1)

**Yang Dilakukan:**
1. ✅ Baca current version dari `havn/__init__.py`
2. ✅ Tentukan bump type (patch/minor/major)
3. ✅ Update version di:
   - `setup.py`
   - `havn/__init__.py`
   - `CHANGELOG.md`
4. ✅ Commit perubahan
5. ✅ Create Git tag (format: `v1.0.1`)
6. ✅ Create GitHub Release
7. ✅ Trigger `publish.yml` untuk upload ke PyPI

### Manual (Workflow Dispatch)

Anda juga bisa trigger manual dengan memilih bump type:

1. Go to **Actions** tab di GitHub
2. Select **"Auto Version Bump & Release"** workflow
3. Click **"Run workflow"**
4. Pilih bump type: `patch`, `minor`, atau `major`
5. Click **"Run workflow"**

## 📝 Contoh Commit Messages

```bash
# Minor bump (1.0.0 → 1.1.0)
git commit -m "feat: add new transaction method"

# Patch bump (1.0.0 → 1.0.1)
git commit -m "fix: resolve authentication error"

# Major bump (1.0.0 → 2.0.0)
git commit -m "breaking: change API signature"

# Skip version bump
git commit -m "docs: update README [skip version]"
```

## 🔄 Workflow Flow

```
Push to main
    ↓
version-bump.yml (auto detect bump type)
    ↓
Update version files
    ↓
Commit & Push
    ↓
Create Tag (v1.0.1)
    ↓
Create GitHub Release
    ↓
publish.yml (triggered by release)
    ↓
Build & Upload to PyPI
```

## ⚙️ Configuration

### Ignore Paths

Workflow akan **skip** jika hanya file berikut yang berubah:
- `*.md` files
- `.github/**`
- `docs/**`
- `examples/**`

### Skip Version Bump

Tambahkan `[skip version]` di commit message:

```bash
git commit -m "docs: update documentation [skip version]"
```

### Disable Auto Version

Jika ingin disable sementara, tambahkan kondisi di workflow atau gunakan `[skip version]` di semua commit.

## 🐛 Troubleshooting

### Workflow tidak berjalan

**Check:**
1. Apakah push ke branch `main`?
2. Apakah ada perubahan di file yang di-ignore?
3. Apakah commit message mengandung `[skip version]`?

### Tag sudah ada

Workflow akan **skip** jika tag sudah ada untuk versi yang sama. Ini mencegah duplicate release.

### Release tidak dibuat

**Check:**
1. Apakah `GITHUB_TOKEN` permission sudah benar?
2. Apakah tag berhasil dibuat?
3. Check workflow logs untuk error messages

### Version tidak update

**Check:**
1. Apakah format version di `havn/__init__.py` benar? (format: `"1.0.0"`)
2. Apakah workflow berhasil read version?
3. Check workflow logs

## 📚 Related Workflows

- **version-bump.yml**: Auto version bump & release
- **release.yml**: Fallback untuk manual tag creation
- **publish.yml**: Build & publish ke PyPI (triggered by release)

## 🎯 Best Practices

1. **Gunakan Conventional Commits**: Format commit message dengan prefix `feat:`, `fix:`, dll
2. **Update CHANGELOG.md Manual**: Workflow hanya auto-add minimal entry, lebih baik update manual
3. **Test Sebelum Release**: Pastikan semua test pass sebelum push ke main
4. **Review Changes**: Review perubahan sebelum merge ke main

## 📞 Support

Jika ada masalah dengan workflow:
1. Check workflow logs di Actions tab
2. Review error messages
3. Open issue di GitHub repository

