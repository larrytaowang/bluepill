load(
    "@build_bazel_rules_apple//apple:providers.bzl",
    "AppleBundleInfo",
    "AppleTestInfo",
)

def _nm_symbol_extractor_impl(ctx):
    all_test_bundles = []
    test_target_bundle_dict = {}
    for test_target in ctx.attr.test_targets:
        test_target_name = test_target.label.name
        bundle_info = test_target[AppleBundleInfo]
        all_test_bundles.append(bundle_info.archive)

        test_target_bundle_dict[test_target_name] = bundle_info.archive.path
    test_target_symbols_str = repr(test_target_bundle_dict)

    out_file = ctx.actions.declare_file("nm_symbol_extract.json")
    args = [out_file.path, test_target_symbols_str]

    out_file = ctx.actions.declare_file("nm_symbol_extract.json")

    ctx.actions.run(
        inputs = all_test_bundles,
        outputs = [out_file],
        arguments = args,
        progress_message = "Use nm to extract symbols",
        executable = ctx.executable._nm_py_exec,
    )

    return [
        DefaultInfo(
            files = depset([out_file]), 
            runfiles = ctx.runfiles(
                files = all_test_bundles,
            ),
        )
    ]

nm_symbol_extractor = rule(
    implementation = _nm_symbol_extractor_impl,
    attrs = {
        "test_targets": attr.label_list(
            doc = """
A list of test targets to be bundled and run by bluepill.
""",
        ),
        "_nm_py_exec": attr.label(
            default = Label(
                "//:nm_extract_symbol_py",
            ),
            # allow_single_file = True,
            executable = True,
            cfg = "host",
        ), 
    },
)