//! Renderer for type aliases.

use hir::{AsAssocItem, HirDisplay};
use ide_db::SymbolKind;
use syntax::SmolStr;

use crate::{item::CompletionItem, render::RenderContext};

pub(crate) fn render_type_alias(
    ctx: RenderContext<'_>,
    type_alias: hir::TypeAlias,
) -> Option<CompletionItem> {
    let _p = profile::span("render_type_alias");
    render(ctx, type_alias, false)
}

pub(crate) fn render_type_alias_with_eq(
    ctx: RenderContext<'_>,
    type_alias: hir::TypeAlias,
) -> Option<CompletionItem> {
    let _p = profile::span("render_type_alias_with_eq");
    render(ctx, type_alias, true)
}

fn render(
    ctx: RenderContext<'_>,
    type_alias: hir::TypeAlias,
    with_eq: bool,
) -> Option<CompletionItem> {
    let db = ctx.db();

    let name = if with_eq {
        SmolStr::from_iter([&*type_alias.name(db).to_smol_str(), " = "])
    } else {
        type_alias.name(db).to_smol_str()
    };
    let detail = type_alias.display(db).to_string();

    let mut item = CompletionItem::new(SymbolKind::TypeAlias, ctx.source_range(), name.clone());
    item.set_documentation(ctx.docs(type_alias))
        .set_deprecated(ctx.is_deprecated(type_alias) || ctx.is_deprecated_assoc_item(type_alias))
        .detail(detail)
        .set_relevance(ctx.completion_relevance());

    if let Some(actm) = type_alias.as_assoc_item(db) {
        if let Some(trt) = actm.containing_trait_or_trait_impl(db) {
            item.trait_name(trt.name(db).to_smol_str());
            item.insert_text(name);
        }
    }

    Some(item.build())
}
