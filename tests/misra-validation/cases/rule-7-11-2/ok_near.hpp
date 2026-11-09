// Near misses: compliant code close to a violation.
#ifndef KV_RULE_7_11_2_OK_NEAR_HPP
#define KV_RULE_7_11_2_OK_NEAR_HPP

#include <array>
#include <cstdint>

namespace kv::rule_7_11_2::ok_near {

inline std::int32_t first_of(std::array<std::int32_t, 2> const& values) { return values[0]; }

inline std::int32_t through_data(std::int32_t const* p) { return *p; }

inline std::int32_t use() {
  std::array<std::int32_t, 2> const values{4, 5};
  return (first_of(values) == 4) ? through_data(values.data()) : 0;
}

}  // namespace kv::rule_7_11_2::ok_near

#endif  // KV_RULE_7_11_2_OK_NEAR_HPP
