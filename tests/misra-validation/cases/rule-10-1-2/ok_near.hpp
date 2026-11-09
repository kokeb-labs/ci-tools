// Near misses (near): volatile only on register objects reached by reference.
#ifndef KV_RULE_10_1_2_OK_NEAR_HPP
#define KV_RULE_10_1_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_10_1_2::ok_near {

struct Registers {
  volatile std::uint32_t data;
  volatile std::uint32_t control;
};

inline std::uint32_t sample(Registers& regs) {
  regs.control = 1U;
  const std::uint32_t value = regs.data;
  return value;
}

// A reference to a volatile object is permitted: the parameter itself is not volatile.
inline std::uint32_t peek(const volatile std::uint32_t& reg) { return reg; }

}  // namespace kv::rule_10_1_2::ok_near

#endif  // KV_RULE_10_1_2_OK_NEAR_HPP
