// Near misses (near): a declaration that leaves the parameter unnamed.
#ifndef KV_RULE_13_3_3_OK_NEAR_HPP
#define KV_RULE_13_3_3_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_13_3_3::ok_near {

std::uint32_t scaled(std::uint32_t);

inline std::uint32_t scaled(std::uint32_t value) { return value << 1U; }

}  // namespace kv::rule_13_3_3::ok_near

#endif  // KV_RULE_13_3_3_OK_NEAR_HPP
