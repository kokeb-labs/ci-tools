// Near miss: a plain aggregate, no special member declared.
#ifndef KV_RULE_15_0_1_OK_ZERO_HPP
#define KV_RULE_15_0_1_OK_ZERO_HPP

#include <cstdint>

namespace kv::rule_15_0_1::ok_zero {

struct Sample {
  std::uint16_t raw = 0U;
  std::uint8_t channel = 0U;
};

[[nodiscard]] inline Sample copy(const Sample& s) { return s; }

}  // namespace kv::rule_15_0_1::ok_zero

#endif  // KV_RULE_15_0_1_OK_ZERO_HPP
