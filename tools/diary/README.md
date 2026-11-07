# Winter diary

The reader is `diary/`. It deliberately stays uninitialized and keeps password input hidden until `public.json`, `vault.json`, and `manifest.json` all pass structural checks. No personal diary entries or real keys are included in this implementation.

## Local checks

Requires Node.js 20+ (Web Crypto) and Python 3. No packages are required.

```sh
python3 tools/diary/build-initializer.py
node --test tools/diary/tests/*.test.cjs
```

The initializer outputs are self-contained: `diary/setup/index.html` for actual user-operated setup, `diary/setup/self-test.html` for synthetic browser testing, and an offline copy under this excluded tools directory. The self-test uses the displayed public test password and exports a deliberately incompatible `winter-diary-self-test` package. Never install that package.

`reference-vault.json` is only the already-public password verifier used by Snow Journal. It is not a password or an unwrapped private key. Its source is `vault.json` on the repository's `private` branch. Verify it still matches the existing app before rebuilding.

## Activation

1. The user opens the verified HTTPS initializer on a trusted device, reads the warnings, explicitly consents, and personally enters the existing password. Never request the password or plaintext private key in chat.
2. The page generates a separate RSA key pair, encrypts its private key with the existing password and a fresh salt, verifies a full round trip, and downloads the encrypted package. It does not upload anything.
3. The user keeps a safe backup and separately approves storing the public key, encrypted private-key wrapper, and empty manifest in this public repository for cross-device use. Anyone can download these bytes and attempt offline password guessing. Explain this before publishing them.
4. Receive the package and its fingerprint through the trusted user handoff. Pin the trusted fingerprint independently of the repository file. Validate without decrypting:

```sh
node tools/diary/inspect-setup.cjs --setup /path/to/encrypted-package.json --expected-key-id TRUSTED_FINGERPRINT
```

5. Ensure no previous diary keys or entries exist on the latest remote. Install the three documents in one non-force, checked commit. Never overwrite an existing key set or reuse a synthetic package. This structural check does not prove the encrypted private key decrypts; the user-operated initializer already self-tests it.
6. After deployment the user personally verifies unlocking with the existing password. Do not claim activation complete until this succeeds.

## Appending explicitly approved entries

Keep the private-key wrapper out of the write workflow. Read only the latest public key and manifest, and compare against the pinned trusted fingerprint. Fix one UUID per approved write and retain the same ciphertext for retries. Pipe approved plaintext through stdin, not command-line arguments or commit messages:

```sh
node tools/diary/encrypt-entry.cjs --public /path/to/public.json --expected-key-id TRUSTED_FINGERPRINT --id UUID --out /path/to/UUID.json
node tools/diary/prepare-manifest.cjs --manifest /path/to/manifest.json --entry /path/to/UUID.json --expected-key-id TRUSTED_FINGERPRINT
```

The first command creates ciphertext exclusively and refuses overwrite. The second prepares an additive manifest and reports the base manifest's SHA256. Re-read the remote head and atomically commit entry plus manifest. If the head changed, merge the newest manifest; never discard another entry. If the UUID already exists, compare exact ciphertext bytes before deciding whether the prior write succeeded.

Public-key encryption does not authenticate authors. Only the authorized repository write process accepts entries. No automatic collection from conversations is authorized by creating the diary.

## Security boundaries

The application uses browser-native RSA-OAEP-3072/SHA256, AES-256-GCM and PBKDF2-SHA256 with 600,000 iterations. The common password remains limited by the older 310,000-iteration verifier. Public ciphertext leaks sizes, counts, and commit times. Old Git history remains available after password changes.

The initializer embeds its CSS and JavaScript with exact CSP hashes and denies scripts from other sources, network connections, image loads and form submissions. Its application code contains no fetch, storage, telemetry, or upload operation. Hashes only bind resources to the loaded HTML: a malicious replacement of that HTML can replace the policy too. HTTPS and the site's integrity must still be trusted. Browser extensions, compromised devices or a compromised site can defeat this protection. JavaScript strings cannot be guaranteed physically erased.

This is reviewed application code and synthetic test coverage, not a professional cryptographic audit. Lost encrypted private keys or forgotten passwords cannot be recovered.
