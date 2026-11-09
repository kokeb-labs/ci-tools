// Compliant: explicit byte handling with shifts and masks, no union.
#ifndef KV_RULE_12_3_1_OK_HPP
#define KV_RULE_12_3_1_OK_HPP

#include <cstdint>

namespace kv::rule_12_3_1::ok {

inline std::uint8_t low_byte(std::uint32_t v) { return static_cast<std::uint8_t>(v & 0xFFU); }

}  // namespace kv::rule_12_3_1::ok

#endif  // KV_RULE_12_3_1_OK_HPP
