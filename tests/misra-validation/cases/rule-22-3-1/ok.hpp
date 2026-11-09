// Compliant: the compile-time fact is a static_assert.
#ifndef KV_RULE_22_3_1_OK_HPP
#define KV_RULE_22_3_1_OK_HPP

#include <cstdint>

namespace kv::rule_22_3_1::ok {

static_assert(sizeof(std::int32_t) == 4U, "32-bit registers");

[[nodiscard]] inline std::int32_t widen(std::int16_t value) { return value; }

}  // namespace kv::rule_22_3_1::ok

#endif  // KV_RULE_22_3_1_OK_HPP
