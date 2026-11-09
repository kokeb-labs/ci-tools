// Seeded violation: a function-like macro where a constexpr function would do.
#include <cstdint>

#define KV_SQUARE(x) ((x) * (x))

namespace kv::rule_19_0_2::bad {

std::uint32_t area(std::uint32_t side) { return KV_SQUARE(side); }

}  // namespace kv::rule_19_0_2::bad
