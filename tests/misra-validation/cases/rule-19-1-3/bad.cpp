// Seeded violation: #if tests an identifier that was never defined.
#if KV_LOG_LEVEL > 1
namespace kv::rule_19_1_3::bad {
constexpr int kVerbose = 1;
}
#endif
