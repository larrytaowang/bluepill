load(
    "@build_bazel_rules_apple//apple:providers.bzl",
    "AppleBundleInfo",
    "AppleTestInfo",
)

def _rbe_test_sharding_impl(ctx):
    pass

rbe_test_sharding = rule(
    implementation = _rbe_test_sharding_impl,
    "test_targets": attr.label_list(
            doc = """
A list of test targets to be bundled and run by bluepill.
""",
    ),

)
