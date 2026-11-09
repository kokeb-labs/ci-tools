// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_3_2::bad_edge {

std::int32_t same(std::int32_t v) { return +v; }

using Fn = std::int32_t (*)();

Fn to_pointer() { return +[]() -> std::int32_t { return 1; }; }

}  // namespace kv::rule_8_3_2::bad_edge
