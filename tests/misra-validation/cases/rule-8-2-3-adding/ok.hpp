// Compliant: the const_cast only adds const.
#ifndef KV_RULE_8_2_3_ADDING_OK_HPP
#define KV_RULE_8_2_3_ADDING_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_3_adding::ok {

inline std::uint32_t set_and_read(std::uint32_t* value) {
  *value = 1U;
  const std::uint32_t* view = const_cast<const std::uint32_t*>(value);
  return *view;
}

}  // namespace kv::rule_8_2_3_adding::ok

#endif  // KV_RULE_8_2_3_ADDING_OK_HPP
