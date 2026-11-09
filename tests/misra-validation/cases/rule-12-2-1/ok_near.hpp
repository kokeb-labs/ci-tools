// Near misses (near): flags in a whole-word member with masks.
#ifndef KV_RULE_12_2_1_OK_NEAR_HPP
#define KV_RULE_12_2_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_12_2_1::ok_near {

struct Flags {
  std::uint32_t bits = 0U;
};

inline constexpr std::uint32_t kReady = 0x01U;

inline bool ready(const Flags& f) { return (f.bits & kReady) != 0U; }

}  // namespace kv::rule_12_2_1::ok_near

#endif  // KV_RULE_12_2_1_OK_NEAR_HPP
