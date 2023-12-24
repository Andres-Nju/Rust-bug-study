import logging
import time
import random
import requests
import threading
import json


# A list of GitHub repositories along with issue tags that suggest an issue is bug-related
repos = [
    ("rust-lang/rust-analyzer", ["C-bug", "I-crash", "I-panic"]),
    ("swc-project/swc", ["C-bug"]),
    ("AleoHQ/snarkOS",["bug", "compilation", "crash", "security", "critical", "feature", "linux", "macos", "performance", "windows"]),
    ("meilisearch/meilisearch", ["bug", "lmdb", "security"]),
    ("rust-lang/libc", ["C-bug", "C-bug-missing-packed", "C-bug-outdated-constant", "C-bug-outdated-type"]),
    ("cube-js/cube", ["bug"]),
    ("lencx/ChatGPT",["bug"]),
    ("vercel/turbo", ["kind:bug"]),
    ("AleoHQ/snarkVM", ["bug"]),
    ("mimblewimble/grin", ["bug"]),
    (
        "rust-lang/rust",
        [
            "C-bug",
            "I-crash",
            "I-unsound",
            "S-bug-has-test",
            "A-LLVM",
            "ICEBreaker-LLVM",
            "const-generics-fixed-by-const_generics",
            "const-generics-fixed-by-min_const_generics",
            "NLL-fixed-by-NLL",
        ],
    ),
    ("denoland/deno", ["bug"]),
    (
        "rust-lang/rust",
        [
            "C-bug",
            "I-crash",
            "I-unsound",
            "S-bug-has-test",
            "A-LLVM",
            "ICEBreaker-LLVM",
            "const-generics-fixed-by-const_generics",
            "const-generics-fixed-by-min_const_generics",
            "NLL-fixed-by-NLL",
        ],
    ),
    ("tock/tock", ["bug"]),
    ("tauri-apps/tauri", ["type: bug"]),
    ("alacritty/alacritty", ["B - bug", "B - build failure", "B - crash"]),
    ("sharkdp/bat", ["bug", "macOS", "windows", "security"]),
    ("BurntSushi/ripgrep", ["bug", "windows"]),
    ("rustdesk/rustdesk", ["bug"]),
    ("rust-lang/rustlings", ["C-bug"]),
    
    ("starship/starship", ["🐛 bug", ":lock: security"]),
    ("sharkdp/fd", ["bug"]),
    ("yewstack/yew", ["bug"]),
    
    ("nushell/nushell", [":bug:  bug", "panic", "syntax-highlighting"]),
    ("rome/tools", ["S-Bug: confirmed"]),
    ("lapce/lapce", ["C-bug", "C-crash"]),
    ("bevyengine/bevy", ["C-bug", "C-Crash", "C-Regression", "C-Unsoundness"]),
    ("firecracker-microvm/firecracker", ["Type: Bug"]),
    ("dani-garcia/vaultwarden", ["bug"]),
    ("ogham/exa", ["good-first-bug", "errors › build error", "errors › runtime error"]),
    ("xi-editor/xi-editor", ["bug", "crash", "build error"]),
    ("SergioBenitez/Rocket", ["bug"]),
    ("tokio-rs/tokio", ["C-bug", "I-crash", "I-unsound"]),
    ("iced-rs/iced", ["bug"]),
    ("diem/diem", ["bug"]),
    ("helix-editor/helix", ["C-bug"]),
    ("actix/actix-web", ["C-bug", "unsafe"]),
    ("dandavison/delta", ["bug"]),
    ("surrealdb/surrealdb", ["bug"]),
    ("Rigellute/spotify-tui", ["bug", "security"]),
    ("sharkdp/hyperfine", ["bug"]),
    ("wasmerio/wasmer", ["bug", "🔈soundness"]),
    ("RustPython/RustPython", ["C-bug"]),
    ("tikv/tikv", ["type/bug"]),
    ("denisidoro/navi", ["bug"]),
    ("emilk/egui", ["bug"]),
    ("vectordotdev/vector", ["type: bug"]),
    ("extrawurst/gitui", ["bug"]),
    ("rust-lang/mdBook", ["C-bug", "C-panic"]),
    ("ruffle-rs/ruffle", ["bug", "panic", "security"]),
    ("rust-lang/rust-analyzer", ["C-bug", "I-crash", "I-panic"]),
    ("hyperium/hyper", ["S-bug"]),
    ("rust-lang/book", ["bug"]),
    ("bytecodealliance/wasmtime", ["bug", "fuzz-bug"]),
    ("tree-sitter/tree-sitter", ["bug", "panic"]),
    ("clap-rs/clap", ["C-bug"]),
    ("getzola/zola", ["bug"]),
    ("solana-labs/solana", ["bug", "concensus"]),
    ("diesel-rs/diesel", ["bug"]),
    ("benfred/py-spy", ["bug"]),
    ("rust-lang/cargo", ["C-bug"]),
    ("pola-rs/polars", ["fix", "bug"]),
    ("fdehau/tui-rs", ["bug"]),
    ("zellij-org/zellij", ["bug"]),
    ("neovide/neovide", ["bug", "crash"]),
    ("BurntSushi/xsv", ["bug"]),
    ("qarmin/czkawka", ["bug"]),
    ("Peltoche/lsd", ["kind/bug"]),
    ("rust-lang/rust-clippy", ["C-bug", "I-ICE"]),
    ("paritytech/substrate", ["I3-bug", "I1-panic", "I2-security"]),
    ("LemmyNet/lemmy", ["bug"]),
    ("openethereum/parity-ethereum", ["F2-bug 🐞", "F1-panic 🔨", "F1-security 🛡"]),
    ("serde-rs/serde", ["bug", "compiler bug", "build"]),
    ("wez/wezterm", ["bug"]),
    ("rustwasm/wasm-bindgen", ["bug", "panic"]),
    ("gfx-rs/gfx", ["type: bug"]),
    ("rust-lang/rustup", ["bug", "security"]),
    ("mimblewimble/grin", ["bug"]),
    ("datafuselabs/databend", ["C-bug"]),
    ("rust-lang/rustfmt", ["bug"]),
    ("foundry-rs/foundry", ["T-bug"]),
    ("MaterializeInc/materialize", ["C-bug", "T-security"]),
    ("uutils/coreutils", ["I - Crash", "security"]),
    ("servo/servo", ["I-crash", "I-panic", "A-security"]),
    ("AppFlowy-IO/AppFlowy", ["bug"]),
]

gh_api_url = "https://api.github.com"
# GitHub fine-grained personal access tokens, replace with your own ones
gh_tokens = [
    "",
]
gh_token, timestamp, mux = gh_tokens[0], time.time(), threading.Lock()


# Encapsule GitHub API usage for simplicity of use
def gh_api(rel_url, params):
    global gh_token, timestamp
    logging.info(f"GitHub-API {rel_url}")
    trials = 3
    resp = None
    while trials > 0:
        try:
            time.sleep(0.1 + random.random() * 0.2)
            resp = requests.get(
                gh_api_url + rel_url,
                params=params,
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": "Bearer " + gh_token,
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            if 200 <= resp.status_code < 300:
                break
            logging.warning(f"GitHub-API {rel_url} status code {resp.status_code}")
            mux.acquire()
            # Switch to the next access token when the quota is exhausted
            if resp.status_code == 403 and time.time() - timestamp > 30.0:
                timestamp = time.time()
                gh_token = gh_tokens[(gh_tokens.index(gh_token) + 1) % len(gh_tokens)]
                logging.info("Changed to the next GitHub-API token")
            mux.release()
            # Sleep for a while when requested too frequently
            if resp.status_code == 429:
                time.sleep(3.0 + random.random() * 4.0)
        except:
            trials -= 1
    assert resp is not None
    return json.loads(resp.text), resp.links
