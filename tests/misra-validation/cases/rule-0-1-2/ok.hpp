// Compliant: results are used or explicitly discarded.
#ifndef KV_RULE_0_1_2_OK_HPP
#define KV_RULE_0_1_2_OK_HPP

#include <cstdint>

namespace kv::rule_0_1_2::ok {

inline std::uint32_t next(std::uint32_t v) { return v | 1U; }

inline std::uint32_t step(std::uint32_t v) { return next(v); }

inline void touch(std::uint32_t v) {
  static_cast<void>(next(v));  // deliberately discarded: only the call matters here
}

}  // namespace kv::rule_0_1_2::ok

#endif  // KV_RULE_0_1_2_OK_HPP
