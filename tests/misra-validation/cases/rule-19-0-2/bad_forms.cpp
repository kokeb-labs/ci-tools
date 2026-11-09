// Seeded violation: an empty-parameter and a variadic function-like macro.
#include <cstdint>

#define KV_NOW() 0U  // seeded: codeql
#define KV_FIRST(...) KV_FIRST_IMPL(__VA_ARGS__, 0U)  // seeded
#define KV_FIRST_IMPL(a, ...) (a)

namespace kv::rule_19_0_2::bad_forms {

std::uint32_t now() { return KV_NOW(); }
std::uint32_t first() { return KV_FIRST(3U, 4U); }

}  // namespace kv::rule_19_0_2::bad_forms
