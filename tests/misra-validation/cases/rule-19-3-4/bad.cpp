// Seeded violation: a macro parameter used in an expression without parentheses.
#include <cstdint>

#define KV_DOUBLE(x) (x * 2U)

namespace kv::rule_19_3_4::bad {

std::uint32_t twice(std::uint32_t a, std::uint32_t b) { return KV_DOUBLE(a + b); }  // seeded

}  // namespace kv::rule_19_3_4::bad
