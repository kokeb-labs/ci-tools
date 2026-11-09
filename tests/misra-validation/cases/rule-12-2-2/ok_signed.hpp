// Near miss: plain int and std::int32_t are signed integer types, which the guideline allows.
#ifndef KV_RULE_12_2_2_OK_SIGNED_HPP
#define KV_RULE_12_2_2_OK_SIGNED_HPP

#include <cstdint>

namespace kv::rule_12_2_2::ok_signed {

struct Offsets {
  int coarse : 4;
  std::int32_t fine : 6;
};

[[nodiscard]] inline bool ordered(const Offsets& o) { return o.coarse < o.fine; }

}  // namespace kv::rule_12_2_2::ok_signed

#endif  // KV_RULE_12_2_2_OK_SIGNED_HPP
