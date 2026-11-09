// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_4_OK_NEAR_HPP
#define KV_RULE_8_2_4_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_2_4::ok_near {

inline std::int32_t handler(std::int32_t code) { return code; }

using Narrow = std::int32_t (*)(std::int32_t);

inline bool usable(Narrow f) { return f != nullptr; }

inline std::int32_t call() {
  Narrow const f = &handler;
  return usable(f) ? f(1) : 0;
}

}  // namespace kv::rule_8_2_4::ok_near

#endif  // KV_RULE_8_2_4_OK_NEAR_HPP
