// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_3_ADDING_OK_NEAR_HPP
#define KV_RULE_8_2_3_ADDING_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_2_3_adding::ok_near {

inline bool add_volatile(std::uint32_t* value) {
  std::uint32_t volatile* v = const_cast<std::uint32_t volatile*>(value);
  std::uint32_t const volatile* cv = const_cast<std::uint32_t const volatile*>(value);
  *v = 1U;
  return *cv == 1U;
}

}  // namespace kv::rule_8_2_3_adding::ok_near

#endif  // KV_RULE_8_2_3_ADDING_OK_NEAR_HPP
