load(
    "@build_bazel_rules_apple//apple:providers.bzl",
    "AppleBundleInfo",
    "AppleTestInfo",
)

def _rbe_test_sharding_impl(ctx):
    input_files = []
    args = []

    args.append(str(ctx.attr.jobs))

    test_symbol_file = ctx.attr.test_method_symbols[DefaultInfo].files.to_list()[0]
    args.append(test_symbol_file.path)
    input_files.append(test_symbol_file)

    args.append(ctx.file.time_estimates.path)
    input_files.append(ctx.file.time_estimates)

    shading_plan_json_file = ctx.actions.declare_file("test-sharding.json")
    args.append(shading_plan_json_file.path)

    for target in ctx.attr.no_sharding_test_targets:
        args.append(target.label.name)

    ctx.actions.run(
        inputs = input_files,
        outputs = [shading_plan_json_file],
        arguments = args,
        progress_message = "shard",
        executable = ctx.executable._rbe_test_sharding_py_exec,
    )

    return [
        DefaultInfo(
            files = depset([shading_plan_json_file]),
            runfiles = ctx.runfiles(
                files = input_files,
            ), 
        )
    ]

rbe_test_sharding = rule(
    implementation = _rbe_test_sharding_impl,
    attrs = {
        "test_targets": attr.label_list(),
        "no_sharding_test_targets": attr.label_list(),
        "time_estimates": attr.label(
            allow_single_file = True,
        ),
         "bluepill_config_template": attr.label(
            allow_single_file = True,
        ),
        "test_method_symbols": attr.label(
            allow_single_file = True,
        ),
        "jobs": attr.int(),
        "_rbe_test_sharding_py_exec": attr.label(
            default = Label(
                "//:rbe_test_sharding_py",
            ),
            executable = True,
            cfg = "host",
        ), 
    },   
)