// Compliant: the conversion is explicit.
#ifndef KV_RULE_8_3_2_OK_HPP
#define KV_RULE_8_3_2_OK_HPP

#include <cstdint>

namespace kv::rule_8_3_2::ok {

inline std::int32_t widen(std::uint8_t value) { return static_cast<std::int32_t>(value); }

}  // namespace kv::rule_8_3_2::ok

#endif  // KV_RULE_8_3_2_OK_HPP
