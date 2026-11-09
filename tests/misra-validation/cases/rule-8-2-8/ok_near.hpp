// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_8_OK_NEAR_HPP
#define KV_RULE_8_2_8_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_2_8::ok_near {

inline std::intptr_t signed_address(std::uint32_t const* word) { return reinterpret_cast<std::intptr_t>(word); }

}  // namespace kv::rule_8_2_8::ok_near

#endif  // KV_RULE_8_2_8_OK_NEAR_HPP
