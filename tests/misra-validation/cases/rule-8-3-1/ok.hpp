// Compliant: the two's-complement negation is written as a subtraction from zero.
#ifndef KV_RULE_8_3_1_OK_HPP
#define KV_RULE_8_3_1_OK_HPP

#include <cstdint>

namespace kv::rule_8_3_1::ok {

inline std::uint32_t negate(std::uint32_t value) { return 0U - value; }

}  // namespace kv::rule_8_3_1::ok

#endif  // KV_RULE_8_3_1_OK_HPP
