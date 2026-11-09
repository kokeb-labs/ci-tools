#ifndef KV_RULE_7_0_6_OK_HPP
#define KV_RULE_7_0_6_OK_HPP

// Compliant: assignments keep the type; a deliberate change is an explicit cast.
#include <cstdint>

namespace kv::rule_7_0_6::ok {

inline std::int16_t narrow(std::int32_t wide) {
  std::int32_t const bounded = (wide > 100) ? 100 : ((wide < -100) ? -100 : wide);
  std::int16_t const small = static_cast<std::int16_t>(bounded);
  return small;
}

}  // namespace kv::rule_7_0_6::ok

#endif  // KV_RULE_7_0_6_OK_HPP
