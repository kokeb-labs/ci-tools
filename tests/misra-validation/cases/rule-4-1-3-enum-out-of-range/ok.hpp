// Compliant: the same task without the undefined behaviour.
#ifndef KV_RULE_4_1_3_ENUM_OUT_OF_RANGE_OK_HPP
#define KV_RULE_4_1_3_ENUM_OUT_OF_RANGE_OK_HPP

#include <cstdint>

namespace kv::rule_4_1_3_enum_out_of_range::ok {

enum class Mode : std::uint8_t { kOff, kOn };

inline Mode to_mode(bool on) {
  Mode m = Mode::kOff;
  if (on) {
    m = Mode::kOn;
  }
  return m;
}

}  // namespace kv::rule_4_1_3_enum_out_of_range::ok

#endif  // KV_RULE_4_1_3_ENUM_OUT_OF_RANGE_OK_HPP
