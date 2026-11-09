// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_7_OK_NEAR_HPP
#define KV_RULE_8_2_7_OK_NEAR_HPP

#include <array>
#include <cstddef>
#include <cstdint>

namespace kv::rule_8_2_7::ok_near {

inline std::ptrdiff_t distance(std::uint32_t const* first, std::uint32_t const* last) { return last - first; }

inline bool before(std::array<std::uint32_t, 4> const& a) { return &a[0] < &a[1]; }

}  // namespace kv::rule_8_2_7::ok_near

#endif  // KV_RULE_8_2_7_OK_NEAR_HPP
