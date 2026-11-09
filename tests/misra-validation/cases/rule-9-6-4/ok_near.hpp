// Near misses (near): [[noreturn]] chains and plain void functions.
#ifndef KV_RULE_9_6_4_OK_NEAR_HPP
#define KV_RULE_9_6_4_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_9_6_4::ok_near {

[[noreturn]] inline void spin(volatile std::uint32_t& sink) {
  for (;;) {
    sink = 1U;
  }
}

[[noreturn]] inline void fail(volatile std::uint32_t& sink) { spin(sink); }

inline void reset(std::uint32_t& value) { value = 0U; }

}  // namespace kv::rule_9_6_4::ok_near

#endif  // KV_RULE_9_6_4_OK_NEAR_HPP
