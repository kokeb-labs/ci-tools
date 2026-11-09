// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_3_OK_NEAR_HPP
#define KV_RULE_8_2_3_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_2_3::ok_near {

inline std::uint32_t read(std::uint32_t const* p) { return *p; }

inline std::uint32_t use(std::uint32_t* p) {
  *p = 1U;
  std::uint32_t const* view = static_cast<std::uint32_t const*>(p);
  return read(view);
}

}  // namespace kv::rule_8_2_3::ok_near

#endif  // KV_RULE_8_2_3_OK_NEAR_HPP
