//! This module provides primitives for showing type and function parameter information when editing
//! a call or use-site.

use either::Either;
use hir::{HasAttrs, HirDisplay, Semantics};
use ide_db::{
    active_parameter::{callable_for_token, generics_for_token},
    base_db::FilePosition,
};
use stdx::format_to;
use syntax::{algo, AstNode, Direction, TextRange, TextSize};

use crate::RootDatabase;

/// Contains information about an item signature as seen from a use site.
///
/// This includes the "active parameter", which is the parameter whose value is currently being
/// edited.
#[derive(Debug)]
pub struct SignatureHelp {
    pub doc: Option<String>,
    pub signature: String,
    pub active_parameter: Option<usize>,
    parameters: Vec<TextRange>,
}

impl SignatureHelp {
    pub fn parameter_labels(&self) -> impl Iterator<Item = &str> + '_ {
        self.parameters.iter().map(move |&it| &self.signature[it])
    }

    pub fn parameter_ranges(&self) -> &[TextRange] {
        &self.parameters
    }

    fn push_call_param(&mut self, param: &str) {
        self.push_param('(', param);
    }

    fn push_generic_param(&mut self, param: &str) {
        self.push_param('<', param);
    }

    fn push_param(&mut self, opening_delim: char, param: &str) {
        if !self.signature.ends_with(opening_delim) {
            self.signature.push_str(", ");
        }
        let start = TextSize::of(&self.signature);
        self.signature.push_str(param);
        let end = TextSize::of(&self.signature);
        self.parameters.push(TextRange::new(start, end))
    }
}

/// Computes parameter information for the given position.
pub(crate) fn signature_help(db: &RootDatabase, position: FilePosition) -> Option<SignatureHelp> {
    let sema = Semantics::new(db);
    let file = sema.parse(position.file_id);
    let file = file.syntax();
    let token = file
        .token_at_offset(position.offset)
        .left_biased()
        // if the cursor is sandwiched between two space tokens and the call is unclosed
        // this prevents us from leaving the CallExpression
        .and_then(|tok| algo::skip_trivia_token(tok, Direction::Prev))?;
    let token = sema.descend_into_macros_single(token);

    if let Some((callable, active_parameter)) = callable_for_token(&sema, token.clone()) {
        return Some(signature_help_for_callable(db, callable, active_parameter));
    }

    if let Some((generic_def, active_parameter)) = generics_for_token(&sema, token.clone()) {
        return signature_help_for_generics(db, generic_def, active_parameter);
    }

    None
}

fn signature_help_for_callable(
    db: &RootDatabase,
    callable: hir::Callable,
    active_parameter: Option<usize>,
) -> SignatureHelp {
    let mut res =
        SignatureHelp { doc: None, signature: String::new(), parameters: vec![], active_parameter };

    match callable.kind() {
        hir::CallableKind::Function(func) => {
            res.doc = func.docs(db).map(|it| it.into());
            format_to!(res.signature, "fn {}", func.name(db));
        }
        hir::CallableKind::TupleStruct(strukt) => {
            res.doc = strukt.docs(db).map(|it| it.into());
            format_to!(res.signature, "struct {}", strukt.name(db));
        }
        hir::CallableKind::TupleEnumVariant(variant) => {
            res.doc = variant.docs(db).map(|it| it.into());
            format_to!(
                res.signature,
                "enum {}::{}",
                variant.parent_enum(db).name(db),
                variant.name(db)
            );
        }
        hir::CallableKind::Closure => (),
    }

    res.signature.push('(');
    {
        if let Some(self_param) = callable.receiver_param(db) {
            format_to!(res.signature, "{}", self_param)
        }
        let mut buf = String::new();
        for (pat, ty) in callable.params(db) {
            buf.clear();
            if let Some(pat) = pat {
                match pat {
                    Either::Left(_self) => format_to!(buf, "self: "),
                    Either::Right(pat) => format_to!(buf, "{}: ", pat),
                }
            }
            format_to!(buf, "{}", ty.display(db));
            res.push_call_param(&buf);
        }
    }
    res.signature.push(')');

    match callable.kind() {
        hir::CallableKind::Function(_) | hir::CallableKind::Closure => {
            let ret_type = callable.return_type();
            if !ret_type.is_unit() {
                format_to!(res.signature, " -> {}", ret_type.display(db));
            }
        }
        hir::CallableKind::TupleStruct(_) | hir::CallableKind::TupleEnumVariant(_) => {}
    }
    res
}

fn signature_help_for_generics(
    db: &RootDatabase,
    mut generics_def: hir::GenericDef,
    active_parameter: usize,
) -> Option<SignatureHelp> {
    let mut res = SignatureHelp {
        doc: None,
        signature: String::new(),
        parameters: vec![],
        active_parameter: Some(active_parameter),
    };

    match generics_def {
        hir::GenericDef::Function(it) => {
            res.doc = it.docs(db).map(|it| it.into());
            format_to!(res.signature, "fn {}", it.name(db));
        }
        hir::GenericDef::Adt(hir::Adt::Enum(it)) => {
            res.doc = it.docs(db).map(|it| it.into());
            format_to!(res.signature, "enum {}", it.name(db));
        }
        hir::GenericDef::Adt(hir::Adt::Struct(it)) => {
            res.doc = it.docs(db).map(|it| it.into());
            format_to!(res.signature, "struct {}", it.name(db));
        }
        hir::GenericDef::Adt(hir::Adt::Union(it)) => {
            res.doc = it.docs(db).map(|it| it.into());
            format_to!(res.signature, "union {}", it.name(db));
        }
        hir::GenericDef::Trait(it) => {
            res.doc = it.docs(db).map(|it| it.into());
            format_to!(res.signature, "trait {}", it.name(db));
        }
        hir::GenericDef::TypeAlias(it) => {
            res.doc = it.docs(db).map(|it| it.into());
            format_to!(res.signature, "type {}", it.name(db));
        }
        hir::GenericDef::Variant(it) => {
            // In paths, generics of an enum can be specified *after* one of its variants.
            // eg. `None::<u8>`
            // We'll use the signature of the enum, but include the docs of the variant.
            res.doc = it.docs(db).map(|it| it.into());
            let it = it.parent_enum(db);
            format_to!(res.signature, "enum {}", it.name(db));
            generics_def = it.into();
        }
        // These don't have generic args that can be specified
        hir::GenericDef::Impl(_) | hir::GenericDef::Const(_) => return None,
    }

    res.signature.push('<');
    let params = generics_def.params(db);
    let mut buf = String::new();
    for param in params {
        if let hir::GenericParam::TypeParam(ty) = param {
            if ty.is_implicit(db) {
                continue;
            }
        }

        buf.clear();
        format_to!(buf, "{}", param.display(db));
        res.push_generic_param(&buf);
    }
    res.signature.push('>');

    Some(res)
}

#[cfg(test)]
mod tests {
    use expect_test::{expect, Expect};
    use ide_db::base_db::{fixture::ChangeFixture, FilePosition};

    use crate::RootDatabase;

    /// Creates analysis from a multi-file fixture, returns positions marked with $0.
    pub(crate) fn position(ra_fixture: &str) -> (RootDatabase, FilePosition) {
        let change_fixture = ChangeFixture::parse(ra_fixture);
        let mut database = RootDatabase::default();
        database.apply_change(change_fixture.change);
        let (file_id, range_or_offset) =
            change_fixture.file_position.expect("expected a marker ($0)");
        let offset = range_or_offset.expect_offset();
        (database, FilePosition { file_id, offset })
    }

    fn check(ra_fixture: &str, expect: Expect) {
        // Implicitly add `Sized` to avoid noisy `T: ?Sized` in the results.
        let fixture = format!(
            r#"
#[lang = "sized"] trait Sized {{}}
{ra_fixture}
            "#
        );
        let (db, position) = position(&fixture);
        let call_info = crate::signature_help::signature_help(&db, position);
        let actual = match call_info {
            Some(call_info) => {
                let docs = match &call_info.doc {
                    None => "".to_string(),
                    Some(docs) => format!("{}\n------\n", docs.as_str()),
                };
                let params = call_info
                    .parameter_labels()
                    .enumerate()
                    .map(|(i, param)| {
                        if Some(i) == call_info.active_parameter {
                            format!("<{}>", param)
                        } else {
                            param.to_string()
                        }
                    })
                    .collect::<Vec<_>>()
                    .join(", ");
                format!("{}{}\n({})\n", docs, call_info.signature, params)
            }
            None => String::new(),
        };
        expect.assert_eq(&actual);
    }

    #[test]
    fn test_fn_signature_two_args() {
        check(
            r#"
fn foo(x: u32, y: u32) -> u32 {x + y}
fn bar() { foo($03, ); }
"#,
            expect![[r#"
                fn foo(x: u32, y: u32) -> u32
                (<x: u32>, y: u32)
            "#]],
        );
        check(
            r#"
fn foo(x: u32, y: u32) -> u32 {x + y}
fn bar() { foo(3$0, ); }
"#,
            expect![[r#"
                fn foo(x: u32, y: u32) -> u32
                (<x: u32>, y: u32)
            "#]],
        );
        check(
            r#"
fn foo(x: u32, y: u32) -> u32 {x + y}
fn bar() { foo(3,$0 ); }
"#,
            expect![[r#"
                fn foo(x: u32, y: u32) -> u32
                (x: u32, <y: u32>)
            "#]],
        );
        check(
            r#"
fn foo(x: u32, y: u32) -> u32 {x + y}
fn bar() { foo(3, $0); }
"#,
            expect![[r#"
                fn foo(x: u32, y: u32) -> u32
                (x: u32, <y: u32>)
            "#]],
        );
    }

    #[test]
    fn test_fn_signature_two_args_empty() {
        check(
            r#"
fn foo(x: u32, y: u32) -> u32 {x + y}
fn bar() { foo($0); }
"#,
            expect![[r#"
                fn foo(x: u32, y: u32) -> u32
                (<x: u32>, y: u32)
            "#]],
        );
    }

    #[test]
    fn test_fn_signature_two_args_first_generics() {
        check(
            r#"
fn foo<T, U: Copy + Display>(x: T, y: U) -> u32
    where T: Copy + Display, U: Debug
{ x + y }

fn bar() { foo($03, ); }
"#,
            expect![[r#"
                fn foo(x: i32, y: {unknown}) -> u32
                (<x: i32>, y: {unknown})
            "#]],
        );
    }

    #[test]
    fn test_fn_signature_no_params() {
        check(
            r#"
fn foo<T>() -> T where T: Copy + Display {}
fn bar() { foo($0); }
"#,
            expect![[r#"
                fn foo() -> {unknown}
                ()
            "#]],
        );
    }

    #[test]
    fn test_fn_signature_for_impl() {
        check(
            r#"
struct F;
impl F { pub fn new() { } }
fn bar() {
    let _ : F = F::new($0);
}
"#,
            expect![[r#"
                fn new()
                ()
            "#]],
        );
    }

    #[test]
    fn test_fn_signature_for_method_self() {
        check(
            r#"
struct S;
impl S { pub fn do_it(&self) {} }

fn bar() {
    let s: S = S;
    s.do_it($0);
}
"#,
            expect![[r#"
                fn do_it(&self)
                ()
            "#]],
        );
    }

    #[test]
    fn test_fn_signature_for_method_with_arg() {
        check(
            r#"
struct S;
impl S {
    fn foo(&self, x: i32) {}
}

fn main() { S.foo($0); }
"#,
            expect![[r#"
                fn foo(&self, x: i32)
                (<x: i32>)
            "#]],
        );
    }

    #[test]
    fn test_fn_signature_for_generic_method() {
        check(
            r#"
struct S<T>(T);
impl<T> S<T> {
    fn foo(&self, x: T) {}
}

fn main() { S(1u32).foo($0); }
"#,
            expect![[r#"
                fn foo(&self, x: u32)
                (<x: u32>)
            "#]],
        );
    }

    #[test]
    fn test_fn_signature_for_method_with_arg_as_assoc_fn() {
        check(
            r#"
struct S;
impl S {
    fn foo(&self, x: i32) {}
}

fn main() { S::foo($0); }
"#,
            expect![[r#"
                fn foo(self: &S, x: i32)
                (<self: &S>, x: i32)
            "#]],
        );
    }

    #[test]
    fn test_fn_signature_with_docs_simple() {
        check(
            r#"
/// test
// non-doc-comment
fn foo(j: u32) -> u32 {
    j
}

fn bar() {
    let _ = foo($0);
}
"#,
            expect![[r#"
            test
            ------
            fn foo(j: u32) -> u32
            (<j: u32>)
        "#]],
        );
    }

    #[test]
    fn test_fn_signature_with_docs() {
        check(
            r#"
/// Adds one to the number given.
///
/// # Examples
///
/// ```
/// let five = 5;
///
/// assert_eq!(6, my_crate::add_one(5));
/// ```
pub fn add_one(x: i32) -> i32 {
    x + 1
}

pub fn do() {
    add_one($0
}"#,
            expect![[r##"
            Adds one to the number given.

            # Examples

            ```
            let five = 5;

            assert_eq!(6, my_crate::add_one(5));
            ```
            ------
            fn add_one(x: i32) -> i32
            (<x: i32>)
        "##]],
        );
    }

    #[test]
    fn test_fn_signature_with_docs_impl() {
        check(
            r#"
struct addr;
impl addr {
    /// Adds one to the number given.
    ///
    /// # Examples
    ///
    /// ```
    /// let five = 5;
    ///
    /// assert_eq!(6, my_crate::add_one(5));
    /// ```
    pub fn add_one(x: i32) -> i32 {
        x + 1
    }
}

pub fn do_it() {
    addr {};
    addr::add_one($0);
}
"#,
            expect![[r##"
            Adds one to the number given.

            # Examples

            ```
            let five = 5;

            assert_eq!(6, my_crate::add_one(5));
            ```
            ------
            fn add_one(x: i32) -> i32
            (<x: i32>)
        "##]],
        );
    }

    #[test]
    fn test_fn_signature_with_docs_from_actix() {
        check(
            r#"
struct WriteHandler<E>;

impl<E> WriteHandler<E> {
    /// Method is called when writer emits error.
    ///
    /// If this method returns `ErrorAction::Continue` writer processing
    /// continues otherwise stream processing stops.
    fn error(&mut self, err: E, ctx: &mut Self::Context) -> Running {
        Running::Stop
    }

    /// Method is called when writer finishes.
    ///
    /// By default this method stops actor's `Context`.
    fn finished(&mut self, ctx: &mut Self::Context) {
        ctx.stop()
    }
}

pub fn foo(mut r: WriteHandler<()>) {
    r.finished($0);
}
"#,
            expect![[r#"
            Method is called when writer finishes.

            By default this method stops actor's `Context`.
            ------
            fn finished(&mut self, ctx: &mut {unknown})
            (<ctx: &mut {unknown}>)
        "#]],
        );
    }

    #[test]
    fn call_info_bad_offset() {
        check(
            r#"
fn foo(x: u32, y: u32) -> u32 {x + y}
fn bar() { foo $0 (3, ); }
"#,
            expect![[""]],
        );
    }

    #[test]
    fn test_nested_method_in_lambda() {
        check(
            r#"
struct Foo;
impl Foo { fn bar(&self, _: u32) { } }

fn bar(_: u32) { }

fn main() {
    let foo = Foo;
    std::thread::spawn(move || foo.bar($0));
}
"#,
            expect![[r#"
                fn bar(&self, _: u32)
                (<_: u32>)
            "#]],
        );
    }

    #[test]
    fn works_for_tuple_structs() {
        check(
            r#"
/// A cool tuple struct
struct S(u32, i32);
fn main() {
    let s = S(0, $0);
}
"#,
            expect![[r#"
            A cool tuple struct
            ------
            struct S(u32, i32)
            (u32, <i32>)
        "#]],
        );
    }

    #[test]
    fn generic_struct() {
        check(
            r#"
struct S<T>(T);
fn main() {
    let s = S($0);
}
"#,
            expect![[r#"
                struct S({unknown})
                (<{unknown}>)
            "#]],
        );
    }

    #[test]
    fn works_for_enum_variants() {
        check(
            r#"
enum E {
    /// A Variant
    A(i32),
    /// Another
    B,
    /// And C
    C { a: i32, b: i32 }
}

fn main() {
    let a = E::A($0);
}
"#,
            expect![[r#"
            A Variant
            ------
            enum E::A(i32)
            (<i32>)
        "#]],
        );
    }

    #[test]
    fn cant_call_struct_record() {
        check(
            r#"
struct S { x: u32, y: i32 }
fn main() {
    let s = S($0);
}
"#,
            expect![[""]],
        );
    }

    #[test]
    fn cant_call_enum_record() {
        check(
            r#"
enum E {
    /// A Variant
    A(i32),
    /// Another
    B,
    /// And C
    C { a: i32, b: i32 }
}

fn main() {
    let a = E::C($0);
}
"#,
            expect![[""]],
        );
    }

    #[test]
    fn fn_signature_for_call_in_macro() {
        check(
            r#"
macro_rules! id { ($($tt:tt)*) => { $($tt)* } }
fn foo() { }
id! {
    fn bar() { foo($0); }
}
"#,
            expect![[r#"
                fn foo()
                ()
            "#]],
        );
    }

    #[test]
    fn call_info_for_lambdas() {
        check(
            r#"
struct S;
fn foo(s: S) -> i32 { 92 }
fn main() {
    (|s| foo(s))($0)
}
        "#,
            expect![[r#"
                (S) -> i32
                (<S>)
            "#]],
        )
    }

    #[test]
    fn call_info_for_fn_ptr() {
        check(
            r#"
fn main(f: fn(i32, f64) -> char) {
    f(0, $0)
}
        "#,
            expect![[r#"
                (i32, f64) -> char
                (i32, <f64>)
            "#]],
        )
    }

    #[test]
    fn call_info_for_unclosed_call() {
        check(
            r#"
fn foo(foo: u32, bar: u32) {}
fn main() {
    foo($0
}"#,
            expect![[r#"
            fn foo(foo: u32, bar: u32)
            (<foo: u32>, bar: u32)
        "#]],
        );
        // check with surrounding space
        check(
            r#"
fn foo(foo: u32, bar: u32) {}
fn main() {
    foo( $0
}"#,
            expect![[r#"
            fn foo(foo: u32, bar: u32)
            (<foo: u32>, bar: u32)
        "#]],
        )
    }

    #[test]
    fn test_generics_simple() {
        check(
            r#"
/// Option docs.
enum Option<T> {
    Some(T),
    None,
}

fn f() {
    let opt: Option<$0
}
        "#,
            expect![[r#"
                Option docs.
                ------
                enum Option<T>
                (<T>)
            "#]],
        );
    }

    #[test]
    fn test_generics_on_variant() {
        check(
            r#"
/// Option docs.
enum Option<T> {
    /// Some docs.
    Some(T),
    /// None docs.
    None,
}

use Option::*;

fn f() {
    None::<$0
}
        "#,
            expect![[r#"
                None docs.
                ------
                enum Option<T>
                (<T>)
            "#]],
        );
    }

    #[test]
    fn test_lots_of_generics() {
        check(
            r#"
trait Tr<T> {}

struct S<T>(T);

impl<T> S<T> {
    fn f<G, H>(g: G, h: impl Tr<G>) where G: Tr<()> {}
}

fn f() {
    S::<u8>::f::<(), $0
}
        "#,
            expect![[r#"
                fn f<G: Tr<()>, H>
                (G: Tr<()>, <H>)
            "#]],
        );
    }

    #[test]
    fn test_generics_in_trait_ufcs() {
        check(
            r#"
trait Tr {
    fn f<T: Tr, U>() {}
}

struct S;

impl Tr for S {}

fn f() {
    <S as Tr>::f::<$0
}
        "#,
            expect![[r#"
                fn f<T: Tr, U>
                (<T: Tr>, U)
            "#]],
        );
    }

    #[test]
    fn test_generics_in_method_call() {
        check(
            r#"
struct S;

impl S {
    fn f<T>(&self) {}
}

fn f() {
    S.f::<$0
}
        "#,
            expect![[r#"
            fn f<T>
            (<T>)
        "#]],
        );
    }

    #[test]
    fn test_generic_kinds() {
        check(
            r#"
fn callee<'a, const A: (), T, const C: u8>() {}

fn f() {
    callee::<'static, $0
}
        "#,
            expect![[r#"
            fn callee<'a, const A: (), T, const C: u8>
            ('a, <const A: ()>, T, const C: u8)
        "#]],
        );
    }
}
