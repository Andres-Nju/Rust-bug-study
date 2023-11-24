use swc_common::chain;
use swc_ecma_ast::*;
use swc_ecma_visit::{as_folder, noop_visit_mut_type, Fold, VisitMut};

pub use crate::rename::rename;
use crate::rename::{renamer, Renamer};

#[cfg(test)]
mod tests;

#[derive(Debug, Clone, Default)]
pub struct Config {
    /// If true, the `hygiene` pass will preserve class names.
    pub keep_class_names: bool,
}

/// See [hygiene_with_config] for doc. Creates a `hygiene` pass with default
/// value of [Config].
pub fn hygiene() -> impl Fold + VisitMut + 'static {
    hygiene_with_config(Default::default())
}

/// The pass actually modifies the identifiers in the way that different
/// identifier (with respect to span hygiene) becomes different identifier.
/// (e.g. `a1` for `a#6`, `a2` for `a#23`)
///
/// # Implementation details
///
/// This document exists For curious people and potential contributors.
///
/// `hygiene` consists of four phases.
///
/// ## First phase
///
/// At first phase, we mark (using [swc_common::Mark]) nodes which can be
/// considered as a `scope`. e.g. [Function], [BlockStmt], [ArrowExpr]
///
/// ## Second phase
///
/// At second phase, we analyzes the file and determine identifiers to rename.
///
/// Note that we store scoping information for each node, using the fact that
/// [SyntaxContext] of all `scope` nodes are unique, thanks to the first phase.
///
///
/// ## Third phase
///
///  At third phase, we rename all identifiers in the queue.
pub fn hygiene_with_config(config: Config) -> impl 'static + Fold + VisitMut {
    chain!(renamer(config, HygieneRenamer), as_folder(HygieneRemover))
}

struct HygieneRenamer;

impl Renamer for HygieneRenamer {
    const PARALLEL: bool = false;
    const RESET_N: bool = true;

    fn new_name_for(&self, orig: &Id, n: &mut usize) -> swc_atoms::JsWord {
        let res = if *n == 0 {
            orig.0.clone()
        } else {
            format!("{}{}", orig.0, n).into()
        };
        *n += 1;
        res
    }
}

struct HygieneRemover;

impl VisitMut for HygieneRemover {
    noop_visit_mut_type!();

    fn visit_mut_ident(&mut self, i: &mut Ident) {
        i.span.ctxt = Default::default();
    }
}