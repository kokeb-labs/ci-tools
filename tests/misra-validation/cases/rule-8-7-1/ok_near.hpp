// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_7_1_OK_NEAR_HPP
#define KV_RULE_8_7_1_OK_NEAR_HPP

#include <array>
#include <cstdint>

namespace kv::rule_8_7_1::ok_near {

inline std::uint8_t const* end_of(std::array<std::uint8_t, 4> const& a) { return a.data() + 4; }

inline std::uint8_t const* last_of(std::array<std::uint8_t, 4> const& a) { return a.data() + 3; }

}  // namespace kv::rule_8_7_1::ok_near

#endif  // KV_RULE_8_7_1_OK_NEAR_HPP
