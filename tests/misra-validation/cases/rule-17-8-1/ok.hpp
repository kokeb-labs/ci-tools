#ifndef KV_RULE_17_8_1_OK_HPP
#define KV_RULE_17_8_1_OK_HPP

// Compliant: a plain overload takes the place of the specialisation.
#include <cstdint>

namespace kv::rule_17_8_1::ok {

template <typename T>
T clamp_low(T v) {
  return v;
}

inline std::int32_t clamp_low(std::int32_t v) { return (v < 0) ? 0 : v; }

}  // namespace kv::rule_17_8_1::ok

#endif  // KV_RULE_17_8_1_OK_HPP
