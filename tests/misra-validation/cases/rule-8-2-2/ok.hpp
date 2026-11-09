// Compliant: the conversion is a static_cast.
#ifndef KV_RULE_8_2_2_OK_HPP
#define KV_RULE_8_2_2_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_2::ok {

inline std::int32_t narrow(std::int64_t wide) { return static_cast<std::int32_t>(wide); }

}  // namespace kv::rule_8_2_2::ok

#endif  // KV_RULE_8_2_2_OK_HPP
