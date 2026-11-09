// Near miss: an unnamed signed one-bit bit-field is padding and cannot be read.
#ifndef KV_RULE_12_2_3_OK_UNNAMED_HPP
#define KV_RULE_12_2_3_OK_UNNAMED_HPP

#include <cstdint>

namespace kv::rule_12_2_3::ok_unnamed {

struct Bits {
  std::uint32_t low : 3;
  std::int32_t : 1;
  std::uint32_t high : 4;
};

[[nodiscard]] inline std::uint32_t both(const Bits& b) { return static_cast<std::uint32_t>(b.low) | static_cast<std::uint32_t>(b.high); }

}  // namespace kv::rule_12_2_3::ok_unnamed

#endif  // KV_RULE_12_2_3_OK_UNNAMED_HPP
