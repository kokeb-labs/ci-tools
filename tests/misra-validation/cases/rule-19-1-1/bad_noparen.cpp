// Seeded violation: #if expands a macro that produces defined without parentheses.
#define KV_HAS_SAFE defined KV_SAFE

#if KV_HAS_SAFE  // seeded
namespace kv::rule_19_1_1::bad_noparen {
constexpr int kSafe = 1;
}  // namespace kv::rule_19_1_1::bad_noparen
#endif
