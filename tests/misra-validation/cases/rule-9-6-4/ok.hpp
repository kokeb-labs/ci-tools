// Compliant: the [[noreturn]] function never returns on any path.
#ifndef KV_RULE_9_6_4_OK_HPP
#define KV_RULE_9_6_4_OK_HPP

#include <cstdint>

namespace kv::rule_9_6_4::ok {

[[noreturn]] inline void halt(volatile std::uint32_t& sink) {
  for (;;) {
    sink = 0U;
  }
}

}  // namespace kv::rule_9_6_4::ok

#endif  // KV_RULE_9_6_4_OK_HPP
