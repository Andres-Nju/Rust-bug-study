//! Grammar for the command-line arguments.
#![allow(unreachable_pub)]
use std::{path::PathBuf, str::FromStr};

use ide_ssr::{SsrPattern, SsrRule};

use crate::cli::Verbosity;

xflags::xflags! {
    src "./src/cli/flags.rs"

    /// LSP server for the Rust programming language.
    cmd rust-analyzer {
        /// Verbosity level, can be repeated multiple times.
        repeated -v, --verbose
        /// Verbosity level.
        optional -q, --quiet

        /// Log to the specified file instead of stderr.
        optional --log-file path: PathBuf
        /// Flush log records to the file immediately.
        optional --no-log-buffering

        /// Wait until a debugger is attached to (requires debug build).
        optional --wait-dbg

        default cmd lsp-server {
            /// Print version.
            optional --version
            /// Print help.
            optional -h, --help

            /// Dump a LSP config JSON schema.
            optional --print-config-schema
        }

        /// Parse stdin.
        cmd parse {
            /// Suppress printing.
            optional --no-dump
        }

        /// Parse stdin and print the list of symbols.
        cmd symbols {}

        /// Highlight stdin as html.
        cmd highlight {
            /// Enable rainbow highlighting of identifiers.
            optional --rainbow
        }

        /// Batch typecheck project and print summary statistics
        cmd analysis-stats
            /// Directory with Cargo.toml.
            required path: PathBuf
        {
            optional --output format: OutputFormat

            /// Randomize order in which crates, modules, and items are processed.
            optional --randomize
            /// Run type inference in parallel.
            optional --parallel
            /// Collect memory usage statistics.
            optional --memory-usage
            /// Print the total length of all source and macro files (whitespace is not counted).
            optional --source-stats

            /// Only analyze items matching this path.
            optional -o, --only path: String
            /// Also analyze all dependencies.
            optional --with-deps
            /// Don't load sysroot crates (`std`, `core` & friends).
            optional --no-sysroot

            /// Don't run build scripts or load `OUT_DIR` values by running `cargo check` before analysis.
            optional --disable-build-scripts
            /// Don't use expand proc macros.
            optional --disable-proc-macros
            /// Only resolve names, don't run type inference.
            optional --skip-inference
        }

        cmd diagnostics
            /// Directory with Cargo.toml.
            required path: PathBuf
        {
            /// Don't run build scripts or load `OUT_DIR` values by running `cargo check` before analysis.
            optional --disable-build-scripts
            /// Don't use expand proc macros.
            optional --disable-proc-macros
        }

        cmd ssr
            /// A structured search replace rule (`$a.foo($b) ==> bar($a, $b)`)
            repeated rule: SsrRule
        {}

        cmd search
            /// A structured search replace pattern (`$a.foo($b)`)
            repeated pattern: SsrPattern
        {
            /// Prints debug information for any nodes with source exactly equal to snippet.
            optional --debug snippet: String
        }

        cmd proc-macro {}

        cmd lsif
            required path: PathBuf
        {}
    }
}

// generated start
// The following code is generated by `xflags` macro.
// Run `env UPDATE_XFLAGS=1 cargo build` to regenerate.
#[derive(Debug)]
pub struct RustAnalyzer {
    pub verbose: u32,
    pub quiet: bool,
    pub log_file: Option<PathBuf>,
    pub no_log_buffering: bool,
    pub wait_dbg: bool,
    pub subcommand: RustAnalyzerCmd,
}

#[derive(Debug)]
pub enum RustAnalyzerCmd {
    LspServer(LspServer),
    Parse(Parse),
    Symbols(Symbols),
    Highlight(Highlight),
    AnalysisStats(AnalysisStats),
    Diagnostics(Diagnostics),
    Ssr(Ssr),
    Search(Search),
    ProcMacro(ProcMacro),
    Lsif(Lsif),
}

#[derive(Debug)]
pub struct LspServer {
    pub version: bool,
    pub help: bool,
    pub print_config_schema: bool,
}

#[derive(Debug)]
pub struct Parse {
    pub no_dump: bool,
}

#[derive(Debug)]
pub struct Symbols;

#[derive(Debug)]
pub struct Highlight {
    pub rainbow: bool,
}

#[derive(Debug)]
pub struct AnalysisStats {
    pub path: PathBuf,

    pub output: Option<OutputFormat>,
    pub randomize: bool,
    pub parallel: bool,
    pub memory_usage: bool,
    pub source_stats: bool,
    pub only: Option<String>,
    pub with_deps: bool,
    pub no_sysroot: bool,
    pub disable_build_scripts: bool,
    pub disable_proc_macros: bool,
    pub skip_inference: bool,
}

#[derive(Debug)]
pub struct Diagnostics {
    pub path: PathBuf,

    pub disable_build_scripts: bool,
    pub disable_proc_macros: bool,
}

#[derive(Debug)]
pub struct Ssr {
    pub rule: Vec<SsrRule>,
}

#[derive(Debug)]
pub struct Search {
    pub pattern: Vec<SsrPattern>,

    pub debug: Option<String>,
}

#[derive(Debug)]
pub struct ProcMacro;

#[derive(Debug)]
pub struct Lsif {
    pub path: PathBuf,
}

impl RustAnalyzer {
    pub const HELP: &'static str = Self::HELP_;

    #[allow(dead_code)]
    pub fn from_env() -> xflags::Result<Self> {
        Self::from_env_()
    }

    #[allow(dead_code)]
    pub fn from_vec(args: Vec<std::ffi::OsString>) -> xflags::Result<Self> {
        Self::from_vec_(args)
    }
}
// generated end

#[derive(Debug, PartialEq, Eq)]
pub enum OutputFormat {
    Csv,
}

impl RustAnalyzer {
    pub fn verbosity(&self) -> Verbosity {
        if self.quiet {
            return Verbosity::Quiet;
        }
        match self.verbose {
            0 => Verbosity::Normal,
            1 => Verbosity::Verbose,
            _ => Verbosity::Spammy,
        }
    }
}

impl FromStr for OutputFormat {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "csv" => Ok(Self::Csv),
            _ => Err(format!("unknown output format `{}`", s)),
        }
    }
}
