// Seeded violation: #undef of a macro that this file never defined.
#include <cstdint>

#undef KV_RULE_19_0_4_FROM_ELSEWHERE

namespace kv::rule_19_0_4::bad {

constexpr std::uint8_t kValue = 1U;

}  // namespace kv::rule_19_0_4::bad
