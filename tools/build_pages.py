# Builds the Citius sub-pages (get-started, releases, research, contribute) from one shell.
# Usage: python3 -I build_pages.py <site dir>
import sys, os, html

SITE = sys.argv[1]
GH = 'https://github.com/agile-crypto'

HEAD = '''<!doctype html>
<html lang="en" data-type="software" data-radius="sharp" data-ground="sage" data-buttons="pill" data-motion>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="share.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#ffffff">
<meta name="site-kind" content="software">
<meta name="page-type" content="software">
<link rel="preload" href="assets/fonts/ibm-plex-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/system.css">
<link rel="stylesheet" href="assets/ui/cards.css">
<link rel="stylesheet" href="assets/motion/motion.css">
<link rel="stylesheet" href="assets/icons/icon.css">
<style>
:root {{
  --p-bg: #161c1a; --p-surface: #1f2725; --p-ink: #e3e2da; --p-muted: #8e948d;
  --p-accent: #9fc7b8; --p-accent-ink: #161c1a; --p-action: #9fc7b8; --p-action-ink: #161c1a;
  --p-inv-bg: #e3e2da; --p-inv-surface: #d3d2cb; --p-inv-ink: #161c1a; --p-inv-muted: #555a55;
  --p-inv-accent: #161c1a; --p-inv-accent-ink: #e3e2da; --p-inv-action: #161c1a; --p-inv-action-ink: #e3e2da;
  --font-display: "Familjen Grotesk", system-ui, sans-serif;
  --font-text: "Familjen Grotesk", system-ui, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
  --display-weight: 400;
  --display-tracking: -0.03em;
  --display-tracking-xl: -0.04em;
}}
</style>
<link rel="stylesheet" href="assets/site.css?v=10">
<link rel="stylesheet" href="assets/ibm.css?v=15">
<script>document.documentElement.classList.add('m-enter');setTimeout(()=>document.documentElement.classList.add('m-enter-done'),700)</script>
</head>
<body class="doc-page">
'''

NAV_ITEMS = [('index.html#how', 'Concepts', None), ('releases.html', 'Releases', 'releases'),
             ('research.html', 'Research', 'research'), ('contribute.html', 'Contribute', 'contribute')]

def nav(cur):
    items = []
    for href, word, key in NAV_ITEMS:
        ac = ' aria-current="page"' if key and key == cur else ''
        items.append(f'      <div class="nav__item"><a class="nav__link" href="{href}"{ac}>{word}</a></div>')
    return f'''<header class="nav nav--centre">
  <div class="wrap nav__bar">
    <a class="skip-link" href="#top">Skip to content</a>
    <a class="nav__logo" href="index.html">Citius</a>
    <nav class="nav__links" aria-label="Main">
{chr(10).join(items)}
    </nav>
    <div class="nav__actions">
      <a class="nav__link" href="{GH}">GitHub</a>
      <a class="btn btn--primary" href="get-started.html">Try the quickstart</a>
    </div>
    <button class="nav__toggle" type="button" aria-expanded="false" aria-label="Menu">
      <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M2 5h14M2 13h14" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
    </button>
  </div>
</header>
'''

FOOT = f'''<footer class="doc-foot ground-inverse" id="contact">
  <div class="wrap">
    <div class="grid">
      <div class="span-4 stack-4">
        <a class="nav__logo" href="index.html">Citius</a>
        <p class="footer__lede">An intent-based cryptography API from IBM Research Europe, Zurich.</p>
      </div>
      <div class="span-2 footer__col"><h3>Use</h3><ul><li><a href="get-started.html">Quickstart</a></li><li><a href="get-started.html#install">Install</a></li><li><a href="get-started.html#docs">Documentation</a></li></ul></div>
      <div class="span-2 footer__col"><h3>Reference</h3><ul><li><a href="releases.html">Releases</a></li><li><a href="{GH}/api">API specification</a></li></ul></div>
      <div class="span-2 footer__col"><h3>Project</h3><ul><li><a href="research.html">Research</a></li><li><a href="contribute.html">Contributing</a></li></ul></div>
      <div class="span-2 footer__col"><h3>Help</h3><ul><li><a href="contribute.html#security">Security</a></li><li><a href="contribute.html#community">Community</a></li><li><a href="{GH}">GitHub</a></li></ul></div>
    </div>
    <div class="footer__legal">
      <span>&copy; 2026 IBM Research Europe and contributors &nbsp; <a href="https://www.apache.org/licenses/LICENSE-2.0">Apache License 2.0</a></span>
      <span class="credits">Product names and logos are trademarks of their owners</span>
    </div>
  </div>
</footer>
'''

SCRIPTS = '''<script type="module" src="assets/system.js"></script>
<script type="module" src="assets/motion/motion.js"></script>
{extra}<script src="assets/site.js" defer></script>
</body>
</html>
'''

def code(text, lang=''):
    """A copyable code block; lines starting with '# ' become muted comments."""
    out = []
    for ln in text.strip('\n').split('\n'):
        e = html.escape(ln)
        if ln.lstrip().startswith('# ') or ln.lstrip().startswith('// '):
            e = f'<span class="c">{e}</span>'
        out.append(e)
    body = '\n'.join(out)
    return f'<div class="copy-wrap"><pre class="block"><code>{body}</code></pre><button class="copy-btn" type="button" data-copy>Copy</button></div>'

def sec(id_, title, body, toc=None):
    return f'''  <section class="doc-sec" id="{id_}" aria-labelledby="{id_}-h">
    <div class="wrap doc-grid">
      <div><h2 id="{id_}-h">{title}</h2></div>
      <div class="doc-body">
{body}
      </div>
    </div>
  </section>
'''

def page(fname, cur, title, desc, h1, lead, sections, extra=''):
    hero = f'''  <section class="doc-hero" aria-labelledby="page-h">
    <div class="wrap">
      <a class="crumb" href="index.html">Citius home</a>
      <h1 id="page-h">{h1}</h1>
      <p class="t-lead">{lead}</p>
    </div>
  </section>
'''
    doc = HEAD.format(title=html.escape(title), desc=html.escape(desc)) + nav(cur) + '<main id="top"><div class="doc-main">\n' + hero + ''.join(sections) + '</div></main>\n' + FOOT + SCRIPTS.format(extra=extra)
    with open(os.path.join(SITE, fname), 'w') as f:
        f.write(doc)

# ---------------------------------------------------------------- get-started.html
POLICY = '''{
  "version": "1",
  "allowed_templates": [
    "ecdsa-p256-sha256-der",
    "ml-dsa-65"
  ],
  "allowed_operations": {
    "key_operations": [
      "create_key", "read_key", "sign", "verify"
    ]
  }
}'''

GO_MAIN = '''package main

import (
	"context"
	"log"

	"github.com/agile-crypto/go-sdk/client/common"
	"github.com/agile-crypto/go-sdk/client/common/scope"
	"github.com/agile-crypto/go-sdk/client/crypto"
	"github.com/agile-crypto/go-sdk/client/cryptopolicy"
	"github.com/agile-crypto/go-sdk/client/keymanagement"
)

func main() {
	ctx := context.Background()
	pol, err := cryptopolicy.NewClientFromConfigFile(ctx, "citius.yaml")
	if err != nil { log.Fatal(err) }
	km, err := keymanagement.NewClientFromConfigFile(ctx, "citius.yaml")
	if err != nil { log.Fatal(err) }
	cr, err := crypto.NewClientFromConfigFile(ctx, "citius.yaml")
	if err != nil { log.Fatal(err) }

	// 1. a policy: which templates keys under it may use
	if _, msg, err := pol.CreatePolicy(ctx, "prod-signing", policyDoc); err != nil {
		log.Fatal(err, msg)
	}

	// 2. a key by intent: a standard signature, no algorithm named
	key, err := km.CreateKey(ctx, keymanagement.NewCreateKeyRequest(
		"contract-signing-key", "prod-signing", scope.SignatureStandard))
	if err != nil { log.Fatal(err) }
	log.Println("template:", key.KeyMetadata.TemplateId)

	// 3. sign and verify by key name
	doc := []byte("contract v1")
	sig, err := cr.Sign(ctx, crypto.NewSignRequest("contract-signing-key", doc))
	if err != nil { log.Fatal(err) }
	v, err := cr.Verify(ctx, crypto.NewVerifyRequest(
		"contract-signing-key", doc, sig.Signature(), sig.Metadata()))
	if err != nil { log.Fatal(err) }
	log.Println("valid:", v.Valid())

	// 4. move the key to a quantum-safe template; the Sign call above stays as it is
	t, err := km.TransformKey(ctx, keymanagement.NewTransformKeyRequest(
		"contract-signing-key", scope.SignatureStandard).
		WithSecurityProperties(&common.SecurityProperties{QuantumSafe: true}))
	if err != nil { log.Fatal(err) }
	log.Println("now:", t.NewKeyMetadata.TemplateId, "version", t.NewKeyMetadata.Version)
}'''

YAML = '''default:
  endpoint: "localhost:50051"
  tls:
    insecure: true   # dev only: the local server runs without TLS
  auth:
    enabled: false
  timeout: "30s"

# add an entry for each service that the program uses; {} uses the defaults
key_management: {}
crypto: {}
crypto_policy: {}'''

paths = f'''        <ul class="path-rows ic-dark">
          <li><img class="ic ic-40 ic-wide" src="assets/icons/grpc.svg" alt="" width="40" height="16"><div><a class="path-rows__name" href="#quickstart">Run the server</a><p>Run citius-server on localhost:50051, with in-memory keys and no authentication. Try it with grpcurl in five minutes.</p></div></li>
          <li><img class="ic ic-40 ic-wide" src="assets/icons/go.svg" alt="" width="40" height="15"><div><a class="path-rows__name" href="{GH}/citius-go-sdk">Call it from Go</a><p>The Go SDK gives Go clients for the services, with TLS, bearer tokens and YAML configuration.</p></div></li>
          <li><img class="ic ic-40 ic-ink" src="assets/icons/rust.svg" alt="" width="40" height="40"><div><a class="path-rows__name" href="#in-process">Link it into C</a><p>libagilecrypto runs the same API in your process. It has agc_* C headers and a Rust implementation.</p></div></li>
        </ul>'''

gs = []
gs.append(sec('paths', 'Three ways to use Citius', '''        <p>All three follow the same specification. The concepts are the same in each.</p>
''' + paths))
QS_STEPS = """# 2. create a policy: it lists the templates that its keys can use
jq -Rs '{name: "prod-signing", policyDocument: .}' policy.json \
  | grpcurl -plaintext -d @ localhost:50051 caas.crypto.v1.CryptoPolicyService/CreateCryptoPolicy

# 3. create a key from a scope: a standard signature, no algorithm
grpcurl -plaintext -d '{"name": "contract-signing-key", "policy": "prod-signing",
  "scopeSpec": {"signature": {"scope": "SIGNATURE_SCOPE_STANDARD"}}}' \
  localhost:50051 caas.crypto.v1.KeyManagementService/CreateKey | jq '.keyMetadata | {templateId, version}'

# 4. sign with the key name ("contract v1" in base64), then verify
grpcurl -plaintext -d '{"keyName": "contract-signing-key", "input": "Y29udHJhY3QgdjE=", "noContext": {}}' \
  localhost:50051 caas.crypto.v1.CryptoService/Sign > sig.json
jq '{keyName: "contract-signing-key", input: "Y29udHJhY3QgdjE=", signature, metadata, noContext: {}}' sig.json \
  | grpcurl -plaintext -d @ localhost:50051 caas.crypto.v1.CryptoService/Verify | jq '{valid}'

# 5. move the key to a quantum-safe template. The Sign request does not change.
grpcurl -plaintext -d '{"name": "contract-signing-key",
  "scopeSpec": {"signature": {"scope": "SIGNATURE_SCOPE_STANDARD", "security": {"quantumSafe": true}}}}' \
  localhost:50051 caas.crypto.v1.KeyManagementService/TransformKey | jq '.keyMetadata | {templateId, version}'"""

QS_OUT = """# step 3
{ "templateId": "ecdsa-p256-sha256-der", "version": 1 }
# step 4
{ "valid": true }
# step 5
{ "templateId": "ml-dsa-65", "version": 2 }"""

gs.append(sec('quickstart', 'Quickstart: sign, then move the key to ML-DSA', f'''        <p>This quickstart takes about five minutes. You need <a class="link" href="https://github.com/fullstorydev/grpcurl">grpcurl</a> and jq. You run the reference server and create a policy and a key from a scope. Then you sign, verify and move the key to a quantum-safe template.</p>
        <h3>1. Run citius-server</h3>
{code("""git clone https://github.com/agile-crypto/citius-server
cd citius-server
make run-dev    # gRPC on 127.0.0.1:50051 with reflection, no authentication, no TLS""")}
        <h3>2. Save the policy as policy.json</h3>
{code(POLICY)}
        <h3>3. Create, sign, verify, transform</h3>
{code(QS_STEPS)}
        <p>The commands return these results:</p>
{code(QS_OUT)}
        <p>Run the Verify command of step 4 again after step 5. The old signature is still valid against key version 1. A new Sign uses key version 2 and makes an ML-DSA-65 signature of 3,309 bytes.</p>
        <div class="note"><p>The server keeps keys in memory. When you restart the server, the key store is empty.</p></div>'''))
gs.append(sec('in-process', 'In-process from C', f'''        <p>libagilecrypto is the C API, written in Rust. You need a Rust toolchain, libclang for bindgen and a C compiler. The install command writes the library, the headers, a pkg-config file and a CMake package.</p>
{code("""git clone https://github.com/agile-crypto/citius-c-api
git clone https://github.com/agile-crypto/citius-rust
cd citius-rust
cargo xtask install --prefix /opt/agilecrypto
cc app.c $(pkg-config --cflags --libs agilecrypto)""")}
{code("""find_package(agilecrypto 1.0 REQUIRED)
target_link_libraries(app PRIVATE agilecrypto::agilecrypto)""")}
        <p>The <code>examples/c/</code> folder in citius-rust has three small programs: encrypt and decrypt, sign and verify, and a persistent key store. By default, keys stay in memory. To keep them on disk, set <code>key_store_uri</code> to a <code>file:</code> directory and supply a 32-byte wrapping key.</p>'''))
gs.append(sec('install', 'Install', f'''        <div class="table-scroll"><table class="doc-table">
          <thead><tr><th scope="col">Component</th><th scope="col">How to get it</th><th scope="col">Needs</th></tr></thead>
          <tbody>
            <tr><td>go-sdk</td><td>Clone citius-go-sdk and run <code>make sdk</code>. There is no tagged release yet.</td><td>Go, buf</td></tr>
            <tr><td>citius-server</td><td>Build from source with <code>make build</code> or <code>make docker-build</code></td><td>Go and OpenSSL 3.5 or later, or Docker or Podman</td></tr>
            <tr><td>citius-core</td><td><code>go get github.com/agile-crypto/citius-core@v0.4.2</code></td><td>Go</td></tr>
            <tr><td>libagilecrypto</td><td><code>cargo xtask install --prefix …</code> in citius-rust</td><td>Rust, libclang, a C compiler</td></tr>
            <tr><td>agc_* headers</td><td>Installed with libagilecrypto, or read from citius-c-api</td><td>A C99 or C++11 compiler</td></tr>
            <tr><td>api (protobuf)</td><td>Run <code>./build_proto.sh</code> in <code>proto/</code>. It writes Go code, a gRPC gateway and OpenAPI files.</td><td>buf, protoc plugins</td></tr>
          </tbody>
        </table></div>
        <p>There are no prebuilt binaries, signed release archives or published container images yet. If a repository has tags, build from a tagged commit. The <a class="link" href="releases.html">releases page</a> lists the tags. The team develops and tests on macOS and Linux.</p>'''))
docs = [
    ('API design philosophy', f'{GH}/api/blob/main/proto/API_DESIGN_PHILOSOPHY.md', 'Why the API is an abstraction layer, the deployment modes and the PKCS#11 v3.2 coverage'),
    ('Scope design summary', f'{GH}/api/blob/main/docs/SCOPE_DESIGN_SUMMARY.md', 'How scopes express intent, and the limits of each scope'),
    ('C API mapping', f'{GH}/citius-c-api/blob/main/docs/C_API_MAPPING.md', 'How protobuf types map to C: slices, buffers, tribools and tagged unions'),
    ('Deliberate divergences', f'{GH}/citius-c-api/blob/main/conformance/DIVERGENCES.yaml', 'Each difference between the C API and the wire format, with its reason'),
    ('Proposed extensions', f'{GH}/citius-c-api/blob/main/docs/PROTO_RFCS.md', 'RFCs for the specification, optional through agc_ext.h'),
    ('Rust implementation notes', f'{GH}/citius-rust/blob/main/DEVIATIONS.md', 'The differences between libagilecrypto and the Go server, with reasons'),
    ('Performance summary', f'{GH}/citius-rust/blob/main/docs/performance-summary.md', 'The cost of an agc_* call compared with RustCrypto: time, memory and stack'),
    ('Go SDK architecture', f'{GH}/citius-go-sdk/blob/main/ARCHITECTURE.md', 'How the clients, requests and configuration work together'),
    ('Server README', f'{GH}/citius-server#readme', 'The current features, flags, container, optional authentication and make targets'),
]
rows = '\n'.join(f'            <li><a class="rows__name link" href="{h}">{t}</a><p>{d}</p></li>' for t, h, d in docs)
gs.append(sec('docs', 'Documentation', f'''        <p>The reference documentation is in the repositories, next to the code. It includes the commented protobuf files, the OpenAPI files from <code>build_proto.sh</code>, the Go documentation of each module and the commented C headers.</p>
        <ul class="rows doc-rows">
{rows}
        </ul>
'''))
page('get-started.html', None, 'Get started with Citius: quickstart, installation and documentation',
     'Run the Citius reference server, create a key from a scope, sign, and move the key to ML-DSA. Or link libagilecrypto into a C program.',
     'Get started with Citius', 'Run the reference server and sign with a key that you create from a scope. Or link the C library into your process. Then find the reference documentation.', gs)

# ---------------------------------------------------------------- releases.html
comp_rows = [
    ('api', f'{GH}/api', 'Protobuf specification, caas.crypto.v1', 'v0.3.0', 'v0.2.0, v0.3.0', 'defines the specification'),
    ('citius-core', f'{GH}/citius-core', 'Go domain library', 'v0.4.2', 'v0.1.0 to v0.4.2', 'v0.3.0 (citius-api-go)'),
    ('citius-server', f'{GH}/citius-server', 'Reference gRPC server', 'main', 'none yet', 'v0.3.0 (citius-api-go), core v0.4.2'),
    ('go-sdk', f'{GH}/citius-go-sdk', 'Go clients', 'main', 'none yet', 'follows api main'),
    ('citius-c-api', f'{GH}/citius-c-api', 'C headers', 'API 1.0', 'none yet', 'v0.3.0 and two RPCs from main'),
    ('citius-rust', f'{GH}/citius-rust', 'libagilecrypto', '1.0.0', 'none yet', 'citius-c-api at HEADERS_PIN'),
    ('zitadel-grpc-auth', f'{GH}/zitadel-grpc-auth', 'Optional gRPC authentication', 'main', 'none yet', 'not related to the specification'),
]
trs = '\n'.join(f'            <tr><td><a class="link" href="{h}">{n}</a></td><td>{w}</td><td><code>{v}</code></td><td>{t}</td><td>{s}</td></tr>' for n, h, w, v, t, s in comp_rows)
rel = []
rel.append(sec('components', 'Components and versions', f'''        <div class="table-scroll"><table class="doc-table">
          <thead><tr><th scope="col">Repository</th><th scope="col">What it is</th><th scope="col">Current</th><th scope="col">Tags</th><th scope="col">Specification version</th></tr></thead>
          <tbody>
{trs}
          </tbody>
        </table></div>
        <p>The server also uses these Go modules from the same organization: <code>citius-api-go</code> v0.3.0 (the generated Go code of the specification), <code>citius-provider-go</code> v0.1.0, <code>ossl-go</code> v0.1.0 (OpenSSL bindings) and <code>vault-storage</code>.</p>'''))
page('releases.html', 'releases', 'Citius releases: components and versions',
     'Every Citius component with its current version and the spec version it follows.',
     'Releases', 'Seven core repositories follow one specification. This page shows the current version of each repository and the specification version that it follows.', rel)

# ---------------------------------------------------------------- research.html
BIB = '''@misc{rameshan2026intent,
  title         = {Intent-Based Cryptographic API Design for Cryptographic Agility},
  author        = {Rameshan, Navaneeth and Messmer, Gregoire},
  year          = {2026},
  eprint        = {2606.13445},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CR},
  url           = {https://arxiv.org/abs/2606.13445}
}

@misc{rameshan2026assessment,
  title         = {An Assessment Framework for Application-Level Cryptographic Agility},
  author        = {Rameshan, Navaneeth and Messmer, Gregoire},
  year          = {2026},
  eprint        = {2606.13425},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CR},
  url           = {https://arxiv.org/abs/2606.13425}
}'''
res = []
res.append(sec('assessment', 'An Assessment Framework for Application-Level Cryptographic Agility', '''        <p class="muted-meta">Navaneeth Rameshan and Gregoire Messmer, IBM Research Europe, Zurich. arXiv:2606.13425, cs.CR, 11 June 2026.</p>
        <blockquote class="abstract"><p>We introduce a component-based assessment framework that characterizes application-level cryptographic agility along seven orthogonal dimensions: three coupling dimensions that measure what the application code knows about algorithms and providers, a cross-cutting decoupling mechanism, a governance authority dimension, and two agility enablers that measure actual migration capability.</p></blockquote>
        <div class="btn-row"><a class="btn btn--secondary" href="https://arxiv.org/abs/2606.13425">Read the framework paper</a><a class="link" href="https://arxiv.org/pdf/2606.13425">Download the PDF</a></div>
'''))
res.append(sec('design', 'Intent-Based Cryptographic API Design for Cryptographic Agility', '''        <p class="muted-meta">Navaneeth Rameshan and Gregoire Messmer, IBM Research Europe, Zurich. arXiv:2606.13445, cs.CR, 11 June 2026.</p>
        <blockquote class="abstract"><p>As organizations move toward post-quantum cryptography, they face the major challenge of updating cryptographic algorithms across large, complex software portfolios. However, most cryptographic APIs in use today were designed around specific algorithms. … With this approach, updating cryptography becomes an operational process without the need to rewrite application code.</p></blockquote>
        <div class="btn-row"><a class="btn btn--secondary" href="https://arxiv.org/abs/2606.13445">Read the design paper</a><a class="link" href="https://arxiv.org/pdf/2606.13445">Download the PDF</a></div>
        <h3>Contributions of the paper</h3>
        <ul>
          <li>Thirteen design principles, from five properties: abstraction, stability, temporal flexibility, separation and extensibility.</li>
          <li>A scope vocabulary that names intent. Key creation does not name an algorithm.</li>
          <li>Two separate registries: one for templates and one for providers.</li>
          <li>A policy abstraction with two-phase evaluation. It does not set a policy format.</li>
          <li>Three types of key evolution: rotation, transformation and migration. Each key keeps its version history.</li>
        </ul>
        <p>The paper ends with a full migration scenario. The post-quantum transition is an operational procedure, and the application code does not change.</p>'''))
res.append(sec('cite', 'How to cite', f'''        <p>If you use Citius or its design in your work, cite the design paper. For the assessment and the comparison of existing APIs, cite the framework paper.</p>
{code(BIB)}
        <p>This page will list new papers and talks when they are published.</p>'''))
page('research.html', 'research', 'Citius research: two papers on cryptographic agility and how to cite them',
     'The two arXiv papers that are the basis of Citius: a framework that assesses cryptographic agility in six APIs, and the design of the intent-based API.',
     'Research behind Citius', 'Two IBM Research papers are the basis of Citius. The first paper measures how difficult an algorithm change is with current cryptographic APIs. The second paper designs the API that Citius implements.', res)

# ---------------------------------------------------------------- contribute.html
con = []
con.append(sec('ways', 'Ways to contribute', '''        <ul>
          <li><b>Report a bug or a missing feature.</b> Open an issue on the related repository. Include the component, the version and the platform.</li>
          <li><b>Add a provider or a template.</b> Write a new backend for citius-server, or a catalog entry with its security properties.</li>
          <li><b>Write a client in another language.</b> Use the protobuf specification. The Go SDK is an example.</li>
          <li><b>Improve the documentation.</b> There are no guides yet for policies, the key lifecycle or post-quantum migration. You can write them.</li>
          <li><b>Do research.</b> You can review and extend the assessment framework and the design principles.</li>
        </ul>'''))
con.append(sec('setup', 'Development setup', f'''        <h3>citius-server (Go)</h3>
{code("""make build      # compile all packages
make test       # unit tests
make test-race  # with the race detector
make lint       # golangci-lint and buf lint
make ci         # lint, race tests and smoke tests, required before a merge""")}
        <h3>citius-rust (Rust and C)</h3>
{code("""cargo test --workspace   # unit, architecture and header-pin tests
cargo xtask test-c       # rebuild the library, run the C tests without and with ASan+UBSan
cargo xtask all          # test-c, Miri, TSan and the Go interoperability tests
git config core.hooksPath .githooks   # pre-push: clippy, tests, test-c""")}
        <p>Miri and TSan need a nightly toolchain in addition to the default toolchain: <code>rustup toolchain install nightly --component miri --component rust-src</code>. The interoperability tests need Go and a citius-server clone in the same parent folder.</p>
        <h3>citius-c-api (headers)</h3>
{code("""cmake -S . -B build
cmake --build build      # fails if any header does not compile on its own
ctest --test-dir build --output-on-failure""")}
        <h3>api (protobuf)</h3>
{code("""cd proto && ./build_proto.sh   # Go, gRPC gateway and OpenAPI output""")}'''))
con.append(sec('spec-changes', 'Changes to the specification', '''        <p>Four implementations follow the protobuf specification, so each change to it starts as a proposal. Write the proposal as an RFC in the style of <a class="link" href="https://github.com/agile-crypto/citius-c-api/blob/main/docs/PROTO_RFCS.md">PROTO_RFCS.md</a>. Then open an issue on the api repository. Proposed C functions stay in <code>agc_ext.h</code>, behind <code>AGC_ENABLE_PROPOSED_EXTENSIONS</code>, until the specification includes them.</p>
        <p>An automatic check compares the C headers with a pinned copy of the specification. Each RPC must map to exactly one C function. <code>DIVERGENCES.yaml</code> records each intentional difference and its reason.</p>'''))
con.append(sec('security', 'Report a vulnerability', '''        <p>Do not report security problems in public issues. Use the private vulnerability reporting of GitHub on the affected repository: open Security, then Report a vulnerability. Include the component, the version or commit, and the steps to reproduce the problem.</p>
        <p>Citius is a research prototype. Do not use it in production. There is no commitment to a response time yet.</p>'''))
con.append(sec('community', 'Community and support', '''        <p>Send questions, ideas and bug reports as issues on the related repository at <a class="link" href="https://github.com/agile-crypto">github.com/agile-crypto</a>. All code is under the Apache License 2.0.</p>
        <p>The repositories do not have a contributing guide, a code of conduct or contributor terms yet. This page will link to them when they are available.</p>'''))
page('contribute.html', 'contribute', 'Contributing to Citius: setup, specification changes and security',
     'How to contribute to Citius: ways to help, the setup for each repository, the procedure for specification changes and how to report a vulnerability.',
     'Contributing to Citius', 'You can open issues and pull requests on every repository. This page shows the setup for each repository, the procedure for a specification change and how to report a vulnerability.', con)
print('built 4 pages')
