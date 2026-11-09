// Compliant near miss: assert on a run-time value; the compile-time fact is a static_assert.
#ifndef KV_RULE_22_3_1_OK_RUNTIME_HPP
#define KV_RULE_22_3_1_OK_RUNTIME_HPP

#include <cassert>
#include <cstdint>

namespace kv::rule_22_3_1::ok_runtime {

inline constexpr std::int32_t kChannels = 8;
static_assert(kChannels > 0, "at least one channel");

[[nodiscard]] inline std::int32_t checked(std::int32_t channel) {
  assert((channel >= 0) && (channel < kChannels));
  return channel;
}

// A run-time range check of our own, named like assert, instead of the assert macro.
[[nodiscard]] inline bool assert_channel(std::int32_t channel) { return (channel >= 0) && (channel < kChannels); }

}  // namespace kv::rule_22_3_1::ok_runtime

#endif  // KV_RULE_22_3_1_OK_RUNTIME_HPP
