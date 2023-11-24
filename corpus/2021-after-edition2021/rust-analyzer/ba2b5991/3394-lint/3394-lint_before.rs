//! Completion for lints
use ide_db::helpers::generated_lints::Lint;
use syntax::{ast, T};

use crate::{
    context::CompletionContext,
    item::{CompletionItem, CompletionItemKind, CompletionKind},
    Completions,
};

pub(super) fn complete_lint(
    acc: &mut Completions,
    ctx: &CompletionContext,
    derive_input: ast::TokenTree,
    lints_completions: &[Lint],
) {
    if let Some(existing_lints) = super::parse_comma_sep_paths(derive_input) {
        for &Lint { label, description } in lints_completions {
            let (qual, name) = {
                // FIXME: change `Lint`'s label to not store a path in it but split the prefix off instead?
                let mut parts = label.split("::");
                let ns_or_label = match parts.next() {
                    Some(it) => it,
                    None => continue,
                };
                let label = parts.next();
                match label {
                    Some(label) => (Some(ns_or_label), label),
                    None => (None, ns_or_label),
                }
            };
            let lint_already_annotated = existing_lints
                .iter()
                .filter_map(|path| {
                    let q = path.qualifier();
                    if q.as_ref().and_then(|it| it.qualifier()).is_some() {
                        return None;
                    }
                    Some((q.and_then(|it| it.as_single_name_ref()), path.segment()?.name_ref()?))
                })
                .any(|(q, name_ref)| {
                    let qualifier_matches = match (q, qual) {
                        (None, None) => true,
                        (None, Some(_)) => false,
                        (Some(_), None) => false,
                        (Some(q), Some(ns)) => q.text() == ns,
                    };
                    qualifier_matches && name_ref.text() == name
                });
            if lint_already_annotated {
                continue;
            }
            let insert = match (qual, ctx.previous_token_is(T![:])) {
                (Some(qual), false) => format!("{}::{}", qual, name),
                // user is completing a qualified path but this completion has no qualifier
                // so discard this completion
                // FIXME: This is currently very hacky and will propose odd completions if
                // we add more qualified (tool) completions other than clippy
                (None, true) => continue,
                _ => name.to_owned(),
            };
            let mut item =
                CompletionItem::new(CompletionKind::Attribute, ctx.source_range(), label);
            item.kind(CompletionItemKind::Attribute)
                .insert_text(insert)
                .documentation(hir::Documentation::new(description.to_owned()));
            item.add_to(acc)
        }
    }
}
